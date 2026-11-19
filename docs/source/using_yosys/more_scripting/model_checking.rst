符号模型检验
------------


.. todo:: 检查文本上下文

.. note::

    虽然可以直接在 Yosys 中进行模型检验，但强烈建议使用 SBY 或 EQY 进行硬件
    形式化验证。

符号模型检验（SMC）用于形式化证明一个电路具有（或不具有）给定的性质。

其中一个应用是形式化等价检查：证明两个电路完全相同。例如，在调试 Yosys 中的
自定义 pass（处理流程）时，这是一个非常有用的特性。

其他应用包括检查模块是否符合接口标准。

Yosys 中的 `sat` 命令可用于执行符号模型检验。

检查 techmap
~~~~~~~~~~~~


.. todo:: 补充/扩充说明文字

让我们看一个包含在 Yosys 代码库 |code_examples/synth_flow|_ 下的示例：

.. |code_examples/synth_flow| replace:: :file:`docs/source/code_examples/synth_flow`
.. _code_examples/synth_flow: https://github.com/YosysHQ/yosys/tree/main/docs/source/code_examples/synth_flow

.. literalinclude:: /code_examples/synth_flow/techmap_01_map.v
   :language: verilog
   :caption: :file:`techmap_01_map.v`

.. literalinclude:: /code_examples/synth_flow/techmap_01.v
   :language: verilog
   :caption: :file:`techmap_01.v`

.. literalinclude:: /code_examples/synth_flow/techmap_01.ys
   :language: yoscrypt
   :caption: :file:`techmap_01.ys`

要检查它是否正确，我们可以使用以下代码：

.. todo:: 替换行内代码

.. code:: yoscrypt

    # read test design
    read_verilog techmap_01.v
    hierarchy -top test

    # create two version of the design: test_orig and test_mapped
    copy test test_orig
    rename test test_mapped

    # apply the techmap only to test_mapped
    techmap -map techmap_01_map.v test_mapped

    # create a miter circuit to test equivalence
    miter -equiv -make_assert -make_outputs test_orig test_mapped miter
    flatten miter

    # run equivalence check
    sat -verify -prove-asserts -show-inputs -show-outputs miter

结果：

.. code::

    Solving problem with 945 variables and 2505 clauses..
    SAT proof finished - no model found: SUCCESS!

AXI4 Stream Master
~~~~~~~~~~~~~~~~~~


本节使用的代码包含在 Yosys 代码库 |code_examples/axis|_ 下。

.. |code_examples/axis| replace:: :file:`docs/source/code_examples/axis`
.. _code_examples/axis: https://github.com/YosysHQ/yosys/tree/main/docs/source/code_examples/axis

下面的 AXI4 Stream Master 存在一个缺陷。但如果从设备始终把 ``tready`` 保持为
有效，这个缺陷就不会暴露。（测试平台可能会这样做。）

符号模型检验可用于暴露该缺陷，并找出会导致错误行为的 ``tready`` 取值序列。

.. todo:: 补充/扩充说明文字

.. literalinclude:: /code_examples/axis/axis_master.v
   :language: verilog
   :caption: :file:`axis_master.v`

.. literalinclude:: /code_examples/axis/axis_test.v
   :language: verilog
   :caption: :file:`axis_test.v`

.. literalinclude:: /code_examples/axis/axis_test.ys
   :language: yoscrypt
   :caption: :file:`test.ys`

未修改的 :file:`axis_master.v` 的结果：

.. todo:: 替换行内代码

.. code::

    Solving problem with 159344 variables and 442126 clauses..
    SAT proof finished - model found: FAIL!

修复后的 :file:`axis_master.v` 的结果：

.. code::

    Solving problem with 159144 variables and 441626 clauses..
    SAT proof finished - no model found: SUCCESS!

见证框架与逐性质跟踪
~~~~~~~~~~~~~~~~~~~~


当使用基于 AIGER 的形式化验证流程（例如 SBY 中的 ``abc`` 引擎）时，Yosys 提供在
整个验证流水线中跟踪单个形式化性质的基础设施。

`rename -witness` pass 为所有参与见证（witness）框架的单元分配公开名称：

- 见证信号单元：`$anyconst`、`$anyseq`、`$anyinit`、`$allconst`、`$allseq`
- 形式化性质单元：`$assert`、`$assume`、`$cover`、`$live`、`$fair`、`$check`

这些公开名称使下游工具可以通过层次化路径而不是匿名内部标识符来引用各个性质。

`write_aiger -ywmap` 选项会生成一个映射文件，用于与 Yosys witness 轨迹相互转换，
还允许按名称把 AIGER 的坏状态（bad-state）性质和不变式约束映射回各个形式化性质。
这样就能实现逐性质通过/失败报告等功能（例如在 ``--keep-going`` 模式下运行
``abc pdr``）。

`write_smt2` 后端在输出 SMT2 注释时同样使用公开的 witness 名称。``hdlname``
属性包含 ``_witness_`` 标记的单元在注释中会被视为具有私有名称，从而保持求解器
输出简洁。
