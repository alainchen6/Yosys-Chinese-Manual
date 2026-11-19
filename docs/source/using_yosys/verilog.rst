Yosys 中 Verilog 支持的说明
===========================


不支持的 Verilog-2005 特性
--------------------------


Yosys 不支持以下 Verilog-2005 特性，且目前没有添加这些支持的
计划：

- IEC 62142(E):2005 / IEEE Std. 1364.1(E):2002 中定义的
  不可综合语言特性

- ``tri``、``triand`` 和 ``trior`` 网络类型

- ``config`` 和 ``disable`` 关键字以及库映射文件


Verilog 属性与非标准特性
------------------------


- 支持 case 语句上的 ``full_case`` 属性（也支持非标准的
  ``// synopsys full_case`` 指令）

- 支持 case 语句上的 ``parallel_case`` 属性（也支持非标准的
  ``// synopsys parallel_case`` 指令）

- 也支持 ``// synopsys translate_off`` 和 ``// synopsys translate_on`` 指令
  （但强烈建议改用 ``` `ifdef .. `endif ```）。

- 模块或数组上的 ``nomem2reg`` 属性会禁止将数组自动提前转换为独立的
  寄存器。这可能有潜在危险。通常前端有充分理由将数组转换为寄存器
  列表。禁止此步骤很可能导致错误的综合结果。

- 模块或数组上的 ``mem2reg`` 属性强制将数组提前转换为独立的寄存器。

- 模块或数组上的 ``nomeminit`` 属性禁止创建已初始化的存储器。这实际上
  会对所有在 ``initial`` 块中写入且不是 ROM 的存储器应用 ``mem2reg``。

- 寄存器上的 ``no_rw_check`` 属性表示：当读写访问同一地址时，推断出的
  存储器可以具有未定义行为。
  参见 :ref:`关于存储器处理的章节 <no_rw_check>`。

- 模块或 always 块上的 ``nolatches`` 属性禁止为锁存器生成逻辑环路。取而代之的是，
  所有未显式赋值的值默认为 x 位。这不会影响触发器之类的时钟存储元件。

- 寄存器上的 ``nosync`` 属性禁止生成存储元件。该寄存器本身将始终把所有位都置为
  'x'（未定义）。该变量只能用作 always 块内的阻塞赋值临时变量。这主要供
  Yosys 内部用于综合 Verilog 函数和访问数组。

- 寄存器上的 ``nowrshmsk`` 属性禁止为该寄存器的位切片写入生成
  移位并掩码类型的电路。

- 信号线上的 ``onehot`` 属性将其标记为 one-hot 状态寄存器。例如它被用于
  存储器端口共享，由 fsm_map pass 设置。

- 模块上的 ``blackbox`` 属性用于标记空存根模块，这些模块具有与真实模块
  相同的端口，但不包含内部配置的信息。这些模块只被综合 pass 用于
  识别单元的输入和输出端口。Verilog 后端默认也不输出 blackbox 模块。
  `read_verilog` 除非以 ``-noblackbox`` 调用，否则会自动对它读取的任何空
  模块设置 blackbox 属性。

- 在空模块上设置的 ``noblackbox`` 属性可阻止 `read_verilog`
  自动在该模块上设置 blackbox 属性。

- 模块上的 ``whitebox`` 属性会触发与 ``blackbox`` 相同的行为，
  但用于白盒模块，即包含该单元类型行为模型的库模块。

- 当 `read_verilog` 以 ``-lib`` 模式运行时，``lib_whitebox`` 属性会覆盖 ``whitebox``。
  否则它会自动被移除。

- ``dynports`` 属性由 Verilog 前端使用，用于标记其端口宽度
  取决于参数的模块。

- ``hdlname`` 属性被某些 pass 用于在重命名模块时记录模块的原始
  （HDL）名称。它应包含单个名称，或者在描述展平设计中的层次名称时，
  包含用单个空格字符分隔的多个名称。

- 单元和信号线上的 ``keep`` 属性用于标记永远不应被优化器移除的
  对象。例如它被用于具有不属于网表的隐藏连接的单元，如 I/O pad。
  在模块上设置 ``keep`` 属性与在该模块的所有实例上设置该属性效果相同。

- 单元和模块上的 ``keep_hierarchy`` 属性可阻止 `flatten`
  命令展平所指示的单元和模块。

- 模块上的 ``gate_cost_equivalent`` 属性可用于以基本门实例数量指定
  该模块的估计成本。请参见命令 `keep_hierarchy` 的帮助信息，该命令会
  解释此属性。

- 当寄存器以 ``reg foo = val`` 的“FPGA 风格”初始化时，前端会在信号线上
  设置 ``init`` 属性。它可用于在综合期间添加必要的复位逻辑。

- 模块上的 ``top`` 属性将该模块标记为设计层次的顶层。`hierarchy`
  命令在以 ``-top`` 调用时会设置此属性。其他命令（如 `flatten` 和各种
  后端）使用此属性来确定顶层模块。

- ``src`` 属性由 HDL 前端在创建的单元和信号线上设置为
  ``<hdl-file-name>:<line-number>`` 字符串，然后贯穿整个综合过程。
  当实体合并时，会创建一个新的以 \|-分隔的字符串，其中包含来自原始
  实体的所有字符串。

- ``defaultvalue`` 属性用于存储模块输入的默认值。当输入
  声明带有默认值时，HDL 前端会将该属性附加到输入信号线上。

- ``parameter`` 和 ``localparam`` 属性用于标记代表模块参数
  或 localparam 的信号线（当 HDL 前端以 ``-pwires`` 模式运行时）。

- 带有 ``hierconn`` 属性的信号线在通过 `flatten` 从
  子模块导入时，会连接到同名（格式为 ``cell_name.identifier``）的信号线。

- 可以在黑盒模块的输出端口上设置 ``clkbuf_driver`` 属性，将其标记为
  时钟缓冲器输出，从而阻止 `clkbufmap` 在此类输出驱动的网络上
  插入另一个时钟缓冲器。

- 可以在模块的输入端口上设置 ``clkbuf_sink`` 属性，以
  请求 `clkbufmap` pass 插入时钟缓冲器。

- 可以在模块的输出端口上设置 ``clkbuf_inv`` 属性，其值为该模块
  某个输入端口的名称。当 `clkbufmap` 原本要在此输出上插入
  时钟缓冲器时，它会改为尝试在该输入端口上插入时钟缓冲器（这用于实现
  时钟缓冲器插入会“看穿”的时钟反相器单元）。

- ``clkbuf_inhibit`` 是要在信号线上设置的默认属性，用于阻止
  `clkbufmap` 自动插入时钟缓冲器。可以通过为 `clkbufmap`
  提供自定义选择集来覆盖此行为。

- 可以在端口上设置 ``invertible_pin`` 属性，以将其标记为可通过单元参数
  反转。反转参数的名称指定为该属性的值。反转参数的值必须与
  端口宽度相同，其中 1 表示反转位，0 表示非反转位。

- 黑盒模块端口上的 ``iopad_external_pin`` 属性将其标记为
  I/O pad 的朝外引脚，并阻止 `iopadmap` 在其上插入
  另一个 pad 单元。

- 模块属性 ``abc9_lut`` 是一个整数属性，向 `abc9`
  表明该模块描述了一个 LUT，其面积成本为该值，
  并使用 ``specify`` 语句描述传播延迟。

- 模块属性 ``abc9_box`` 是一个布尔值，指定一个黑盒/白盒
  定义，使用 ``specify`` 语句描述传播延迟，
  供 `abc9` 使用。

- 端口属性 ``abc9_carry`` 标记盒子的进位输入端口（如果是输入端口）和
  进位输出端口（如果是输出端口）。此信息对于 `abc9` 保持
  进位链的完整性是必要的。将此属性指定到总线端口上只会影响
  其最高有效位。

- 模块属性 ``abc9_flop`` 是一个布尔值，将该模块标记为
  触发器。这允许 `abc9` 分析其内容以执行
  时序综合。

- 前端会根据 always 块的类型，在由 SystemVerilog 风格 always 块
  派生的进程上设置 ``always_comb``、``always_latch`` 和
  ``always_ff`` 属性。这些属性会在
  ``proc_dlatch`` 中检查正确性。由 ``always_latch`` 进程推断出的锁存器不受
  ``proc -latches <info|warn|error>`` 报告策略的约束，并且
  生成的锁存器单元带有 ``always_latch`` 属性，这也
  使它们免于 `check` ``-nolatches``。

- 单元属性 ``wildcard_port_conns`` 表示通配符端口
  连接（SystemVerilog ``.*``）。在 `hierarchy` 中，它们会被解析为与
  匹配信号线的具体连接。

- 除了 ``(* ... *)`` 属性语法外，Yosys 还支持
  非标准的 ``{* ... *}`` 属性语法，用于为
  ``{* ... *}`` 语句之后的所有内容设置默认属性。（通过添加
  空的 ``{* *}`` 语句来重置。）

- 在模块参数和端口声明，以及单元端口和参数列表中，
  末尾逗号会被忽略。这在某些情况下简化了编写 Verilog 代码生成器
  的工作。

- 模块可以用 ``module mod_name(...);`` 来声明（用三个点
  代替模块端口列表）。使用此语法时，只需
  在模块体中简单地将模块端口声明为 'input' 或 'output' 即可。

- 使用 ``\`define`` 定义宏时，三引号之间的所有文本
  都会被解释为宏体，即使其中包含未转义的换行符。
  三引号会从宏体中移除。例如：

.. code-block:: verilog

      `define MY_MACRO(a, b) """
         assign a = 23;
         assign b = 42;
      """


- ``via_celltype`` 属性可用于通过实例化指定的单元类型来实现 Verilog 任务
  或函数。其值为要使用的单元类型名称。对于函数，可以通过在单元类型后
  附加以空白分隔的输出端口名称来指定该端口。此时任务或函数的主体
  不被使用，可用于指定该单元类型的行为模型以供仿真。例如：

.. code-block:: verilog

      module my_add3(A, B, C, Y);
        parameter WIDTH = 8;
        input [WIDTH-1:0] A, B, C;
        output [WIDTH-1:0] Y;
        ...
      endmodule

      module top;
        ...
        (* via_celltype = "my_add3 Y" *)
        (* via_celltype_defparam_WIDTH = 32 *)
        function [31:0] add3;
          input [31:0] A, B, C;
          begin
            add3 = A + B + C;
          end
        endfunction
        ...
      endmodule


- ``wiretype`` 属性由 Verilog 解析器添加到 typedef 类型的信号线上，
  以指示类型标识符。

- 各种 ``enum_value_{value}`` 属性会被添加到枚举类型的信号线上，
  以给出可能枚举项到其值的映射。

- ``enum_base_type`` 属性会被添加到枚举项上，以指示它们属于哪个枚举
  （匿名的枚举和其他枚举都会用自增计数器自动命名）。注意，枚举目前
  不是强类型的。

- 支持有限的 DPI-C 函数子集。可以使用插件机制（参见
  ``help plugin``）加载包含 DPI-C 例程实现的 .so 文件。作为
  非标准扩展，可以使用 ``<alias>:`` 语法指定插件别名。例如：

.. code-block:: verilog

      module dpitest;
        import "DPI-C" function foo:round = real my_round (real);
        parameter real r = my_round(12.345);
      endmodule

.. code-block::

      $ yosys -p 'plugin -a foo -i /lib/libm.so; read_verilog dpitest.v'

- 带尺寸的常量（语法 ``<size>'s?[bodh]<value>``）支持将常量
  表达式作为 ``<size>``。如果表达式不是简单标识符，则
  必须放在括号中。示例：``WIDTH'd42``、``(4+2)'b101010``

- 系统任务 ``$finish``、``$stop`` 和 ``$display`` 在
  initial 块中、在无条件上下文中受支持（只允许对
  参数和常量值上的表达式使用 if/case 语句）。其预期用途
  是综合时 DRC。

- 对将 ``specify`` .. ``endspecify`` 语句转换为特殊
  ``$specify2``、``$specify3`` 和 ``$specrule`` 单元（用于黑盒和白盒）的支持有限。
  使用 ``read_verilog -specify`` 启用此功能。（默认情况下这些块会被
  忽略。）

- ``reprocess_after`` 内部属性由 Verilog 前端使用，用于
  标记其绑定可能取决于所指定实例化模块的单元。带有此类单元的模块
  会在 `hierarchy` pass 期间、在引用的模块定义可用后
  被重新处理。

- 可以在黑盒模块上设置 ``smtlib2_module`` 属性，以直接
  使用 SMT-LIB 2 指定形式模型。对于此类模块，
  可以在输出端口上使用 ``smtlib2_comb_expr`` 属性，以使用 SMT-LIB 2
  表达式定义其值。例如：

.. code-block:: verilog

      (* blackbox *)
      (* smtlib2_module *)
      module submod(a, b);
        input [7:0] a;
        (* smtlib2_comb_expr = "(bvnot a)" *)
        output [7:0] b;
      endmodule

用于形式化验证的非标准或 SystemVerilog 特性
-------------------------------------------


- 当 `read_verilog` 以 ``-formal`` 调用时，会启用对
  ``assert``、``assume``、``restrict`` 和 ``cover`` 的支持。

- 系统任务 ``$initstate`` 在初始状态下求值为 1，否则求值为 0。

- 系统函数 ``$anyconst`` 求值为任意常量值。这
  等价于将 reg 声明为 ``rand const``，但在
  检查器之外也可用。（Yosys 也支持检查器之外的 ``rand const``。）

- 系统函数 ``$anyseq`` 求值为任意值，在每个周期中可能
  是不同的值。这等价于将 reg 声明为 ``rand``，但在
  检查器之外也可用。（Yosys 也支持检查器之外的 ``rand`` 变量。）

- 系统函数 ``$allconst`` 和 ``$allseq`` 可用于构造
  形式化的存在-全称（exist-forall）问题。只有当迹（trace）对所有
  ``$allconst/$allseq`` 值都满足假设时，假设才成立。对于断言和 cover
  语句，只要有一个 ``$allconst/$allseq`` 值触发
  该属性就足够了（类似于 ``$anyconst/$anyseq``）。

- 使用 ``anyconst/anyseq/allconst/allseq``
  属性声明的信号线/寄存器（例如 ``(* anyconst *) reg [7:0] foobar;``）将表现得
  如同由 ``$anyconst/$anyseq/$allconst/$allseq`` 函数驱动。

- SystemVerilog 任务 ``$past``、``$stable``、``$rose`` 和 ``$fell``
  在任何时钟块中都受支持。

- 语法 ``@($global_clock)`` 可用于创建没有
  显式时钟输入的触发器（``$ff`` 单元）。当 ``<netname>``
  标有 ``(* gclk *)`` Verilog 属性时，使用
  ``@(posedge <netname>)`` 或 ``@(negedge <netname>)`` 也可以达到相同效果。


支持的 SystemVerilog 特性
-------------------------


当 `read_verilog` 以 ``-sv`` 调用时，它接受一些 SystemVerilog 中的
语言特性：

- SystemVerilog 的 ``assert`` 语句在其最基本的形式下受支持。在模块上下文中：
  ``assert property (<expression>);``，在 always 块内：
  ``assert(<expression>);``。它会被转换为 ``$assert``
  单元。

- SystemVerilog 的 ``assume``、``restrict`` 和 ``cover`` 语句
  也受支持。适用于 ``assert`` 语句的相同限制也同样适用。

- 关键字 ``always_comb``、``always_ff`` 和 ``always_latch``、``logic``
  和 ``bit`` 受支持。

- 支持使用 ``rand`` 和 ``rand const`` 声明自由变量。

- 支持没有端口列表、不需要实例化（而是
  像命名块一样行为）的检查器。

- 支持 SystemVerilog 包。一旦使用 `read_verilog` 将 SystemVerilog 文件读入
  设计，其所有包都可供之后读入同一设计的 SystemVerilog
  文件使用。

  - 目前不支持嵌套包（即在 ``package`` .. ``endpackage`` 块内调用
    ``import``）

- 支持 typedef（包括包内的）

  - 目前不支持类型转换

- 支持枚举（包括包内的）

  - 但目前不是强类型的

- 支持打包结构体和联合体

  - 目前不支持打包结构体/联合体的数组
  - 目前不支持结构体字面量

- 支持多维数组

  - 目前不支持非打包数组的数组赋值
  - 目前不支持数组字面量

- SystemVerilog 接口（SVI）部分受支持，包括用于指定
  端口是输入还是输出的 modport。

  - 接口必须作为 *命名* 参数提供，而不是位置参数。
    即 ``foo bar(.intf(intf0), .x(x));`` 受支持，但 ``foo bar(intf0,
    x);`` 不受支持。

- 支持表达式内的赋值。

- ``unique``、``unique0`` 和 ``priority`` SystemVerilog 关键字
  在 ``if`` 和 ``case`` 条件语句上受支持。（Verilog 前端
  会通过用适当的 ``full_case`` 和/或 ``parallel_case``
  属性标注其表示来处理使用这些关键字的条件语句，这些属性
  已在上文描述。）

- 支持 SystemVerilog 字符串字面量（三引号字符串以及
  续行和十六进制转义等转义序列）。
