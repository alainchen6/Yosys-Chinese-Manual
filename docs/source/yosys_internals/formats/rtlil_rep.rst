RTL 中间语言（RTLIL）
=====================


Yosys 中的所有前端、pass（处理流程）和后端都对以 RTLIL 表示的设计进行操作。
唯一的例外是高层前端：它们在生成 RTLIL 数据之前，使用 AST 表示作为中间步骤。

为了避免为 RTLIL 的各个类重新造出名称，本文档直接用它们的完整 C++ 名称来指代，
即包含 ``RTLIL::`` 命名空间前缀。

:numref:`图 %s <fig:Overview_RTLIL>` 给出了 RTLIL 的简化实体关系图（ER 图）。
在 :math:`1:N` 关系中，箭头从 :math:`N` 一侧指向 :math:`1` 一侧。例如一个
``RTLIL::Design`` 包含 :math:`N`（零个或多个）个 ``RTLIL::Module`` 实例。双
箭头表示 :math:`1:1` 关系。

``RTLIL::Design`` 是 RTLIL 数据结构的根对象。内存中总有一个“当前设计”，
pass 对它进行操作，前端向它添加数据，后端把它转换为可导出的格式。但在某些
情况下，pass 会在内部生成额外的 ``RTLIL::Design`` 对象。例如，当某个 pass
读取一个辅助 Verilog 文件（例如单元库）时，它可能会创建一个额外的
``RTLIL::Design`` 对象，并用这个新对象调用 Verilog 前端来解析该单元库。

.. figure:: /_images/internals/overview_rtlil.*
	:class: width-helper invert-helper
	:name: fig:Overview_RTLIL

	简化的 RTLIL 实体关系图

只有一个活动的 ``RTLIL::Design`` 对象，由用户调用的所有前端、pass 和后端
使用，例如通过一个综合脚本调用。这个 ``RTLIL::Design`` 随后包含零个或多个
``RTLIL::Module`` 对象，它们对应 Verilog 中的模块或 VHDL 中的实体。每个模块
又包含三类不同的对象：

-  ``RTLIL::Cell`` 和 ``RTLIL::Wire`` 对象表示经典的网表数据。

-  ``RTLIL::Process`` 对象表示来自 Verilog always 块和 VHDL 过程块的决策树
   （if-then-else 语句等）和同步声明（时钟信号与敏感列表）。

-  ``RTLIL::Memory`` 对象表示可寻址的存储器（数组）。

通常综合过程的输出是一个网表，即所有 ``RTLIL::Process`` 和 ``RTLIL::Memory``
对象都必须由综合 pass 替换为 ``RTLIL::Cell`` 和 ``RTLIL::Wire`` 对象。

HDL 中所有无法直接映射到这些 RTLIL 类的特性，都必须由 HDL 前端转换为
与 RTLIL 兼容的表示。这包括 generate 块、循环和参数等 Verilog 特性。

以下各节更详细地描述 RTLIL 的各个部分，以及某些设计决策背后的理由。

RTLIL 标识符
------------


RTLIL 中的所有标识符（例如模块名、端口名、信号名、单元类型等）都遵循以下
命名约定：它们必须以反斜杠（``\``）或美元符号（``$``）开头。

以反斜杠开头的标识符是公开可见的标识符。它们通常来自某个 HDL 输入文件。
例如信号名 ``\sig42`` 很可能是在某个 HDL 输入文件中用名字 ``sig42`` 声明的
信号。另一方面，信号名 ``$sig42`` 是自动生成的信号名。后端会把所有以美元
符号开头的标识符转换为不与以反斜杠开头的标识符冲突的标识符。

这样做有三个好处：

-  第一，自动生成的标识符不可能与用户提供的标识符冲突。

-  第二，关于哪些标识符最初由用户提供的信息始终可用，这有助于指导某些优化。
   例如，`opt_clean` 会尽量保留用户提供了名字的信号，但当自动生成名字的信号
   只是重复其他信号时，它会毫不犹豫地删除它们。注意，可以用 ``-purge`` 选项
   覆盖这一行为，从而也删除带有用户提供名字的内部网络。

-  第三，寻找合适的自动生成公开可见名字这件棘手的工作被集中到一处完成。在内部，那些可能对 Yosys 开发者包含重要信息的自动生成名字可以在不
   干扰外部工具的情况下使用。例如 Verilog 后端按 ``_123_`` 的形式分配名字。

RTLIL 标识符中不允许出现空白字符和控制字符（ASCII 码小于等于 32 的字符）；
大多数前端和后端也无法在标识符中支持这些字符。

为了避免编程错误，RTLIL 数据结构会检查所有标识符是否都以反斜杠或美元符号
开头，并且不包含空白字符或控制字符。违反这些规则会导致运行时错误。

所有 RTLIL 标识符都区分大小写。

某些变换（例如展平）可能必须更改用户提供的标识符，以避免名字冲突。发生这种
情况时，会把属性 ``hdlname`` 附加到该标识符被更改的对象上。该属性包含一个
名字（如果由前端直接给出，或来自消歧结果），或以空格分隔的多个名字（如果是
展平的结果）。``hdlname`` 属性中指定的所有名字都是公开的，且不包含开头的
``\``。

RTLIL::Design 与 RTLIL::Module
------------------------------


``RTLIL::Design`` 对象基本上只是 ``RTLIL::Module`` 对象的容器。除了
``RTLIL::Module`` 对象的列表之外，``RTLIL::Design`` 还维护一个选中对象的
列表，即 pass 应当操作的对象。大多数情况下整个设计都被选中，因此 pass 操作
于整个设计。但在更复杂的综合任务中，只有设计的一部分应受某些 pass 影响时，
这一机制会很有用。

除了上面 :ref:`ER 图 <fig:Overview_RTLIL>` 中所示的对象之外，``RTLIL::Module``
对象还包含以下额外属性：

-  模块名
-  属性列表
-  信号线之间的连接列表
-  一个可选的前端回调，用于派生该模块的参数化变体

这些属性可以是 Verilog 前端导入的 Verilog 属性，也可以是 pass 赋予的属性。
它们可用于存储关于模块的额外元数据，或只是标记模块供综合脚本的某一部分使用
而不被其他部分使用。

Verilog 和 VHDL 都支持参数化模块（VHDL 中称为“泛型实体”）。RTLIL 格式本身
不支持参数化模块。每个模块改为包含一个指向 AST 前端的回调函数，按需生成
``RTLIL::Module`` 的参数化变体。该回调随后返回该模块参数化变体的自动生成名字。
（对参数和模块名计算哈希，用来防止同一个参数化变体被生成两次。对于只有少数
参数的模块，会生成一个直接包含所有参数的名字，而不使用哈希字符串。）

.. _sec:rtlil_cell_wire:

RTLIL::Cell 与 RTLIL::Wire
--------------------------


一个模块包含零个或多个 ``RTLIL::Cell`` 和 ``RTLIL::Wire`` 对象。这些类型的
对象用于对网表建模。通常所有综合工作的目标都是把所有模块转换为这样的状态：
模块的功能仅由某个给定单元库中的单元实现，并由信号线把这些单元彼此连接起来。
注意模块端口只是带有特殊属性的信号线。

``RTLIL::Wire`` 对象具有以下属性：

-  信号线名
-  属性列表
-  宽度（总线就是宽度大于 1 的信号线）
-  总线方向（从 MSb 到 LSb，或相反）
-  最低有效位索引（取决于总线方向，为 LSb 或 MSb）
-  如果该信号线是端口：端口号和方向（input/output/inout）

与模块一样，这些属性可以是 Verilog 前端导入的 Verilog 属性，也可以是 pass
赋予的属性。

在 Yosys 中，总线（信号向量）用一个宽度大于 1 的信号线对象表示。因此 Yosys
不会把信号向量转换为单个信号。这使 RTLIL 的某些方面变得更复杂，但使 Yosys
能用于粗粒度综合——在这种综合中，目标架构的单元操作于整个信号向量，而不是
单位信号线。

在 Verilog 和 VHDL 中，总线可以有任意边界，并且 LSb 既可以是索引最低的位，
也可以是索引最高的位。在 RTLIL 中，位 0 始终对应 LSb；不过来自 HDL 前端的信息
会被保留，以便在错误消息、后端输出、约束文件等中正确地索引总线。

``RTLIL::Cell`` 对象具有以下属性：

-  单元名和类型
-  属性列表
-  参数列表（用于参数化单元）
-  单元端口，以及端口到信号线和常量的连接

端口到信号线的连接通过给每个单元端口分配一个 ``RTLIL::SigSpec`` 来表示。
``RTLIL::SigSpec`` 数据类型在下一节中描述。

.. _sec:rtlil_sigspec:

RTLIL::SigSpec
--------------


“信号”是任何可以施加到单元端口上的东西。即：

-  | 信号线中的一位（``RTLIL::SigBit``）
   | 1em 例如：``mywire[24]``

-  | 信号线中的一段位范围（``RTLIL::SigChunk`` 的信号线变体）
   | 1em 例如：``mywire, mywire[15:8]``

-  | 任意位宽的常量值（``RTLIL::SigChunk`` 的 ``std::vector<RTLIL::State>>`` 变体）
   | 1em 例如：``1337, 16'b0000010100111001, 1'b1, 1'bx``

``RTLIL::SigSpec`` 数据类型用于表示信号。它包含单个 ``RTLIL::SigChunk`` 或一个
``RTLIL::SigBit`` 向量。``RTLIL::Cell`` 对象为每个单元端口包含一个
``RTLIL::SigSpec``。

此外，信号线之间的连接用一对 ``RTLIL::SigSpec`` 对象表示。这样的对在不同位置
都会用到，因此为这样的对定义了类型名 ``RTLIL::SigSig``。

.. _sec:rtlil_process:

RTLIL::Process
--------------


当高层 HDL 前端处理行为级代码时，会把它拆分为数据通路逻辑（例如表达式
``a + b`` 被替换为一个以 a 和 b 为输入的加法器的输出）和一个对行为级代码的
控制逻辑建模的 ``RTLIL::Process``。让我们看一个简单例子：

.. code:: verilog
   :number-lines:

   module ff_with_en_and_async_reset(clock, reset, enable, d, q);
   input clock, reset, enable, d;
   output reg q;
   always @(posedge clock, posedge reset)
       if (reset)
           q <= 0;
       else if (enable)
           q <= d;
   endmodule

在这个例子中没有数据通路，因此前端生成的 ``RTLIL::Module`` 只包含几个
``RTLIL::Wire`` 对象和一个 ``RTLIL::Process``。该 ``RTLIL::Process`` 的 RTLIL
语法如下：

.. code:: RTLIL
   :number-lines:

   process $proc$ff_with_en_and_async_reset.v:4$1
       assign $0\q[0:0] \q
       switch \reset
           case 1'1
               assign $0\q[0:0] 1'0
           case
               switch \enable
                   case 1'1
                       assign $0\q[0:0] \d
                   case
               end
       end
       sync posedge \clock
           update \q $0\q[0:0]
       sync posedge \reset
           update \q $0\q[0:0]
   end

这个 ``RTLIL::Process`` 包含两个 ``RTLIL::SyncRule`` 对象、两个
``RTLIL::SwitchRule`` 对象和五个 ``RTLIL::CaseRule`` 对象。信号线
``$0\q[0:0]`` 是一个自动创建的信号线，保存 ``\q`` 的下一个值。第 2..12 行
描述应如何计算 ``$0\q[0:0]``。第 13..16 行描述如何使用 ``$0\q[0:0]`` 的值来
更新 ``\q``。

``RTLIL::Process`` 是零个或多个 ``RTLIL::SyncRule`` 对象和一个且仅一个
``RTLIL::CaseRule`` 对象的容器，后者称为根 case。

``RTLIL::SyncRule`` 对象包含一个（可选的）同步条件（信号和边沿类型）、零个或
多个赋值（``RTLIL::SigSig``），以及零个或多个存储器写操作
（``RTLIL::MemWriteAction``）。当应当推断出锁存器时，always 同步条件用于打破
组合逻辑环路。

``RTLIL::CaseRule`` 是零个或多个赋值（``RTLIL::SigSig``）和零个或多个
``RTLIL::SwitchRule`` 对象的容器。``RTLIL::SwitchRule`` 对象是零个或多个
``RTLIL::CaseRule`` 对象的容器。

在上面的例子中，第 2..12 行是根 case。这里首先把旧值 ``\q`` 作为默认值赋给
``$0\q[0:0]``（第 2 行）。根 case 还包含一个 ``RTLIL::SwitchRule`` 对象
（第 3..12 行）。该对象与 C 的 switch 语句非常相似，因为它用一个控制信号
（本例中为 ``\reset``）来决定它的哪个 case 应当处于活动状态。
``RTLIL::SwitchRule`` 对象随后为每个 case 包含一个 ``RTLIL::CaseRule`` 对象。
本例中有一个针对 ``\reset == 1`` 的 case [1]_，它使 ``$0\q[0:0]`` 被置位
（第 4、5 行），还有一个默认 case，后者又包含一个 switch，在 ``\enable`` 有效
时把 ``$0\q[0:0]`` 置为 ``\d`` 的值（第 6..11 行）。

一个 case 可以指定零个或多个比较值，用来决定它是否匹配。每个比较值的位宽都
必须与控制信号完全相同。当指定多个比较值时，只要其中任意一个与控制信号匹配，
该 case 就匹配；当指定零个比较值时，该 case 总是匹配（即它是默认 case）。

switch 按从第一个到最后一个的顺序确定 case 的优先级：多个 case 可能匹配，但
只有第一个匹配的 case 会变为活动状态。这通常会综合为优先级编码器。
parallel_case 属性允许 pass 假定不会有多于一个 case 匹配，full_case 属性允许
pass 假定恰好有一个 case 匹配；如果这些不变式在任何时候被动态违反，行为是
未定义的。当某个对综合器不可见的不变式使得控制信号永远不会取某些位模式时，
这些属性会很有用。

第 13..16 行随后使 ``\q`` 在 ``\clock`` 或 ``\reset`` 上出现正时钟边沿时被
更新。

为了生成这样的表示，语言前端必须能够正确处理阻塞和非阻塞赋值。不过，语言
前端不需要为输出信号确定正确的存储元件类型，也不需要为决策树生成多路复用器。
这些工作由操作于 RTLIL 表示的 pass 完成。因此，用其他算法替换这些步骤相对
容易，这些算法可以面向不同的目标架构，或在进一步处理决策树之前对其进行优化
或其他变换。

在大多数综合脚本中，对 RTLIL 表示的设计最先执行的动作之一是识别异步复位。
这通常使用 `proc_arst` pass 完成。该 pass 把上面的例子变换为以下
``RTLIL::Process``：

.. code:: RTLIL
   :number-lines:

   process $proc$ff_with_en_and_async_reset.v:4$1
       assign $0\q[0:0] \q
       switch \enable
           case 1'1
               assign $0\q[0:0] \d
           case
       end
       sync posedge \clock
           update \q $0\q[0:0]
       sync high \reset
           update \q 1'0
   end

这个 pass 把外层的 ``RTLIL::SwitchRule`` 变换为针对 ``\reset`` 信号的修改后的
``RTLIL::SyncRule`` 对象。进一步的处理会把该 ``RTLIL::Process`` 转换为例如带
异步复位的 D 类触发器，以及为使能信号生成的多路复用器：

.. code:: RTLIL
   :number-lines:

   cell $adff $procdff$6
       parameter \ARST_POLARITY 1'1
       parameter \ARST_VALUE 1'0
       parameter \CLK_POLARITY 1'1
       parameter \WIDTH 1
       connect \ARST \reset
       connect \CLK \clock
       connect \D $0\q[0:0]
       connect \Q \q
   end
   cell $mux $procmux$3
       parameter \WIDTH 1
       connect \A \q
       connect \B \d
       connect \S \enable
       connect \Y $0\q[0:0]
   end

不同的 pass 组合可能产生不同的结果。注意 `$adff` 和 `$mux` 是内部单元类型，
仍需映射到目标单元库中的单元类型。

有些 pass 拒绝操作于仍包含 ``RTLIL::Process`` 对象的模块，因为模块中存在这些
对象会增加复杂性。因此，把过程转换为单元网表的 pass 通常在综合脚本中很早就
被调用。proc pass 会调用一系列其他 pass，它们共同以适合大多数综合任务的方式
完成这一转换。

.. _sec:rtlil_memory:

RTLIL::Memory
-------------


对 HDL 代码中的每个数组（存储器）都会创建一个 ``RTLIL::Memory`` 对象。
存储器对象具有以下属性：

-  存储器名
-  属性列表
-  可寻址字的宽度
-  存储器的大小（以字数为单位）

语言前端会把对存储器的所有读访问变换为 `$memrd` 单元，把所有写访问变换为
`$memwr` 单元。这些单元包含相互独立的存储器读端口和写端口。语言前端会把
存储器初始化变换为 `$meminit` 单元。这些单元上的 ``\MEMID`` 参数用于把它们
相互关联起来，并关联到它们所属的 ``RTLIL::Memory`` 对象。

为各个端口使用独立单元、而不是在语言前端中直接创建一个大型多端口存储器单元，
其理由是独立的 `$memrd` 和 `$memwr` 单元可以通过资源共享来合并。由于资源共享
是一个非平凡的优化问题，不同综合任务可能有不同要求，因此适合在单独的 pass 中
完成优化，并在资源共享完成之后把 ``RTLIL::Memory`` 对象以及 `$memrd` 和
`$memwr` 单元合并为多端口存储器块。

memory pass 完成这一转换，并且（取决于传给它的选项）可以把存储器直接变换为
D 类触发器和地址逻辑，或生成多端口存储器块（用 `$mem` 单元表示）。

关于存储器单元类型的细节，参见 :ref:`sec:memcells`。

.. [1]
   RTLIL 代码中的语法 ``1'1`` 指定一个长度为一 bit（第一个 ``1``）且该 bit 为
   1（第二个 ``1``）的常量。
