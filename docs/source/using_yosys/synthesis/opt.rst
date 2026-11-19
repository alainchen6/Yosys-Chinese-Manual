优化 pass
=========


Yosys 采用多种优化来生成更好、更干净的结果。本章概述这些优化。

.. todo:: 是“概述这些优化”，还是只“概述部分”优化？

`opt` 宏命令
------------


Yosys 的 `opt` pass（处理流程）执行若干简单优化，包括删除未使用的信号和单元以及
常量折叠。建议在综合脚本的每个主要步骤之后运行这个 pass。这条宏命令会调用以下
``opt_*`` 命令：

.. literalinclude:: /code_examples/macro_commands/opt.ys
   :language: yoscrypt
   :start-after: #end:
   :caption: `opt` 调用的 pass

.. _adv_opt_expr:

常量折叠与简单表达式重写 - `opt_expr`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. todo:: 不确定这里的细节是否过多，是否应该放在 :doc:`/yosys_internals/index` 中

这个 pass 对 :doc:`/cell_index` 中描述的内部组合单元类型执行常量折叠。也就是说，
所有输入都是常量的单元会被替换为该单元所驱动的常量值。在某些情况下，这个 pass
也能优化只有部分输入为常量的单元。

.. table:: `opt_expr` 中使用的 `$_AND_` 单元的常量折叠规则。
   :name: tab:opt_expr_and
   :align: center

   ========= ========= ===========
   A 输入    B 输入    替换结果
   ========= ========= ===========
   任意      0         0
   0         任意      0
   1         1         1
   --------- --------- -----------
   X/Z       X/Z       X
   1         X/Z       X
   X/Z       1         X
   --------- --------- -----------
   任意      X/Z       0
   X/Z       任意      0
   --------- --------- -----------
   :math:`a` 1         :math:`a`
   1         :math:`b` :math:`b`
   ========= ========= ===========

:numref:`表 %s <tab:opt_expr_and>` 给出了优化 `$_AND_` 门时使用的替换规则。前三条
规则实现显而易见的常量折叠规则。注意，“任意”可能包含电路其他部分计算出的动态值。
接下来的三行传播未定义（X）状态。根据 IEEE Std. 1364-2005 :cite:p:`Verilog2005`
第 5.1.10 节，这是允许传播未定义值的仅有的三种情况。

再接下来的两行假定未定义状态的值为 0。这两条规则仅在当前模块中无法进行其他替换时
才会使用。如果可以进行其他替换，则先执行那些替换，希望“任意”会变成未定义值或 1，
从而可以把输出设为未定义。

最后两行只是把一个带有一个常量 1 输入的 `$_AND_` 门替换为缓冲器。

除了这种基本常量折叠之外，如果其中一个输入是常量，`opt_expr` pass 还可以把 1 位宽
的 `$eq` 和 `$ne` 单元替换为缓冲器或非门。如果参数中存在冗余位（即两个输入上都是
常量的位），相等性检查的规模也可以减小。例如，如果被比较的信号只有 8 位，就像
:doc:`/getting_started/example_synth` 中的 :ref:`addr_gen_clean` 那样，那么像
``255`` 这样的 32 位宽常量可以被缩减为 8 位值 ``8'11111111``。

`opt_expr` pass 在优化 `$mux` 单元方面非常保守，因为这些单元常用于对决策树建模，
破坏这些树会干扰其他优化。

.. literalinclude:: /code_examples/opt/opt_expr.ys
   :language: Verilog
   :start-after: read_verilog <<EOT
   :end-before: EOT
   :caption: 用于演示 `opt_expr` 的 Verilog 示例

.. figure:: /_images/code_examples/opt/opt_expr.svg
   :class: width-helper invert-helper

   `opt_expr` 处理前后

合并相同的单元 - `opt_merge`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~


这个 pass 执行简单的资源共享，即找出输入完全相同的单元，并用该单元的一个实例替换
它们。

选项 ``-nomux`` 可用于对多路复用器单元（`$mux` 和 `$pmux`）禁用资源共享。这可能
有用，因为它能阻止多路复用器树被合并，而这种合并可能会妨碍 `opt_muxtree` 识别
可能的优化。

.. literalinclude:: /code_examples/opt/opt_merge.ys
   :language: Verilog
   :start-after: read_verilog <<EOT
   :end-before: EOT
   :caption: 用于演示 `opt_merge` 的 Verilog 示例

.. figure:: /_images/code_examples/opt/opt_merge.svg
   :class: width-helper invert-helper

   `opt_merge` 处理前后

从多路复用器树中删除永不激活的分支 - `opt_muxtree`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


这个 pass 通过分析选择输入来优化多路复用器单元构成的树。看下面这个简单的例子：

.. literalinclude:: /code_examples/opt/opt_muxtree.ys
   :language: Verilog
   :start-after: read_verilog <<EOT
   :end-before: EOT
   :caption: 用于演示 `opt_muxtree` 的 Verilog 示例

输出永远不可能是 ``c``，因为这要求 ``a`` 在外层多路复用器中为 1，而在内层多路
复用器中为 0。`opt_muxtree` pass 检测到这一矛盾，并把内层多路复用器替换为常量 1，
从而得到 ``y = a ? b : d`` 的逻辑。

.. figure:: /_images/code_examples/opt/opt_muxtree.svg
   :class: width-helper invert-helper

   `opt_muxtree` 处理前后

化简大型 MUX 和 AND/OR 门 - `opt_reduce`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


这是一个简单的优化 pass，它找出 `$reduce_and` 和 `$reduce_or` 单元中相同的输入位
并将它们合并。它还会对输入位排序，以便其他 pass 更容易识别可共享的 `$reduce_and`
和 `$reduce_or` 单元。

这个 pass 还会找出多路复用器单元的相同输入并将它们合并。在这种情况下，新的共享
选择位由一个 `$reduce_or` 单元驱动，该单元把原来的选择位组合起来。

最后，这个 pass 把 `$reduce_and` 单元树和 `$reduce_or` 单元树分别合并为单个大型
`$reduce_and` 或 `$reduce_or` 单元。

这三种简单优化会在一个循环中反复执行，直到产生稳定的结果。

合并共享输入的互斥单元 - `opt_share`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


这个 pass 会找出满足以下条件的同类型互斥单元：
   a. 共享一个输入信号，并且
   b. 驱动同一个 `$mux`、`$_MUX_` 或 `$pmux` 多路复用单元，

从而允许合并该单元，并把多路复用器从对其输出进行多路复用改为对非共享输入信号进行
多路复用。

.. literalinclude:: /code_examples/opt/opt_share.ys
   :language: Verilog
   :start-after: read_verilog <<EOT
   :end-before: EOT
   :caption: 用于演示 `opt_share` 的 Verilog 示例

.. figure:: /_images/code_examples/opt/opt_share.svg
   :class: width-helper invert-helper

   `opt_share` 处理前后

完整运行 `opt` 时，原来的 `$mux` 单元（标记为 ``$3``）会被 `opt_expr` 优化掉。

执行 DFF 优化 - `opt_dff`
~~~~~~~~~~~~~~~~~~~~~~~~~


.. todo:: ``$_DFF_`` 不是有效的单元

这个 pass 找出数据输入为常量的单比特 D 型触发器（`$_DFF_`、`$dff` 和 `$adff`
单元），并把它们替换为常量驱动源。它还可以合并时钟使能和同步复位多路复用器，
删除未使用的控制输入。

使用 ``-nodffe`` 和 ``-nosdff`` 调用时，这个 pass 用于为
:doc:`/using_yosys/synthesis/fsm` 准备设计。

层次优化 - `opt_hier` pass
~~~~~~~~~~~~~~~~~~~~~~~~~~


这个 pass 考虑设计的层次结构，跨模块边界传播未使用的信号、常量信号和连在一起的
信号，以便其他 pass 进行优化。

删除未使用的单元和信号线 - `opt_clean` pass
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


这个 pass 找出未使用的信号和单元，并把它们从设计中删除。

何时使用 `opt` 或 `clean`
~~~~~~~~~~~~~~~~~~~~~~~~~


通常，在综合脚本中每条常规命令之后调用 `opt` 并无坏处。但这会增加综合时间，因此
只在能够带来改进时才调用 `opt` 更有利。

通常建议在 `sat` 或 `freduce` 这类本身就开销很大的命令之前调用 `opt`，因为在这类
情况下可能的收益远大于可能的损失。

另一方面，`clean` 命令是 `opt_clean` 的别名（输出的信息更少），它非常快，而且许多
命令会留下杂乱状态（悬空的信号线等）。例如，大多数命令不会删除任何信号线或单元，
它们只是改变连接，并依赖稍后调用 clean 来清除此时已不再使用的对象。因此，在每个综合
脚本中偶尔使用 ``;;`` 是个好主意（它本身也是 `clean` 的别名），例如：

.. code-block:: yoscrypt

   hierarchy; proc; opt; memory; opt_expr;; fsm;;

其他优化
--------


.. todo:: 补充其他优化的内容

- 更多内容参见 :doc:`/cmd/index_passes_opt`。
- `abc` 和 `abc9`，另见 :doc:`abc`。
