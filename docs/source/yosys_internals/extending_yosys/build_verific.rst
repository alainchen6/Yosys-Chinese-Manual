使用 Verific 库编译
===================


获取带 Verific 支持的 Yosys 最简单的方式，是向 `contact YosysHQ`_ 申请
`Tabby CAD Suite`_ 的评估许可证和下载链接。为了在使用 Yosys 时充分发挥
Verific 解析器的作用，TabbyCAD Suite 包含额外的补丁和一个自定义扩展库。

如果你已经拥有 Verific 解析器的许可证（无论源码形式还是二进制形式），
你也许能够自行编译带部分 Verific 支持的 Yosys。

.. _contact YosysHQ : https://www.yosyshq.com/contact
.. _Tabby CAD Suite: https://www.yosyshq.com/tabby-cad-datasheet

Yosys-Verific 补丁
------------------


YosysHQ 维护并开发 Verific 的补丁，以便更好地与 Yosys 集成，并提供某些
形式化验证前端工具所需的功能。若要为你自己的 Yosys 构建获得该补丁的
许可，请联系 `contact YosysHQ`_。

.. warning::

   虽然没有该补丁也可能从 RTL 完成综合，但 YosysHQ 不保证正确性，
   也无法提供支持。

除非你熟悉形式化验证前端工具的内部机制，否则我们建议不要将未打补丁的
Yosys+Verific 构建与这些工具一起使用。在某些情况下，这些工具看起来能
正常工作，却会产生错误的结果。

.. note::

   如果没有完整的 TabbyCAD 套件，某些形式化验证前端工具可能无法得到完整
   支持。如果你想使用这些工具（包括 SBY），请务必向我们确认 Yosys-Verific
   补丁是否适合你。

编译选项
--------


要启用 Verific 支持，请将 :makevar:`YOSYS_VERIFIC_DIR` CMake 变量设置为
该库所在的位置，例如

.. code-block:: console

   cmake -B build . -DYOSYS_VERIFIC_DIR="/usr/local/src/verific_lib"

在构建过程中，CMake 会尝试自动检测可用的 Verific 库组件，以启用 Yosys 中
对应的编译期选项。你可以通过手动设置 :makevar:`YOSYS_VERIFIC_FEATURES`
CMake 变量来覆盖这一行为。该变量应包含一个以分号分隔的列表，例如
``-DYOSYS_VERIFIC_FEATURES="systemverilog;hier_tree"``。下表列出了 Yosys
可用的特性。

============== =========== ===================================
特性             目录          说明
============== =========== ===================================
systemverilog  verilog     SystemVerilog 支持
vhdl           vhdl        VHDL 支持
hier_tree      hier_tree   层次树支持
extensions     extensions  YosysHQ 专有扩展支持
edif           edif        EDIF 支持
liberty        synlib      Liberty 文件支持
============== =========== ===================================

.. note::

   只有在 TabbyCAD 套件中才提供 YosysHQ 特有的扩展。

必需的 Verific 特性
~~~~~~~~~~~~~~~~~~~


Yosys-Verific 补丁需要以下特性以及对应的 Yosys 构建参数：

* RTL 细化，使用

  * 通过 ``systemverilog`` 支持 SystemVerilog，和/或
  * 通过 ``vhdl`` 支持 VHDL。

* 通过 ``hier_tree`` 支持层次树和静态细化。

请注意，要构建完整支持的版本，需要启用以下 Verific 配置构建参数：

::

   database/DBCompileFlags.h:
       DB_PRESERVE_INITIAL_VALUE

.. note::

   Yosys+Verific 构建在缺少这些特性时可能仍能编译，但如果它们被禁用或
   未使用 Yosys-Verific 补丁，我们不提供任何保证，也无法提供支持。

可选的 Verific 特性
~~~~~~~~~~~~~~~~~~~


以下 Verific 特性随 TabbyCAD 提供；如果 :makevar:`YOSYS_VERIFIC_DIR` 中
包含所列目录，它们会在 Yosys 构建中被自动启用：

* 通过 ``edif`` 目录支持 EDIF，以及
* 通过 ``synlib`` 目录支持 Liberty 文件。

部分支持的构建
~~~~~~~~~~~~~~


本节介绍的 Yosys+Verific 配置过去被我们确认可用，但它们不属于常规测试
范围，因此我们无法保证它们仍然有效。

要能够用 Verific 编译 Yosys，Verific 库必须至少支持一种启用了 RTL 细化的
HDL 语言。下表列出了一些可行的构建配置，但它们只提供有限的功能子集。
请注意，如果没有 YosysHQ 针对 Verific 库的特定扩展，支持是有限的。

======================================================================= =================================
特性                                                                      :makevar:`YOSYS_VERIFIC_FEATURES`
======================================================================= =================================
SystemVerilog + RTL 细化                                                  systemverilog
VHDL + RTL 细化                                                           vhdl
SystemVerilog + VHDL + RTL 细化                                           systemverilog;vhdl
SystemVerilog + RTL 细化 + 静态细化 + 层次树                                     systemverilog;vhdl;hier_tree
VHDL + RTL 细化 + 静态细化 + 层次树                                              vhdl;hier_tree
SystemVerilog + VHDL + RTL 细化 + 静态细化 + 层次树                              systemverilog;vhdl;hier_tree
======================================================================= =================================

.. note::

   如果你的 Verific 构建支持 EDIF 和/或 Liberty，你可以启用这些选项。
   为简化起见，上面的表格没有列出它们。
