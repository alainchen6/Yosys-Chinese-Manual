使用 Pyosys 编写脚本
====================


.. TODO:: 记录不使用 Python 的 libyosys

Pyosys 是 Yosys C++ API（即 “libyosys”）的一个有限子集，通过 Python 编程语言
提供。

与 ``.ys`` 和 ``.tcl`` 脚本一样，Pyosys 提供了用 Python 编程语言编写 Yosys
脚本的接口，让你享有类型系统、控制流、面向对象编程等好处；尤其是
其他选项都缺少类型系统，而 Tcl 中的控制流/OOP 也有限。

不过与这两者不同，Pyosys 更进一步，允许你使用
Yosys API 实现原本需要编写 C++ 自定义 pass 才能实现的高级功能。

.. note::

   建议安装 :program:`uv` 来管理 Python 环境：

   .. code:: console

      curl -LsSf https://astral.sh/uv/install.sh | sh

获取 Pyosys
-----------


Pyosys 支持 CPython 3.8 或更高版本。你可以通过以下两种方法之一
使用 Pyosys：

1. 使用 CMake 标志 ``-DYOSYS_WITH_PYTHON=ON`` 编译 Yosys

   这会为 Yosys 二进制添加 ``-y`` 标志，允许你使用嵌入在 Yosys
   自身的解释器执行 Python 脚本：

   ``yosys -y ./my_pyosys_script.py``

   请注意，这需要 Python 能使用一些构建时依赖，
   即 ``pybind11`` 和 ``cxxheaderparser``。如果当前的 Python 环境未提供这些工具，
   可以使用 :program:`uv` 创建一个已安装正确版本工具的
   临时环境。

2. 安装 Pyosys wheel 包

   在 macOS 和 GNU/Linux 上，你可以使用 ``pip`` 安装 Yosys 的预构建
   wheel 包：

   ``python3 -m pip install pyosys``

   然后即可按如下方式运行脚本：

   ``python3 ./my_pyosys_script.py``


编写脚本与数据库检查
--------------------


首先，需要按如下方式导入 libyosys：

.. code-block:: python

   from pyosys import libyosys


提醒一下，Python 允许为导入的模块和对象起别名，因此
为了简洁，可能更倾向于这样导入：

.. code-block:: python

   from pyosys import libyosys as ys


现在，编写脚本实际上与 ``.ys`` 和 ``.tcl`` 脚本非常相似，因为
你可以主要提供文本命令。不过，你可以利用 Python 的便利功能（如条件执行、
循环和函数）来构建脚本：

.. code-block:: python

   do_flatten = True

   ys.run_pass("read_verilog tests/simple/fiedler-cooley.v")
   ys.run_pass("hierarchy -check -auto-top")
   if do_flatten:
      ys.run_pass("flatten")

……但这并没有严格提供任何 Tcl 脚本无法提供给你的东西。使用 Pyosys
的真正强大之处在于，你可以手动实例化、管理
设计数据库并与它交互。

例如，下面是同一个脚本，但使用了手动实例化的设计。

.. literalinclude:: /code_examples/pyosys/simple_database.py
   :start-after: loading design
   :end-before: top module inspection
   :language: python

这里的新增之处在于，你可以手动检查设计的数据库。这
让你能够访问 ``kernel/rtlil.h`` 头文件中声明的大量
设计数据库 API。

例如，下面介绍如何列出设计顶层模块的
输入和输出端口：

.. literalinclude:: /code_examples/pyosys/simple_database.py
   :start-after: top module inspection
   :end-before: # synth
   :language: python

.. tip::

   Yosys 中的 C++ 数据结构会桥接到 Python，使其具有与 Python 对象
   非常相似的 API，例如：

   - ``std::vector`` 支持与 Python 中的
     `可迭代对象 <https://docs.python.org/3/glossary.html#term-iterable>`_ 相同的方法。
   - ``std::set`` 和 hashlib 的 ``pool`` 支持与 Python 中的 ``set``\s 相同的方法。
     虽然 ``set`` 是有序的，但 ``pool`` 不是，修改可能
     导致集合完全重排。
   - ``dict`` 支持与 Python 中的 ``dict``\s 相同的方法，尽管它是
     无序的，修改可能导致字典
     完全重排。
   - ``idict`` 使用一组自定义方法，因为它无法很清晰地
     映射到现有的 Python 数据结构。更多信息请参见
     ``pyosys/hashlib.h``。

   对于大多数操作，也可以将 Python 中的等价类型作为参数，
   它们会被自动转换为正确的类型，因此你不必
   自己手动实例化正确的底层 C++ 对象。

修改数据库
----------


.. warning::

   对数据库的任何修改都可能使 Python 先前持有的引用失效，
   就像编写 C++ 时一样。如果 Python 持有某个引用，Pyosys 目前不会尝试
   让已删除的对象保持存活。

你也不必局限于检查数据库：你可以修改它，
并向设计中引入新元素和/或改动。

作为一个演示示例，假设我们想为 fiedler-cooley 设计中的所有触发器
添加一条使能线。

首先，我们将运行 :yoscrypt:`synth`，把所有逻辑转换为
Yosys 的内部单元结构（参见 :ref:`sec:celllib_gates`）：

.. literalinclude:: /code_examples/pyosys/simple_database.py
   :start-after: # synth
   :end-before: adding the enable line
   :language: python

接下来，我们需要添加新端口。用于此的方法为 ``Module::addWire``\.

.. tip::

   IdString 是 Yosys 内部对字符串的表示形式，用作 Verilog 设计中的
   标识符。它们很高效，因为只存储和传递整数，
   但可以随意与普通字符串相互转换。

   Pyosys 会自动为你将 Python 字符串转换为 IdString，但
   围绕 IdString 的规则仍然适用，即 *大致* 来说：

   - 内部单元的标识符必须以 ``$`` 开头。
   - 所有其他标识符必须以 ``\`` 开头。

.. literalinclude:: /code_examples/pyosys/simple_database.py
   :start-after: adding the enable line
   :end-before: hooking the enable line
   :language: python

请注意，我们修改了信号线，然后调用了一个方法让 Yosys 重新处理
端口。

接下来，我们可以遍历所有组成单元，如果它们的类型是
``$_DFF_P_``，我们就做两件事：

1. 将其类型改为 ``$_DFFE_PP_``，以便能够连接使能信号。
2. 连接使能信号。

.. literalinclude:: /code_examples/pyosys/simple_database.py
   :start-after: hooking the enable line
   :end-before: run check
   :language: python

为了验证一切正确，在完成一组改动后，谨慎的做法是对正在操作的
模块按如下方式调用 ``.check()``：

.. literalinclude:: /code_examples/pyosys/simple_database.py
   :start-after: run check
   :end-before: write output
   :language: python

最后，写出你的输出。这里我选择一个中间 Verilog
文件和 :yoscrypt:`synth_ice40`，将其映射到 iCE40 架构。

.. literalinclude:: /code_examples/pyosys/simple_database.py
   :start-after: write output
   :language: python

瞧，你会注意到在中间输出中，所有 ``always @``
语句都应该带有一个 ``if (enable)``\.

封装为 pass
-----------


就像编写 C++ 时一样，你可以用 “pass（处理流程）” 封装例程，
这会把你的 Pass 添加到可通过 ``run_pass`` 访问的全局命令注册表中。

.. literalinclude:: /code_examples/pyosys/pass.py
   :language: python

通常，由于复杂性，Pyosys 并不真正支持抽象类和虚方法，
但有两个例外：

- ``kernel/register.h`` 中的 ``Pass``
- ``kernel/rtlil.h`` 中的 ``Monitor``
