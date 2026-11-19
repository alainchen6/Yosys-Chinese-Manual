:orphan:


010：将 Verilog 转换为 BLIF 页面
================================


摘要
====


Verilog-2005 是一种强大的硬件描述语言（HDL），可以用简短的 HDL 代码
构建出复杂的设计。对许多设计者来说，它是首选的设计输入方式。

Berkeley Logic Interchange Format（BLIF）是一种用于在程序之间交换时序
逻辑的简单文件格式。它易于生成、易于解析，因此是许多逻辑综合工具作者
首选的设计输入方式。

Yosys 是一个功能丰富的开源 Verilog 综合工具，可以用来弥合这两种文件
格式之间的鸿沟。它实现了 Verilog-2005 的大部分内容，因此可以把现代
行为级 Verilog 设计导入基于 BLIF 的设计流程，而不依赖专有综合工具。

当然，Yosys 的适用范围远不止 Verilog 逻辑综合。但这是一项有用且重要的
特性，本应用笔记将重点讨论 Yosys 的这一方面。

下载
====


本文档最初于 2015 年 4 月发布：
:download:`将 Verilog 转换为 BLIF PDF</_downloads/APPNOTE_010_Verilog_to_BLIF.pdf>`

..
   安装


   Yosys 用 C++ 编写（使用 C++11 中的特性），并在现代 Linux 上测试。
   它应当能在大多数带有 C++11 编译器的 UNIX 系统上正常编译。README 文件
   包含关于构建 Yosys 及其先决条件的有用信息。

   Yosys 是一个庞大且功能丰富的程序，带有若干依赖项。不过，可以在
   Makefile 中停用其中一些依赖项，代价是 Yosys 的某些特性会变得不可用。
   当构建 Yosys 遇到问题时，只关心本应用笔记所讨论特性的用户，可以停用
   Makefile 中的 TCL、Qt 和 MiniSAT 支持，并选择不构建 yosys-abc。

   本应用笔记基于 2013-11-23 的 `Yosys GIT`_ `Rev. e216e0e`_。示例中使用的
   Verilog 源码取自 `yosys-bigsim`_，这是一个用于回归测试 Yosys 的真实设计
   集合。

   .. _Yosys GIT: https://github.com/YosysHQ/yosys

   .. _Rev. e216e0e: https://github.com/YosysHQ/yosys/tree/e216e0e

   .. _yosys-bigsim: https://github.com/YosysHQ/yosys-bigsim

   入门


   我们的旅程从 yosys-bigsim 中的 Navré 处理器开始。`Navré
   processor`_ 是一个开源 AVR 克隆。它是单个设计文件（softusb_navre.v）
   中的单个模块（softusb_navre）。它还只使用了能很好地映射到 BLIF 格式
   的特性，例如它只使用同步复位。

   .. _Navré processor: http://opencores.org/projects/navre

   把 softusb_navre.v 转换为 softusb_navre.blif 再简单不过：

   .. code:: sh

      yosys -o softusb_navre.blif -S softusb_navre.v

   在幕后，Yosys 由综合脚本控制，这些脚本执行作用于 Yosys 内部状态的
   命令。例如，-o softusb_navre.blif 选项只是把命令 write_blif
   softusb_navre.blif 追加到脚本末尾。同样，命令行上的文件——这里是
   softusb_navre.v——会把命令 read_verilog softusb_navre.v 添加到综合
   脚本的开头。这两种情况下，文件类型都由文件扩展名确定。

   最后，-S 选项会实例化一个内置的默认综合脚本。除了使用 -S，也可以在
   命令行上用 -p 选项指定脚本中的综合命令：既可以给每条命令单独使用
   选项，也可以传入一个包含分号分隔命令列表的大命令字符串。但在大多数
   情况下，使用实际的脚本文件更为方便。

   使用综合脚本


   有了脚本文件，我们就能更好地控制 Yosys。下面的脚本文件重复了上一节
   那条命令所做的事情：

   .. code:: yoscrypt

      read_verilog softusb_navre.v
      hierarchy
      proc; opt; memory; opt; techmap; opt
      write_blif softusb_navre.blif

   第一行和最后一行显然分别是读取 Verilog 文件、写出 BLIF 文件。

   第 2 行检查设计层次，并在必要时实例化设计中模块的参数化版本。对于
   这个简单设计来说，这一步没有任何作用。不过，作为一般规则，综合脚本
   在读取输入文件之后，应始终把这条命令作为第一条命令。

   第 3 行完成了大部分实际工作：

   -  命令 opt 是 Yosys 内置的优化器。它可以执行一些简单的优化，例如
      常量折叠、移除设计中未连接的部分。通常的做法是在综合过程的每个
      主要步骤之后调用 opt。如果不希望过度优化（例如分析某个设计时），
      建议改为调用 clean。

   -  命令 proc 把过程块（Yosys 对 Verilog always 块和 initial 块的内部
      表示）转换为由多路复用器和存储元件（各种类型的触发器）构成的电路。

   -  命令 memory 把 Yosys 对数组和数组访问的内部表示转换为多端口块
      存储器，然后把这种块存储器映射为地址译码器和触发器；除非使用了
      -nomap 选项，此时多端口块存储器会保留在设计中，之后可以用其他
      命令映射到特定架构的存储器原语。

   -  命令 techmap 把带有粗粒度单元（例如宽加法器和乘法器）的高层电路
      转换为由简单逻辑原语和单比特存储元件构成的细粒度电路。该命令通过
      用更简单单元的电路替换复杂单元来完成转换。可以像下一节将要看到的
      那样，以 Verilog 源文件的形式为这一过程提供自定义规则集。

   现在可以用综合脚本的文件名作为参数来运行 Yosys：

   .. code:: sh

      yosys softusb_navre.ys

   既然使用了综合脚本，我们就可以方便地修改 Yosys 综合设计的方式。
   首先应该定制的是对 hierarchy 命令的调用：

   当已知设计中不存在隐式黑盒（即被引用但未定义的模块）时，应以 -check
   选项调用 hierarchy 命令。这样，当设计中发现隐式黑盒时，综合就会失败。

   关于 hierarchy 命令，我们可以改进的第 2 点是：可以告诉它设计层次中
   顶层模块的名称。这样它就会自动移除所有没有被该顶层模块引用的模块。

   对许多设计来说，还希望优化设计中有限状态机（FSM）的编码。fsm 命令
   会找到 FSM、提取它们、执行一些基本优化，然后根据提取并优化后的描述
   生成电路。也可以让 fsm 命令把 FSM 保持为提取后的形式，以便用自定义
   命令进一步处理它们。但在这个例子中我们不想这样做。

   所以现在我们就得到了为 Navré CPU 生成 BLIF 文件的最终综合脚本：

   .. code:: yoscrypt

      read_verilog softusb_navre.v
      hierarchy -check -top softusb_navre
      proc; opt; memory; opt; fsm; opt; techmap; opt
      write_blif softusb_navre.blif

   进阶示例：Amber23 ARMv2a CPU


   我们的第 2 个示例是 `Amber23 ARMv2a CPU`_。我们同样以 `yosys-bigsim`_
   中包含的 Verilog 代码为基础。

   .. _Amber23 ARMv2a CPU: http://opencores.org/projects/amber

   .. code-block:: yoscrypt
      :caption: `amber23.ys`
      :name: amber23.ys

      read_verilog a23_alu.v
      read_verilog a23_barrel_shift_fpga.v
      read_verilog a23_barrel_shift.v
      read_verilog a23_cache.v
      read_verilog a23_coprocessor.v
      read_verilog a23_core.v
      read_verilog a23_decode.v
      read_verilog a23_execute.v
      read_verilog a23_fetch.v
      read_verilog a23_multiply.v
      read_verilog a23_ram_register_bank.v
      read_verilog a23_register_bank.v
      read_verilog a23_wishbone.v
      read_verilog generic_sram_byte_en.v
      read_verilog generic_sram_line_en.v
      hierarchy -check -top a23_core
      add -global_input globrst 1
      proc -global_arst globrst
      techmap -map adff2dff.v
      opt; memory; opt; fsm; opt; techmap
      write_blif amber23.blif

   这个核心的问题在于它没有专门的复位逻辑。取而代之的是，使用
   :numref:`glob_arst` 中所示的编码技巧，为 FPGA 实现中的全局异步复位
   定义复位值。这个设计无法按原样在 BLIF 中表达。我们需要改用综合脚本，
   把这种形式转换为可以在 BLIF 中表达的同步复位。

   （注意，如果这些编码技巧用于对 ROM 建模——其中寄存器用这种语法初始化，
   之后不再更新——那么没有问题。）

   :numref:`amber23.ys` 显示了 Amber23 核心的综合脚本。在第 17 行，add
   命令用于添加一个 1 位宽的全局输入信号，名称为 ``globrst``。这意味着
   每个层次模块都会添加一个该名称的输入，然后所有模块实例化都会被修改，
   使这个新信号连接到整个设计层次中。

   .. code-block:: verilog
      :caption: 全局异步复位的隐式编码
      :name: glob_arst

      reg [7:0] a = 13, b;
      initial b = 37;

   .. code-block:: verilog
      :caption: `adff2dff.v`
      :name: adff2dff.v

      (* techmap_celltype = "$adff" *)
      module adff2dff (CLK, ARST, D, Q);

      parameter WIDTH = 1;
      parameter CLK_POLARITY = 1;
      parameter ARST_POLARITY = 1;
      parameter ARST_VALUE = 0;

      input CLK, ARST;
      input [WIDTH-1:0] D;
      output reg [WIDTH-1:0] Q;

      wire [1023:0] _TECHMAP_DO_ = "proc";

      wire _TECHMAP_FAIL_ =
         !CLK_POLARITY || !ARST_POLARITY;

      always @(posedge CLK)
            if (ARST)
                     Q <= ARST_VALUE;
            else
                     Q <= D;

      endmodule

   在第 18 行调用了 :cmd:ref:`proc` 命令。但在这个脚本中，信号名 globrst
   作为全局复位信号传给该命令，用于把寄存器复位到它们被赋予的初始值。

   最后，在第 19 行使用 techmap 命令，把所有带异步复位的触发器实例替换为
   带同步复位的触发器。所用的映射文件如 :numref:`adff2dff.v` 所示。注意
   第 1 行中如何使用 ``techmap_celltype`` 属性告诉 techmap 命令在设计里
   替换哪些单元，第 15 和 16 行中的 ``_TECHMAP_FAIL_`` 信号线（其值为
   常量）如何判断参数集是否与该替换电路兼容，以及第 13 行中的
   ``_TECHMAP_DO_`` 信号线如何提供一个用于处理该单元的小型综合脚本。

   .. code-block:: c
      :caption: Amber23 CPU 的测试程序（埃拉托斯特尼筛法）。使用 GCC 4.6.3

               using GCC 4.6.3 for ARM with ``-Os -marm -march=armv2a
         -mno-thumb-interwork -ffreestanding``, linked with ``--fix-v4bx``
         set and booted with a custom setup routine written in ARM assembler.
      :name: sieve

      #include <stdint.h>
      #include <stdbool.h>

      #define BITMAP_SIZE 64
      #define OUTPORT 0x10000000

      static uint32_t bitmap[BITMAP_SIZE/32];

      static void bitmap_set(uint32_t idx) { bitmap[idx/32] |= 1 << (idx % 32); }
      static bool bitmap_get(uint32_t idx) { return (bitmap[idx/32] & (1 << (idx % 32))) != 0; }
      static void output(uint32_t val) { *((volatile uint32_t*)OUTPORT) = val; }

      int main() {
         uint32_t i, j, k;
         output(2);
         for (i = 0; i < BITMAP_SIZE; i++) {
            if (bitmap_get(i)) continue;
            output(3+2*i);
            for (j = 2*(3+2*i);; j += 3+2*i) {
                  if (j%2 == 0) continue;
                  k = (j-3)/2;
                  if (k >= BITMAP_SIZE) break;
                  bitmap_set(k);
            }
         }
         output(0);
         return 0;
      }

   Amber23 CPU 的验证


   为 Amber23 核心生成的 BLIF 文件（使用 :numref:`amber23.ys`、
   :numref:`adff2dff.v` 以及 yosys-bigsim 自带的 Amber23 RTL 源码版本生成）
   已用 yosys-bigsim 的测试平台验证。它成功在测试平台中执行了
   :numref:`sieve` 所示的程序。

   为了仿真，又用 `ABC`_ 把 BLIF 文件转换回 Verilog。因此这个测试也包含了
   把 BLIF 文件成功转换为 ABC 内部格式的过程。

   .. _ABC: https://github.com/berkeley-abc/abc

   关于仿真本身，唯一还值得写的是：这大概是作者做过的、为成功计算前 31 个
   质数而进行的最耗能、最耗时的方式之一。

   限制


   在撰写本文时，Yosys 不支持多维存储器，不支持写入数组元素的单个位，
   不支持用 ``$readmemb`` 和 ``$readmemh`` 初始化数组，并且对三态逻辑只有
   有限支持——这里只列出少数几项限制。

   话虽如此，Yosys 仍能综合绝大多数真实世界的 Verilog RTL 代码。剩下的
   情况通常可以很容易地修改到与 Yosys 兼容。

   yosys-bigsim 中的各种设计是查找 Yosys 能力范围示例的好地方。

   结论


   Yosys 是一个功能丰富的 Verilog-2005 综合工具。它有许多用途，其中之一
   是提供一条从高层 Verilog 代码通往低层逻辑电路的便捷通道。

   命令行选项 ``-S`` 可用于轻松地把 Verilog 代码综合为 BLIF 文件。

   借助自定义综合脚本，可以轻松执行高层优化，例如对 FSM 重新编码。在某些
   极端情况下，例如 Amber23 ARMv2 CPU，可以使用 Yosys 更高级的特性来
   修改设计以满足特定需求，而无需改动 RTL 代码。
