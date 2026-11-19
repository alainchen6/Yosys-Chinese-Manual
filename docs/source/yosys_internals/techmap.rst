以示例讲解技术映射
------------------


作为快速回顾，`techmap` 命令用 Verilog 代码给出的实现（称为“映射文件”）替换设计
中的单元。它既可以替换 Yosys 的内部单元类型（例如 `$or`），也可以替换用户自定义的
单元类型。

- Verilog 参数被大量用于定制内部单元类型。
- techmap 还使用额外的特殊参数向映射文件传递元数据。
- 映射文件中使用特殊信号线来指示 techmap 如何处理某个模块。
- 生成块和递归是编写映射文件的强大工具。

本文档使用的代码示例包含在 Yosys 代码库的 |code_examples/techmap|_ 下。

.. |code_examples/techmap| replace:: :file:`docs/source/code_examples/techmap`
.. _code_examples/techmap: https://github.com/YosysHQ/yosys/tree/main/docs/source/code_examples/techmap


映射 OR3X1
~~~~~~~~~~


.. todo:: 补充/扩充说明文字

.. note::

    这只是一个用于演示的简单示例。不应用 techmap 来实现基本逻辑优化。

.. literalinclude:: /code_examples/techmap/red_or3x1_map.v
   :language: verilog
   :caption: :file:`red_or3x1_map.v`

.. figure:: /_images/code_examples/techmap/red_or3x1.svg
    :class: width-helper invert-helper

.. literalinclude:: /code_examples/techmap/red_or3x1_test.ys
   :language: yoscrypt
   :caption: :file:`red_or3x1_test.ys`

.. literalinclude:: /code_examples/techmap/red_or3x1_test.v
   :language: verilog
   :caption: :file:`red_or3x1_test.v`

条件化技术映射
~~~~~~~~~~~~~~


- 在某些情况下，只应替换具有特定属性的单元。
- 特殊信号线 ``_TECHMAP_FAIL_`` 可用于针对某组参数禁用映射文件中的模块。
- ``_TECHMAP_FAIL_`` 信号线必须设置为常量值。如果它非零，则该模块对这组参数被
  禁用。
- 示例用例：

    - 仅对特定位宽起作用的粗粒度单元类型
    - 适用于不同存储器几何形状（宽度、深度、端口数等）的存储器资源

示例：

.. figure:: /_images/code_examples/techmap/sym_mul.svg
    :class: width-helper invert-helper

.. literalinclude:: /code_examples/techmap/sym_mul_map.v
   :language: verilog
   :caption: :file:`sym_mul_map.v`

.. literalinclude:: /code_examples/techmap/sym_mul_test.v
   :language: verilog
   :caption: :file:`sym_mul_test.v`

.. literalinclude:: /code_examples/techmap/sym_mul_test.ys
   :language: yoscrypt
   :caption: :file:`sym_mul_test.ys`

在映射模块中使用脚本
~~~~~~~~~~~~~~~~~~~~


- 特殊信号线 ``_TECHMAP_DO_*`` 可用于在替换模块的上下文中运行 Yosys 脚本。
- 按字母顺序排在最前面的信号线会被解释为脚本字符串（必须连接到常量），并作为
  脚本执行。随后该信号线被移除。如此重复。
- 你甚至可以递归地调用 techmap！
- 示例用例：

    - 在映射模块中使用 always 块：调用 `proc`
    - 对已知效果良好的单元执行开销较大的优化（例如 `freduce`）。
    - 与自定义命令交互。

.. note:: 提示：

    在 ``_TECHMAP_DO_*`` 脚本中可以使用 `shell`、``show -pause`` 和 `dump` 等
    命令来调试映射模块。

示例：

.. figure:: /_images/code_examples/techmap/mymul.svg
    :class: width-helper invert-helper

.. literalinclude:: /code_examples/techmap/mymul_map.v
   :language: verilog
   :caption: :file:`mymul_map.v`

.. literalinclude:: /code_examples/techmap/mymul_test.v
   :language: verilog
   :caption: :file:`mymul_test.v`

.. literalinclude:: /code_examples/techmap/mymul_test.ys
   :language: yoscrypt
   :caption: :file:`mymul_test.ys`

处理常量输入
~~~~~~~~~~~~


- 特殊参数 ``_TECHMAP_CONSTMSK_<port-name>_`` 和 ``_TECHMAP_CONSTVAL_<port-name>_``
  可用于处理输入到单元的常量值。
- 前者对端口上所有常量输入位都包含 1 位。
- 后者包含常量位，或对非常量位包含 undef（x）。
- 示例用例：

    - 转换算术运算（例如把乘法转换为移位）。
    - 识别存储器接口中的常量地址或使能位。

示例：

.. figure:: /_images/code_examples/techmap/mulshift.svg
    :class: width-helper invert-helper

.. literalinclude:: /code_examples/techmap/mulshift_map.v
   :language: verilog
   :caption: :file:`mulshift_map.v`

.. literalinclude:: /code_examples/techmap/mulshift_test.v
   :language: verilog
   :caption: :file:`mulshift_test.v`

.. literalinclude:: /code_examples/techmap/mulshift_test.ys
   :language: yoscrypt
   :caption: :file:`mulshift_test.ys`

处理短接的输入
~~~~~~~~~~~~~~


- 特殊参数 ``_TECHMAP_BITS_CONNMAP_`` 和 ``_TECHMAP_CONNMAP_<port-name>_`` 可用于
  处理短接的输入。
- 端口的每一位对应 ``_TECHMAP_CONNMAP_<port-name>_`` 中一个
  ``_TECHMAP_BITS_CONNMAP_`` 位宽的数。
- 每个唯一的信号位被分配自己的编号。``_TECHMAP_CONNMAP_<port-name>_`` 参数中相同
  的字段表示短接的信号位。
- 编号 0-3 分别保留给 ``0``、``1``、``x`` 和 ``z``。
- 示例用例：

    - 检测存储器接口中共享的时钟或控制信号。
    - 在某些情况下，这可用于优化。

示例：

.. figure:: /_images/code_examples/techmap/addshift.svg
    :class: width-helper invert-helper

.. literalinclude:: /code_examples/techmap/addshift_map.v
   :language: verilog
   :caption: :file:`addshift_map.v`

.. literalinclude:: /code_examples/techmap/addshift_test.v
   :language: verilog
   :caption: :file:`addshift_test.v`

.. literalinclude:: /code_examples/techmap/addshift_test.ys
   :language: yoscrypt
   :caption: :file:`addshift_test.ys`

使用 techmap 的注意事项
~~~~~~~~~~~~~~~~~~~~~~~


- 不要在映射模块中使用按位置指定的单元参数。
- 可以为内部单元类型使用 ``$__`` 前缀，以避免与用户命名空间冲突。但务必使用两个
  下划线，否则内部一致性检查器会对这些单元报错。
- Techmap 有两个主要用例：

    - 为算术函数创建良好的逻辑级表示。这也意味着在 ASIC 中使用半加器和全加器单元
      等专用硬件资源，或在 FPGA 中使用专用进位逻辑。
    - 映射块存储器或 DSP 单元等粗粒度资源。
