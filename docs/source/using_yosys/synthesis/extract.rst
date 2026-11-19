extract pass
------------


- 与 `techmap` pass（处理流程）类似，`extract` pass 也是通过映射文件调用的。
  它把映射文件中各模块内部的电路与设计进行比较，并在设计中寻找与映射文件中
  任一模块匹配的子电路。
- 如果找到匹配，`extract` pass 会用映射文件中相应模块的一个实例替换匹配的
  子电路。
- 从某种意义上说，`extract` pass 是 techmap pass 的逆运算。

.. todo:: 补充/扩充说明文字，同时提及自定义模式匹配和 pmgen

示例代码见 |code_examples/macc|_。

.. |code_examples/macc| replace:: :file:`docs/source/code_examples/macc`
.. _code_examples/macc: https://github.com/YosysHQ/yosys/tree/main/docs/source/code_examples/macc


.. literalinclude:: /code_examples/macc/macc_simple_test.ys
    :language: yoscrypt
    :lines: 1-2

.. figure:: /_images/code_examples/macc/macc_simple_test_00a.svg
    :class: width-helper invert-helper

    `extract` 之前

.. literalinclude:: /code_examples/macc/macc_simple_test.ys
    :language: yoscrypt
    :lines: 6

.. figure:: /_images/code_examples/macc/macc_simple_test_00b.svg
    :class: width-helper invert-helper

    `extract` 之后

.. literalinclude:: /code_examples/macc/macc_simple_test.v
   :language: verilog
   :caption: :file:`macc_simple_test.v`

.. literalinclude:: /code_examples/macc/macc_simple_xmap.v
   :language: verilog
   :caption: :file:`macc_simple_xmap.v`

.. literalinclude:: /code_examples/macc/macc_simple_test_01.v
   :language: verilog
   :caption: :file:`macc_simple_test_01.v`

.. figure:: /_images/code_examples/macc/macc_simple_test_01a.svg
    :class: width-helper invert-helper

.. figure:: /_images/code_examples/macc/macc_simple_test_01b.svg
    :class: width-helper invert-helper

.. literalinclude:: /code_examples/macc/macc_simple_test_02.v
   :language: verilog
   :caption: :file:`macc_simple_test_02.v`

.. figure:: /_images/code_examples/macc/macc_simple_test_02a.svg
    :class: width-helper invert-helper

.. figure:: /_images/code_examples/macc/macc_simple_test_02b.svg
    :class: width-helper invert-helper

wrap-extract-unwrap 方法
~~~~~~~~~~~~~~~~~~~~~~~~


粗粒度单元通常具有固定的位宽，但也可以用来实现位宽更小的运算。例如，18x25 位
的乘法器也可以用来实现 16x20 位的乘法。

在粗粒度综合中映射这类单元的一种方法是 wrap-extract-unwrap 方法：

wrap
  在电路中识别候选单元，并用 `techmap` 把它们包装进一个位宽固定且更宽的单元
  中。包装单元使用与原单元相同的参数，因此端口原始位宽的信息得以保留。然后
  使用 `connwrappers` 命令连接包装单元中经过位扩展的输入和输出。

extract
  此时所有运算都按与粗粒度单元相同的位宽进行编码。可以用 `extract` 命令把
  电路替换为目标架构的单元。

unwrap
  剩余的包装单元可以用 `techmap` 解包。

示例：DSP48_MACC
~~~~~~~~~~~~~~~~


本节详细给出一个示例，展示如何把任意大小的 MACC 运算映射到带有 18x25 位乘法器
和 48 位加法器的 MACC 单元（例如 Xilinx DSP48 单元）。

预处理：:file:`macc_xilinx_swap_map.v`

确保 ``A`` 是所有乘法器上较小的端口

.. todo:: 补充/扩充说明文字

.. literalinclude:: /code_examples/macc/macc_xilinx_swap_map.v
   :language: verilog
   :caption: :file:`macc_xilinx_swap_map.v`

包装乘法器：:file:`macc_xilinx_wrap_map.v`

.. literalinclude:: /code_examples/macc/macc_xilinx_wrap_map.v
   :language: verilog
   :lines: 1-46
   :caption: :file:`macc_xilinx_wrap_map.v`

包装加法器：:file:`macc_xilinx_wrap_map.v`

.. literalinclude:: /code_examples/macc/macc_xilinx_wrap_map.v
   :language: verilog
   :lines: 48-89
   :caption: :file:`macc_xilinx_wrap_map.v`

提取：:file:`macc_xilinx_xmap.v`

.. literalinclude:: /code_examples/macc/macc_xilinx_xmap.v
   :language: verilog
   :caption: :file:`macc_xilinx_xmap.v`

……只需对该模块使用与设计中相同的包装命令，即可为 `extract` 命令创建一个模板。

解包乘法器：:file:`macc_xilinx_unwrap_map.v`

.. literalinclude:: /code_examples/macc/macc_xilinx_unwrap_map.v
   :language: verilog
   :lines: 1-30
   :caption: :file:`macc_xilinx_unwrap_map.v` 中的 ``$__mul_wrapper`` 模块

解包加法器：:file:`macc_xilinx_unwrap_map.v`

.. literalinclude:: /code_examples/macc/macc_xilinx_unwrap_map.v
   :language: verilog
   :lines: 32-61
   :caption: :file:`macc_xilinx_unwrap_map.v` 中的 ``$__add_wrapper`` 模块

.. literalinclude:: /code_examples/macc/macc_xilinx_test.v
   :language: verilog
   :lines: 1-6
   :caption: :file:`macc_xilinx_test.v` 中的 ``test1``

.. figure:: /_images/code_examples/macc/macc_xilinx_test1a.svg
    :class: width-helper invert-helper

.. figure:: /_images/code_examples/macc/macc_xilinx_test1b.svg
    :class: width-helper invert-helper

.. literalinclude:: /code_examples/macc/macc_xilinx_test.v
   :language: verilog
   :lines: 8-13
   :caption: :file:`macc_xilinx_test.v` 中的 ``test2``

.. figure:: /_images/code_examples/macc/macc_xilinx_test2a.svg
    :class: width-helper invert-helper

.. figure:: /_images/code_examples/macc/macc_xilinx_test2b.svg
    :class: width-helper invert-helper

``test1`` 中的包装：

.. figure:: /_images/code_examples/macc/macc_xilinx_test1b.svg
    :class: width-helper invert-helper

.. literalinclude:: /code_examples/macc/macc_xilinx_test.ys
    :language: yoscrypt
    :start-after: part c
    :end-before: end part c

.. figure:: /_images/code_examples/macc/macc_xilinx_test1c.svg
    :class: width-helper invert-helper

``test2`` 中的包装：

.. figure:: /_images/code_examples/macc/macc_xilinx_test2b.svg
    :class: width-helper invert-helper

.. literalinclude:: /code_examples/macc/macc_xilinx_test.ys
    :language: yoscrypt
    :start-after: part c
    :end-before: end part c

.. figure:: /_images/code_examples/macc/macc_xilinx_test2c.svg
    :class: width-helper invert-helper

``test1`` 中的提取：

.. figure:: /_images/code_examples/macc/macc_xilinx_test1c.svg
    :class: width-helper invert-helper

.. literalinclude:: /code_examples/macc/macc_xilinx_test.ys
    :language: yoscrypt
    :start-after: part d
    :end-before: end part d

.. figure:: /_images/code_examples/macc/macc_xilinx_test1d.svg
    :class: width-helper invert-helper

``test2`` 中的提取：

.. figure:: /_images/code_examples/macc/macc_xilinx_test2c.svg
    :class: width-helper invert-helper

.. literalinclude:: /code_examples/macc/macc_xilinx_test.ys
    :language: yoscrypt
    :start-after: part d
    :end-before: end part d

.. figure:: /_images/code_examples/macc/macc_xilinx_test2d.svg
    :class: width-helper invert-helper

``test2`` 中的解包：

.. figure:: /_images/code_examples/macc/macc_xilinx_test2d.svg
    :class: width-helper invert-helper

.. literalinclude:: /code_examples/macc/macc_xilinx_test.ys
    :language: yoscrypt
    :start-after: part e
    :end-before: end part e

.. figure:: /_images/code_examples/macc/macc_xilinx_test2e.svg
    :class: width-helper invert-helper
