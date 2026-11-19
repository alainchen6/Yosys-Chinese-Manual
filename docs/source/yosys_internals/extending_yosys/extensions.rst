编写扩展
========


.. role:: yoscrypt(code)
   :language: yoscrypt

.. todo:: 检查文字是否连贯

.. todo:: 更新为使用 :file:`/code_examples/extensions/test*.log`

本章包含一些关于编写 Yosys 扩展的零散信息。不要害怕在 YosysHQ Discourse 上提问。

.. todo:: 提及编码指南

快速指南
--------


本节中的代码示例包含在 Yosys 源代码的 |code_examples/extensions|_ 目录中。

.. |code_examples/extensions| replace:: :file:`docs/source/code_examples/extensions`
.. _code_examples/extensions: https://github.com/YosysHQ/yosys/tree/main/docs/source/code_examples/extensions


程序组件与数据格式
~~~~~~~~~~~~~~~~~~


关于 Yosys 内部使用的数据存储格式及其提供的类，参见
:doc:`/yosys_internals/formats/rtlil_rep` 文档。

本文聚焦于执行 `proc` 和 `memory` 命令（或 :yoscrypt:`memory -nomap`）之后剩下
的简化得多的 RTLIL 版本：

.. figure:: /_images/internals/simplified_rtlil.svg
    :class: width-helper invert-helper
    :name: fig:Simplified_RTLIL

    不含存储器和过程块的简化 RTLIL 实体关系图

可以只处理这个更简单的版本：

.. todo:: 考虑替换行内代码

.. code:: c++

    for (RTLIL::Module *module : design->selected_modules() {
        if (module->has_memories_warn() || module->has_processes_warn())
            continue;
        ....
    }


在试图理解某条命令的作用时，可以创建一个小测试用例，查看该命令执行前后 `dump`
和 `show` 的输出，这会很有帮助。关于这些命令的用法，
:doc:`/using_yosys/more_scripting/selections` 中有更多信息。

创建命令
~~~~~~~~


.. todo:: 补充/扩展配套文字

我们来创建一个非常简单的测试命令，它会打印调用它时传入的参数，并列出当前设计
中的模块。

.. literalinclude:: /code_examples/extensions/my_cmd.cc
   :language: c++
   :lines: 1, 4, 6, 7-20
   :caption: 来自 :file:`my_cmd.cc` 的示例命令 :yoscrypt:`my_cmd`

注意，我们创建了一个派生自 ``Yosys::Pass`` 的类的全局实例，这个类是通过包含
:file:`kernel/yosys.h` 得到的。

编译为插件
~~~~~~~~~~


可以通过向 Yosys 代码库添加额外的 C++ 代码来扩展 Yosys，也可以向 Yosys 中加载
插件。出于可维护性考虑，通常建议创建插件。

下面的命令把我们的示例 :yoscrypt:`my_cmd` 编译为 Yosys 插件：

.. todo:: 替换行内代码

.. code:: shell

   yosys-config --exec --cxx --cxxflags --ldflags \
   -o my_cmd.so -shared my_cmd.cc --ldlibs

或者用更短的写法：

.. code:: shell

   yosys-config --build my_cmd.so my_cmd.cc

使用 ``-m`` 选项运行 Yosys 就可以使用该插件。下面是一个简单的示例，它还使用了
``-p`` 选项来运行 :yoscrypt:`my_cmd foo bar`。

.. code:: shell-session

   $ yosys -m ./my_cmd.so -p 'my_cmd foo bar'

   -- Running command `my_cmd foo bar' --
   Arguments to my_cmd:
     my_cmd
     foo
     bar
   Modules in current design:

从零创建模块
~~~~~~~~~~~~


我们用 RTLIL API 创建以下模块：

.. literalinclude:: /code_examples/extensions/absval_ref.v
   :language: Verilog
   :caption: absval_ref.v

我们将像之前一样，把它写成 ``Yosys::Pass`` 的形式。

.. literalinclude:: /code_examples/extensions/my_cmd.cc
   :language: c++
   :lines: 23-47
   :caption: :yoscrypt:`test1` - 创建 absval 模块，来自 :file:`my_cmd.cc`

.. code:: shell-session

   $ yosys -m ./my_cmd.so -p 'test1' -Q

   -- Running command `test1' --
   Name of this module: absval

如果查看这个新模块的原理图，会看到如下内容：

.. figure:: /_images/code_examples/extensions/test1.svg
   :class: width-helper invert-helper

   ``yosys -m ./my_cmd.so -p 'test1; show'`` 的输出

修改模块
~~~~~~~~


大多数命令修改已有模块，而不是创建新模块。

修改已有模块时，请遵循以下该做与不该做的事项：

- 不要移除信号线。只需将它们断开，让后续的 `clean` 命令负责移除它们。
- 修改信号线的 ``port_*`` 属性后，要调用 ``module->fixup_ports()``。
- 可以安全地移除单元或修改单元的 ``connections`` 属性，但在改变连接到单元端口
  的 ``SigSpec`` 大小时要小心。
- 当你需要为每个信号位获取唯一句柄时，请使用 ``SigMap`` 辅助类（见下一节）。

使用 SigMap 辅助类
~~~~~~~~~~~~~~~~~~


考虑以下模块：

.. literalinclude:: /code_examples/extensions/sigmap_test.v
   :language: Verilog
   :caption: :file:`sigmap_test.v`

在这里，``a``、``x`` 和 ``y`` 都是同一个信号的不同名称。然而：

.. todo:: 使用 my_cmd.cc 的 literalincludes

.. code:: C++

    RTLIL::SigSpec a(module->wire("\\a")), x(module->wire("\\x")),
                                           y(module->wire("\\y"));
    log("%d %d %d\n", a == x, x == y, y == a); // will print "0 0 0"

``SigMap`` 辅助类可以把所有这些互为别名的信号映射到该组中的唯一信号（通常是
由单元或端口直接驱动的信号线）。

.. code:: C++

    SigMap sigmap(module);
    log("%d %d %d\n", sigmap(a) == sigmap(x), sigmap(x) == sigmap(y),
                      sigmap(y) == sigmap(a)); // will print "1 1 1"

打印日志消息
~~~~~~~~~~~~


``log()`` 函数是一个类似 ``printf()`` 的函数，可用于生成日志消息。

使用 ``log_signal()`` 为 SigSpec 对象创建 C 字符串：

.. code:: C++

    log("Mapped signal x: %s\n", log_signal(sigmap(x)));

``log_signal()`` 返回的指针之后会由日志框架自动释放。

使用 ``log_header()`` 和 ``log_push()``/\ ``log_pop()`` 来组织日志消息：

.. todo:: 替换行内代码

.. code:: C++

    log_header(design, "Doing important stuff!\n");
    log_push();
    for (int i = 0; i < 10; i++)
        log("Log message #%d.\n", i);
    log_pop();

错误处理
~~~~~~~~


使用 ``log_error()`` 报告不可恢复的错误：

.. todo:: 替换行内代码

.. code:: C++

    if (design->modules.count(module->name) != 0)
        log_error("A module with the name %s already exists!\n", module);

使用 ``log_cmd_error()`` 报告可恢复的错误：

.. code:: C++

    if (design->selection().empty())
        log_cmd_error("This command can't operator on an empty selection!\n");

请使用 ``log_assert()`` 和 ``log_abort()``，而不要使用 ``assert()`` 和
``abort()``。

"stubnets" 示例模块
-------------------


下面是 "stubnets" 示例模块的完整代码。它包含在 Yosys 源码发行版的
|code_examples/stubnets|_ 目录下。

.. |code_examples/stubnets| replace:: :file:`docs/source/code_examples/stubnets`
.. _code_examples/stubnets: https://github.com/YosysHQ/yosys/tree/main/docs/source/code_examples/stubnets

.. literalinclude:: /code_examples/stubnets/stubnets.cc
    :language: c++
    :linenos:
    :caption: :file:`stubnets.cc`

.. literalinclude:: /code_examples/stubnets/Makefile
    :language: makefile
    :linenos:
    :caption: :file:`Makefile`

.. literalinclude:: /code_examples/stubnets/test.v
    :language: verilog
    :linenos:
    :caption: :file:`test.v`
