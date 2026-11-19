.. _chapter:verilog:

Verilog 与 AST 前端
===================


本章概述 Yosys 的 Verilog 前端与 AST 前端的实现。Verilog 前端读取
Verilog-2005 代码，并为输入创建抽象语法树（AST）表示。该 AST 表示随后
被传递给 AST 前端，由后者将其转换为 RTLIL 数据，如
:numref:`图 %s <fig:Verilog_flow>` 所示。

.. figure:: /_images/internals/verilog_flow.svg
	:class: width-helper invert-helper
	:name: fig:Verilog_flow

	简化的 Verilog 到 RTLIL 数据流

将 Verilog 转换为 AST
---------------------


Verilog 前端将 Verilog 源文件转换为内部 AST 表示，该表示与原始 Verilog
代码的结构十分相似。Verilog 前端由三个组件构成：预处理器、词法分析器和
语法分析器。

Verilog 前端的源代码可在 Yosys 源码树的
:file:`frontends/verilog/` 中找到。

Verilog 预处理器
~~~~~~~~~~~~~~~~


Verilog 预处理器扫描 Verilog 源代码，并解释诸如 :literal:`\`include`、
:literal:`\`define` 和 :literal:`\`ifdef` 之类的 Verilog 编译指令。

它实现为一个 C++ 函数：输入是一个文件描述符，返回预处理后的 Verilog
代码，类型为 ``std::string``。

Verilog 预处理器的源代码可在 Yosys 源码树的
:file:`frontends/verilog/preproc.cc` 中找到。

Verilog 词法分析器
~~~~~~~~~~~~~~~~~~


Verilog 词法分析器使用词法分析器生成器 flex 编写。其源代码可在 Yosys
源码树的 :file:`frontends/verilog/verilog_lexer.l` 中找到。该词法分析器
所做的工作不多，主要是识别 Yosys Verilog 前端所识别的所有关键字和字面量。

词法分析器用 ``VerilogLexer::out_loc`` 跟踪 Verilog 源代码中的当前位置，
并用它来构造语法分析器定义的符号对象。

最后，词法分析器识别并处理特殊注释，例如
"``// synopsys translate_off``" 和 "``// synopsys full_case``"。（建议尽可能
使用 :literal:`\`ifdef` 结构代替 Synopsys 的 translate_on/off 注释，并使用
``(* full_case *)`` 之类的属性代替 "``// synopsys full_case``"。）

Verilog 语法分析器
~~~~~~~~~~~~~~~~~~


Verilog 语法分析器使用语法分析器生成器 bison 编写。其源代码可在 Yosys
源码树的 :file:`frontends/verilog/verilog_parser.y` 中找到。

它使用 :file:`frontends/ast/ast.h` 中定义的 ``AST::AstNode`` 数据结构
生成 AST。``AST::AstNode`` 对象具有以下属性：

.. list-table:: AST 节点类型及其对应的 Verilog 构造。
    :name: tab:Verilog_AstNodeType
    :widths: 50 50

    * - AST 节点类型
      - 对应的 Verilog 构造
    * - AST_NONE
      - 此节点类型永远不应被使用。
    * - AST_DESIGN
      - 此节点类型用于 AST 树的顶层节点。它没有对应的 Verilog 构造。
    * - AST_MODULE, AST_TASK, AST_FUNCTION
      - ``module``、``task`` 和 ``function``
    * - AST_WIRE
      - ``input``、``output``、``wire``、``reg`` 和 ``integer``
    * - AST_MEMORY
      - Verilog 数组
    * - AST_AUTOWIRE
      - 使用未声明的信号名时由化简器创建。
    * - AST_PARAMETER, AST_LOCALPARAM
      - ``parameter`` 和 ``localparam``
    * - AST_PARASET
      - 单元实例化中设置的参数
    * - AST_ARGUMENT
      - 单元实例化中的端口连接
    * - AST_RANGE
      - 信号中的位索引或数组中的元素索引
    * - AST_CONSTANT
      - 字面量值
    * - AST_CELLTYPE
      - 单元实例化中单元的类型
    * - AST_IDENTIFIER
      - 标识符（表达式中的信号名，或其他上下文中的单元/任务等名称）
    * - AST_PREFIX
      - 构造形如 <prefix>[<index>].<suffix> 的标识符（仅用于高级 generate
        构造）
    * - AST_FCALL, AST_TCALL
      - 调用函数或任务
    * - AST_TO_SIGNED, AST_TO_UNSIGNED
      - ``$signed()`` 和 ``$unsigned()`` 函数
    * - AST_CONCAT, AST_REPLICATE
      - ``{...}`` 和 ``{...{...}}`` 运算符
    * - AST_BIT_NOT, AST_BIT_AND, AST_BIT_OR, AST_BIT_XOR, AST_BIT_XNOR
      - 按位运算符 ``~``、``&``、``|``、``^`` 和 ``~^``
    * - AST_REDUCE_AND, AST_REDUCE_OR, AST_REDUCE_XOR, AST_REDUCE_XNOR
      - 一元归约运算符 ``~``、``&``、``|``、``^`` 和 ``~^``
    * - AST_REDUCE_BOOL
      - 从多位值到布尔值的转换（等价于 AST_REDUCE_OR）
    * - AST_SHIFT_LEFT, AST_SHIFT_RIGHT, AST_SHIFT_SLEFT, AST_SHIFT_SRIGHT
      - 移位运算符 ``<<``、``>>``、``<<<`` 和 ``>>>``
    * - AST_LT, AST_LE, AST_EQ, AST_NE, AST_GE, AST_GT
      - 关系运算符 ``<``、``<=``、``==``、``!=``、``>=`` 和 ``>``
    * - AST_ADD, AST_SUB, AST_MUL, AST_DIV, AST_MOD, AST_POW
      - 二元运算符 ``+``、``-``、``*``、``/``、``%`` 和 ``**``
    * - AST_POS, AST_NEG
      - 前缀运算符 ``+`` 和 ``-``
    * - AST_LOGIC_AND, AST_LOGIC_OR, AST_LOGIC_NOT
      - 逻辑运算符 ``&&``、``||`` 和 ``!``
    * - AST_TERNARY
      - 三目 ``?:`` 运算符
    * - AST_MEMRD AST_MEMWR
      - 读写存储器。这些节点由 AST 化简器针对 Verilog 数组的写/读生成。
    * - AST_ASSIGN
      - ``assign`` 语句
    * - AST_CELL
      - 单元实例化
    * - AST_PRIMITIVE
      - 原语单元（``and``、``nand``、``or`` 等）
    * - AST_ALWAYS, AST_INITIAL
      - Verilog ``always`` 块和 ``initial`` 块
    * - AST_BLOCK
      - ``begin``-``end`` 块
    * - AST_ASSIGN_EQ. AST_ASSIGN_LE
      - ``always`` 块或 ``initial`` 块内的阻塞赋值（``=``）和非阻塞赋值
        （``<=``）
    * - AST_CASE. AST_COND, AST_DEFAULT
      - 分别对应 ``case``（``if``）语句、case 内的条件以及默认分支
    * - AST_FOR
      - ``always`` 块或 ``initial`` 块中的 ``for`` 循环
    * - AST_GENVAR, AST_GENBLOCK, AST_GENFOR, AST_GENIF
      - ``genvar`` 和 ``generate`` 关键字，以及 generate 块中的 ``for``
        和 ``if``
    * - AST_POSEDGE, AST_NEGEDGE, AST_EDGE
      - ``always`` 块的事件条件。

-  | 节点类型
   | 该枚举（``AST::AstNodeType``）指定节点的角色。
     :numref:`表 %s <tab:Verilog_AstNodeType>` 列出了所有节点类型。

-  | 子节点
   | 这是指向抽象语法树中所有子节点的指针列表。

-  | 属性
   | 由于几乎每个 AST 节点都可能带有 Verilog 属性，``AST::AstNode`` 直接
     支持属性。注意，属性值本身又是 AST 节点。

-  | 节点内容
   | 每个节点都可能带有附加的内容数据。存在一系列成员变量用于保存此类数据。
     例如，成员 ``std::string str`` 可以保存字符串值，在 ``AST_IDENTIFIER``
     节点类型中用于存储标识符名称。

-  | 源代码位置
   | 每个 ``AST::AstNode`` 都由 ``AST::AstNode`` 构造函数自动标注当前源代码
     位置。``location`` 类型是对 bison 提供的位置类型的手工重新实现。该
     类型定义在 ``frontends/verilog/verilog_location.h``。

``AST::AstNode`` 构造函数最多可以接受 4 个子节点。这在一定程度上简化了
为简单表达式创建 AST 节点的工作。例如，用于解析乘法的 bison 代码：

.. code:: none
   :number-lines:

   basic_expr TOK_ASTER attr basic_expr {
     $$ = std::make_unique<AstNode>(AST_MUL, std::move($1), std::move($4));
     SET_AST_NODE_LOC($$.get(), @1, @4);
     append_attr($$.get(), $3);
   } |

生成的 AST 数据结构随后被直接传递给 AST 前端，由后者执行到 RTLIL 的
实际转换。

注意，Yosys 命令 ``read_verilog`` 提供了 ``-yydebug`` 和 ``-dump_ast``
两个选项，可分别用于打印分析树或抽象语法树。

将 AST 转换为 RTLIL
-------------------


AST 前端将一组 AST 表示的模块转换为 RTLIL 表示的模块，并把它们加入
当前设计。这一转换分两步完成：化简和 RTLIL 生成。

AST 前端的源代码可在 Yosys 源码树的 ``frontends/ast/`` 中找到。

AST 化简
~~~~~~~~


功能完整的 AST 过于复杂，无法直接转换为 RTLIL。因此必须首先将其变为
更简单的形式。具体做法是对 AST 中所有 ``AST_MODULE`` 节点调用
``AST::AstNode::simplify()`` 方法。这会启动一个递归过程，对 AST 数据结构
执行以下变换：

-  内联所有任务和函数调用。

-  求值所有 ``generate`` 语句，并展开所有 ``for`` 循环。

-  在必要处执行常量折叠（例如 ``AST_PARAMETER``、``AST_LOCALPARAM``、
   ``AST_PARASET`` 和 ``AST_RANGE`` 节点的值部分）。

-  用适当的 ``AST_ASSIGN`` 节点替换 ``AST_PRIMITIVE`` 节点。

-  将赋值左侧的动态位范围替换为 ``AST_CASE`` 节点，并为每种可能情况添加
   ``AST_COND`` 子节点。

-  检测对 ``RTLIL::Memory`` 抽象而言过于复杂的数组访问模式，并为所有读
   和/或写将其替换为一组信号和 case。

-  否则，用 ``AST_MEMRD`` 和 ``AST_MEMWR`` 节点替换数组访问。

除这些变换外，化简器还为 AST 标注 RTLIL 生成器所需的附加信息，即：

-  所有范围（信号宽度和位选择）不仅会被常量折叠，而且（在找到常量值时）
   还会写入 AST_RANGE 节点中的成员变量。

-  所有标识符都会被解析，所有 ``AST_IDENTIFIER`` 节点都会标注一个指向
   包含该标识符声明的 AST 节点的指针。如果未找到声明，则创建一个
   ``AST_AUTOWIRE`` 节点并用于标注。

这样产生的 AST 相当容易转换为 RTLIL 格式。

生成 RTLIL
~~~~~~~~~~


完成 AST 化简后，会调用 AST 中每个 ``AST_MODULE`` 节点的
``AST::AstNode::genRTLIL()`` 方法。这会启动一个递归过程，为 AST 数据生成
等价的 RTLIL 数据。

``AST::AstNode::genRTLIL()`` 方法返回 ``RTLIL::SigSpec`` 结构。对于表示
表达式的节点（运算符、常量、信号等），会创建实现该表达式所描述计算所需的
单元，并返回结果信号。这样，使用深度优先递归就很容易为大表达式生成电路。
对于不表示表达式的节点（例如 ``AST_CELL``），则生成相应的电路并返回空的
``RTLIL::SigSpec``。

综合 Verilog always 块
----------------------


对于行为级 Verilog 代码（使用 ``always`` 块和 ``initial`` 块的代码），
还需要生成 ``RTLIL::Process`` 对象。具体做法如下：

每当 ``AST::AstNode::genRTLIL()`` 遇到 ``always`` 块或 ``initial`` 块时，
它会创建一个 ``AST_INTERNAL::ProcessGenerator`` 实例。该对象随后为该块生成
``RTLIL::Process`` 对象。它还会对该块内包含的所有右侧表达式调用
``AST::AstNode::genRTLIL()``。

首先，``AST_INTERNAL::ProcessGenerator`` 创建该块内所有被赋值信号的列表。
然后，它为每个被赋值的信号使用命名方案 ``$ <number> \ <original_name>``
创建一组临时信号。

接着创建一个 ``RTLIL::Process``，在其
``RTLIL::CaseRule``/``RTLIL::SwitchRule`` 树中把每个左侧信号的所有中间值
赋给对应的临时信号。

最后，为该 ``RTLIL::Process`` 创建一个 ``RTLIL::SyncRule``，把保存最终值的
临时信号赋给实际信号。

一个过程还可能包含存储器写操作。每个写操作都会创建一个
``RTLIL::MemWriteAction``。

右侧表达式会按需生成对 ``AST::AstNode::genRTLIL()`` 的调用。使用阻塞赋值
时，通过全局变量配置 ``AST::AstNode::genRTLIL()``，使得在表达式中使用先前
已被赋值的信号时，改用保存正确中间值的临时信号。

遗憾的是，为行为级代码生成正确的
``RTLIL::CaseRule``/\ ``RTLIL::SwitchRule`` 树是一项不简单的任务。AST 前端
采用下文所述的方法解决该问题。下面的例子说明了该算法要完成的工作。考虑以下
Verilog 代码：

.. code:: verilog
   :number-lines:

   always @(posedge clock) begin
       out1 = in1;
       if (in2)
           out1 = !out1;
       out2 <= out1;
       if (in3)
           out2 <= out2;
       if (in4)
           if (in5)
               out3 <= in6;
           else
               out3 <= in7;
       out1 = out1 ^ out2;
   end

这段代码由 Verilog 前端和 AST 前端转换为以下 RTLIL 代码（未包含属性、单元
参数和信号线声明）：

.. code:: RTLIL
   :number-lines:

   cell $logic_not $logic_not$<input>:4$2
     connect \A \in1
     connect \Y $logic_not$<input>:4$2_Y
   end
   cell $xor $xor$<input>:13$3
     connect \A $1\out1[0:0]
     connect \B \out2
     connect \Y $xor$<input>:13$3_Y
   end
   process $proc$<input>:1$1
     assign $0\out3[0:0] \out3
     assign $0\out2[0:0] $1\out1[0:0]
     assign $0\out1[0:0] $xor$<input>:13$3_Y
     switch \in2
       case 1'1
         assign $1\out1[0:0] $logic_not$<input>:4$2_Y
       case
         assign $1\out1[0:0] \in1
     end
     switch \in3
       case 1'1
         assign $0\out2[0:0] \out2
       case
     end
     switch \in4
       case 1'1
         switch \in5
           case 1'1
             assign $0\out3[0:0] \in6
           case
             assign $0\out3[0:0] \in7
         end
       case
     end
     sync posedge \clock
       update \out1 $0\out1[0:0]
       update \out2 $0\out2[0:0]
       update \out3 $0\out3[0:0]
   end

注意，两个运算符被转换为所生成过程之外的独立单元。信号 ``out1`` 使用
阻塞赋值，因此在初始赋值之后的所有表达式中，``out1`` 都被替换为另一个
信号。信号 ``out2`` 使用非阻塞赋值，因此不会在右侧表达式中被替换。

``RTLIL::CaseRule``/\ ``RTLIL::SwitchRule`` 树必须按以下方式理解：

-  在每个 case 层级上（过程的主体是根 case），先求值该层级上的动作，再求值
   该 case 内的各个 switch。（注意，Verilog 代码第 13 行的最后一条赋值已被
   移到 RTLIL 过程的开头，即 RTLIL 清单的第 13 行。）

   也就是说，switch 层次中更深的特殊 case 会覆盖上层的默认值。RTLIL 代码中
   第 12 行和第 22 行的赋值就是这方面的例子。

   注意，与此不同的是，``RTLIL::CaseRule`` 中各 ``RTLIL::SwitchRule`` 对象
   内部的顺序相对于原始 AST 和 Verilog 代码是保持不变的。

-  整个 ``RTLIL::CaseRule``/\ ``RTLIL::SwitchRule`` 树描述的是一个异步电路。
   也就是说，由各个 switch 形成的判定树可以针对每个被赋值的信号独立看待。
   每当某个被赋值的信号发生变化，所有依赖于这些变化信号的其他信号都需要
   更新。例如，RTLIL 代码中第 16 行和第 18 行的赋值实际上会影响第 12 行的
   赋值，尽管它们的“顺序是错误的”。

过程中唯一同步的部分是 RTLIL 代码第 35 行生成的 ``RTLIL::SyncRule`` 对象。
同步规则是该过程中唯一对原始信号赋值的部分。原始 Verilog 代码中的同步事件
已被转换为 ``RTLIL::SyncRule`` 对象的同步类型（posedge）和信号（``\clock``）。
在这个简单例子中，``RTLIL::SyncRule`` 对象随后被简单地转换为一组 D 型触发器，
而 ``RTLIL::CaseRule``/\ ``RTLIL::SwitchRule`` 树则转换为使用多路复用器的
判定树。

在更复杂的例子中（例如异步复位），
``RTLIL::CaseRule``/\ ``RTLIL::SwitchRule`` 树中描述异步复位的部分必须首先
转换为正确的 ``RTLIL::SyncRule`` 对象。这由 ``proc_arst`` pass（处理流程）
完成。

ProcessGenerator 算法
~~~~~~~~~~~~~~~~~~~~~


``AST_INTERNAL::ProcessGenerator`` 使用以下内部状态变量：

-  | ``subst_rvalue_from`` 和 ``subst_rvalue_to``
   | 这两个变量保存 ``AST::AstNode::genRTLIL()`` 对使用阻塞赋值的信号应采用
     的替换模式。在 ``AST_INTERNAL::ProcessGenerator`` 初始化之后，这两个
     变量为空。

-  | ``subst_lvalue_from`` 和 ``subst_lvalue_to``
   | 这两个变量保存从左侧信号（``\
     <name>``）到对应当前临时信号（初始为
     ``$0\ <name>``）的映射。

-  | ``current_case``
   | 指向一个 ``RTLIL::CaseRule`` 对象的指针。初始时它是所生成
     ``RTLIL::Process`` 的根 case。

随着算法运行，这些变量会不断被修改，同时被压入栈，随后又通过从栈中弹出
恢复为之前的值。

启动时，ProcessGenerator 生成一个新的 ``RTLIL::Process`` 对象，其根 case
为空，并按上述方式初始化其状态变量。然后，使用 AST_ALWAYS 节点中的同步事件
以及 ``subst_lvalue_from`` 和 ``subst_lvalue_to`` 的初始值创建
``RTLIL::SyncRule`` 对象。接着递归求值该过程对应的 AST。

在这个递归求值过程中，可以发现三种相关的 AST 节点类型：
``AST_ASSIGN_LE``（非阻塞赋值）、``AST_ASSIGN_EQ``（阻塞赋值）和
``AST_CASE``（``if`` 或 ``case`` 语句）。

处理非阻塞赋值
^^^^^^^^^^^^^^

当发现 ``AST_ASSIGN_LE`` 节点时，ProcessGenerator 执行以下操作：

-  使用 ``AST::AstNode::genRTLIL()`` 求值左侧，并利用 ``subst_lvalue_from``
   和 ``subst_lvalue_to`` 将其映射到一个临时信号名。

-  使用 ``AST::AstNode::genRTLIL()`` 求值右侧。对于该调用，会使用
   ``subst_rvalue_from`` 和 ``subst_rvalue_to`` 的值来正确映射阻塞赋值的
   信号。

-  从 ``current_case`` 及其内部所有 case 中，移除所有与此赋值左侧相同的
   赋值。

-  把新赋值加入 ``current_case``。

处理阻塞赋值
^^^^^^^^^^^^

当发现 ``AST_ASSIGN_EQ`` 节点时，ProcessGenerator 执行以下操作：

-  执行处理非阻塞赋值时会执行的所有步骤（见上文）。

-  从 ``subst_rvalue_from`` 中移除所找到的左侧（左值映射之前），并从
   ``subst_rvalue_to`` 中移除相应的位。

-  把所找到的左侧（左值映射之前）追加到 ``subst_rvalue_from``，并把所找到
   的右侧追加到 ``subst_rvalue_to``。

处理 case 与 if 语句
^^^^^^^^^^^^^^^^^^^^

当发现 ``AST_CASE`` 节点时，ProcessGenerator 执行以下操作：

-  把 ``subst_rvalue_from``、``subst_rvalue_to``、``subst_lvalue_from`` 和
   ``subst_lvalue_to`` 的值压入栈。

-  生成一个新的 ``RTLIL::SwitchRule`` 对象，使用
   ``AST::AstNode::genRTLIL()``（并借助 ``subst_rvalue_from`` 和
   ``subst_rvalue_to``）求值选择表达式并加入该 ``RTLIL::SwitchRule`` 对象，
   然后把这个对象加入 ``current_case``。

-  收集 ``AST_CASE`` 节点内用阻塞赋值所赋值的所有左值，保存在局部变量
   ``this_case_eq_lvalue`` 中。

-  为 ``this_case_eq_lvalue`` 中的所有信号生成新的临时信号，存入
   ``this_case_eq_ltemp``。

-  使用 ``subst_rvalue_from`` 和 ``subst_rvalue_to`` 映射
   ``this_case_eq_lvalue`` 中的信号，得到的信号集合存入
   ``this_case_eq_rvalue``。

然后对 ``AST_CASE`` 节点内的每个 ``AST_COND`` 节点执行以下步骤：

-  把 ``subst_rvalue_from``、``subst_rvalue_to``、``subst_lvalue_from`` 和
   ``subst_lvalue_to`` 设为已压入栈的值。

-  从 ``subst_lvalue_from``/``subst_lvalue_to`` 中移除
   ``this_case_eq_lvalue``。

-  把 ``this_case_eq_lvalue`` 追加到 ``subst_lvalue_from``，把
   ``this_case_eq_ltemp`` 追加到 ``subst_lvalue_to``。

-  压入 ``current_case`` 的值。

-  创建一个新的 ``RTLIL::CaseRule``。把 ``current_case`` 设为该新对象，并把
   新对象加入上面创建的 ``RTLIL::SwitchRule``。

-  向新的 ``current_case`` 添加一条从 ``this_case_eq_rvalue`` 到
   ``this_case_eq_ltemp`` 的赋值。

-  使用 ``AST::AstNode::genRTLIL()``（并借助 ``subst_rvalue_from`` 和
   ``subst_rvalue_to``）求值该 case 的比较值，并相应地修改新的
   ``current_case``。

-  递归进入 ``AST_COND`` 节点的子节点。

-  从栈中弹出旧值以恢复 ``current_case``。

最后执行以下步骤：

-  把 ``subst_rvalue_from``、``subst_rvalue_to``、``subst_lvalue_from`` 和
   ``subst_lvalue_to`` 的值从栈中弹出。

-  从 ``subst_rvalue_from``/``subst_rvalue_to`` 对中移除
   ``this_case_eq_lvalue`` 中的信号。

-  把 ``this_case_eq_lvalue`` 的值追加到 ``subst_rvalue_from``，把
   ``this_case_eq_ltemp`` 的值追加到 ``subst_rvalue_to``。

-  使用 ``subst_lvalue_from``/``subst_lvalue_to`` 映射
   ``this_case_eq_lvalue`` 中的信号。

-  在 ``current_case`` 及其内部所有 case 中，移除对
   ``this_case_eq_lvalue`` 中信号的所有赋值。

-  向 ``current_case`` 添加一条从 ``this_case_eq_ltemp`` 到
   ``this_case_eq_lvalue`` 的赋值。

进一步分析处理 case 与 if 语句的算法
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

对于非阻塞赋值，该算法很简单：后面的赋值会使前面的赋值失效。对于每个用
非阻塞赋值的信号，恰好生成一个临时变量（带 ``$0`` 前缀），该变量的所有
赋值都使用这个临时变量。

注意，当不使用阻塞赋值时，所有 ``_eq_`` 变量都会变为空，因此算法中的许多
步骤也就可以忽略。

对于带阻塞赋值的变量，该算法表现出以下行为：首先创建一个新的临时变量。
然后把这个新临时变量登记为该 ``AST_CASE`` 节点各 case 中对该变量所有赋值的
赋值目标。接着，对每个 case，先把旧临时变量赋给新临时变量。如果该变量在此
case 中确实被赋值，这条赋值会被覆盖；否则它作为默认值保留。

这样得到的 ``RTLIL::CaseRule`` 会在所有分支中给新临时变量赋值。因此，当
所有 case 都处理完毕后，会向包含它的块添加一条最终赋值，把新临时变量赋给旧
临时变量。注意，这一步总会覆盖先前对旧临时变量的赋值。与非阻塞赋值不同，
旧赋值仍可能对设计中的某处产生影响，因为此前曾以包含旧赋值右侧的
``subst_rvalue_from``/\ ``subst_rvalue_to`` 元组调用过
``AST::AstNode::genRTLIL()``。

proc pass
~~~~~~~~~


ProcessGenerator 将 AST 表示的行为模型转换为 ``RTLIL::Process`` 表示的
行为模型。从行为模型到 RTL 表示的实际转换由 `proc` pass 及其启动的各 pass
完成：

-  | `proc_clean` 和 `proc_rmdead`
   | 这两个 pass 只是清理 ``RTLIL::Process`` 结构。`proc_clean` pass 从
     过程中移除空的部分（例如空赋值），`proc_rmdead` 则检测并移除过程判定树
     中不可达的分支。

-  | `proc_arst`
   | 该 pass 检测描述带异步复位的 D 型触发器的过程，并重写该过程以更好地
     反映其建模内容：在此 pass 之前，异步复位具有两条边沿敏感的同步规则和
     一条用于复位路径的顶层 ``RTLIL::SwitchRule``。在此 pass 之后，复位的
     同步规则变为电平敏感，且顶层 ``RTLIL::SwitchRule`` 已被移除。

-  | `proc_mux`
   | 该 pass 将 ``RTLIL::CaseRule``/\ ``RTLIL::SwitchRule`` 树转换为针对每个
     被写信号的由多路复用器构成的树。此后，``RTLIL::Process`` 结构只包含
     描述输出寄存器的那些 ``RTLIL::SyncRule``。

-  | `proc_dff`
   | 该 pass 把各个 ``RTLIL::SyncRule`` 替换为 D 型触发器（必要时带异步
     复位）。

-  | `proc_memwr`
   | 该 pass 把各个 ``RTLIL::MemWriteAction`` 替换为 `$memwr` 单元。

-  | `proc_clean`
   | 最后再调用一次 `proc_clean`，移除此时已为空的 ``RTLIL::Process``
     对象。

把这些最后的处理步骤放在 pass 中而不是 Verilog 前端中执行，有两点重要好处：

首先，它提高了过程的透明性。在单独 pass 中发生的所有事情都更易于调试，
因为可以在每个步骤前后方便地考察 RTLIL 数据结构。

其次，它提高了灵活性。这一方案可以很容易地扩展以支持其他类型的存储元件，
例如 SR 锁存器或 D 锁存器，而无需扩展实际的 Verilog 前端。

.. todo:: 综合 Verilog 数组

  补充一些关于 `$memrd` 和 `$memwr` 单元如何生成、以及它们如何在 memory
  pass 中处理的信息。


.. todo:: 综合参数化设计

  补充一些关于 ``RTLIL::Module::derive()`` 方法、以及如何通过 hierarchy pass
  用它来综合参数化模块的信息。
