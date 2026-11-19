.. _chapter:textrtlil:

RTLIL 文本表示
--------------


本附录以扩展巴科斯范式（EBNF）的形式记录 RTLIL 的文本表示。

该文法并不意图表达语义上的限制。也就是说，文法是“宽松的”，更严格的检查由
后续处理阶段执行。

该文法也不意图表示 RTLIL 前端实际使用的文法，因为后者是专门针对 lex 和 yacc
的处理而写的，更加宽松，而且比简单的 EBNF 记法更难理解。

最后需要注意，所有语句（以 ``-stmt`` 结尾的规则）都以行结束符终止。因此，
一条语句不能拆成多行。

词法元素
~~~~~~~~


字符
^^^^

RTLIL 文件是字节流。严格地说，RTLIL 文件中的“字符”就是单个字节。词法分析器
把多字节编码的字符当作连续的多个单字节字符处理。虽然其他编码 *可能* 可以工作，
但已知 UTF-8 可以安全使用。文件开头的字节顺序标记会导致错误。

ASCII 空格（32）和制表符（9）分隔词法单元。

标识符中使用的 ``nonws`` 字符，是指编码中所有字节都大于 ASCII 空格（32）的
字符。

``eol`` 是一个或多个连续的 ASCII 换行（10）和回车（13）。

标识符
^^^^^^

RTLIL 中有两类标识符：

-  公开可见的标识符
-  自动生成的标识符

.. code:: BNF

    <id>            ::= <public-id> | <autogen-id>
    <public-id>     ::= \ <nonws>+
    <autogen-id>    ::= $ <nonws>+

值
^^

*值* 由位宽和位表示组成，最高有效位在前。位可以是以下任意一种：

-  ``0``：逻辑零值
-  ``1``：逻辑一值
-  ``x``：未知逻辑值（在 case 模式中表示无关项）
-  ``z``：高阻值（在 case 模式中表示无关项）
-  ``m``：标记位（仅供内部使用）
-  ``-``：无关值

当位表示的位数少于位宽时，会用最高有效的显式位将其填充到位宽；如果最高有效
显式位是 ``1``，则用 ``0`` 填充；如果没有任何显式位，则用 ``x`` 填充。

*整数* 就是十进制格式的有符号整数值。**警告：** 整数常量限制为 32 位。
也就是说，它们只能位于 :math:`[-2147483648, 2147483648)` 区间内。
超出该范围的整数会导致错误。

.. code:: BNF

    <value>         ::= <decimal-digit>+ ' <binary-digit>*
    <decimal-digit> ::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
    <binary-digit>  ::= 0 | 1 | x | z | m | -
    <integer>       ::= -? <decimal-digit>+

字符串
^^^^^^

字符串是由双引号界定的一系列字符。字符串内可以使用除 ASCII NUL（0）之外的
任何字符。此外还可以使用若干转义序列：

-  ``\n``：换行符
-  ``\t``：制表符
-  ``\ooo``：以一位、两位或三位八进制值指定的字符

所有其他字符都可以用反斜杠转义，转义后即成为其后的那个字符。因此：

-  ``\\``：反斜杠
-  ``\"``：双引号
-  ``\r``：字符 'r'

注释
^^^^

注释以 ``#`` 字符开始，一直延续到行尾。所有注释都会被忽略。

文件
~~~~


文件由一个可选的自动索引语句和零个或多个模块组成。

.. code:: BNF

    <file> ::= <autoidx-stmt>? <module>*

自动索引语句
^^^^^^^^^^^^

当 Yosys 需要生成唯一名称（例如 ``flattenN``）时，会使用设计的 autoindex 值；
autoindex 语句会提高该值。其中 N 部分由 autoindex 值填充，随后该值会自增。
每个设计都有自己的 autoindex 值。该值必须被转储到 RTLIL 中，否则，
例如“转储后再运行某个 pass”与“直接在热设计上运行该 pass”会具有不同的性质。

.. code:: BNF

    <autoidx-stmt> ::= autoidx <integer> <eol>

模块
^^^^

声明一个模块，可带零个或多个属性，模块由零个或多个信号线、存储器、单元、
过程以及连接组成。

.. code:: BNF

    <module>            ::= <attr-stmt>* <module-stmt> <module-body> <module-end-stmt>
    <module-stmt>       ::= module <id> <eol>
    <module-body>       ::= (<param-stmt>
                         |   <conn-stmt>
                         |   <wire>
                         |   <memory>
                         |   <cell>
                         |   <process>)*
    <param-stmt>        ::= parameter <id> <constant>? <eol>
    <constant>          ::= <value> | <integer> | <string>
    <module-end-stmt>   ::= end <eol>

属性语句
^^^^^^^^

声明一个属性，带有给定的标识符和值。

.. code:: BNF

    <attr-stmt> ::= attribute <id> <constant> <eol>

信号规格
^^^^^^^^

信号是指任何可以施加到单元端口上的东西，即常量值、信号线的全部位或其中选出
的若干位，以及它们的拼接。

**警告：** 当整数常量作为 sigspec 时，它总是 32 位宽、二进制补码形式。
例如，常量 :math:`-1` 等同于
``32'11111111111111111111111111111111``，而常量 :math:`1` 等同于 ``32'1``。

关于信号规格的概述，参见 :ref:`sec:rtlil_sigspec`。

.. code:: BNF

    <sigspec> ::= <constant>
               |  <wire-id>
               |  <sigspec> [ <integer> (:<integer>)? ]
               |  { <sigspec>* }

指定 ``<wire-id>`` 时，该信号线必须已经声明过。

指定信号切片时，左边的整数必须大于或等于右边的整数。

连接
^^^^

声明给定信号之间的连接。

.. code:: BNF

    <conn-stmt> ::= connect <sigspec> <sigspec> <eol>

信号线
^^^^^^

在外围模块中声明一条信号线，带有给定的标识符和选项，并可带零个或多个属性。

关于信号线的概述，参见 :ref:`sec:rtlil_cell_wire`。

.. code:: BNF

    <wire>          ::= <attr-stmt>* <wire-stmt>
    <wire-stmt>     ::= wire <wire-option>* <wire-id> <eol>
    <wire-id>       ::= <id>
    <wire-option>   ::= width <integer>
                     |  offset <integer>
                     |  input <integer>
                     |  output <integer>
                     |  inout <integer>
                     |  upto
                     |  signed

存储器
^^^^^^

在外围模块中声明一个存储器，带有给定的标识符和选项，并可带零个或多个属性。

关于存储器单元的概述参见 :ref:`sec:rtlil_memory`，关于存储器单元类型的细节
参见 :ref:`sec:memcells`。

.. code:: BNF

    <memory>        ::= <attr-stmt>* <memory-stmt>
    <memory-stmt>   ::= memory <memory-option>* <id> <eol>
    <memory-option> ::= width <integer>
                     |  size <integer>
                     |  offset <integer>

单元
^^^^

在外围模块中声明一个单元，带有给定的标识符和类型，并可带零个或多个属性。

单元对输入信号执行功能。单元类型的详细列表参见 :doc:`/cell_index`。

.. code:: BNF

    <cell>              ::= <attr-stmt>* <cell-stmt> <cell-body-stmt>* <cell-end-stmt>
    <cell-stmt>         ::= cell <cell-type> <cell-id> <eol>
    <cell-id>           ::= <id>
    <cell-type>         ::= <id>
    <cell-body-stmt>    ::= parameter (signed | real)? <id> <constant> <eol>
                         |  connect <id> <sigspec> <eol>
    <cell-end-stmt>     ::= end <eol>


过程
^^^^

在外围模块中声明一个过程，带有给定的标识符，并可带零个或多个属性。过程体由
零个或多个赋值、随后的零个或多个开关以及零个或多个同步组成。

关于过程的概述，参见 :ref:`sec:rtlil_process`。

.. code:: BNF

    <process>       ::= <attr-stmt>* <proc-stmt> <process-body> <proc-end-stmt>
    <proc-stmt>     ::= process <id> <eol>
    <process-body>  ::= <assign-stmt>* <switch>* <sync>*
    <assign-stmt>   ::= assign <dest-sigspec> <src-sigspec> <eol>
    <dest-sigspec>  ::= <sigspec>
    <src-sigspec>   ::= <sigspec>
    <proc-end-stmt> ::= end <eol>

开关
^^^^

开关将一个信号与一组 case 逐一比较是否相等。每个 case 指定一个以逗号分隔的
信号列表用于比较。如果列表中没有信号，则该 case 是默认 case。case 体由
零个或多个赋值以及随后的零个或多个开关组成。开关和 case 都可以带有零个或
多个属性。

.. code:: BNF

    <switch>            ::= <switch-stmt> <case>* <switch-end-stmt>
    <switch-stmt>       ::= <attr-stmt>* switch <sigspec> <eol>
    <case>              ::= <attr-stmt>* <case-stmt> <case-body>
    <case-stmt>         ::= case <compare>? <eol>
    <compare>           ::= <sigspec> (, <sigspec>)*
    <case-body>         ::= <assign-stmt>* <switch>*
    <switch-end-stmt>   ::= end <eol>

同步
^^^^

同步在其他事件发生时用其他信号更新信号。这类事件可以是：

-  信号上的边沿或电平
-  全局时钟节拍
-  初始化
-  始终

.. code:: BNF

    <sync>          ::= <sync-stmt> <update-stmt>*
    <sync-stmt>     ::= sync <sync-type> <sigspec> <eol>
                     |  sync global <eol>
                     |  sync init <eol>
                     |  sync always <eol>
    <sync-type>     ::= low | high | posedge | negedge | edge
    <update-stmt>   ::= update <dest-sigspec> <src-sigspec> <eol>
                     |  <attr-stmt>* memwr <id> <sigspec> <sigspec> <sigspec> <constant> <eol>
