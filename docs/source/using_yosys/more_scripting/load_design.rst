加载设计
--------


.. _input files:

命令行上的输入文件
~~~~~~~~~~~~~~~~~~


- 根据文件扩展名猜测前端

  + ``.v`` -> ``read -vlog2k``
  + ``.sv`` -> ``read -sv``
  + ``.vhd`` 和 ``.vhdl`` -> ``read -vhdl``
  + ``.blif`` 和 ``.eblif`` -> `read_blif`
  + ``.json`` -> `read_json`
  + ``.il`` -> `read_rtlil`，它是 Yosys 内部状态的直接文本表示

- 命令行还支持

  + ``.ys`` -> `script`
  + ``.tcl`` -> `tcl`
  + ``-`` -> 读取 stdin 并将其视为脚本

`read` 命令
~~~~~~~~~~~


- 加载设计的标准方法
- 也用于定义宏和包含目录
- 如果可用，则使用 `verific` 命令

  + ``-verific`` 和 ``-noverific`` 选项用于强制使用/不使用 Verific
  + 查看 ``help read`` 了解可用选项和支持的文件类型
  + 用 ``verific -import [options] <top>`` 展开设计（或使用
    `hierarchy`）

- 回退到带 ``-defer`` 选项的 `read_verilog`

  + 直到执行 `hierarchy` 命令时才编译设计，如
    :doc:`/getting_started/example_synth` 所述
  + 行为更接近 `verific`

- ``read -define`` 等映射到 `verific` 或 `verilog_defines`
- 类似地，``read -incdir`` 等映射到 `verific` 或 `verilog_defaults`

.. note::

   Yosys 的 Verific 前端提供 :cmd:ref:`verific` 命令，它要求 Yosys 在构建时
   启用 Verific。要获得完整功能，需要使用 YosysHQ 对 Verific 源码的自定义修改，
   但某些原版 Verific 构建也能提供有限的功能。更多信息请查看
   :doc:`/yosys_internals/extending_yosys/build_verific`。

.. _Frontend:

Yosys 前端
~~~~~~~~~~


- :doc:`/cmd/index_frontends`
- 通常以 ``read_`` 开头
- 内置对 heredoc 的支持

  + 使用 ``<<EOT`` 的内联代码
  + 可以使用任意 eot 标记，但最常见的是 EOT（End-of-Transmission）和 EOF
    （End-of-File）

- 内置支持在同一条命令中读取多个文件

  + 会作为对前端的多次连续调用执行

- 兼容 ``-f`` 命令行选项，例如 ``yosys -f verilog
  design.txt`` 会使用 `read_verilog` 前端读取输入文件
  ``design.txt``

- `verific` 和 `read` 命令严格来说并不是“前端”（Frontend），但它们的行为保持
  同步

.. note::

   这里的“前端”指该命令实现为 ``RTLIL::Frontend`` 的子类，而不是通常的
   ``RTLIL::Pass``。

.. todo:: 把该注释链接到 :doc:`/yosys_internals/extending_yosys/index` 下尚不存在的

          ``RTLIL::Pass`` 小节

`read_verilog` 命令
"""""""""""""""""""


- :cmd:title:`read_verilog`；另外还有

  + :cmd:title:`verilog_defaults`,
  + :cmd:title:`verilog_defines`, 以及
  + :cmd:title:`read_verilog_file_list`

- 支持 Verilog-2005 的大部分内容
- 对 SystemVerilog 的支持有限
- 一些用于启用形式化验证的非标准特性/扩展
- 请不要依赖 `read_verilog` 进行语法检查

  + 建议先使用仿真器（例如 Icarus Verilog）或借助其他工具（如 verilator）
    做 lint 检查

.. todo:: 理清这个示例代码块

.. code-block:: yoscrypt

    read_verilog file1.v
    read_verilog -I include_dir -D enable_foo -D WIDTH=12 file2.v
    read_verilog -lib cell_library.v

    verilog_defaults -add -I include_dir
    read_verilog file3.v
    read_verilog file4.v
    verilog_defaults -clear

    verilog_defaults -push
    verilog_defaults -add -I include_dir
    read_verilog file5.v
    read_verilog file6.v
    verilog_defaults -pop

其他内置 ``read_*`` 命令
""""""""""""""""""""""""


- :cmd:title:`read_rtlil`
- :cmd:title:`read_aiger`
- :cmd:title:`read_blif`
- :cmd:title:`read_json`
- :cmd:title:`read_liberty`

.. TODO:: `write_file` 算不算？

外部维护的插件
~~~~~~~~~~~~~~


- 用于 VHDL 的 `GHDL plugin`_（查看 ``help ghdl``）
- 用于更全面的 SystemVerilog 支持的 `yosys-slang plugin`_（查看
  ``help read_slang``）

  + yosys-slang 以 '`Frontend`_' 的形式实现，因而自动获得随之而来的全部内置
    支持

.. _GHDL plugin: https://github.com/ghdl/ghdl-yosys-plugin
.. _yosys-slang plugin: https://github.com/povik/yosys-slang

- 上述两个插件都包含在 `OSS CAD Suite`_ 中

.. _OSS CAD Suite: https://github.com/YosysHQ/oss-cad-suite-build

- `Synlig`_，它使用 `Surelog`_ 提供 SystemVerilog 支持

  + 同样实现为 '`Frontend`_'

.. _Synlig: https://github.com/chipsalliance/synlig
.. _Surelog: https://github.com/chipsalliance/Surelog
