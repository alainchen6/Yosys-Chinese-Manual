使用 FunctionalIR 编写新后端
============================


什么是 FunctionalIR
-------------------


为了简化面向函数式语言或类似目标的后端编写，Yosys 提供了一种替代的中间表示，
称为 FunctionalIR，它更直接地映射到这些目标上。

FunctionalIR 把设计表示为一个函数 ``(inputs, current_state) ->
(outputs, next_state)``。该函数被分解为一系列对变量的赋值。每个赋值都是简单的
运算，例如加法。复杂的运算被拆分成多个步骤。例如，一个 RTLIL 加法会被翻译为对
输入做符号扩展或零扩展，随后再做一次加法。

与 SSA 形式一样，每个变量只被赋值一次。因此我们可以把变量和赋值视为等价；又
因为这是一种图状表示，这些变量也被称为“节点”。与 RTLIL 的单元和信号线表示不
同，这种表示是严格有序的（按拓扑排序），定义出现在使用之前。

每个节点都有一个“种类”（sort），这是 FunctionalIR 中用来称呼通常所谓“类型”的
术语。可用的种类有

- ``bit[n]``，表示 ``n`` 位的位向量；以及
- ``memory[n,m]``，表示由 ``2**n`` 个 ``bit[m]`` 种类的值组成的不可变数组。

就实际代码而言，Yosys 提供了 ``Functional::IR`` 类来表示 FunctionalIR 中的设计。
``Functional::IR::from_module`` 从一个 RTLIL 模块生成实例。整个设计作为一个整体
存储在内部数据结构中。要访问设计，``Functional::Node`` 类提供了对设计中某个特定
节点的引用。``Functional::IR`` 类支持 ``for(auto node : ir)`` 语法来遍历每个
节点。

``Functional::IR`` 还跟踪输入、输出和状态。这里的“状态”指的是一个“当前状态”
输入和一个“下一状态”输出组成的对。每个寄存器和每个存储器都会创建这样一对。每个
输入、输出和状态都有一个名字（与它们在 RTLIL 中的名字相同）、一个种类和一个
kind。kind 字段通常保持默认值 ``$input``、``$output`` 或 ``$state``，不过某些
RTLIL 单元（例如 ``$assert`` 或 ``$anyseq``）会生成辅助的输入/输出/状态，并
赋予不同的 kind，以便与普通的 RTLIL 输入/输出/状态区分开。

- 要访问单个输入/输出/状态，使用 ``ir.input(name, kind)``、
  ``ir.output(name, kind)`` 或 ``ir.state(name, kind)``。``kind`` 默认为默认
  kind。
- 要遍历某一 kind 的所有输入/输出/状态，可以使用 ``ir.inputs``、
  ``ir.outputs``、``ir.states`` 方法。它们的参数默认为前面提到的默认 kind。
- 要遍历任意 kind 的输入/输出/状态，使用 ``ir.all_inputs``、``ir.all_outputs``
  和 ``ir.all_states``。
- 输出有一个指示其值的节点，可以通过 ``output.value()`` 获取。
- 状态有一个指示其下一值的节点，可以通过 ``state.next_value()`` 获取。状态还有
  初始值，视其种类可通过 ``state.initial_value_signal()`` 或
  ``state.initial_value_memory()`` 访问。

每个节点都有一个“函数”（function），用于定义其运算（函数及其运算的完整列表和
规范见 ``functional.h``）。函数用枚举 ``Functional::Fn`` 表示，函数字段可以通过
``node.fn()`` 访问。由于最常见的操作是对函数做 switch 并同时访问参数，``Node``
类提供了实现访问者模式的 ``visit`` 方法。例如，对于参数为 ``n1`` 和 ``n2`` 的
加法节点 ``node``，``node.visit(visitor)`` 会调用
``visitor.add(node, n1, n2)``。因此，通常的做法是为每个函数实现一个方法。访问者
应继承 ``Functional::AbstractVisitor<ReturnType>`` 或
``Functional::DefaultVisitor<ReturnType>``。前者在某个分支未处理时会产生编译
错误，后者则会改为调用 ``default_handler(node)``。访问者方法应标记为
``override``，以便在参数错误时产生编译错误。

工具类
~~~~~~


``functional.h`` 还提供了一些工具类，它们独立于 FunctionalIR 主表示，但对后端
可能很有用。

``Functional::Writer`` 提供了一个简单的格式化类，它封装 ``std::ostream``，并
提供以下方法：

- ``writer << value`` 封装 ``os << value``。
- ``writer.print(fmt, value0, value1, value2, ...)`` 依次用 ``value0``、
  ``value1``、``value2`` 等替换字符串 ``fmt`` 中的 ``{0}``、``{1}``、``{2}``
  等。每个值都用 ``os << value`` 格式化。也可以写 ``{}`` 来引用最后一个索引
  之后的位置，即 ``{1} {} {} {7} {}`` 等价于 ``{1} {2} {3} {7} {8}``。
- ``writer.print_with(fn, fmt, value0, value1, value2, ...)`` 的作用与 ``print``
  大致相同，但它使用 ``os << fn(value)`` 打印每个值；如果 ``fn(value)`` 不合法，
  则回退到 ``os << value``。

``Functional::Scope`` 负责跟踪目标语言中的变量名。它用于在不同的合法字符集之间
转换，并避免意外重复定义标识符。用户应从 ``Scope`` 派生一个类，并提供以下内容：

- ``Scope<Id>`` 接受一个模板参数，用于指定唯一区分变量的类型。通常为 ``int``
  （如果变量用于 ``Functional::IR`` 节点）或 ``IdString``。
- 派生类应提供构造函数，对目标语言中的每个保留字调用 ``reserve``。
- 必须提供方法 ``bool is_character_legal(char c, int index)``，当且仅当 ``c``
  在位置 ``index`` 的标识符中合法时返回 ``true``。

给定派生类的实例 ``scope``，随后可使用以下方法：

- ``scope.reserve(std::string name)`` 把给定名字标记为已使用
- ``scope.unique_name(IdString suggestion)`` 生成一个此前未使用过的名字，并尽量
  使其与 ``suggestion`` 相似。
- ``scope(Id id, IdString suggestion)`` 的作用与 ``unique_name`` 类似，但对同一个
  ``id`` 的多次调用保证得到相同的名字（与 ``suggestion`` 无关）。

``sexpr.h`` 提供了表示和美化打印 S-表达式的类。S-表达式可以用 ``SExpr::list``
构造，例如 ``SExpr expr = SExpr::list("add", "x", SExpr::list("mul", "y",
"z"))`` 表示 ``(add x (mul y z))``；在文件顶部添加 ``using SExprUtil::list``
后，可以用 ``list`` 作为 ``SExpr::list`` 的简写。为了实现美化打印，
``SExprWriter`` 封装 ``std::ostream``，并提供以下方法：

- ``writer << sexpr`` 把给定表达式写到输出，并对过长的行进行换行、添加合适的
  缩进。
- ``writer.open(sexpr)`` 与 ``writer << sexpr`` 类似，但会省略最后一个右括号。
  之后可以用 ``<<`` 或 ``open`` 单独添加更多参数。这样一来，无需先在内存中构造
  整个表达式，就能打印大型 S-表达式。
- ``writer.open(sexpr, false)`` 与 ``writer.open(sexpr)`` 类似，但后续参数不会
  缩进。这用于避免在无限嵌套的结构上产生无限缩进。
- ``writer.close(n = 1)`` 关闭最后 ``n`` 个尚未关闭的 S-表达式。
- ``writer.push()`` 和 ``writer.pop()`` 用于自动关闭 S-表达式。``writer.pop()``
  会关闭自上次调用 ``writer.push()`` 以来打开的所有 S-表达式。
- ``writer.comment(string)`` 在单独一行写出注释。``writer.comment(string, true)``
  把注释追加到最近打印的 S-表达式之后。
- ``writer.flush()`` 刷新所有缓冲，在直接访问底层 ``std::ostream`` 之前应调用
  它。它不会关闭未关闭的括号。
- 析构函数会调用 ``flush``，同时关闭所有未关闭的括号。

.. _minimal backend:

示例：一个最小的函数式后端
--------------------------


对于一个最小的函数式后端，最基本需要完成三个步骤。首先，需要把设计转换为
FunctionalIR。最简单的方法是，用顶层模块调用
``Functional::IR::from_module()`` 静态方法，或者遍历设计中的每个模块并逐个
转换。其次，需要处理设计中的每个 ``Functional::Node``\ s。遍历
``Functional::IR`` 包含读取模块输入和当前状态，但不包含写出结果。因此最后一步
是处理输出和下一状态。

为了给 Yosys 添加一个输出命令，我们实现 ``Yosys::Backend`` 类并提供它的一个
实例：

.. literalinclude:: /code_examples/functional/dummy.cc
   :language: c++
   :caption: 最小函数式后端的示例源代码，``dummy.cc``

因为我们使用了 ``Backend`` 类，所以 ``"functional_dummy"`` 被注册为
``write_functional_dummy`` 命令。``execute`` 方法是用户调用该命令时运行的部分，
它负责处理各种选项、准备要写入的输出文件，并遍历设计中选中的模块。由于这里没有
任何选项，我们设置 ``argidx = 1`` 并调用 ``extra_args()`` 方法。该方法会读取
命令参数，若出现任何意料之外的参数就报错。它还会把指针 ``f`` 指向输出文件；若
未给出输出文件，则指向 stdout。

.. note::

   关于向 Yosys 添加新命令以及它们如何工作的更多内容，请参阅
   :doc:`/yosys_internals/extending_yosys/extensions`。

在这个最小示例中，我们所做的只是打印出每个节点。``node.name()`` 方法返回一个
``RTLIL::IdString``，我们用 ``unescape()`` 转换它以便打印。然后，为了打印节点的
函数，我们使用 ``node.to_string()``，它给出的字符串形如 ``function(args)``。
其中 ``function`` 部分是 ``Functional::IR::fn_to_string(node.fn())`` 的结果；
``args`` 则是传给该函数的零个或多个参数，最常见的是另一个节点的名字。在幕后，
``node.to_string()`` 方法实际上用一个返回类型为 ``std::string`` 的私有访问者
封装了 ``node.visit(visitor)``。

最后，我们遍历模块的输出和状态，分别使用 ``Functional::IROutput::value()`` 和
``Functional::IRState::next_value()`` 获取转移函数的结果。

示例：为 Rosette 改造 SMT-LIB 后端
----------------------------------


本节将介绍 SMT-LIB 函数式后端（`write_functional_smt2`），以及要让它适用于另一个
S-表达式目标 `Rosette`_ 需要做哪些修改，对应命令为 `write_functional_rosette`。

.. _Rosette: http://emina.github.io/rosette/

概述
~~~~


   Rosette 是一种求解器辅助的编程语言，它扩展了 `Racket`_，加入用于程序综合、
   验证等的语言构造。为了验证或综合代码，Rosette 会把代码编译为逻辑约束，再用
   现成的 `SMT`_ 求解器求解。

   -- https://emina.github.io/rosette/

.. _Racket: http://racket-lang.org/
.. _SMT: http://smtlib.cs.uiowa.edu/

Rosette 由 SMT 求解器支撑，并且是用 S-表达式书写的，因此其代码与
`write_functional_smt2` 的输出非常相似。因此，SMT-LIB 函数式后端可以作为实现
Rosette 后端的起点。

初始 SMT-LIB 后端以及转换后的 Rosette 后端的完整代码清单包含在 Yosys 源码仓库的
:file:`backends/functional` 目录下，分别为 ``smtlib.cc`` 和
``smtlib_rosette.cc``。请注意，Rosette 语言是 Racket 语言的扩展；本指南在讨论
该语言的底层语义/语法时，倾向于用 Racket 来指代。

相对于 SMT-LIB 后端的主要改动如下：

- 名字中所有的 ``Smt`` 前缀都替换为 ``Smtr``，表示 ``smtlib_rosette``；
- 针对 Racket 调整了语法；
- 输入/输出/状态的数据结构从使用带有静态类型字段的 ``declare-datatype``，改为
  使用没有静态类型的 ``struct``；
- 转移函数也失去了静态类型；
- Rosette 中的符号扩展/零扩展使用输出宽度，而不是额外位数，从而获得了静态类型；
- 用全局作用域加上每个结构体各自的局部作用域，取代原来的单一作用域；
- 初始状态以常量值的形式提供，而不是一组断言；
- 并引入了 ``-provides`` 选项，以便更容易在基于 Rosette 的应用中使用生成的代码。

Scope
~~~~~


我们在上述 `minimal backend`_ 基础上的第一处增加是：对于 SMT-LIB 和 Rosette
两种后端，我们面对的都是真实语言，而这些语言对可用作标识符的内容有各自的约束。
上一节介绍的 ``Functional::Scope`` 类正是为此而生；使用该类，我们可以在生成的
输出中安全地重命名标识符，而不必担心冲突或非法的名字/字符。

在 SMT-LIB 版本中，``SmtScope`` 类实现了 ``Scope<int>``；提供了遍历保留关键字
列表、对每个关键字调用 ``reserve`` 的构造函数；并定义了
``is_character_legal`` 方法，拒绝 SMT-LIB 变量名不允许的任何字符，随后在输出中
把这些字符替换为下划线。要使用这个作用域，我们创建它的一个实例，并调用
``Scope::unique_name()`` 方法为每个标识符生成唯一且合法的名字。

在 Rosette 版本中，我们把 ``is_character_legal`` 方法中的合法 ASCII 字符列表
更新为仅包含 Racket 变量名允许的字符。

.. literalinclude:: /generated/functional/rosette.diff
   :language: diff
   :caption: ``Scope`` 类的 diff
   :start-at: -struct SmtScope : public Functional::Scope<int> {
   :end-at: };

在保留关键字方面，我们把 SMT-LIB 规范换成 Racket 规范，以防设计中的某些部分被
意外当作 Racket 代码处理。我们也不再需要保留 ``pair``、``first`` 和 ``second``。
在 `write_functional_smt2` 中，这些名字用于把 ``(inputs, current_state)`` 和
``(outputs, next_state)`` 组合成单个变量。Racket 通过 ``cons`` 原生提供这一
功能，我们稍后会看到。

.. inlined diff for skipping the actual lists
.. code-block:: diff
   :caption: ``reserved_keywords`` 列表的 diff

    const char *reserved_keywords[] = {
   -  // reserved keywords from the smtlib spec
   -  ...
   +  // reserved keywords from the racket spec
   +  ...

      // reserved for our own purposes
   -  "pair", "Pair", "first", "second",
   -  "inputs", "state",
   +  "inputs", "state", "name",
      nullptr
    };

.. note:: 为节省本文篇幅，我们跳过了 smtlib 和 racket 规范中保留关键字的具体

   列表。

Sort
~~~~


接下来在 `write_functional_smt2` 中我们看到 ``Sort`` 类。它是对
``Functional::Sort`` 类的封装，额外提供了用 ``to_sexpr()`` 方法把变量声明映射
为 S-表达式的功能。从 ``SmtSort`` 到 ``SmtrSort`` 的主要变化是语法上的：信号
表示为 ``bitvector``\ s，存储器表示为信号的 ``list``\ s。

.. literalinclude:: /generated/functional/rosette.diff
   :language: diff
   :caption: ``Sort`` 封装的 diff
   :start-at: SExpr to_sexpr() const {
   :end-before: };

Struct
~~~~~~


如上文 `minimal backend`_ 中所见，``Functional::IR`` 类跟踪输入集合、输出集合
以及“状态”变量集合。SMT-LIB 后端把每个集合映射到各自的 ``SmtStruct`` 中，每个
变量在结构体中都有一个对应的字段，并指定 `Sort`_。随后
`write_functional_smt2` 把每个结构体定义为一个新的 ``datatype``，其中每个元素
都是强类型的。

在 Rosette 中，我们不为结构体定义新的数据类型，而是使用原生的 ``struct``。此外，
由于 Racket 提供的静态类型较少，我们只按名字声明每个字段。为便于使用，我们以
注释形式给出每个字段的预期类型。

.. literalinclude:: /generated/functional/rosette.diff
   :language: diff
   :caption: ``write_definition`` 方法的 diff
   :start-at: void write_definition
   :end-before: template<typename Fn> void write_value

每个字段都用 ``insert`` 方法添加到 ``SmtStruct``，该方法还会在 `Scope`_ 中保留
一个唯一的名字（或访问器）。这些访问器由结构体名和字段名组合而成，在全局范围内
唯一，并在 ``access`` 方法中用于从输入/当前状态读取值。

.. literalinclude:: /generated/functional/smtlib.cc
   :language: c++
   :caption: ``Struct::access()`` 方法
   :start-at: SExpr access(
   :end-before: };

在 Rosette 中，结构体字段按 ``<struct_name>-<field_name>`` 的形式访问，因此在
字段名中包含结构体名是冗余的。对于 `write_functional_rosette`，我们改为让字段名
仅在结构体内唯一，而访问器在整个模块内唯一。为此我们修改了类的构造函数和
``insert`` 方法；提供一个结构体局部的作用域（``local_scope``）和一个整个模块
共享的作用域（``global_scope``），而 ``access`` 方法保持不变。

.. literalinclude:: /generated/functional/rosette.diff
   :language: diff
   :caption: 结构体构造函数的 diff
   :start-at: SmtStruct(std::string name, SmtScope &scope)
   :end-before: void write_definition

最后，``SmtStruct`` 还提供了一个 ``write_value`` 模板方法，它对结构体中的每个
元素调用给定的函数。该方法稍后用于给输出/下一状态对赋值。这里唯一的改动是移除了
对零参数构造函数的检查，因为在使用 Rosette 的 ``struct``\ s 时并不需要它。

.. literalinclude:: /generated/functional/rosette.diff
   :language: diff
   :caption: ``write_value`` 方法的 diff
   :start-at: template<typename Fn> void write_value
   :end-before: SExpr access

PrintVisitor
~~~~~~~~~~~~


还记得在 `minimal backend`_ 中，我们使用 ``node.to_string()`` 方法把节点转换成
字符串来写出，该方法用一个私有访问者封装了 ``node.visit()``。现在我们需要一个能
把节点转换为 S-表达式的自定义访问者。``PrintVisitor`` 正是为此而来，它实现了
抽象类 ``Functional::AbstractVisitor``，返回类型为 ``SExpr``。对大多数函数而言，
Rosette 的输出与相应的 SMT-LIB 函数非常相似，只需对语法做少量调整。

.. literalinclude:: /generated/functional/rosette.diff
   :language: diff
   :caption: ``Functional::AbstractVisitor`` 实现 diff 中展示相似之处的部分
   :start-at: SExpr logical_shift_left
   :end-at: "list-set-bv"

不过，两种格式在处理布尔值的方式上存在一些差异，Rosette 为转换提供了内建函数。

.. literalinclude:: /generated/functional/rosette.diff
   :language: diff
   :caption: ``Functional::AbstractVisitor`` 实现 diff 中展示差异的部分
   :start-at: SExpr from_bool
   :end-before: SExpr extract

这里值得注意的是一个罕见的情况：Rosette 实现反而 *获得了* 静态类型，而不是失去
静态类型。SMT_LIB 在调用零扩展/符号扩展时传入所需的额外位数（由
``out_width - a.width()`` 给出），而 Rosette 则指定输出的类型（由
``list("bitvector", out_width)`` 给出）。

.. literalinclude:: /generated/functional/rosette.diff
   :language: diff
   :caption: 零扩展/符号扩展实现的 diff
   :start-after: SExpr buf(
   :end-before: SExpr concat(
   :lines: 2-3, 5-6

.. note:: 请务必查看源代码以了解此处差异的完整列表。

Module
~~~~~~


大部分辅助类都已介绍完毕，现在我们回到 `minimal backend`_ 中的三个主要步骤。
这些都由 ``SmtModule`` 类处理，从 RTLIL 模块到 FunctionalIR 的映射发生在构造
函数中。三个 ``SmtStruct``\ s（输入、输出和状态）也都在构造函数中创建，IR 中
相应列表里的每个值都会被 ``insert``\ ed。

.. literalinclude:: /generated/functional/smtlib.cc
   :language: c++
   :caption: ``SmtModule`` 构造函数
   :start-at: SmtModule(Module
   :end-at: }

由于 Racket 使用 ``-`` 访问结构体字段，``SmtrModule`` 改用下划线来命名初始状态。

.. literalinclude:: /generated/functional/rosette.diff
   :language: diff
   :caption: ``Module`` 构造函数的 diff
   :start-at: scope.reserve(name
   :end-before: for (auto input

``write`` 方法随后负责把 FunctionalIR 按相应后端的格式写入输出文件。
``SmtModule::write()`` 把输出文件分成四部分：定义三个结构体、声明
``pair`` 数据类型、用 ``write_eval`` 定义转移函数
``(inputs, current_state) -> (outputs, next_state)``，以及用 ``write_initial``
声明初始状态。对 ``SmtrModule`` 而言，唯一的改动是不再需要 ``pair`` 声明。

.. literalinclude:: /generated/functional/rosette.diff
   :language: diff
   :caption: ``Module::write()`` 方法的 diff
   :start-at: void write(std::ostream &out)
   :end-at: }

``write_eval`` 方法负责处理 FunctionalIR 节点、输出和下一状态。与
`minimal backend`_ 中一样，我们用 ``for(auto n : ir)`` 遍历节点，然后对
``output_struct`` 和 ``state_struct`` 使用 ``Struct::write_value()`` 方法，
分别遍历输出和下一状态。

.. literalinclude:: /generated/functional/smtlib.cc
   :language: c++
   :caption: 在 ``SmtModule::write_eval()`` 中遍历 FunctionalIR 节点
   :start-at: for(auto n : ir)
   :end-at: }

这里两个后端之间的主要差异在于语法。首先，我们把 ``define-fun`` 换成 Racket
风格的 ``define``，后者去掉了显式类型化的输入/输出。然后，我们把最终结果从
``pair`` 改为原生的 ``cons``，后者的作用基本相同，都在单个变量中返回
``outputs`` 和 ``next_state``。

.. literalinclude:: /generated/functional/rosette.diff
   :language: diff
   :caption: ``Module::write_eval()`` 转移函数声明的 diff
   :start-at: w.open(list("define-fun"
   :end-at: w.open(list("define"

.. literalinclude:: /generated/functional/rosette.diff
   :language: diff
   :caption: 输出/下一状态处理 ``Module::write_eval()`` 的 diff
   :start-at: w.open(list("pair"
   :end-at: w.pop();

对于 ``write_initial`` 方法，SMT-LIB 后端使用 ``declare-const`` 以及必须始终
成立的 ``assert``\ s。对于 Rosette，我们改为把初始状态定义为可供外部代码使用的
普通变量。这个变量 ``[name]_initial`` 随后可以在 ``[name]`` 函数调用中使用；
从而让 Rosette 代码可以用于生成 ``next_state``，而 SMT-LIB 代码只能验证给定的
``next_state`` 是否正确。

.. literalinclude:: /generated/functional/rosette.diff
   :language: diff
   :caption: ``Module::write_initial()`` 方法的 diff
   :start-at: void write_initial
   :end-before: void write

Backend
~~~~~~~


最后一部分是 ``Backend`` 本身，其中大部分样板代码与 `minimal backend`_ 相同。
主要区别在于我们使用 `Module`_ 来执行实际的处理。

.. literalinclude:: /generated/functional/smtlib.cc
   :language: c++
   :caption: ``FunctionalSmtBackend``
   :start-at: struct FunctionalSmtBackend
   :end-at: } FunctionalSmtBackend;

这里为 Rosette 增加了两处内容。第一，输出文件需要以 ``#lang`` 定义开头，告诉
编译器/解释器我们要使用 Rosette 语言模块。第二，`write_functional_rosette`
命令接受一个可选参数 ``-provides``。如果给出了该参数，输出文件就会多出一行，
声明文件中的所有内容都应导出以供使用；从而使该文件可以被当作一个 Racket 包，
其中的结构体和映射函数可供外部使用。

.. literalinclude:: /generated/functional/rosette.diff
   :language: diff
   :caption: ``Backend::execute()`` 方法 diff 的相关部分
   :start-at: lang rosette/safe
   :end-before: for (auto module
