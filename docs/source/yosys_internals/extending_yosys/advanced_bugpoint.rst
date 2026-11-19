定位 bug 的根本原因
===================


本文涉及 Yosys 内部实现，面向有兴趣解决或调查 Yosys bug 的人。如果你使用
模糊测试工具，本文同样适用：fuzzer 往往会发现同一个 bug 的许多变体，因此定位
根本原因对于避免 issue 泛滥很重要。

如果你熟悉 C/C++，可以试着查看出错命令的源代码。即使你自己无法修复问题，如果
你能指出问题出在哪里，对其他调查者也会非常有帮助。


找到失败的命令
--------------


使用 ``-L`` 标志会有所帮助，它允许你指定日志输出的文件，例如
``yosys -L out.log -s script.ys``。大多数命令在开始执行时会打印一条头部消息，
类似 ``2.48. Executing HIERARCHY pass (managing design hierarchy).``。最后一条
头部消息通常就是失败的命令。有些命令不会打印头部消息，因此你可能需要在脚本
开头加上 ``echo on``。`echo` 命令会回显每条执行的命令及其参数。对于上面
`hierarchy` 的例子，可能是 ``yosys> hierarchy -check``。

.. note::

   使用 `log` 命令添加消息也很有帮助，之后你可以在终端或日志文件中搜索这些
   消息。如果你的脚本包含脚本 pass，例如 :doc:`/using_yosys/synthesis/synth`，
   这些 pass 会调用许多子命令，而你不确定究竟是哪个脚本 pass 调用了失败的命令，
   那么这种做法会相当有用。


最小化脚本
----------


.. warning::

   本节介绍的是**高级用法**，对于普通的 bug 报告通常并不需要。

如果你使用的是命令行形式，例如
``yosys -p 'synth_xilinx' -o design.json design.v``，可以考虑把它改写成脚本。
对文件中的脚本反复修改通常比修改命令行上的一长串参数容易得多，也更便于与他人
分享。

.. code-block:: yoscrypt
   :caption: 示例脚本 ``script.ys``，对应命令 ``yosys -p 'synth_xilinx' -o design.json design.v``

   read_verilog design.v
   synth_xilinx
   write_json design.json

接下来，你要把错误发生*之后*的所有内容删掉。如果最后一条命令会调用子命令，
先把它替换成这些子命令的内容。对于 :doc:`/using_yosys/synthesis/synth` 以及
某些其他脚本 pass，你可以使用 ``-run`` 选项来简化这一过程。例如，我们可以用
:ref:`replace_synth` 替换 ``synth -top <top> -lut``。选项 ``-top <top> -lut``
可以提供给每个 `synth` 步骤，也可以只提供给相关的步骤，如下所示。

.. code-block:: yoscrypt
   :caption: `synth` 命令的示例替换脚本
   :name: replace_synth

   synth -top <top> -run :coarse
   synth -lut -run coarse:fine
   synth -lut -run fine:check
   synth -run check:

假设我们运行 :ref:`replace_synth`，并且能够删掉 ``synth -run check:`` 后仍然得到
同样的错误，然后查看日志，发现错误之前最后的内容是 ``7.2. Executing MEMORY_MAP
pass (converting memories to logic and flip-flops)``。查看 ``yosys -h synth`` 的
输出（或 `synth` 的帮助页面），可以看到 `memory_map` pass 是在 ``fine`` 步骤中
被调用的。于是我们可以把脚本改成下面这样：

.. code-block:: yoscrypt
   :caption: `memory_map` 失败时 `synth` 的示例替换脚本

   synth -top <top> -run :fine
   opt -fast -full
   memory_map

给 `synth` 加上 ``-run :fine`` 选项，就是让它从脚本开头一直运行到 ``fine``
步骤，然后我们再给出该步骤之后要运行的确切命令。有些情况下，帮助输出中给出的
命令与实际运行的命令并不完全一致，而是一种简化形式。如果你发现用脚本 pass 的
内容替换它之后，错误消失或发生了变化，可以试试带 ``echo on`` 调用该脚本 pass，
看看究竟调用了哪些命令、使用了哪些选项。

.. warning::

   在继续之前，请*备份你的代码*。下面的步骤可能移除上下文，导致脚本被过度
   最小化，从而掩盖底层问题。更多内容参见
   :ref:`yosys_internals/extending_yosys/advanced_bugpoint:为什么上下文很重要`。

当问题出现在脚本靠后的许多步骤之后时，只在脚本开头最小化设计并不足以定位问题
原因。脚本中每多一个步骤，都可能需要输入设计中更大的部分，才能让这个特定问题
一直保留到引发崩溃。因此，为了找到最小的复现用例，有时删掉失败点之前的命令会
有所帮助。

最简单的做法是把设计写出、重置当前状态，然后再读回设计：

.. code-block:: yoscrypt

   write_rtlil <design.il>; design -reset; read_rtlil <design.il>;

在大多数情况下，可以把这一行插到失败命令之前，同时仍能产生该错误，从而可以用
``<design.il>`` 输出
:ref:`最小化你的 RTLIL<using_yosys/bugpoint:用 bugpoint 最小化 RTLIL 设计>`。
对于前面 `memory_map` 的例子，如果 :ref:`map_reset` 仍然给出同样的错误，那么
现在应该可以用 ``yosys design.il -p 'memory_map'`` 来复现它。

.. code-block:: yoscrypt
   :caption: 在失败之前立即重置设计
   :name: map_reset

   synth -top <top> -run :fine
   opt -fast -full
   write_rtlil design.il; design -reset; read_rtlil design.il;
   memory_map

如果这样做得不到该错误（或者得到的不是同一个错误），就应当把 write/reset/read
往脚本前面移动，直到能复现为止。如果你完全不知道应当把重置放在哪里，最好的
办法是采用“二分查找”式的做法，每次尝试后把可能的范围缩小一半。

.. note::

   默认情况下，`write_rtlil` 不包含平台相关的 IP 块，也不包含通常在综合脚本
   开头用 ``read_verilog -lib`` 命令加载的其他原语单元模型。你可能需要在
   ``design -reset`` 调用*之后*重复这些命令。也可以用
   ``select =*; write_rtlil -selected <design.il>`` 把*所有内容*写出来。

举个例子，你的脚本在失败之前有 16 条命令，在第 17 条上失败。如果在第 17 条
之前重置无法复现该错误，就试试在第 8 条和第 9 条之间重置（8 是总数 16 的一半）。
如果这样能产生该错误，就可以删掉 `read_rtlil` 之前的所有内容，然后在剩余部分
的中间再次尝试重置，并确保输出文件使用不同的名字，以免覆盖已经得到的结果。
如果没有产生该错误，就需要再往前，这种情况下应在第 4 条和第 5 条之间重置
（4 是之前的 8 的一半）。重复这一过程，直到剩余命令无法再缩减为止。

另一种更保守但更繁琐的方法是删除或注释掉失败命令之前的命令。可以一次禁用一个
命令或一组命令，同时检查错误是否仍然出现，最终得到把原始输入带到该错误所需的
最少的命令子集。这种方法的困难在于：取决于你的设计，有些命令可能是必需的，
即使复现错误并不需要它们。例如，如果你的设计包含 ``process`` 块，许多命令都会
失败，除非你先运行 `proc` 命令。虽然这种做法能更好地保持上下文，但通常更容易的
做法是：先为产生错误而最小化设计，然后再*恢复*上下文。关于恢复上下文的更多
内容，参见
:ref:`yosys_internals/extending_yosys/advanced_bugpoint:为什么上下文很重要`。


为什么上下文很重要
------------------


有时一条命令报错时，你看到的只是症状，而不是底层问题。有可能更早的某条命令把
设计置于无效状态，直到报错时才被发现。对于预打包的
:doc:`/using_yosys/synthesis/synth` 尤其如此，它们依赖通用 pass 和架构相关
pass 的组合。随着 Yosys 加入新特性、支持更多设计，一个 pass 输出的单元类型
可能会增加和变化；有时这会导致某个 pass 预期处理的内容与实际不符。

如果你最小化了脚本，并删掉了失败之前的命令以得到更小的复现用例，那么试着倒退
回去，找出哪些命令可能导致了设计失败。从最小化后的设计出发，你应当对产生错误
的那个或那些单元有所了解；但这些单元是从哪里来的呢？单元的名称和/或类型通常
能为你指明方向：

.. code-block::

   # internal cell types start with a $
   # lowercase for word-level, uppercase for bit-level
   $and
   $_AND_

   # cell types with $__ are typically intermediate cells used in techmapping
   $__MUL16X16

   # cell types without a $ are either user-defined or architecture specific
   my_module
   SB_MAC16

   # object names might give you the name of the pass that created them
   $procdff$1204
   $memory\rom$rdmux[0][0][0]$a$1550

   # or even the line number in the Yosys source
   $auto$muxcover.cc:557:implement_best_cover$2152
   $auto$alumacc.cc:495:replace_alu$1209

试着运行未最小化的脚本，并在日志中搜索最小化设计里对象的名称。对于单元，也可以
搜索单元的类型。记住，调用 `stat` 会列出设计当前使用的所有单元类型，
``select -list =*`` 会列出当前所有对象的名称。你可以把这些命令加入脚本，或者
在交互式终端中逐条运行。把命令加入脚本重复性更好；但如果运行到所关心的位置
需要很长时间，那么到达该位置后，交互式 shell 会话能给你更多灵活性。你也可以在
脚本中的任何位置调用 `shell` 命令来启动交互式会话，这样可以把准备工作都
脚本化，等准备工作完成后再回来。

``--dump-design`` 选项
~~~~~~~~~~~~~~~~~~~~~~


Yosys 提供 ``--dump-design`` 选项（简写为 ``-P``），用于根据日志头部在脚本的
特定步骤处导出设计。如果错误之前的最后一步是 ``7.2. Executing MEMORY_MAP pass
(converting memories to logic and flip-flops)``，那么用 ``--dump-design
7.2:bad.il`` 调用 Yosys，就会在运行该命令*之前*把设计保存到文件 ``bad.il`` 中。

也可以多次使用该选项，例如 ``-P2:hierarchy.il -P7 -P7.2:bad.il``，从而在一次
运行中得到多份导出结果。这样可以更容易地跟踪设计经过每个步骤的变化，找出某些
单元或连接来自哪里。还允许使用 ``--dump-design ALL``，它会在每个日志头部处
写出设计。

一个完整示例
~~~~~~~~~~~~


假设你完成了所有最小化工作，发现 `synth_xilinx` 中的错误发生在：定义了
``MIN_MUX_INPUTS`` 时，调用 ``techmap -map +/xilinx/cells_map.v`` 解析一个所有
输入都被设为 ``1'x`` 的 `$_MUX16_`。你可以在 ``+/xilinx/cells_map.v`` 中修复
这个 bug，但那样可能只解决这一个案例，而留下其他尚未发现的问题。于是你逐步运行
原始脚本，在每一步之后调用 `stat`，找出 `$_MUX16_` 是何时被加入的。

你发现 `$_MUX16_` 是由一次 `muxcover` 调用引入的，但此时所有输入都已定义，因此
现在调用 `techmap` 能按预期工作。通过用失败的 techmap 运行 `bugpoint`，你得知
索引为 ``2297`` 的单元会失败，于是调用 ``select top/*$2297`` 只保留该单元。然后
可以用 ``design -save pre_bug`` 或 ``write_rtlil -selected pre_bug.il`` 把它
保存下来，这样就不必重新运行之前的所有步骤回到这里。

接下来你逐步运行剩余的命令，并在每条命令之后调用 `dump`，找出输入是在何时被
断开的。你发现 ``opt -full`` 优化掉了电路的一部分，使得 `opt_expr` 把无驱动的
多路复用器输入设为 ``x``，却没有删除此时已不再需要的 `$_MUX16_`。这样你就
定位到 `opt_expr` 中的一个问题，它影响所有宽多路复用器，并且可能在任何综合流程
中发生，而不仅限于 `synth_xilinx`。

.. seealso::

   本示例取自 `YosysHQ/yosys#4590
   <https://github.com/YosysHQ/yosys/issues/4590>`_，可以用 0.45 到 0.51 之间的
   Yosys 版本复现。
