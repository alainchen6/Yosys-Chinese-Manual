转换过程块
~~~~~~~~~~


.. role:: yoscrypt(code)
   :language: yoscrypt

Verilog 前端会把 ``always`` 块转换为用于表达式的 RTL 网表，以及用于控制和存储器
元件的“进程”。`proc` 命令随后把这些“进程”转换为由 RTL 多路复用器和寄存器单元
组成的网表。它也是一条宏命令，会按合理的顺序调用其他 ``proc_*`` 命令：

.. literalinclude:: /code_examples/macro_commands/proc.ys
   :language: yoscrypt
   :start-after: #end:
   :caption: `proc` 调用的 pass

在全部 ``proc_*`` 命令之后会调用 `opt_expr`。可以通过调用 :yoscrypt:`proc -noopt`
来禁用这一步。有关 `proc` 的更多信息（例如禁用某些子命令），参见
:doc:`/cmd/index_passes_proc`。

许多命令无法处理含有“进程”的模块。通常，`proc` 是设计细化之后实际综合流程中的
第一条命令。

示例
^^^^

.. todo:: 描述 ``proc`` 的图片

|code_examples/synth_flow|_。

.. |code_examples/synth_flow| replace:: :file:`docs/source/code_examples/synth_flow`
.. _code_examples/synth_flow: https://github.com/YosysHQ/yosys/tree/main/docs/source/code_examples/synth_flow

.. literalinclude:: /code_examples/synth_flow/proc_01.v
   :language: verilog
   :caption: :file:`proc_01.v`

.. literalinclude:: /code_examples/synth_flow/proc_01.ys
   :language: yoscrypt
   :caption: :file:`proc_01.ys`

.. figure:: /_images/code_examples/synth_flow/proc_01.svg
   :class: width-helper invert-helper

.. figure:: /_images/code_examples/synth_flow/proc_02.svg
   :class: width-helper invert-helper

.. literalinclude:: /code_examples/synth_flow/proc_02.v
   :language: verilog
   :caption: :file:`proc_02.v`

.. literalinclude:: /code_examples/synth_flow/proc_02.ys
   :language: yoscrypt
   :caption: :file:`proc_02.ys`

.. figure:: /_images/code_examples/synth_flow/proc_03.svg
   :class: width-helper invert-helper

.. literalinclude:: /code_examples/synth_flow/proc_03.ys
   :language: yoscrypt
   :caption: :file:`proc_03.ys`

.. literalinclude:: /code_examples/synth_flow/proc_03.v
   :language: verilog
   :caption: :file:`proc_03.v`
