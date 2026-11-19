synth 命令
----------


.. todo:: 说明常见的 ``synth_*`` 选项，例如 ``-run``

预打包的 ``synth_*`` 命令
~~~~~~~~~~~~~~~~~~~~~~~~~


Yosys 中针对不同平台提供的所有 synth 命令列表见 :doc:`/cmd/index_techlibs`。
每个命令都会运行一段针对目标平台的子命令脚本。请注意，并非所有这些脚本都在
积极维护，可能已经过时。

通用综合
~~~~~~~~


除了上述面向具体硬件的 synth 命令外，还有 :cmd:title:`prep`。该命令仅限于粗粒度
综合，不会涉及任何架构相关的映射或优化。除其他用途外，它还适合用于设计验证。

`prep` 命令会执行以下命令：

.. literalinclude:: /code_examples/macro_commands/prep.ys
   :start-at: begin:

:doc:`/getting_started/example_synth` 介绍了其中大多数命令及其作用。
