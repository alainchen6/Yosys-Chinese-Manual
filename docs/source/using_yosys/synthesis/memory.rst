存储器处理
==========


`memory` 命令
^^^^^^^^^^^^^

在 RTL 网表中，存储器的读和写都是一个个独立的单元。这使得合并存储器的端口更容易。
`memory` pass 把存储器变换为一种实现。默认情况下，该实现是用于地址译码器
和寄存器的逻辑。它也是一条宏命令，会按合理的顺序调用其他常用的 ``memory_*``
pass：

.. literalinclude:: /code_examples/macro_commands/memory.ys
   :language: yoscrypt
   :start-after: #end:
   :caption: `memory` 调用的 pass

.. todo:: 把 ``memory_*`` 的简要说明写得更详细

一些简要说明：

-  `memory_dff` 把寄存器合并到存储器的读、写单元中。
-  `memory_collect` 收集某个存储器的所有读、写单元，并把它们变换为一个多端口存储
   器单元。
-  `memory_map` 接收多端口存储器单元，并把它变换为地址译码器逻辑和寄存器。

关于 `memory` 的更多信息（例如禁用某些子命令），参见
:doc:`/cmd/index_passes_memory`。

示例
----


.. todo:: 说明 ``memory`` 的插图

|code_examples/synth_flow|_.

.. |code_examples/synth_flow| replace:: :file:`docs/source/code_examples/synth_flow`
.. _code_examples/synth_flow: https://github.com/YosysHQ/yosys/tree/main/docs/source/code_examples/synth_flow

.. figure:: /_images/code_examples/synth_flow/memory_01.svg
   :class: width-helper invert-helper

.. literalinclude:: /code_examples/synth_flow/memory_01.ys
   :language: yoscrypt
   :caption: :file:`memory_01.ys`

.. literalinclude:: /code_examples/synth_flow/memory_01.v
   :language: verilog
   :caption: :file:`memory_01.v`

.. figure:: /_images/code_examples/synth_flow/memory_02.svg
   :class: width-helper invert-helper

.. literalinclude:: /code_examples/synth_flow/memory_02.v
   :language: verilog
   :caption: :file:`memory_02.v`

.. literalinclude:: /code_examples/synth_flow/memory_02.ys
   :language: yoscrypt
   :caption: :file:`memory_02.ys`

.. _memory_map:

存储器映射
^^^^^^^^^^

通常更倾向于使用特定架构的 RAM 资源来实现存储器。例如：

.. code-block:: yoscrypt

    memory -nomap
    memory_libmap -lib my_memory_map.txt
    techmap -map my_memory_map.v
    memory_map

`memory_libmap` 会尝试借助提供的库（上例中的 :file:`my_memory_map.txt`）把存储器
单元（`$mem_v2` 等）转换为硬件支持的存储器。必要时，会加入仿真逻辑，以保证转换
前后的功能等价。随后 :yoscrypt:`techmap -map
my_memory_map.v` 使用 `techmap` 映射到硬件原语。任何无法转换而剩余下来的存储器
单元会由 `memory_map` 接手，并映射为 DFF 和地址译码器。

.. note::

   启用调试输出后，可以找到更多关于有哪些映射选项可用以及每个选项相关代价的信
   息。可以用 `debug` 命令，或在调用 Yosys 时使用 ``-g`` 选项来全局启用调试消
   息。

关于 `memory_libmap` 所用 lib 格式的更多内容，参见
`passes/memory/memlib.md
<https://github.com/YosysHQ/yosys/blob/main/passes/memory/memlib.md>`_

支持的存储器模式
^^^^^^^^^^^^^^^^

注意，本文档并未收录所有受支持的模式；特别需要说明的是，多种模式的组合通常都能
工作。例如，`wbe`_ 可以与任何一种简单双端口（SDP）模型配合使用。一般来说，如果
某个硬件存储器定义不支持给定的配置，就会实例化额外的逻辑，以保证其行为与仿真
一致。

说明
----


存储器类型选择
~~~~~~~~~~~~~~


存储器推断代码会根据存储器的几何尺寸和所用特性自动选择目标存储器原语。视目标而
定，最多可以有四类存储器原语可供选择：

- FF RAM（即逻辑）：不使用硬件原语，存储器转换为大量触发器和多路复用器

  - 可以处理任意数量的写端口，只要所有写端口位于同一时钟域
  - 可以处理任意数量和任意类型的读端口

- LUT RAM（即分布式 RAM）：使用 LUT 存储作为 RAM

  - 在大多数 FPGA 上受支持（显著例外是 ice40）
  - 通常有一个同步写端口、一个或多个异步读端口
  - 容量小
  - 绝不会用于 ROM（转换为普通 LUT 总是更好）

- 块 RAM：专用的存储器块

  - 基本上在所有 FPGA 上都受支持
  - 只支持同步读
  - 两个端口，时钟各自独立
  - 通常支持真双端口（显著例外是 ice40，它只支持 SDP）
  - 通常支持非对称存储器和按字节写使能
  - 容量为几千比特

- 超大 RAM：

  - 仅在部分目标上受支持：

    - 某些 Xilinx UltraScale 器件（UltraRAM）

      - 两个端口，均为互斥的同步读和写
      - 单一时钟
      - 初始数据必须全为 0

    - 某些 ice40 器件（SPRAM）

      - 单个端口，具有互斥的同步读和写
      - 不支持初始数据

    - Nexus（大容量 RAM）

      - 两个端口，均为互斥的同步读和写
      - 单一时钟

  - 不会被存储器推断代码自动选中，需要通过 ram_style 属性显式启用

一般来说，可以预期自动选择过程大致如下：

- 如果存在异步读端口，则只能使用 LUT RAM（或 FF RAM）。
- 如果写端口多于一个，则只能使用块 RAM，并且这需要是硬件支持的真双端口模式

  - ……除非所有写端口都位于同一时钟域，此时也可以使用 FF RAM，但除了极小的存储
    器之外，这通常不是你想要的

- 否则，将根据存储器大小选用 FF RAM、LUT RAM 或块 RAM

可以通过给存储器附加 ram_style 属性来覆盖这一过程：

- ``(* ram_style = "logic" *)`` 选择 FF RAM
- ``(* ram_style = "distributed" *)`` 选择 LUT RAM
- ``(* ram_style = "block" *)`` 选择块 RAM
- ``(* ram_style = "huge" *)`` 选择超大 RAM

如果该覆盖无法在给定目标上实现，就会报错。

为了与其他软件兼容，该属性的许多替代拼写也被接受。

初始数据
~~~~~~~~


大多数 FPGA 目标都支持把各类存储器初始化为用户提供的值。如果不使用显式初始化，
存储器的初始值就是未定义的。初始数据可以由逐条写存储器单元的 initial 语句提供，
也可以由 ``$readmemh`` 或 ``$readmemb`` 系统任务提供。示例模式参见 `sr_init`_。

.. _wbe:

带字节使能的写端口
~~~~~~~~~~~~~~~~~~


- 字节使能可用于任何受支持的模式
- 为确保多次写会合并到一个端口，它们的位范围必须互不重叠，并且具有相同的地址和
  相同的时钟
- 任何写使能粒度都会被接受（最低可到按位写使能），但使用比目标原生支持更小的粒
  度很可能效率低下（例如，在 ECP5 上使用 4 位字节，要么会用 5 个填充位把字节补
  齐为原生的 9 位单元，要么会把 RAM 拆分成两个块 RAM）

.. code:: verilog

	reg [31 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge clk) begin
		if (write_enable[0])
			mem[write_addr][7:0] <= write_data[7:0];
		if (write_enable[1])
			mem[write_addr][15:8] <= write_data[15:8];
		if (write_enable[2])
			mem[write_addr][23:16] <= write_data[23:16];
		if (write_enable[3])
			mem[write_addr][31:24] <= write_data[31:24];
		if (read_enable)
			read_data <= mem[read_addr];
	end

简单双端口（SDP）存储器模式
---------------------------


.. todo:: 各种使能信号，例如 cen、wen+ren

异步读 SDP
~~~~~~~~~~


- 在受支持的目标上会得到 LUT RAM

.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];
	always @(posedge clk)
		if (write_enable)
			mem[write_addr] <= write_data;
	assign read_data = mem[read_addr];

跨时钟域的同步 SDP
~~~~~~~~~~~~~~~~~~


- 视大小会得到块 RAM 或 LUT RAM
- 对同一地址同时读写时，不保证行为

.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge write_clk) begin
		if (write_enable)
			mem[write_addr] <= write_data;
	end

	always @(posedge read_clk) begin
		if (read_enable)
			read_data <= mem[read_addr];
	end

读优先的同步 SDP
~~~~~~~~~~~~~~~~


- 读部分和写部分可以位于同一过程块，也可以位于不同过程块。
- 视大小会得到块 RAM 或 LUT RAM
- 只要两者使用同一时钟，Yosys 就会保证读优先行为。在某些目标上，块 RAM 可能需
  要额外电路。如果不需要读优先行为，请使用下面的模式之一。

.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge clk) begin
		if (write_enable)
			mem[write_addr] <= write_data;
		if (read_enable)
			read_data <= mem[read_addr];
	end

.. _no_rw_check:

冲突行为未定义的同步 SDP
~~~~~~~~~~~~~~~~~~~~~~~~


- 与上面类似，但当读、写端口在同一周期指向同一地址时，读出的值未定义

.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge clk) begin
		if (write_enable)
			mem[write_addr] <= write_data;

		if (read_enable) begin
			read_data <= mem[read_addr];

		if (write_enable && read_addr == write_addr)
			// this if block
			read_data <= 'x;
		end
	end

- 或者如下，使用 no_rw_check 属性

.. code:: verilog

	(* no_rw_check *)
	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge clk) begin
		if (write_enable)
			mem[write_addr] <= write_data;

		if (read_enable)
			read_data <= mem[read_addr];
	end

.. _sdp_wf:

写优先行为的同步 SDP
~~~~~~~~~~~~~~~~~~~~


- 视大小会得到块 RAM 或 LUT RAM
- 如果目标不原生支持写优先，块 RAM 可能需要额外电路。LUT RAM 则总是需要额外
  电路。

.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge clk) begin
		if (write_enable)
			mem[write_addr] <= write_data;

		if (read_enable) begin
			read_data <= mem[read_addr];
			if (write_enable && read_addr == write_addr)
				read_data <= write_data;
		end
	end

写优先行为的同步 SDP（替代模式）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


- 支持该模式是为了兼容性，但它的灵活性远不如上面的模式

.. code:: verilog

	reg [ADDR_WIDTH - 1 : 0] read_addr_reg;
	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge clk) begin
		if (write_enable)
			mem[write_addr] <= write_data;
		read_addr_reg <= read_addr;
	end

	assign read_data = mem[read_addr_reg];

单端口 RAM 存储器模式
---------------------


异步读单端口 RAM
~~~~~~~~~~~~~~~~


- 在受支持的目标上会得到单端口 LUT RAM

.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];
	always @(posedge clk)
		if (write_enable)
			mem[addr] <= write_data;
	assign read_data = mem[addr];

读写互斥的同步单端口 RAM
~~~~~~~~~~~~~~~~~~~~~~~~


- 视大小会得到单端口块 RAM 或 LUT RAM
- 这是在 ice40 上推断 SPRAM 的正确模式（需手动选择 ram_style）
- 在不支持读写块 RAM 端口的目标上（例如 ice40），会改为得到 SDP 块 RAM
- 对于块 RAM，如果可用，将使用“NO_CHANGE”模式

.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge clk) begin
		if (write_enable)
			mem[addr] <= write_data;
		else if (read_enable)
			read_data <= mem[addr];
	end

读优先行为的同步单端口 RAM
~~~~~~~~~~~~~~~~~~~~~~~~~~


- 只有当原生支持读优先行为时，才会得到单端口块 RAM；否则将使用带额外电路的
  SDP RAM
- 许多目标（Xilinx、ECP5、……）只能原生支持读优先/写优先的单端口 RAM（或 TDP
  RAM），且其中 write_enable 信号蕴含 read_enable 信号（即永远不能只写不读）。
  存储器推断代码会对控制信号运行一个简单的 SAT 求解器来判断是否属于这种情况，
  如果无法轻易证明，就会插入仿真电路。

.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge clk) begin
		if (write_enable)
			mem[addr] <= write_data;
		if (read_enable)
			read_data <= mem[addr];
	end

写优先行为的同步单端口 RAM
~~~~~~~~~~~~~~~~~~~~~~~~~~


- 受支持时会得到单端口块 RAM 或 LUT RAM
- 如果原生不支持写优先行为，块 RAM 需要额外电路

.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge clk) begin
		if (write_enable)
			mem[addr] <= write_data;
		if (read_enable)
			if (write_enable)
				read_data <= write_data;
			else
				read_data <= mem[addr];
	end

.. _sr_init:

带初始值的同步读端口
~~~~~~~~~~~~~~~~~~~~


- 初始读端口值可以与任何其他受支持的模式组合
- 如果使用块 RAM，而目标不原生支持初始读端口值，则会插入小型的仿真电路

.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];
	reg [DATA_WIDTH - 1 : 0] read_data;
	initial read_data = 'h1234;

	always @(posedge clk) begin
		if (write_enable)
			mem[write_addr] <= write_data;
		if (read_enable)
			read_data <= mem[read_addr];
	end

读寄存器复位模式
----------------


复位可以与任何其他受支持的模式组合（但同步复位和异步复位不能同时用于同一个读端
口）。如果使用块 RAM，且所选复位（同步或异步）不被目标原生支持，则会插入小型的
仿真电路。

同步复位，复位优先于使能
~~~~~~~~~~~~~~~~~~~~~~~~


.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge clk) begin
		if (write_enable)
			mem[write_addr] <= write_data;

		if (read_reset)
			read_data <= 'h1234;
		else if (read_enable)
			read_data <= mem[read_addr];
	end

同步复位，使能优先于复位
~~~~~~~~~~~~~~~~~~~~~~~~


.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge clk) begin
		if (write_enable)
			mem[write_addr] <= write_data;
		if (read_enable)
			if (read_reset)
				read_data <= 'h1234;
			else
				read_data <= mem[read_addr];
	end

带异步复位的同步读端口
~~~~~~~~~~~~~~~~~~~~~~


.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge clk) begin
		if (write_enable)
			mem[write_addr] <= write_data;
	end

	always @(posedge clk, posedge read_reset) begin
		if (read_reset)
			read_data <= 'h1234;
		else if (read_enable)
			read_data <= mem[read_addr];
	end

非对称存储器模式
----------------


要构造非对称存储器（读写端口宽度不同的存储器）：

- 声明存储器时使用最窄目标端口的宽度
- 把所有宽端口拆分为多个窄端口
- 为确保宽端口能被正确合并：

  - 地址方面，使用高位为实际地址、低位为常量的拼接
  - 确保属于该宽端口的所有端口使用相同的实际地址
  - 确保时钟相同
  - 对于读端口，确保使能/复位信号相同（对于写端口，使能信号可以不同——这将导
    致使用字节使能功能）

非对称存储器在所有目标上都受支持，但在不原生支持的地方可能需要仿真电路。注意，
当存储器大于底层块 RAM 原语时，即使硬件支持非对称存储器，也很可能不会使用它，
因为那样代价更高。

.. _wide_sr:

宽同步读端口
~~~~~~~~~~~~


.. code:: verilog

	reg [7:0] mem [0:255];
	wire [7:0] write_addr;
	wire [5:0] read_addr;
	wire [7:0] write_data;
	reg [31:0] read_data;

	always @(posedge clk) begin
		if (write_enable)
			mem[write_addr] <= write_data;
		if (read_enable) begin
			read_data[7:0] <= mem[{read_addr, 2'b00}];
			read_data[15:8] <= mem[{read_addr, 2'b01}];
			read_data[23:16] <= mem[{read_addr, 2'b10}];
			read_data[31:24] <= mem[{read_addr, 2'b11}];
		end
	end

宽异步读端口
~~~~~~~~~~~~


- 注意：唯一原生支持该模式的目标是 Xilinx UltraScale

.. code:: verilog

	reg [7:0] mem [0:511];
	wire [8:0] write_addr;
	wire [5:0] read_addr;
	wire [7:0] write_data;
	wire [63:0] read_data;

	always @(posedge clk) begin
		if (write_enable)
			mem[write_addr] <= write_data;
	end

	assign read_data[7:0] = mem[{read_addr, 3'b000}];
	assign read_data[15:8] = mem[{read_addr, 3'b001}];
	assign read_data[23:16] = mem[{read_addr, 3'b010}];
	assign read_data[31:24] = mem[{read_addr, 3'b011}];
	assign read_data[39:32] = mem[{read_addr, 3'b100}];
	assign read_data[47:40] = mem[{read_addr, 3'b101}];
	assign read_data[55:48] = mem[{read_addr, 3'b110}];
	assign read_data[63:56] = mem[{read_addr, 3'b111}];

宽写端口
~~~~~~~~


.. code:: verilog

	reg [7:0] mem [0:255];
	wire [5:0] write_addr;
	wire [7:0] read_addr;
	wire [31:0] write_data;
	reg [7:0] read_data;

	always @(posedge clk) begin
		if (write_enable[0])
			mem[{write_addr, 2'b00}] <= write_data[7:0];
		if (write_enable[1])
			mem[{write_addr, 2'b01}] <= write_data[15:8];
		if (write_enable[2])
			mem[{write_addr, 2'b10}] <= write_data[23:16];
		if (write_enable[3])
			mem[{write_addr, 2'b11}] <= write_data[31:24];
		if (read_enable)
			read_data <= mem[read_addr];
	end

真双端口（TDP）模式
-------------------


- 通过在同一存储器上组合两个单端口 RAM 模式，可以构造出许多不同的真双端口存储
  器变体
- 使用 TDP 存储器时，与单个单端口模式（必要时它们最终可能被转换为 SDP 存储器）
  相比，存储器推断代码在实现所要求的语义时可回旋的余地小得多——受支持的模式在
  很大程度上取决于目标
- 特别地，当两个端口具有相同时钟时，很可能需要手动选择“未定义冲突”模式才能启用
  TDP 存储器推断
- 下面的示例并不穷尽——还可以有更多端口类型组合
- 注意：如果两个写端口位于同一过程块中，这就在它们之间定义了优先级关系（如果两
  个端口在同一时钟都有效，则后一个胜出）。在几乎所有目标上，这都会导致需要少量
  额外电路来保证优先级语义。如果你不想要这种行为，请把它们放到不同的过程块中。

  - 使用 verific 前端时不支持优先级，任何优先级语义都会被忽略。

时钟不同、读写互斥的 TDP
~~~~~~~~~~~~~~~~~~~~~~~~


.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge clk_a) begin
		if (write_enable_a)
			mem[addr_a] <= write_data_a;
		else if (read_enable_a)
			read_data_a <= mem[addr_a];
	end

	always @(posedge clk_b) begin
		if (write_enable_b)
			mem[addr_b] <= write_data_b;
		else if (read_enable_b)
			read_data_b <= mem[addr_b];
	end

时钟相同、读优先行为的 TDP
~~~~~~~~~~~~~~~~~~~~~~~~~~


- 这要求硬件具备端口间读优先行为，且只能在某些目标（Xilinx、Nexus）上工作

.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge clk) begin
		if (write_enable_a)
			mem[addr_a] <= write_data_a;
		if (read_enable_a)
			read_data_a <= mem[addr_a];
	end

	always @(posedge clk) begin
		if (write_enable_b)
			mem[addr_b] <= write_data_b;
		if (read_enable_b)
			read_data_b <= mem[addr_b];
	end

多读端口的 TDP
~~~~~~~~~~~~~~


- 单个写端口与任意数量读端口的组合在所有目标上都受支持——如果有可用的多读端口
  原语（例如 Xilinx RAM64M），就会在合适时使用它。否则，存储器会被自动拆分成多
  个原语。

.. code:: verilog

	reg [31:0] mem [0:31];

	always @(posedge clk) begin
		if (write_enable)
			mem[write_addr] <= write_data;
	end

	assign read_data_a = mem[read_addr_a];
	assign read_data_b = mem[read_addr_b];
	assign read_data_c = mem[read_addr_c];

仅在 Verific 下支持的模式
-------------------------


以下模式只有在使用 Verific 前端读入设计时才受支持。

通过阻塞赋值实现写优先行为的同步 SDP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


- 为与 Yosys Verilog 前端兼容，请使用 `sdp_wf`_。

.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @(posedge clk) begin
		if (write_enable)
			mem[write_addr] = write_data;

		if (read_enable)
			read_data <= mem[read_addr];
	end

通过部分选择实现非对称存储器
~~~~~~~~~~~~~~~~~~~~~~~~~~~~


- 为与 Yosys Verilog 前端兼容，请改用窄端口来构造宽端口（参见 `wide_sr`_）。

.. code:: verilog

	reg [31:0] mem [2**ADDR_WIDTH - 1 : 0];

	wire [1:0] byte_lane;
	wire [7:0] write_data;

	always @(posedge clk) begin
		if (write_enable)
			mem[write_addr][byte_lane * 8 +: 8] <= write_data;

		if (read_enable)
			read_data <= mem[read_addr];
	end


不期望的模式
------------


异步写
~~~~~~


- 现代 FPGA 不支持
- Yosys 代码本身也不支持

.. code:: verilog

	reg [DATA_WIDTH - 1 : 0] mem [2**ADDR_WIDTH - 1 : 0];

	always @* begin
		if (write_enable)
			mem[write_addr] = write_data;
	end

	assign read_data = mem[read_addr];
