辅助程序
========


除了主程序 yosys 之外，Yosys 发行版还包含一组额外的辅助程序。

yosys-config
------------


``yosys-config`` 工具（一个自动生成的 shell 脚本）可用于查询为 Yosys 构建
可加载模块所需的编译器选项和其他信息。详情参见
:doc:`/yosys_internals/extending_yosys/extensions`。

.. literalinclude:: /generated/yosys-config
    :start-at: Usage

.. _sec:filterlib:

yosys-filterlib
---------------


.. todo:: filterlib 的规则文件是如何工作的？

``yosys-filterlib`` 工具是一个小型实用程序，可用于从 Liberty 文件中剥离或
提取信息。这对于移除时序等敏感或专有信息以及其他商业秘密很有用。

.. literalinclude:: /generated/yosys-filterlib
    :start-at: Usage

yosys-abc
---------


这是 ABC 的一个分支，包含少量尚未被上游接受的定制修改。并非所有版本的 Yosys
都能与所有版本的 ABC 配合工作。因此 Yosys 自带一份 yosys-abc，以避免两者
之间的兼容性问题。

.. literalinclude:: /generated/yosys-abc
    :start-at: usage

yosys-smtbmc
------------


``yosys-smtbmc`` 工具是 SBY 用来与 SMT 求解器交互的实用程序。

.. literalinclude:: /generated/yosys-smtbmc

yosys-witness
-------------


``yosys-witness`` 是一个新工具，用于检查和转换 Yosys 的 witness 轨迹。
SBY 和 SCY 使用它以独立于求解器的统一格式生成轨迹。

.. literalinclude:: /generated/yosys-witness
    :start-at: Usage

.. note:: 使用 ``yosys-witness`` 需要 Python 包 `click`_。

.. _click: https://pypi.org/project/click/
