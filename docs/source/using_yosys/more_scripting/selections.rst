选择集
------


.. role:: yoscrypt(code)
   :language: yoscrypt

选择集框架
~~~~~~~~~~


.. todo:: 减少与 :doc:`/getting_started/scripting_intro` select 小节的重叠

`select` 命令可用于为后续命令创建选择集。例如：

.. code:: yoscrypt

    select foobar         # select the module foobar
    delete                # delete selected objects

通常 `select` 命令会覆盖先前的选择集。:yoscrypt:`select -add` 和
:yoscrypt:`select -del` 命令可用于在当前选择集中添加或删除对象。

:yoscrypt:`select -clear` 命令可用于把选择集重置为默认值，即完整选中当前模块
中的所有内容。

这一选择集框架也可以直接用于许多其他命令。当某个命令的用法帮助中把
``[selection]`` 作为最后一个参数时，意味着它会使用 `select` 命令背后的引擎来
求值附加参数，并使用得到的选择集，而不是最后一条 `select` 命令创建的选择集。

例如，`delete` 命令会删除当前选择集中的所有内容；而 :yoscrypt:`delete foobar`
只删除模块 foobar。如果尚未执行过 `select` 命令，那么“当前选择集”就是整个
设计。

.. note:: 本页中的许多示例使用 `show` 命令直观地演示选择集的效果。有关该命令

   的更详细介绍，请参阅 :ref:`interactive_show`。

如何创建选择集
~~~~~~~~~~~~~~


按对象名选择
^^^^^^^^^^^^

最简单的选择对象的方式是按对象名选择。这通常只出现在为特定设计专门手工编写的
综合脚本中。

.. code:: yoscrypt

    select foobar         # select module foobar
    select foo*           # select all modules whose names start with foo
    select foo*/bar*      # select all objects matching bar* from modules matching foo*
    select */clk          # select objects named clk from all modules

模块与设计上下文
^^^^^^^^^^^^^^^^

命令可以在 *模块* 或 *设计* 上下文中执行。到目前为止，所有命令都是在设计
上下文中执行的。`cd` 命令可用于切换到模块上下文。

在模块上下文中，所有命令只作用于活动模块。模块中的对象在选择时不带
``<module_name>/`` 前缀。例如：

.. code:: yoscrypt

    cd foo                # switch to module foo
    delete bar            # delete object foo/bar

    cd mycpu              # switch to module mycpu
    dump reg_*            # print details on all objects whose names start with reg_

    cd ..                 # switch back to design

注意：大多数综合脚本从不会切换到模块上下文。但它是一个非常强大的工具，我们会在
:doc:`/using_yosys/more_scripting/interactive_investigation` 中进一步探讨。

按对象属性或类型选择
^^^^^^^^^^^^^^^^^^^^

可以使用特殊模式按对象属性或类型进行选择。例如：

- 选中所有名称以 ``reg_`` 开头的信号线： :yoscrypt:`select w:reg_*`
- 选中所有设置了属性 ``foobar`` 的对象： :yoscrypt:`select
  a:foobar`
- 选中所有属性 ``foobar`` 设置为 42 的对象： :yoscrypt:`select
  a:foobar=42`
- 选中所有设置了属性 ``blabla`` 的模块： :yoscrypt:`select
  A:blabla`
- 选中模块 foo 中的所有 `$add` 单元： :yoscrypt:`select foo/t:$add`

模式表达式的完整列表见 :cmd:title:`select`。

选择集上的操作
~~~~~~~~~~~~~~


组合选择集
^^^^^^^^^^

`select` 命令实际上比乍看起来要强大得多。当以多个参数调用它时，每个参数都会被
单独求值并压入栈中。处理完所有参数后，它只是创建栈上所有元素的并集。因此
:yoscrypt:`select t:$add a:foo` 会选中所有 `$add` 单元以及所有设置了 ``foo``
属性的对象：

.. literalinclude:: /code_examples/selections/foobaraddsub.v
   :caption: 用于选择集运算的测试模块
   :name: foobaraddsub
   :language: verilog

.. code-block::
   :caption: 在 :numref:`foobaraddsub` 上执行命令 ``select t:$add a:foo -list`` 的输出

   yosys> select t:$add a:foo -list
   foobaraddsub/$add$foobaraddsub.v:6$3
   foobaraddsub/$sub$foobaraddsub.v:5$2
   foobaraddsub/$add$foobaraddsub.v:4$1

在许多情况下，只是一味地向选择集中添加内容，并不能有效地选出设计中真正感兴趣的
部分。可以使用特殊参数来组合栈上的元素。例如，``%i`` 参数会弹出栈顶的两个元素，
求它们的交集，再把结果压回栈中。因此 :yoscrypt:`select t:$add a:foo %i` 会选中
所有设置了 ``foo`` 属性的 `$add` 单元：

.. code-block::
   :caption: 在 :numref:`foobaraddsub` 上执行命令 ``select t:$add a:foo %i -list`` 的输出

   yosys> select t:$add a:foo %i -list
   foobaraddsub/$add$foobaraddsub.v:4$1

一些特殊的 ``%`` 代码：

- ``%u``：栈顶两个元素的并集——弹出 2 个，压入 1 个
- ``%d``：栈顶两个元素的差集——弹出 2 个，压入 1 个
- ``%i``：栈顶两个元素的交集——弹出 2 个，压入 1 个
- ``%n``：栈顶元素的补集——弹出 1 个，压入 1 个

完整列表见 :cmd:title:`select`。

扩展选择集
^^^^^^^^^^

:numref:`sumprod` 使用 Yosys 非标准的 ``{... *}`` 语法，为第一条 assign 语句
生成的所有单元设置属性 ``sumstuff``。（该语法适用于任意大的 Verilog 代码块，
可用于标记待分析的代码片段。）

.. literalinclude:: /code_examples/selections/sumprod.v
   :caption: 另一个用于选择集运算的测试模块
   :name: sumprod
   :language: verilog

在该模块中选择 ``a:sumstuff`` 会得到如下电路图：

.. figure:: /_images/code_examples/selections/sumprod_00.svg
   :class: width-helper invert-helper
   :name: sumprod_00

   在 :numref:`sumprod` 上 ``show a:sumstuff`` 的输出

由于只选中了单元本身，而没有选中临时信号线 ``$1_Y``，所以两个加法器显示为两个
不相连的部分。这对于时钟和复位这类全局信号非常有用：只需用
:yoscrypt:`select -del clk rst` 之类的命令取消选中它们，使用它们的每个单元就会
获得各自的网络标号。

不过在这个例子中，我们希望看到单元正确连接在一起。这可以通过 ``%x`` 操作实现：
它会扩展选择集，即对每条被选中的信号线，选中所有与该信号线相连的单元，反之亦然。
因此 :yoscrypt:`show a:sumstuff %x` 会得到 :numref:`sumprod_01` 所示的电路图：

.. figure:: /_images/code_examples/selections/sumprod_01.svg
   :class: width-helper invert-helper
   :name: sumprod_01

   在 :numref:`sumprod` 上 ``show a:sumstuff %x`` 的输出

.. _selecting_logic_cones:

选择逻辑锥
^^^^^^^^^^

:numref:`sumprod_01` 展示了所谓的 ``sum`` 输入锥（``input cone``），即用于
生成信号 ``sum`` 的所有单元和信号。``%ci`` 操作可用于选择 `select` 命令所维护
的栈中，顶层选择集里所有对象的输入锥。

与 ``%x`` 操作一样，这些命令会把选择集扩展一个“步”。但这一次，操作只沿数据流
反方向进行。也就是说，信号线只通过输出端口选择单元，单元只通过输入端口选择信号线。

下面这组电路图演示了这种逐步扩展：

.. figure:: /_images/code_examples/selections/sumprod_02.svg
   :class: width-helper invert-helper

   在 :numref:`sumprod` 上 :yoscrypt:`show prod` 的输出

.. figure:: /_images/code_examples/selections/sumprod_03.svg
   :class: width-helper invert-helper

   在 :numref:`sumprod` 上 :yoscrypt:`show prod %ci` 的输出

.. figure:: /_images/code_examples/selections/sumprod_04.svg
   :class: width-helper invert-helper

   在 :numref:`sumprod` 上 :yoscrypt:`show prod %ci %ci` 的输出

.. figure:: /_images/code_examples/selections/sumprod_05.svg
   :class: width-helper invert-helper

   在 :numref:`sumprod` 上 :yoscrypt:`show prod %ci %ci %ci` 的输出

注意 :yoscrypt:`show prod %ci` 与 :yoscrypt:`show prod %ci %ci` 之间的细微
差别。两幅图都显示 `$mul` 单元由 ``$3_Y`` 和 ``c`` 这两个输入驱动。但只有在
第二幅图中，即在第二次调用 ``%ci`` 之后，`show` 才能区分 ``$3_Y`` 是信号线
而 ``c`` 是输入。改用 `dump` 命令可以更清楚地看到这一点：

.. literalinclude:: /code_examples/selections/sumprod.out
   :language: RTLIL
   :end-at: end
   :caption: :yoscrypt:`dump prod %ci` 的输出

.. literalinclude:: /code_examples/selections/sumprod.out
   :language: RTLIL
   :start-after: end
   :caption: :yoscrypt:`dump prod %ci %ci` 的输出

在选择多级逻辑时，反复书写 ``%ci`` 会有些繁琐。为此有一个快捷方式：可以在操作
后面附加迭代次数。例如操作 ``%ci3`` 等价于执行三次 ``%ci`` 操作。

``%ci*`` 操作会反复执行 ``%ci``，直到不再产生任何效果。

.. _advanced_logic_cones:

高级逻辑锥选择
^^^^^^^^^^^^^^

在大多数情况下，某些单元类型和/或端口不应被 ``%ci`` 操作考虑，或者我们只想沿着
某些单元类型和/或端口追踪。这可以通过在 ``%ci`` 操作后附加额外的模式来实现。

让我们看看 :numref:`memdemo_src`。它没有别的用途，只是作为一个非平凡电路，用来
演示 Yosys 的一些高级特性。该代码位于 Yosys 源码仓库的
``docs/source/code_examples/selections`` 中。

.. literalinclude:: /code_examples/selections/memdemo.v
   :caption: :file:`memdemo.v`
   :name: memdemo_src
   :language: verilog

:file:`memdemo.ys` 脚本用于生成本文包含的图片。我们来看第一节：

.. literalinclude:: /code_examples/selections/memdemo.ys
   :caption: 综合 :ref:`memdemo_src`
   :name: memdemo_ys
   :language: yoscrypt
   :end-at: opt

这段脚本加载 :numref:`memdemo_src` 并综合其中的模块。注意，只要
:file:`memdemo.v` 在同一目录下，这段代码就可以直接复制到 Yosys 命令行会话中
运行。现在我们可以用 ``cd memdemo`` 切换到 ``memdemo`` 模块，并调用 `show` 查看
:numref:`memdemo_00` 中的电路图。

.. figure:: /_images/code_examples/selections/memdemo_00.svg
   :class: width-helper invert-helper
   :name: memdemo_00

   :numref:`memdemo_src` 所示设计的完整电路图

里面内容很多，但我们可能只关心用于选择输出值的多路复用器树。让我们先只显示输出
信号 ``y`` 及其直接前驱。还记得前面的 `选择逻辑锥`_，我们可以使用
:yoscrypt:`show y %ci2`：

.. figure:: /_images/code_examples/selections/memdemo_01.svg
   :class: width-helper invert-helper
   :name: memdemo_01

   :yoscrypt:`show y %ci2` 的输出

由此我们可以了解到：``y`` 由 `$dff` 单元驱动，``y`` 连接到输出端口 ``Q``，
``clk`` 信号进入该单元的 ``CLK`` 输入端口，数据来自一条自动生成的信号线并进入
该触发器单元的输入 ``D``（由名称开头的 ``$`` 标示）。现在我们再往前看一点，试试
:yoscrypt:`show y %ci5`：

.. figure:: /_images/code_examples/selections/memdemo_02.svg
   :class: width-helper invert-helper
   :name: memdemo_02

   :yoscrypt:`show y %ci5` 的输出

这开始变得有些混乱，也许我们想忽略多路复用器的选择输入。要添加模式，只需在
``%ci`` 操作后加上一个冒号和模式。模式本身以 ``-`` 或 ``+`` 开头，表示它是
包含模式还是排除模式，随后是可选的、以逗号分隔的单元类型列表，再随后是方括号中
可选的、以逗号分隔的端口名列表。在这个例子中，我们想用
:yoscrypt:`show y %ci5:-$mux[S]` 排除 `$mux` 单元类型的 ``S`` 端口：

.. figure:: /_images/code_examples/selections/memdemo_03.svg
   :class: width-helper invert-helper
   :name: memdemo_03

   :yoscrypt:`show y %ci5:-$mux[S]` 的输出

我们可以使用 :yoscrypt:`show y %ci2:+$dff[Q,D] %ci*:-$mux[S]:-$dff` 这样的
命令，其中第一个 ``%ci`` 跳过最初的 D 型触发器，第二个操作则在不经过多路复用器
选择输入和触发器单元的情况下选中整个输入锥：

.. figure:: /_images/code_examples/selections/memdemo_05.svg
   :class: width-helper invert-helper
   :name: memdemo_05

   ``show y %ci2:+$dff[Q,D] %ci*:-$mux[S]:-$dff`` 的输出

或者改用 :yoscrypt:`show y %ci*:-[CLK,S]:+$dff:+$mux`，一路沿着输入锥追踪，
但只沿着 `$dff` 和 `$mux` 单元，并忽略任何名为 ``CLK`` 或 ``S`` 的端口：

.. TODO:: 待讨论规则顺序是 bug 还是特性

.. figure:: /_images/code_examples/selections/memdemo_04.svg
   :class: width-helper invert-helper
   :name: memdemo_04

   :yoscrypt:`show y %ci*:-[CLK,S]:+$dff,$mux` 的输出

与 ``%ci`` 类似，还有一个用于选择输出锥的 ``%co`` 操作，它接受相同的模式和
重复次数语法。前面提到的 ``%x`` 操作也接受这种高级语法。

这些遍历电路图的操作，结合交集（``%i``）和差集（``%d``）等布尔运算操作，是
提取被研究电路中相关部分的有力工具。

这些表达式的完整文档同样见 :cmd:title:`select`。

增量选择
^^^^^^^^

有时用一系列添加/删除操作来描述选择集最为简便。如前所述，
:yoscrypt:`select -add` 和 :yoscrypt:`select -del` 命令分别向当前选择集添加或
从中删除对象，而不是覆盖它。

.. code:: yoscrypt

    select -none            # start with an empty selection
    select -add reg_*       # select a bunch of objects
    select -del reg_42      # but not this one
    select -add state %ci   # and add more stuff

在 select 表达式中，记号 ``%`` 可用于把先前的选择集压入栈中。

.. code:: yoscrypt

    select t:$add t:$sub    # select all $add and $sub cells
    select % %ci % %d       # select only the input wires to those cells

存储与调回选择集
~~~~~~~~~~~~~~~~


.. todo:: 为演示重新排版

当前选择集可以用 ``select -set <name>`` 命令存储到内存中，之后可以使用
``select @<name>`` 调回。实际上，``@<name>`` 表达式会把存储的选择集压入 `select`
命令维护的栈中。因此例如 :yoscrypt:`select @foo @bar %i` 会选择存储的选择集
``foo`` 与 ``bar`` 的交集。

在规模较大的研究工作中，强烈建议维护一个用于建立相关选择集的脚本，以便在需要时
轻松调回这些选择集，例如在设计或源代码更改后需要重新运行 Yosys 时。

`history` 命令可用于列出所有最近的交互式命令。这一特性有助于把交互式会话中用到的
命令整理成这样的脚本。

请记住，select 表达式也可以直接作为大多数命令的参数。有些命令的某些选项还接受
单个 select 参数。在这些情况下，必须使用选择集变量来捕获更复杂的选择集。

示例代码见 |code_examples/selections|_：

.. |code_examples/selections| replace:: :file:`docs/source/code_examples/selections`
.. _code_examples/selections: https://github.com/YosysHQ/yosys/tree/main/docs/source/code_examples/selections

.. literalinclude:: /code_examples/selections/select.v
   :language: verilog
   :caption: :file:`select.v`

.. literalinclude:: /code_examples/selections/select.ys
   :language: yoscrypt
   :caption: :file:`select.ys`
   :name: select_ys

.. figure:: /_images/code_examples/selections/select.svg
    :class: width-helper invert-helper

    :numref:`select_ys` 生成的电路图
