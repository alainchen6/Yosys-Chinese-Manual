映射到单元库
------------


.. role:: yoscrypt(code)
   :language: yoscrypt

尽管本文档的大部分内容关注的是将 Yosys 用于 FPGA，但也可以把设计映射到可用于
ASIC 设计的单元库。本节将简要介绍一个 `example project`_，它位于 Yosys 源代码
的 :file:`docs/source/code_examples/intro/` 下。该项目包含一个简单的 ASIC 综合
脚本（:file:`counter.ys`）、一个用 Verilog 编写的数字设计（:file:`counter.v`）
以及一个简单的 CMOS 单元库（:file:`mycells.lib`）。这里的许多早期步骤已在
:doc:`/getting_started/example_synth` 文档中有更详细的介绍。

.. note::
   :file:`counter.ys` 脚本包含本文档中用于生成各张图片的命令。本文档中的代码

   片段省略了这些命令，同时保留行号，以便读者对照源代码跟进。

   要了解这些命令的更多信息，请参阅 :ref:`interactive_show`。

.. _example project: https://github.com/YosysHQ/yosys/tree/main/docs/source/code_examples/intro

一个简单的计数器
~~~~~~~~~~~~~~~~


首先，我们快速看一下这个设计：

.. literalinclude:: /code_examples/intro/counter.v
   :language: Verilog
   :linenos:
   :name: counter-v
   :caption: :file:`counter.v`

这是一个带复位和使能的简单计数器。如果复位信号 ``rst`` 为高，则计数器复位
到 0。否则，如果使能信号 ``en`` 为高，则 ``count`` 寄存器会在时钟 ``clk`` 的
每个上升沿加 1。

加载设计
~~~~~~~~


.. literalinclude:: /code_examples/intro/counter.ys
   :language: yoscrypt
   :lines: 1-3
   :lineno-match:
   :caption: :file:`counter.ys` - 读入设计

此时我们的电路如下所示：

.. figure:: /_images/code_examples/intro/counter_00.svg
   :class: width-helper invert-helper
   :name: counter-hierarchy

   `hierarchy` 之后的 ``counter``

粗粒度表示
~~~~~~~~~~


.. literalinclude:: /code_examples/intro/counter.ys
   :language: yoscrypt
   :lines: 7-10
   :lineno-match:
   :caption: :file:`counter.ys` - 高层内容

.. figure:: /_images/code_examples/intro/counter_01.svg
   :class: width-helper invert-helper

   ``counter`` 模块的粗粒度表示

逻辑门映射
~~~~~~~~~~


.. literalinclude:: /code_examples/intro/counter.ys
   :language: yoscrypt
   :lines: 14-15
   :lineno-match:
   :caption: :file:`counter.ys` - 映射到内部单元库

.. figure:: /_images/code_examples/intro/counter_02.svg
   :class: width-helper invert-helper

   `techmap` 之后的 ``counter``

映射到硬件
~~~~~~~~~~


在本例中，我们使用 Liberty 文件来描述一个单元库，内部单元库将被映射到该单元库上：

.. todo:: 寻找一种 Liberty 的 pygments 样式？

.. literalinclude:: /code_examples/intro/mycells.lib
   :language: text
   :linenos:
   :name: mycells-lib
   :caption: :file:`mycells.lib`

回想一下，Yosys 内置的逻辑门类型有 `$_NOT_`、`$_AND_`、`$_OR_`、`$_XOR_`
和 `$_MUX_`，此外还有各种 dff 存储器类型。:ref:`mycells-lib` 把我们的目标单元
定义为 ``BUF``、``NOT``、``NAND``、``NOR`` 和 ``DFF``。二者之间的映射由
`dfflibmap` 和 `abc` 命令按如下方式完成：

.. literalinclude:: /code_examples/intro/counter.ys
   :language: yoscrypt
   :lines: 20-27
   :lineno-match:
   :caption: :file:`counter.ys` - 映射到硬件

我们的 ``counter`` 模块的最终版本如下所示：

.. figure:: /_images/code_examples/intro/counter_03.svg
   :class: width-helper invert-helper

   硬件单元映射之后的 ``counter``

最后使用 `write_verilog` 将其输出为 verilog 文件，之后即可加载到其他工具中：

.. literalinclude:: /code_examples/intro/counter.ys
   :language: yoscrypt
   :lines: 30-31
   :lineno-match:
   :caption: :file:`counter.ys` - 写出综合后的设计
