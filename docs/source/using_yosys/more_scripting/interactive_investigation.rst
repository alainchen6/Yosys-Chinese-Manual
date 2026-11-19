交互式设计探究
--------------


.. todo:: 交互式设计开篇介绍文字

.. role:: yoscrypt(code)
   :language: yoscrypt

.. _interactive_show:

show 命令初探
~~~~~~~~~~~~~


.. TODO:: 合并到 :doc:`/getting_started/scripting_intro` 的 show 小节

本节探究 `show` 命令，并解释它生成的电路图中所使用的符号。所用代码包含在
Yosys 代码库的 |code_examples/show|_ 下。

.. |code_examples/show| replace:: :file:`docs/source/code_examples/show`
.. _code_examples/show: https://github.com/YosysHQ/yosys/tree/main/docs/source/code_examples/show

简单电路
^^^^^^^^

:ref:`example_v` 给出了一个简单电路的 Verilog 代码，我们将用它在一个简单的
场景中演示 `show` 的用法。

.. literalinclude:: /code_examples/show/example.v
   :language: Verilog
   :caption: :file:`example.v`
   :name: example_v

我们将运行的 Yosys 综合脚本见 :numref:`example_ys`。注意，`show` 通过
``-pause`` 选项调用，该选项会暂停 Yosys 脚本的执行，直到用户按下回车键。使用
:yoscrypt:`show -pause` 还允许用户进入交互式 shell，在继续综合之前进一步探究
电路。

.. literalinclude:: /code_examples/show/example_show.ys
   :language: yoscrypt
   :caption: :file:`example_show.ys`
   :name: example_ys

执行该脚本时，会在三条综合命令中的每一条执行完之后显示设计。下面我们逐一查看
这些图，并解释图中显示的内容。

.. note::

   本文档中使用的图片由 :file:`example.ys` 文件生成，而不是
   :file:`example_show.ys`。:file:`example.ys` 把电路图输出为 :file:`.dot`
   文件，而不是直接显示它们。你可以运行 :file:`yosys example.ys`，然后执行
   ``xdot example_first.dot`` 等命令，亲自查看这些图片。

.. figure:: /_images/code_examples/show/example_first.*
   :class: width-helper invert-helper

   第一条 `show` 命令在 :numref:`example_ys` 中的输出

第一张输出显示的是 Verilog 前端读入之后的设计。输入和输出端口显示为八边形。
单元显示为矩形，左侧是输入，右侧是输出。单元标签为两行：第一行是单元的唯一
标识符，第二行是单元类型。内部单元类型以美元符号开头。关于内部单元库的更多
细节，参见 :doc:`/cell_index`。

常量显示为椭圆，并以常量值作为标签。对于不是 32 位宽、和/或含有非 0 或 1 的
位（即 ``x`` 或 ``z``）的常量，使用 ``<bit_width>'<bits>`` 语法。普通的 32 位
常量用十进制数表示。

单比特信号显示为从驱动源指向负载的细箭头。多位宽的信号显示为粗箭头。

最后， *过程块* 显示为圆角方框。过程块是 Yosys 对 Verilog ``always`` 块中建模
的判定树和同步事件的内部表示。标签第一行为 ``PROC`` 加一个唯一标识符，第二行
给出原始 ``always`` 块的源代码位置。注意，来自 ``?:`` 表达式的多路复用器表示
为 `$mux` 单元，而来自 ``if`` 语句的多路复用器仍隐藏在过程块内部。

`proc` 命令把第一张图中的过程块转换为一个多路复用器和一个 D 型触发器，从而
得到第二张图：

.. figure:: /_images/code_examples/show/example_second.*
   :class: width-helper invert-helper

   第二条 `show` 命令在 :numref:`example_ys` 中的输出

右侧的菱形是一个悬空的信号线。（信号线节点只在悬空或具有“public”名称时显示，
例如由 Verilog 输入赋予的名称。）还要注意，现在设计中包含两个 ``BUF`` 节点的
实例。这些是 `proc` 命令留下的痕迹。在调用会对设计做修改的命令之后看到这类
痕迹相当常见，因为大多数命令只关心以最简单的方式完成变换，而不关心事后的
清理。下一次调用 `clean`（或 `opt`，它把 `clean` 作为其操作之一）就会清除这些
痕迹。该操作在 Yosys 脚本中如此常见，以至于可以简单地用 ``;;`` 记号来缩写，
它同时用作命令之间的分隔符。因此，除非你想专门分析某些操作留下的这些痕迹，
否则建议在调用 `show` 之前总是先调用 `clean`。

在该脚本中，下一步我们直接调用 `opt`，最终得到第三张图：

.. figure:: /_images/code_examples/show/example_third.*
   :class: width-helper invert-helper
   :name: example_out

   第三条 `show` 命令在 :ref:`example_ys` 中的输出

这里我们看到，`opt` 命令不仅移除了 `proc` 留下的痕迹，还正确判定它可以移除
第一个 `$mux` 单元而不改变电路的行为。

信号向量的分线框
^^^^^^^^^^^^^^^^

下面的代码清单展示了一个简单电路，它使用了大量拼接式的信号访问。

.. literalinclude:: /code_examples/show/splice.v
   :caption: :file:`splice.v`
   :name: splice_src

可以看到，`show` 命令为该电路生成的输出（:numref:`splice_dia`）显得相当复杂。
这是 Yosys 把信号向量（又称多位信号线或总线）当作原生对象处理的方式所带来的
一个不幸的副作用。虽然在分析对宽整数进行运算的电路时这带来了很大优势，但在
访问信号向量的各个位时，也引入了一些额外的复杂性。

.. figure:: /_images/code_examples/show/splice.*
   :class: width-helper invert-helper
   :name: splice_dia

   ``yosys -p 'prep -top splice_demo; show' splice.v`` 的输出

理解这张电路图的关键元素，当然是那些圆角方框以及标记为
``<MSB_LEFT>:<LSB_LEFT> - <MSB_RIGHT>:<LSB_RIGHT>`` 的行。每个这样的方框在一侧
每行对应一个信号，在另一侧则是所有行共用的一个信号。``<MSB>:<LSB>`` 元组指定
信号的哪些位被引出并连接。因此，连接信号 ``a`` 和 ``x`` 的方框的顶行表示信号
``a`` 的第 0 位（即范围 0:0）连接到信号 ``x`` 的第 1 位（即范围 1:1）。

连接这些方框的线，以及把这类方框连接到单元端口的线，外观略有不同，以强调
它们并非真实的信号线，而是图形表示所必需的元素。这种区别看似只是技术细节，
直到你想调试与 Yosys 内部表示信号向量的方式有关的问题时（例如编写自定义
Yosys 命令时），才会体会到它的意义。

门级网表
^^^^^^^^

:numref:`first_pitfall` 展示了处理映射到单元库的设计时两个常见的陷阱：

.. figure:: /_images/code_examples/show/cmos_00.*
   :class: width-helper invert-helper
   :name: first_pitfall

   由简单 CMOS 门构成的半加器，演示使用 `show` 时的常见陷阱

.. literalinclude:: /code_examples/show/cmos.ys
   :language: yoscrypt
   :start-after: pitfall
   :end-at: cmos_00
   :name: pitfall_code
   :caption: 生成 :numref:`first_pitfall`

首先，生成这张图时 Yosys 无法访问单元库，导致所有单元端口都默认为输入。这
就是为什么所有端口都画在左侧，而且单元别扭地排成一大列。其次，两位向量
``y`` 需要为其各个位使用分线框，导致图形不必要地复杂。

.. figure:: /_images/code_examples/show/cmos_01.*
   :class: width-helper invert-helper
   :name: second_pitfall

   `splitnets` 命令以及提供单元库对 :numref:`first_pitfall` 中设计的影响

.. literalinclude:: /code_examples/show/cmos.ys
   :language: yoscrypt
   :start-after: fixed
   :end-at: cmos_01
   :name: pitfall_avoided
   :caption: 生成 :numref:`second_pitfall`

对于 :numref:`second_pitfall`，Yosys 得到了一份以 Verilog 文件形式给出的单元
库描述，其中包含黑盒模块。有两种方式把单元描述加载到 Yosys 中：第一种是把
单元库的 Verilog 文件通过 ``-lib <filename>`` 选项直接传给 `show` 命令。第二种
是用 :yoscrypt:`read_verilog -lib <filename>` 命令把单元库加载到设计中。第二种
方法的一大优势是，库只需加载一次，之后所有对 `show` 命令的调用都可以使用它。

此外，:numref:`second_pitfall` 是在对设计运行 :yoscrypt:`splitnet -ports` 之后
生成的。该命令把所有信号向量拆分为单个信号位，这在查看门级电路时通常是需要
的。要同时拆分模块端口，需要使用 ``-ports`` 选项。默认情况下，该命令只作用于
内部信号。

其他说明
^^^^^^^^

默认情况下，`show` 命令输出一个临时 dot 文件，并启动 ``xdot`` 来显示它。可以
用 ``-format``、``-viewer`` 和 ``-prefix`` 选项来改变格式、查看器和文件名前缀。
注意，只有 ``pdf`` 和 ``ps`` 格式支持在一次运行中绘制多个模块。``dot`` 格式
可以输出多个模块，但 ``xdot`` 在尝试读取时会报错。

在连接密集的电路中，有时很难跟踪各个信号线。这种情况下，用
``-colors <integer>`` 参数调用 `show` 会很有用，它会为网络随机分配颜色。该整数
（> 0）用作随机颜色分配的种子值。有时需要尝试几个值，才能找到看起来不错的
颜色分配。

命令 :yoscrypt:`help show` 会打印 `show` 命令支持的全部选项的完整列表。

浏览设计
~~~~~~~~


为设计中的整个模块绘制电路图，只在简单情况下有帮助。对于复杂模块，生成的
电路图大得离谱，毫无帮助。在这种情况下，必须先选出电路中相关的部分。

除了决定显示 *什么* 之外，还需要结合综合流程仔细决定 *何时* 显示。一般来说，最好在
能够复现问题的最早状态排查电路。例如，如果在调用 `techmap` 命令之前的内部
状态就已经无法通过验证，那么与其排查 `techmap` 之后的门级电路，不如排查
`techmap` 之前的粗粒度版本电路。

.. Note::

   通常建议这样验证设计的内部状态：用 :yoscrypt:`write_verilog -noexpr` 把它
   写入 Verilog 文件，并使用 Yosys 数据目录（可由 ``yosys-config --datdir``
   打印）中的 :file:`simlib.v` 和 :file:`simcells.v` 仿真模型。

交互式浏览
^^^^^^^^^^

一旦确定了综合流程中适合调试电路的状态，建议直接在综合脚本的相应位置加入
`shell` 命令。该命令会在指定时刻停止综合并进入 shell 模式，用户可以在其中
交互式地输入命令。

大多数情况下，shell 启动时整个设计都处于选中状态（即综合脚本还没有缩小选择
集）。此时可以用 `ls` 命令列出所有模块。`cd` 命令可用于切换到其中一个模块
（输入 ``cd ..`` 可切换回去）。现在 `ls` 命令列出的是该模块内的对象。下面用
`简单电路`_ 中的 :file:`example.v` 来演示：

.. literalinclude:: /code_examples/show/example.out
   :language: doscon
   :start-at: yosys> ls
   :end-before: yosys [example]> dump
   :caption: 运行 :file:`yosys example.v` 后 `ls` 和 `cd` 的输出
   :name: lscd

使用 `cd` 命令选中某个模块后，所有命令（少数例外，如 ``read_`` 和 ``write_``
命令）都只作用于选中的模块。这对于需要对设计中不同模块采用不同综合策略的
综合脚本也很有用。

可以看到，:numref:`example_out` 中的单元名只是实际单元名的缩写，即最后一个
美元符号之后的部分。大多数自动生成的名称（以美元符号开头的名称）都相当长，
并且包含一些关于命名对象来源的附加信息。但在大多数情况下，直接用最后一部分
来缩写这些名称即可。

通常所有交互式操作都在用 `cd` 命令选中的某个模块中进行。但也可以在设计上下文
（``cd ..``）中操作。此时所有对象名都必须加上 ``<module_name>/`` 前缀。例如
``a*/b*`` 表示所有名称以 ``a`` 开头的模块中名称以 ``b`` 开头的所有对象。

`dump` 命令可用于打印某个对象的全部信息。例如，在上面执行 :yoscrypt:`cd example`
之后调用 :yoscrypt:`dump $2`：

.. literalinclude:: /code_examples/show/example.out
   :language: RTLIL
   :start-after: yosys [example]> dump
   :end-before: yosys [example]> cd
   :dedent:
   :caption: :numref:`lscd` 之后 :yoscrypt:`dump $2` 的输出
   :name: dump2

例如，这对于确定连接到单元的网络名称很有用，因为如果网络名是自动生成的，通常
会在电路图中省略。注意，输出采用 RTLIL 表示形式，其说明见
:doc:`/yosys_internals/formats/rtlil_rep`。

设计探究
~~~~~~~~


Yosys 也可用于探究设计（或其他工具生成的网表）。

- 选择机制，特别是 ``%ci`` 和 ``%co`` 之类的模式，可用于弄清设计的各部分是如何
  连接的。
- `submod`、`expose` 和 `splice` 等命令可用于把设计变换为等价的、更易于分析的
  设计。
- `eval` 和 `sat` 等命令可用于探究电路的行为。
- :cmd:title:`show`。
- :cmd:title:`dump`。
- :cmd:title:`add` 和 :cmd:title:`delete` 可用于动态地修改和重新组织设计。

所用代码包含在 Yosys 代码库的 |code_examples/scrambler|_ 下。

.. |code_examples/scrambler| replace:: :file:`docs/source/code_examples/scrambler`
.. _code_examples/scrambler: https://github.com/YosysHQ/yosys/tree/main/docs/source/code_examples/scrambler

改变设计层次
^^^^^^^^^^^^

`flatten` 和 `submod` 等命令可用于改变设计层次，即展平层次，或把模块的某些
部分移动到一个子模块中。这在综合脚本以及逆向工程和分析中都有应用。下面给出
一个使用 `submod` 在 Yosys 中重新组织模块并检查所得电路的例子。

.. literalinclude:: /code_examples/scrambler/scrambler.v
   :language: verilog
   :caption: :file:`scrambler.v`

.. literalinclude:: /code_examples/scrambler/scrambler.ys
   :language: yoscrypt
   :caption: :file:`scrambler.ys`
   :end-before: cd ..

.. figure:: /_images/code_examples/scrambler/scrambler_p01.*
    :class: width-helper invert-helper

.. figure:: /_images/code_examples/scrambler/scrambler_p02.*
    :class: width-helper invert-helper

用 :cmd:title:`eval` 分析得到的电路：

.. todo:: 替换行内代码

.. code:: text

    > cd xorshift32
    > rename n2 in
    > rename n1 out

    > eval -set in 1 -show out
    Eval result: \out = 270369.

    > eval -set in 270369 -show out
    Eval result: \out = 67634689.

    > sat -set out 632435482
    Signal Name                 Dec        Hex                                   Bin
    -------------------- ---------- ---------- -------------------------------------
    \in                   745495504   2c6f5bd0      00101100011011110101101111010000
    \out                  632435482   25b2331a      00100101101100100011001100011010

行为变更
^^^^^^^^

`techmap` 等命令可用于对设计做行为上的变更，例如把异步复位改为同步复位。这在
设计空间探索（针对一个电路评估各种架构）中有应用。

下面的 techmap 映射文件把所有正边沿异步复位触发器替换为正边沿同步复位触发器。
该代码取自 Amber ARMv2 CPU 的 ASIC 综合示例 Yosys 脚本。

.. todo:: 替换行内代码

.. code:: verilog

    (* techmap_celltype = "$adff" *)
    module adff2dff (CLK, ARST, D, Q);

        parameter WIDTH = 1;
        parameter CLK_POLARITY = 1;
        parameter ARST_POLARITY = 1;
        parameter ARST_VALUE = 0;

        input CLK, ARST;
        input [WIDTH-1:0] D;
        output reg [WIDTH-1:0] Q;

        wire [1023:0] _TECHMAP_DO_ = "proc";

        wire _TECHMAP_FAIL_ = !CLK_POLARITY || !ARST_POLARITY;

        always @(posedge CLK)
            if (ARST)
                Q <= ARST_VALUE;
            else
                Q <= D;

    endmodule

关于 `techmap` 命令的更多内容，参见 :doc:`/yosys_internals/techmap` 页面。

高级探究技术
~~~~~~~~~~~~


处理非常大的模块时，仅仅选出模块中感兴趣的部分往往不够。把电路中感兴趣的部分
提取到一个单独的模块中可能更有用。例如，如果你想对模块的关键部分运行一系列
综合命令，并仔细阅读这些命令产生的所有调试输出以找出问题，这种做法就很有用。
如果被探究的电路封装在单独的模块中，这类排查会容易得多。

回顾 :ref:`advanced_logic_cones` 中的 ``memdemo`` 设计：

.. figure:: /_images/code_examples/selections/memdemo_00.svg
   :class: width-helper invert-helper

   ``memdemo``

由于这会生成相当大的电路，把它拆分成更小的部分以便查看和操作会很有用。
:numref:`submod` 正是这样做的，它利用 `submod` 命令把电路拆分为三个部分：
``outstage``、``selstage`` 和 ``scramble``。

.. literalinclude:: /code_examples/selections/submod.ys
   :language: yoscrypt
   :caption: 使用 `submod` 拆分 :file:`memdemo.v` 中的电路
   :start-after: cd memdemo
   :end-before: cd ..
   :name: submod

``-name`` 选项用于指定新模块的名称，同时也指定当前模块中新单元的名称。得到的
电路如下所示。

.. figure:: /_images/code_examples/selections/submod_02.*
   :class: width-helper invert-helper

   ``outstage``

.. figure:: /_images/code_examples/selections/submod_03.*
   :class: width-helper invert-helper
   :name: selstage

   ``selstage``

.. figure:: /_images/code_examples/selections/submod_01.*
   :class: width-helper invert-helper

   ``scramble``

组合电路的求值
^^^^^^^^^^^^^^

`eval` 命令可用于对组合电路求值。作为例子，我们使用上面找到的 ``memdemo`` 的
``selstage`` 子网络，它显示在 :numref:`selstage` 中。

.. todo:: 替换行内代码

::

      yosys [selstage]> eval -set s2,s1 4'b1001 -set d 4'hc -show n2 -show n1

      1. Executing EVAL pass (evaluate the circuit given an input).
      Full command line: eval -set s2,s1 4'b1001 -set d 4'hc -show n2 -show n1
      Eval result: \n2 = 2'10.
      Eval result: \n1 = 2'10.

因此，``-set`` 选项用于设置输入值，``-show`` 选项用于指定要求值的网络。如果
没有指定 ``-show`` 选项，默认使用所有被选中的输出端口。

如果没有给出必需的输入值，就会产生错误。可以用 ``-set-undef`` 选项改为把所有
未指定的输入网络设为 undef（``x``）。

``-table`` 选项可用于生成真值表。例如：

::

      yosys [selstage]> eval -set-undef -set d[3:1] 0 -table s1,d[0]

      10. Executing EVAL pass (evaluate the circuit given an input).
      Full command line: eval -set-undef -set d[3:1] 0 -table s1,d[0]

        \s1 \d [0] |  \n1  \n2
       ---- ------ | ---- ----
       2'00    1'0 | 2'00 2'00
       2'00    1'1 | 2'xx 2'00
       2'01    1'0 | 2'00 2'00
       2'01    1'1 | 2'xx 2'01
       2'10    1'0 | 2'00 2'00
       2'10    1'1 | 2'xx 2'10
       2'11    1'0 | 2'00 2'00
       2'11    1'1 | 2'xx 2'11

      Assumed undef (x) value for the following signals: \s2

注意，`eval` 命令（以及后续小节中讨论的 `sat` 命令）只作用于展平后的模块。它
无法分析穿过设计层次传递的信号。因此，对于实例化了其他模块的模块，必须先对
其使用 `flatten` 命令，然后才能应用这些命令。

求解组合 SAT 问题
^^^^^^^^^^^^^^^^^

经常需要 `eval` 命令的反向操作，即给定电路的输出，找出匹配的输入信号。对于
只有少数几个输入位的小电路，可以通过尝试所有可能的输入组合来实现，
``eval -table`` 命令就是这样做的。然而对于更大的电路，Yosys 提供了 `sat` 命令，
它使用 `SAT`_ 求解器 `MiniSAT`_ 来求解这类问题。

.. _SAT: http://en.wikipedia.org/wiki/Circuit_satisfiability

.. _MiniSAT: http://minisat.se/

.. note::

    虽然可以直接在 Yosys 中进行模型检验，但强烈建议使用 SBY 或 EQY 进行硬件
    形式化验证。

`sat` 命令的工作方式与 `eval` 命令非常相似。主要区别在于，现在还可以设置输出
值并找出对应的输入值。例如：

.. todo:: 替换行内代码

::

      yosys [selstage]> sat -show s1,s2,d -set s1 s2 -set n2,n1 4'b1001

      11. Executing SAT pass (solving SAT problems in the circuit).
      Full command line: sat -show s1,s2,d -set s1 s2 -set n2,n1 4'b1001

      Setting up SAT problem:
      Import set-constraint: \s1 = \s2
      Import set-constraint: { \n2 \n1 } = 4'1001
      Final constraint equation: { \n2 \n1 \s1 } = { 4'1001 \s2 }
      Imported 3 cells to SAT database.
      Import show expression: { \s1 \s2 \d }

      Solving problem with 81 variables and 207 clauses..
      SAT solving finished - model found:

        Signal Name                 Dec        Hex             Bin
        -------------------- ---------- ---------- ---------------
        \d                            9          9            1001
        \s1                           0          0              00
        \s2                           0          0              00

注意，`sat` 命令的 ``-set`` 选项的两个参数都支持信号名。在上面的例子中，我们用
``-set s1 s2`` 约束 ``s1`` 和 ``s2`` 相等。当需要更复杂的约束时，必须构造一个
包装电路，它检查约束并通过一个额外的输出端口表示约束是否满足，然后可以用
``-set`` 选项把这个端口强制为某个值。（这种包含被测电路以及额外约束检查电路
的电路称为 ``miter`` 电路。）

.. literalinclude:: /code_examples/primetest.v
   :language: verilog
   :caption: :file:`primetest.v`，一个用于判断一个数是否为素数的简单 miter 电路，但它存在一个问题。
   :name: primetest

:numref:`primetest` 展示了一个打算用作素数测试的 miter 电路。如果对于给定的
``p``，对所有输入值 ``a`` 和 ``b`` 都有 ``ok`` 为 1，那么 ``p`` 就是素数——
至少设计意图如此。

.. todo:: 替换行内代码

.. code-block::
   :caption: 对 :file:`primetest.v` 中 miter 电路的实验。
   :name: prime_shell

   yosys [primetest]> sat -prove ok 1 -set p 31

   1. Executing SAT pass (solving SAT problems in the circuit).
   Full command line: sat -prove ok 1 -set p 31

   Setting up SAT problem:
   Import set-constraint: \p = 16'0000000000011111
   Final constraint equation: \p = 16'0000000000011111
   Imported 6 cells to SAT database.
   Import proof-constraint: \ok = 1'1
   Final proof equation: \ok = 1'1

   Solving problem with 2790 variables and 8241 clauses..
   SAT proof finished - model found: FAIL!

      ______                   ___       ___       _ _            _ _
     (_____ \                 / __)     / __)     (_) |          | | |
      _____) )___ ___   ___ _| |__    _| |__ _____ _| | _____  __| | |
     |  ____/ ___) _ \ / _ (_   __)  (_   __|____ | | || ___ |/ _  |_|
     | |   | |  | |_| | |_| || |       | |  / ___ | | || ____( (_| |_
     |_|   |_|   \___/ \___/ |_|       |_|  \_____|_|\_)_____)\____|_|


     Signal Name                 Dec        Hex                   Bin
     -------------------- ---------- ---------- ---------------------
     \a                        15029       3ab5      0011101010110101
     \b                         4099       1003      0001000000000011
     \ok                           0          0                     0
     \p                           31         1f      0000000000011111

:numref:`prime_shell` 中展示的 Yosys shell 会话表明，SAT 求解器甚至能为问题找到
出人意料的解：利用整数溢出，确实存在一种“分解”31 的方法。当然，干净的解法是
在 32 位中执行测试，例如把 miter 中的 ``p != a*b`` 换成 ``p != {16'd0,a}b``，
或者为 32 位乘积 ``a*b`` 使用一个临时变量。但由于 31 可以很好地放进 8 位（而且
本文档的目的就是展示 Yosys 的特性），我们也可以简单地在 `sat` 调用中强制 ``a``
和 ``b`` 的高 8 位为零，如下所示。

.. todo:: 替换行内代码

.. code-block::
   :caption: :file:`primetest.v` 中的 miter 电路，其中 ``a`` 和 ``b`` 的高 8 位被约束以防止溢出。
   :name: prime_fixed

   yosys [primetest]> sat -prove ok 1 -set p 31 -set a[15:8],b[15:8] 0

   1. Executing SAT pass (solving SAT problems in the circuit).
   Full command line: sat -prove ok 1 -set p 31 -set a[15:8],b[15:8] 0

   Setting up SAT problem:
   Import set-constraint: \p = 16'0000000000011111
   Import set-constraint: { \a [15:8] \b [15:8] } = 16'0000000000000000
   Final constraint equation: { \a [15:8] \b [15:8] \p } = { 16'0000000000000000 16'0000000000011111 }
   Imported 6 cells to SAT database.
   Import proof-constraint: \ok = 1'1
   Final proof equation: \ok = 1'1

   Solving problem with 2790 variables and 8257 clauses..
   SAT proof finished - no model found: SUCCESS!

                     /$$$$$$      /$$$$$$$$     /$$$$$$$
                    /$$__  $$    | $$_____/    | $$__  $$
                   | $$  \ $$    | $$          | $$  \ $$
                   | $$  | $$    | $$$$$       | $$  | $$
                   | $$  | $$    | $$__/       | $$  | $$
                   | $$/$$ $$    | $$          | $$  | $$
                   |  $$$$$$/ /$$| $$$$$$$$ /$$| $$$$$$$//$$
                    \____ $$$|__/|________/|__/|_______/|__/
                          \__/

在 :numref:`prime_fixed` 中使用的 ``-prove`` 选项与 ``-set`` 类似，但它试图找出
两个参数不相等的情况。如果没有找到这种情况，则该性质被证明对所有满足其他
约束的输入都成立。

值得一提的是，SAT 求解器在分解大数方面并不特别高效。但如果一个小规模的因子
分解问题作为更大电路问题的一部分出现，Yosys 的 SAT 求解器完全有能力解决它。

求解时序 SAT 问题
^^^^^^^^^^^^^^^^^

Yosys 中的 SAT 求解功能不仅可用于求解组合问题，也可用于求解时序问题。让我们
再次考虑 :ref:`advanced_logic_cones` 中的 ``memdemo`` 设计，假设我们想知道
``d`` 的哪种输入值序列能使输出 y 从任意初始状态开始产生序列 1、2、3。让我们
使用以下命令：

.. todo:: 替换行内代码？

.. code-block:: yoscrypt

      sat -seq 6 -show y -show d -set-init-undef \
        -max_undef -set-at 4 y 1 -set-at 5 y 2 -set-at 6 y 3

``-seq 6`` 选项指示 `sat` 命令在 6 个时间步内求解一个时序问题。（用更少步数
进行的实验表明，至少需要 3 个周期才能使电路进入能够产生序列 1、2、3 的状态。）

``-set-init-undef`` 选项告诉 `sat` 命令把所有寄存器初始化为 undef（``x``）状态。
Verilog 中处理 ``x`` 状态的方式将确保该解对任意初始状态都有效。

``-max_undef`` 选项指示 `sat` 命令寻找 undef 数量最多的解。这样我们就能清楚地
看到哪些输入位与解相关。

最后，三个 ``-set-at`` 选项为 ``y`` 信号添加约束，使其从时间步 4 开始产生
1、2、3 序列。

这会产生以下输出：

.. todo:: 替换行内代码

.. code-block::
   :caption: 在 ``memdemo`` 模块中求解时序 SAT 问题。
   :name: memdemo_sat

   yosys [memdemo]> sat -seq 6 -show y -show d -set-init-undef \
       -max_undef -set-at 4 y 1 -set-at 5 y 2 -set-at 6 y 3

   1. Executing SAT pass (solving SAT problems in the circuit).
   Full command line: sat -seq 6 -show y -show d -set-init-undef
       -max_undef -set-at 4 y 1 -set-at 5 y 2 -set-at 6 y 3

   Setting up time step 1:
   Final constraint equation: { } = { }
   Imported 29 cells to SAT database.

   Setting up time step 2:
   Final constraint equation: { } = { }
   Imported 29 cells to SAT database.

   Setting up time step 3:
   Final constraint equation: { } = { }
   Imported 29 cells to SAT database.

   Setting up time step 4:
   Import set-constraint for timestep: \y = 4'0001
   Final constraint equation: \y = 4'0001
   Imported 29 cells to SAT database.

   Setting up time step 5:
   Import set-constraint for timestep: \y = 4'0010
   Final constraint equation: \y = 4'0010
   Imported 29 cells to SAT database.

   Setting up time step 6:
   Import set-constraint for timestep: \y = 4'0011
   Final constraint equation: \y = 4'0011
   Imported 29 cells to SAT database.

   Setting up initial state:
   Final constraint equation: { \y \s2 \s1 \mem[3] \mem[2] \mem[1]
               \mem[0] } = 24'xxxxxxxxxxxxxxxxxxxxxxxx

   Import show expression: \y
   Import show expression: \d

   Solving problem with 10322 variables and 27881 clauses..
   SAT model found. maximizing number of undefs.
   SAT solving finished - model found:

     Time Signal Name                 Dec        Hex             Bin
     ---- -------------------- ---------- ---------- ---------------
     init \mem[0]                      --         --            xxxx
     init \mem[1]                      --         --            xxxx
     init \mem[2]                      --         --            xxxx
     init \mem[3]                      --         --            xxxx
     init \s1                          --         --              xx
     init \s2                          --         --              xx
     init \y                           --         --            xxxx
     ---- -------------------- ---------- ---------- ---------------
        1 \d                            0          0            0000
        1 \y                           --         --            xxxx
     ---- -------------------- ---------- ---------- ---------------
        2 \d                            1          1            0001
        2 \y                           --         --            xxxx
     ---- -------------------- ---------- ---------- ---------------
        3 \d                            2          2            0010
        3 \y                            0          0            0000
     ---- -------------------- ---------- ---------- ---------------
        4 \d                            3          3            0011
        4 \y                            1          1            0001
     ---- -------------------- ---------- ---------- ---------------
        5 \d                           --         --            001x
        5 \y                            2          2            0010
     ---- -------------------- ---------- ---------- ---------------
        6 \d                           --         --            xxxx
        6 \y                            3          3            0011

该解在第一步设置 ``d = 0`` 并不奇怪，因为这是把 ``s1`` 和 ``s2`` 寄存器置为
已知值的唯一方法。其他步骤的输入值手动推导起来更困难一些，但 SAT 求解器瞬间
就能找到正确的解。

关于 `sat` 命令还有很多可写的内容。例如，有一组选项可用于通过时序归纳
:cite:p:`een2003temporal` 进行时序证明。命令 ``help sat`` 可用于打印所有选项的
列表，并附带对其功能的简短说明。
