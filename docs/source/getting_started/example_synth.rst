综合入门
--------


本页将逐步讲解预打包的 iCE40 FPGA 综合脚本——`synth_ice40`。我们会带着一个简单的
设计走完每一步，观察被调用的命令以及它们对设计做了什么。尽管 `synth_ice40` 专用于
iCE40 平台，但我们将讨论的大多数操作在多数 FPGA 综合脚本中都是通用的。因此，无论
实际使用哪种架构，本文档都能为理解 Yosys 中综合是如何进行的打下良好基础。

.. seealso:: 高级用法文档见
   :doc:`/using_yosys/synthesis/synth`

演示设计
~~~~~~~~


.. role:: yoscrypt(code)
   :language: yoscrypt

首先，我们快速看一下将要综合的设计：

.. todo:: 考虑是否要像这样包含整个设计（约 77 行）

.. literalinclude:: /code_examples/fifo/fifo.v
   :language: Verilog
   :linenos:
   :caption: :file:`fifo.v`
   :name: fifo-v

.. todo:: fifo.v 的说明

尽管开源的 `read_verilog` 前端在处理合法 Verilog 输入方面通常做得不错，但它提供
的错误处理与错误报告并不理想。强烈建议在运行 Yosys 之前使用 `verilator`_ 之类的
外部工具。我们可以通过调用 ``verilator --lint-only fifo.v`` 快速检查设计的 Verilog
语法。

.. _verilator: https://www.veripool.org/verilator/

加载设计
~~~~~~~~


现在把设计加载进 Yosys。在命令行中，我们可以调用 ``yosys fifo.v``。这会打开一个
交互式 Yosys shell 会话，立即解析 :ref:`fifo-v` 中的代码，并将其转换为抽象语法树
（AST）。如果你对这一过程感兴趣，:doc:`/yosys_internals/flow/verilog_frontend`
文档中有更多信息。目前只需知道，这样做是为了简化设计的后续处理。你应该会看到类似
下面的内容：

.. literalinclude:: /code_examples/fifo/fifo.out
   :language: console
   :start-at: $ yosys fifo.v
   :end-before: echo on

.. seealso:: 高级用法文档见
   :doc:`/using_yosys/more_scripting/load_design`

细化
~~~~


现在已进入交互式 shell，可以直接调用 Yosys 命令了。我们的总体目标是调用
:yoscrypt:`synth_ice40 -top fifo`，但眼下我们会逐条运行各个命令，以便更好地体会每
一部分如何参与整个流程。我们还将从单个模块开始：``addr_gen``。

`synth_ice40` 的 `help` 输出底部列出了该脚本调用的全部命令。我们从标为 ``begin``
的小节开始：

.. literalinclude:: /code_examples/macro_commands/synth_ice40.ys
   :language: yoscrypt
   :start-after: begin:
   :end-before: flatten:
   :dedent:
   :caption: ``begin`` 小节
   :name: synth_begin

:yoscrypt:`read_verilog -D ICE40_HX -lib -specify +/ice40/cells_sim.v` 会加载
iCE40 单元模型，使我们能在设计中引用平台相关的 IP 模块。PLL 就是常见的例子：我们
可能需要直接引用 ``SB_PLL40_CORE``，而不能指望后续的映射 pass（处理流程）。由于
我们的简单设计没有用到这些 IP 模块，现在可以先跳过这条命令。不过一旦开始映射到硬件，
仍然需要这些单元模型，所以稍后还得加载它们。

.. note::

   ``+/`` 是对 Yosys ``share`` 目录的动态引用。默认情况下它是
   ``/usr/local/share/yosys``。如果使用从源码目录本地构建的 Yosys，那么它就是同一
   目录下的 ``share`` 文件夹。

.. _addr_gen_example:

addr_gen 模块
^^^^^^^^^^^^^

既然只是入门，我们不妨从 :yoscrypt:`hierarchy -top addr_gen` 开始。这条命令声明
顶层模块是 ``addr_gen``，其他模块都可以丢弃。

.. literalinclude:: /code_examples/fifo/fifo.v
   :language: Verilog
   :start-at: module addr_gen
   :end-at: endmodule //addr_gen
   :lineno-match:
   :caption: ``addr_gen`` 模块源码
   :name: addr_gen-v

.. note::

   `hierarchy` 应该始终是读取设计之后的第一条命令。通过指定顶层模块，`hierarchy`
   还会在其上设置 ``(* top *)`` 属性。其他需要知道哪个模块是顶层的命令会用到这个
   属性。

.. use doscon for a console-like display that supports the `yosys> [command]` format.

.. literalinclude:: /code_examples/fifo/fifo.out
   :language: doscon
   :start-at: yosys> hierarchy -top addr_gen
   :end-before: yosys> select
   :caption: :yoscrypt:`hierarchy -top addr_gen` 的输出
   :name: hierarchy_output

现在我们的 ``addr_gen`` 电路如下所示：

.. figure:: /_images/code_examples/fifo/addr_gen_hier.svg
   :class: width-helper invert-helper
   :name: addr_gen_hier

   `hierarchy` 之后的 ``addr_gen`` 模块

像 ``addr + 1`` 和 ``addr == MAX_DATA-1`` 这样的简单运算可以从 :ref:`addr_gen-v`
中的 ``always @`` 块里提取出来，这就得到了图中高亮的 `$add` 和 `$eq` 单元。但控制
逻辑（例如 ``if .. else``）和存储元件（例如 ``addr <= 0``）就没那么直接了。它们会
被放进“过程”（processes）中，在原理图里显示为 ``PROC``。注意第二行标出的是对应
``always @`` 块起止行的行号。对于 ``initial`` 块，我们看到的 ``PROC`` 则指向第 0 行。

为了处理它们，现在介绍下一条命令：:cmd:title:`proc`。`proc` 和 `synth_ice40` 一样
是一条宏命令。它并不直接修改设计，而是调用一系列其他命令。就 `proc` 而言，这些子命令
的作用是把过程的行为逻辑转换为多路复用器和寄存器。我们看看运行它会发生什么。目前
我们先调用 :yoscrypt:`proc -noopt`，以阻止一些通常会发生的自动优化。

.. figure:: /_images/code_examples/fifo/addr_gen_proc.svg
   :class: width-helper invert-helper
   :name: addr_gen_proc

   :yoscrypt:`proc -noopt` 之后的 ``addr_gen`` 模块

现在出现了几个由 ``always @`` 生成的新单元，它们已被高亮。``if`` 语句现在用 `$mux`
单元建模，而寄存器使用 `$adff` 单元。查看终端输出，还能看到被调用的各个 ``proc_*``
命令。我们会在 :doc:`/using_yosys/synthesis/proc` 中更详细地逐一介绍它们。

注意 :ref:`addr_gen_proc` 的左上角有一条悬空信号线，它来自把 0 初始赋值给 ``addr``
信号线的操作。然而这个初始赋值是不可综合的，因此在生成物理硬件之前需要把它清理掉。
现在就可以调用 `clean` 来做这件事。我们还会调用 `opt_expr`，它通常位于 `proc` 的
末尾。用冒号加空格分隔两条命令，就能同时调用它们：:yoscrypt:`opt_expr; clean`。

.. figure:: /_images/code_examples/fifo/addr_gen_clean.svg
   :class: width-helper invert-helper
   :name: addr_gen_clean

   :yoscrypt:`opt_expr; clean` 之后的 ``addr_gen`` 模块

你可能还会注意到，高亮的 `$eq` 单元输入从 ``255`` 变成了 ``8'11111111``。常量按
``<bit_width>'<bits>`` 的格式表示，而 32 位宽的值改用十进制数表示。这表明该常量输入
已从 32 位宽缩减为 8 位宽。这是运行 `opt_expr` 的副作用，它会执行常量折叠和简单的
表达式重写。关于其原因的更多内容，请参阅 :doc:`/using_yosys/synthesis/opt` 以及
:ref:`关于 opt_expr 的一节 <adv_opt_expr>`。

.. note::

   在任何命令后加两个分号也能调用 :cmd:title:`clean`，例如我们可以用
   :yoscrypt:`opt_expr;;` 代替 :yoscrypt:`opt_expr; clean`。你可能会注意到有些脚本
   会在每行末尾写 ``;;``。在查看中间产物之前运行 `clean` 是有好处的：它可以移除电路
   中残留的、未连接的部分，某些情况下还能减少后续命令所需的处理量。

.. todo:: 考虑为 adff 之类的术语加一个简短术语表

.. seealso:: 高级用法文档见

   - :doc:`/using_yosys/synthesis/proc`
   - :doc:`/using_yosys/synthesis/opt`

完整示例
^^^^^^^^

现在回过头来检查完整的设计，使用 :yoscrypt:`hierarchy -check -top fifo`。在这里
传入 ``-check`` 选项，等于告诉 `hierarchy` 命令：如果设计中存在任何没有实现、又不是
黑盒的模块，它就应该返回错误。

注意，如果现在就运行这条命令会报错。因为除 ``addr_gen`` 之外的所有模块都已经被我们
移除了。我们可以重启 shell 会话，不过我们改用两条新命令：

- :cmd:title:`design`，以及
- :cmd:title:`read_verilog`。

.. literalinclude:: /code_examples/fifo/fifo.out
   :language: doscon
   :start-at: design -reset
   :end-before: yosys> proc
   :caption: 重新加载 :file:`fifo.v` 并运行 :yoscrypt:`hierarchy -check -top fifo`

注意这次我们没有看到那些 ``$abstract`` 模块吧？这是因为运行 ``yosys fifo.v`` 时，
Yosys 调用的第一条命令是 :yoscrypt:`read_verilog -defer fifo.v`。其中的 ``-defer``
选项告诉 `read_verilog` 只读取抽象语法树，把真正的编译推迟到后面的 `hierarchy` 命令。
当模块的默认参数会产生不可综合的非法代码时，这种做法很有用。这也是 Yosys 会自动推迟
编译的原因，同时也是 hierarchy 应当始终是加载设计之后第一条命令的原因之一。如果我们
确信设计不会遇到这个问题，就可以省略 ``-defer``。

.. todo:: `hierarchy` 的失败情况

.. note::

   命令输出前的编号会随每条命令的执行而递增。如果你的编号和我们的不一致，不必担心！
   你看到的输出来自生成本文插图的同一脚本，该脚本在源码中以 :file:`fifo.ys` 提供。
   其中还运行了一些你看不到的额外命令，不过你可以自行尝试它们，或者随意试用不同的
   命令。你随时可以通过调用 ``exit`` 或按 :kbd:`ctrl+d` （即 EOF）退出、再重新启动
   Yosys 交互终端，从干净的状态重新开始。:kbd:`ctrl+c` （即 SIGINT）也会结束终端
   会话，但它返回的是错误码，而不是正常退出。

现在还可以运行 `proc` 来完成 :ref:`synth_begin` 的全部内容。由于设计原理图相当大，
我们只展示 ``rdata`` 输出的数据通路。如果你想自己看整个设计，可以用
:cmd:title:`show`。注意 `show` 命令一次只能处理单个模块，所以可能需要这样调用：
:yoscrypt:`show fifo`。:doc:`/getting_started/scripting_intro` 中的 :ref:`show_intro`
一节介绍了更多 `show` 的用法。

.. figure:: /_images/code_examples/fifo/rdata_proc.svg
   :class: width-helper invert-helper
   :name: rdata_proc

   `proc` 之后的 ``rdata`` 输出

高亮的 ``fifo_reader`` 块中包含一个我们先前看过的 :ref:`addr_gen_proc` 实例。注意
其类型显示为 ``$paramod\\addr_gen\\MAX_DATA=s32'...``。这是一个“参数化模块”：即
``addr_gen`` 模块的一个实例，其中 ``MAX_DATA`` 参数被设为给定值。

另一个高亮的块是 `$memrd` 单元。在综合的这一阶段，我们还不知道最终会实现哪种存储器，
但我们*确实*知道 ``rdata <= data[raddr];`` 可以实现为从存储器读取。注意这里的
`$memrd` 单元是异步的，时钟和使能信号都未定义，在图中以 ``1'x`` 输入表示。

.. seealso:: 高级用法文档见
   :doc:`/using_yosys/synthesis/proc`

展平
~~~~


在综合流程的这一阶段，还有几条别的命令可以运行。在 `synth_ice40` 中我们会看到这些：

.. literalinclude:: /code_examples/macro_commands/synth_ice40.ys
   :language: yoscrypt
   :start-after: flatten:
   :end-before: coarse:
   :dedent:
   :name: synth_flatten
   :caption: ``flatten`` 小节

我们先运行 `check`。它不会改动设计，但能发现一些显然会在后续导致错误的问题。在这里
调用它可以让我们尽早失败，而不是在明知不可能的事情上浪费时间。接下来是 `flatten`。
像这样展平设计，可以让原本会被遗漏的跨模块优化得以进行。我们在自己的设计上运行
:yoscrypt:`flatten;;`。

.. literalinclude:: /code_examples/fifo/fifo.out
   :language: doscon
   :start-at: yosys> flatten
   :end-before: yosys> select
   :name: flat_clean
   :caption: :yoscrypt:`flatten;;` 的输出

.. figure:: /_images/code_examples/fifo/rdata_flat.svg
   :class: width-helper invert-helper
   :name: rdata_flat

   :yoscrypt:`flatten;;` 之后的 ``rdata`` 输出

.. role:: yoterm(code)
   :language: doscon

各部分的位置有些变动，但可以看到先前 :ref:`addr_gen_proc` 中的内容已经替换了
:ref:`rdata_proc` 里的 ``fifo_reader`` 块。我们还能看到 ``addr`` 输出已被重命名为
:file:`fifo_reader.addr`，并与馈入 `$memrd` 单元的 ``raddr`` 信号线合并。这次信号线
合并在调用 `clean` 时发生，我们可以在 :ref:`flat_clean` 中看到。

.. note::

   `flatten` 和 `clean` 通常会合并为一段 :yoterm:`yosys> flatten;;` 输出，但这里
   它们分开出现，这是使用 `echo` 生成终端样式输出的副作用。

取决于目标架构，综合的这一阶段还可能运行诸如带 ``-logic`` 选项的 `tribuf` 以及
`deminout` 这类命令。它们分别移除三态结构和 inout 结构，替换为适合映射到 FPGA 的
逻辑。由于我们的示例中没有这类结构，运行这些命令不会改变设计。

粗粒度表示
~~~~~~~~~~


在这一阶段，设计处于粗粒度表示。它看起来仍然容易辨认，单元是宽度可参数化的字级
运算器。正是综合的这一阶段，我们进行常量传播、表达式重写以及裁剪信号线中未使用的
部分等操作。

我们也会在这一阶段转换有限状态机（FSM）以及 DSP、存储器之类的硬核模块。这类元件
必须从设计中的模式推断出来，并且各自有专门的 pass。模式的检测还可能受到此前所做的
优化和其他变换的影响。

.. note::

   虽然 iCE40 流程有 :ref:`synth_flatten` 一节，并把 `proc` 放在
   :ref:`synth_begin` 中，但有些综合脚本会把它们放在本节。

第 1 部分
^^^^^^^^^

在 iCE40 流程中，我们从以下命令开始：

.. literalinclude:: /code_examples/macro_commands/synth_ice40.ys
   :language: yoscrypt
   :start-after: coarse:
   :end-before: wreduce
   :dedent:
   :caption: ``coarse`` 小节（第 1 部分）
   :name: synth_coarse1

我们已经见过 `opt_expr` 和 `check`；`opt_clean` 与 `clean` 相同，只是输出更详细。
接下来是 :yoscrypt:`opt -nodffe -nosdff`，它对设计执行一组简单优化。这条命令还会
确保只包含特定子集的 FF 类型，为下一条命令 :cmd:title:`fsm` 做准备。`opt` 和 `fsm`
都是宏命令，分别在 :doc:`/using_yosys/synthesis/opt` 和
:doc:`/using_yosys/synthesis/fsm` 中有更详细的介绍。

到目前为止，``rdata`` 的数据通路自 :ref:`rdata_flat` 以来一直保持不变。不过接下来
对 `opt` 的调用确实带来了变化。具体来说，不带 ``-nodffe -nosdff`` 选项的 `opt_dff`
调用能够把其中一个 `$mux` 单元折叠进 `$adff`，形成 `$adffe` 单元；如下方高亮所示：

.. literalinclude:: /code_examples/fifo/fifo.out
   :language: doscon
   :start-at: yosys> opt_dff
   :end-before: yosys> select
   :caption: `opt_dff` 的输出

.. figure:: /_images/code_examples/fifo/rdata_adffe.svg
   :class: width-helper invert-helper
   :name: rdata_adffe

   `opt_dff` 之后的 ``rdata`` 输出

.. seealso:: 高级用法文档见

   - :doc:`/using_yosys/synthesis/fsm`
   - :doc:`/using_yosys/synthesis/opt`

第 2 部分
^^^^^^^^^

下一组命令执行一系列优化：

.. literalinclude:: /code_examples/macro_commands/synth_ice40.ys
   :language: yoscrypt
   :start-at: wreduce
   :end-before: macc-only
   :dedent:
   :caption: ``coarse`` 小节（第 2 部分）
   :name: synth_coarse2

首先是 :cmd:title:`wreduce`。运行它会得到以下结果：

.. literalinclude:: /code_examples/fifo/fifo.out
   :language: doscon
   :start-at: yosys> wreduce
   :end-before: yosys> select
   :caption: `wreduce` 的输出

观察 ``rdata`` 的数据通路，这些宽度缩减中最相关的是影响
``fifo.$flatten\fifo_reader.$add$fifo.v`` 的那些。那就是对 fifo_reader 地址进行
递增的 `$add` 单元。查看原理图可以看到，该单元的输出现在已经改变。

.. todo:: 等待修复 `wreduce` 和/或 `opt_clean` 中的 bug

.. figure:: /_images/code_examples/fifo/rdata_wreduce.svg
   :class: width-helper invert-helper
   :name: rdata_wreduce

   `wreduce` 之后的 ``rdata`` 输出

接下来两条（新）命令是 :cmd:title:`peepopt` 和 :cmd:title:`share`。它们都不影响
我们的设计，而且在 :doc:`/using_yosys/synthesis/opt` 中有更详细的介绍，所以先跳过。
:yoscrypt:`techmap -map +/cmp2lut.v -D LUT_WIDTH=4` 通过把某些比较运算符转换为 LUT
来优化它们。`techmap` 的用法在 :doc:`/using_yosys/synthesis/techmap_synth` 中有更多
介绍。

我们要运行的下一条命令是
:cmd:title:`memory_dff`。

.. literalinclude:: /code_examples/fifo/fifo.out
   :language: doscon
   :start-at: yosys> memory_dff
   :end-before: yosys> select
   :caption: `memory_dff` 的输出

.. figure:: /_images/code_examples/fifo/rdata_memrdv2.svg
   :class: width-helper invert-helper
   :name: rdata_memrdv2

   `memory_dff` 之后的 ``rdata`` 输出

顾名思义，`memory_dff` 把输出端的 `$dff` 合并进了 `$memrd` 单元，并将其转换为
`$memrd_v2` （高亮所示）。它还把 ``CLK`` 端口连接到 ``clk`` 输入，因为现在这是一次
同步存储器读，并带有相应的使能（``EN=1'1``）和复位（``ARST=1'0`` 和
``SRST=1'0``）输入。

.. seealso:: 高级用法文档见

   - :doc:`/using_yosys/synthesis/opt`
   - :doc:`/using_yosys/synthesis/techmap_synth`
   - :doc:`/using_yosys/synthesis/memory`

第 3 部分
^^^^^^^^^

`synth_ice40` 流程的第三部分是一系列用于映射到 DSP 的命令。默认情况下，iCE40 流程
不会映射到硬件 DSP 块，只有在以 ``-dsp`` 标志调用时才会执行：:yoscrypt:`synth_ice40
-dsp`。虽然我们的示例中没有任何可以映射到 DSP 的内容，我们仍然可以快速看一下这些
命令并说明它们的作用。

.. literalinclude:: /code_examples/macro_commands/synth_ice40.ys
   :language: yoscrypt
   :start-at: macc-only
   :end-at: chtype
   :dedent:
   :caption: ``coarse`` 小节（第 3 部分）
   :name: synth_coarse3

前三条命令重新结合乘积之和。:yoscrypt:`alumacc -macc-only` 把每条 `$mul` 和 `$add`
单元链收集到一个 `$macc_v2` 单元中，:yoscrypt:`maccmap -unmap` 再把它直接还原为
`$mul` 和 `$add` 单元，但排成一条把普通加数放在前面的链，这样每个乘法器都有自己
专属的加法器供 `ice40_dsp` 吸收。随后 `opt_clean` 移除原来的单元。

:yoscrypt:`wreduce t:$mul` 再次执行宽度缩减，这次只针对类型为 `$mul` 的单元。
:yoscrypt:`techmap -map +/mul2dsp.v -map +/ice40/dsp_map.v ... -D DSP_NAME=$__MUL16X16`
使用 `techmap` 把 `$mul` 单元映射为 ``$__MUL16X16``，后者再被映射到 iCE40 的
``SB_MAC16``。任何无法转换为 ``$__MUL16X16`` 的乘法器都会先被重新标记为
``$__soft_mul``，再由 `chtype` 改回 `$mul`。

在 mul2dsp 转换过程中，一些中间信号会被标记上 ``mul2dsp`` 属性。通过调用
:yoscrypt:`select a:mul2dsp`，我们把后续命令限制为只作用于这些信号所用到的单元和
信号线。`setattr` 移除此时已不再需要的 ``mul2dsp`` 属性。常量折叠和简单表达式重写
所用的 `opt_expr` 我们已经见过，``-fine`` 选项只是启用更多细粒度优化。之后再执行
最后一次宽度缩减，并清除选择集。

.. todo:: ``ice40_dsp`` 由 pmgen 生成

最后是 `ice40_dsp`：与上一节看到的 `memory_dff` 命令类似，它会把周边的寄存器合并进
``SB_MAC16`` 单元。这不仅包括输入/输出寄存器，还包括流水线寄存器，甚至在适用时包括
后置加法器：从而把一次乘法加一次加法合并为一次乘加。

.. seealso:: 高级用法文档见
   :doc:`/using_yosys/synthesis/techmap_synth`

第 4 部分
^^^^^^^^^

这就来到了 iCE40 综合流程的第四部分，也是最后一部分：

.. literalinclude:: /code_examples/macro_commands/synth_ice40.ys
   :language: yoscrypt
   :start-after: chtype
   :end-before: map_ram:
   :dedent:
   :caption: ``coarse`` 小节（第 4 部分）
   :name: synth_coarse4

此前每种算术运算都有各自的单元，例如 `$add`，现在我们希望把它们提取到 `$alu` 和
`$macc_v2` 单元中，这有助于发现复用逻辑的机会。我们通过运行 `alumacc` 来实现这一点，
可以看到它在示例设计中产生了以下变化：

.. literalinclude:: /code_examples/fifo/fifo.out
   :language: doscon
   :start-at: yosys> alumacc
   :end-before: yosys> select
   :caption: `alumacc` 的输出

.. figure:: /_images/code_examples/fifo/rdata_alumacc.svg
   :class: width-helper invert-helper
   :name: rdata_alumacc

   `alumacc` 之后的 ``rdata`` 输出

这些单元插入之后，对 `opt` 的调用就可以合并那些现在变得相同、但之前可能因为 `$add`
与 `$sub` 的差异等原因而被漏掉的单元。

这一部分另一条新命令是 :cmd:title:`memory`。`memory` 也是一条宏命令，我们会在
:doc:`/using_yosys/synthesis/memory` 中更详细地研究它。就本文档而言，我们只关注与
本例最相关的一步：`memory_collect`。在此之前，存储器读和存储器写是完全不相交的单元，
只是在抽象层面上操作同一个存储器。`memory_collect` 把一个存储器块的所有读和写合并到
单个单元中。

.. figure:: /_images/code_examples/fifo/rdata_coarse.svg
   :class: width-helper invert-helper
   :name: rdata_coarse

   `memory_collect` 之后的 ``rdata`` 输出

查看运行 `memory_collect` 之后的原理图，可以看到 `$memrd_v2` 单元已被替换为名为
``data`` 的 `$mem_v2` 单元，这个名字与我们在 :ref:`fifo-v` 中使用的相同。此前地址
和使能共用一组信号，现在则有一组用于读（``RD_*``），一组用于写（``WR_*``），并且
同时具有 ``WR_DATA`` 输入和 ``RD_DATA`` 输出。

.. seealso:: 高级用法文档见

   - :doc:`/using_yosys/synthesis/opt`
   - :doc:`/using_yosys/synthesis/memory`

最后说明
^^^^^^^^

现在我们已经走到粗粒度表示的终点；其实在加载设计后运行
:yoscrypt:`synth_ice40 -top fifo -run :map_ram` 也能到达这里。
:yoscrypt:`-run <from_label>:<to_label>` 选项在 ``<from_label>`` 为空时从
:ref:`synth_begin` 开始，而 ``<to_label>`` 则一直运行到并包含 :ref:`map_ram`。

硬件映射
~~~~~~~~


其余各节分别映射不同类型的硬件，与前面的小节相比更加依赖具体架构。因此我们只会非常
简要地看看每一节。

如果你之前跳过了 :yoscrypt:`read_verilog -D ICE40_HX -lib -specify
+/ice40/cells_sim.v`，现在补上。

存储器块
^^^^^^^^

映射到硬存储器块要用 `memory_libmap` 和 `techmap` 的组合。

.. literalinclude:: /code_examples/macro_commands/synth_ice40.ys
   :language: yoscrypt
   :start-after: map_ram:
   :end-before: map_ffram:
   :dedent:
   :name: map_ram
   :caption: ``map_ram`` 小节

.. figure:: /_images/code_examples/fifo/rdata_map_ram.svg
   :class: width-helper invert-helper
   :name: rdata_map_ram

   :ref:`map_ram` 之后的 ``rdata`` 输出

:ref:`map_ram` 把通用 `$mem_v2` 转换为 iCE40 的 ``SB_RAM40_4K`` （高亮所示）。我们还
能看到存储器地址已被重新映射，数据位也经过了重排（或 swizzle）。现在还多了一个控制
``rdata`` 值的 `$mux` 单元。在 :ref:`fifo-v` 中我们把存储器写成先读后写，而
``SB_RAM40_4K`` 在同一周期内对同一地址读写时具有未定义行为。因此，额外加入了逻辑，
使生成的电路与 Verilog 的行为一致。:ref:`no_rw_check` 说明了我们如何反过来修改
Verilog 来匹配硬件。

如果我们在 `debug` 命令下运行 `memory_libmap`，就能看到识别出的映射候选，以及各自
的代价和哪些逻辑需要模拟实现。

.. literalinclude:: /code_examples/fifo/fifo.libmap
   :language: doscon
   :lines: 2, 6-

``$__ICE40_RAM4K_`` 单元定义在文件 |techlibs/ice40/brams.txt|_ 中，到
``SB_RAM40_4K`` 的映射由 `techmap` 使用 |techlibs/ice40/brams_map.v|_ 完成。随后
残留的存储器单元会由 `memory_map` 转换为触发器（``logic fallback``）。

.. |techlibs/ice40/brams.txt| replace:: :file:`techlibs/ice40/brams.txt`
.. _techlibs/ice40/brams.txt: https://github.com/YosysHQ/yosys/tree/main/techlibs/ice40/brams.txt
.. |techlibs/ice40/brams_map.v| replace:: :file:`techlibs/ice40/brams_map.v`
.. _techlibs/ice40/brams_map.v: https://github.com/YosysHQ/yosys/tree/main/techlibs/ice40/brams_map.v

.. literalinclude:: /code_examples/macro_commands/synth_ice40.ys
   :language: yoscrypt
   :start-after: map_ffram:
   :end-before: map_gates:
   :dedent:
   :name: map_ffram
   :caption: ``map_ffram`` 小节

.. figure:: /_images/code_examples/fifo/rdata_map_ffram.svg
   :class: width-helper invert-helper
   :name: rdata_map_ffram

   :ref:`map_ffram` 之后的 ``rdata`` 输出

.. note::

   ``RDATA`` 输出端口（高亮处）上出现的视觉杂乱，是 `opt_clean` 作用于重排后的数据位
   所带来的一个不幸副作用。为了减少信号线数量而把 `$mux` 的输入端口直接连接到
   ``RDATA`` 时，``$techmap579\data.0.0.RDATA`` 信号线在视觉上变得更加复杂。

.. seealso:: 高级用法文档见

   - :doc:`/using_yosys/synthesis/techmap_synth`
   - :doc:`/using_yosys/synthesis/memory`

算术
^^^^

使用 `techmap` 把基本算术逻辑映射到硬件。这一步会使单元数量明显膨胀：多位的 `$mux`
和 `$adffe` 被替换为单比特的 `$_MUX_` 和 `$_DFFE_PP0P_` 单元，而 `$alu` 被替换为
基本的 `$_OR_` 和 `$_NOT_` 门以及一个 `$lut` 单元。

.. literalinclude:: /code_examples/macro_commands/synth_ice40.ys
   :language: yoscrypt
   :start-after: map_gates:
   :end-before: map_ffs:
   :dedent:
   :name: map_gates
   :caption: ``map_gates`` 小节

.. figure:: /_images/code_examples/fifo/rdata_map_gates.svg
   :class: width-helper invert-helper
   :name: rdata_map_gates

   :ref:`map_gates` 之后的 ``rdata`` 输出

.. seealso:: 高级用法文档见
   :doc:`/using_yosys/synthesis/techmap_synth`

触发器
^^^^^^

用 `dfflegalize` 把 FF 转换为硬件支持的类型，然后用 `techmap` 进行映射。在我们的
示例中，这会把 `$_DFFE_PP0P_` 单元转换为 ``SB_DFFER``。

我们还会在这里运行 `simplemap`，把任何仍无法映射到硬件的单元转换为门级原语。其中
包括优化某个输入为常量 ``1'0`` 的 `$_MUX_` 单元，改为用 `$_AND_` 单元替换。

.. literalinclude:: /code_examples/macro_commands/synth_ice40.ys
   :language: yoscrypt
   :start-after: map_ffs:
   :end-before: map_luts:
   :dedent:
   :name: map_ffs
   :caption: ``map_ffs`` 小节

.. figure:: /_images/code_examples/fifo/rdata_map_ffs.svg
   :class: width-helper invert-helper
   :name: rdata_map_ffs

   :ref:`map_ffs` 之后的 ``rdata`` 输出

.. seealso:: 高级用法文档见
   :doc:`/using_yosys/synthesis/techmap_synth`

LUT
^^^

`abc` 和 `techmap` 用于映射 LUT，把原语单元类型转换为使用 `$lut` 和 ``SB_CARRY``
单元。注意 iCE40 流程使用的是 `abc9` 而不是 `abc`。关于它们的作用以及这两条命令的
区别，请参阅 :doc:`/using_yosys/synthesis/abc`。

.. literalinclude:: /code_examples/macro_commands/synth_ice40.ys
   :language: yoscrypt
   :start-after: map_luts:
   :end-before: map_cells:
   :dedent:
   :name: map_luts
   :caption: ``map_luts`` 小节

.. figure:: /_images/code_examples/fifo/rdata_map_luts.svg
   :class: width-helper invert-helper
   :name: rdata_map_luts

   :ref:`map_luts` 之后的 ``rdata`` 输出

最后我们用 `techmap` 把通用的 `$lut` 单元映射为 iCE40 的 ``SB_LUT4`` 单元。

.. literalinclude:: /code_examples/macro_commands/synth_ice40.ys
   :language: yoscrypt
   :start-after: map_cells:
   :end-before: check:
   :dedent:
   :name: map_cells
   :caption: ``map_cells`` 小节

.. figure:: /_images/code_examples/fifo/rdata_map_cells.svg
   :class: width-helper invert-helper
   :name: rdata_map_cells

   :ref:`map_cells` 之后的 ``rdata`` 输出

.. seealso:: 高级用法文档见

   - :doc:`/using_yosys/synthesis/techmap_synth`
   - :doc:`/using_yosys/synthesis/abc`

其他单元
^^^^^^^^

以下命令也可用于映射其他单元：

`hilomap`
    有些架构需要特殊的驱动单元来驱动常量高电平或低电平。该命令把简单常量替换为这类
    驱动单元的实例。

`iopadmap`
    顶层输入/输出通常必须用特殊的 I/O pad 单元实现。该命令会把这类单元插入设计。

视流程而定，这些命令通常要么放在 :ref:`map_cells` 中，要么放在 :ref:`check` 之后。

最后步骤
~~~~~~~~


iCE40 综合流程的下一节进行一些合理性检查并做最后的整理：

.. literalinclude:: /code_examples/macro_commands/synth_ice40.ys
   :language: yoscrypt
   :start-after: check:
   :dedent:
   :name: check
   :caption: ``check`` 小节

这里的新命令有：

- :cmd:title:`autoname`，
- :cmd:title:`stat`，以及
- :cmd:title:`blackbox`。

`stat` 的输出有助于检查资源使用情况；它会列出设计中用到的单元及各自数量，以及其他
资源（如信号线和过程）的使用数量。对于本设计，最后一次调用 `stat` 的输出应该类似
下面这样：

.. literalinclude:: /code_examples/fifo/fifo.stat
   :language: doscon
   :start-at: yosys> stat -top fifo

注意这里的 :yoscrypt:`-top fifo` 是可选的。`stat` 会自动使用设置了 ``top`` 属性的
模块，也就是我们调用 `hierarchy` 时为 ``fifo`` 设置的那个。如果没有模块被标记为
``top``，则会为每个选中的模块分别显示统计信息。

`stat` 的输出也可以用作一种合理性检查：由于我们已经运行过 `proc`，不应再有任何过程。
我们还期望 ``data`` 使用硬存储器；如果看到的不是 ``SB_RAM40_4K``，而是大量触发器
被占用，那就可能说明出了问题。

如果我们在 :yoscrypt:`read_verilog fifo.v` 之后立即调用 `stat`，看到的会大不相同：

.. literalinclude:: /code_examples/fifo/fifo.stat
   :language: doscon
   :start-at: yosys> stat
   :end-before: yosys> stat -top fifo

注意 ``fifo`` 和 ``addr_gen`` 是分别列出的，而 ``fifo`` 的统计信息显示有 2 个
``addr_gen`` 模块。由于此时存储器尚未映射，我们还能看到有 1 个存储器、共 2048 个
存储位；这正好对应我们那个 8 位宽、含 256 个值的 ``data`` 存储器
（:math:`8*256=2048`）。

综合输出
^^^^^^^^

iCE40 综合流程提供以下输出模式：

- `write_blif`，
- `write_edif`，以及
- `write_json`。

例如，如果我们调用 :yoscrypt:`synth_ice40 -top fifo -json fifo.json`，综合后的
``fifo`` 设计会输出为 :file:`fifo.json`。之后我们可以用 `read_json` 把设计读回
Yosys，但要确保先使用 :yoscrypt:`design -reset` 或打开新的交互终端。得到的 JSON
输出还可以加载到 `nextpnr`_ 中进行布局布线；不过这超出了本文档的范围。

.. _nextpnr: https://github.com/YosysHQ/nextpnr

.. seealso:: :cmd:title:`synth_ice40`
