:orphan:


012：将 Verilog 转换为 BTOR 页面
================================


摘要
====


Verilog-2005 是一种强大的硬件描述语言（HDL），可以用简短的 HDL 代码
构建出复杂的设计。BTOR 是一种用于模型检验的位精确（bit-precise）字级
（word-level）格式。它是一种简单的格式，易于解析。它允许在一维数组的
位向量理论上对模型检验问题建模，从而能够对带有寄存器和存储器的 Verilog
设计建模。Yosys 是一个开源 Verilog 综合工具，可用于把带有简单断言的
Verilog 设计转换为 BTOR 格式。

下载
====


本文档最初于 2013 年 11 月发布：
:download:`将 Verilog 转换为 BTOR PDF</_downloads/APPNOTE_012_Verilog_to_BTOR.pdf>`

..
   安装


   Yosys 用 C++ 编写（使用 C++11 中的特性），并在现代 Linux 上测试。
   它应当能在大多数带有 C++11 编译器的 UNIX 系统上正常编译。README 文件
   包含关于构建 Yosys 及其先决条件的有用信息。

   Yosys 是一个庞大且功能丰富的程序，带有一些依赖项。对于这项工作，我们
   可以停用 Makefile 中的其他额外特性，例如 TCL 和 ABC 支持。

   本应用笔记基于 2015-04-04 的 `Yosys GIT`_ `Rev. 082550f`。

   .. _Yosys GIT: https://github.com/YosysHQ/yosys

   .. _Rev. 082550f: https://github.com/YosysHQ/yosys/tree/082550f

   快速开始


   我们假设该 Verilog 设计是可综合的，并且假设设计中没有多维存储器。由于
   BTOR 会把寄存器隐式初始化为零值，而存储器保持未初始化，我们假设
   Verilog 设计中不包含 initial 块。关于 BTOR 格式的更多细节，请参阅
   :cite:p:`btor`。

   我们提供了一个 shell 脚本 ``verilog2btor.sh``，可用于把 Verilog 设计
   转换为 BTOR。该脚本位于 ``backends/btor`` 目录中。下面的示例展示了它的
   用法：

   .. code:: sh

      verilog2btor.sh fsm.v fsm.btor test

   脚本 ``verilog2btor.sh`` 接受三个参数。在上面的示例中，第一个参数
   ``fsm.v`` 是输入设计，第二个参数 ``fsm.btor`` 是 BTOR 输出的文件名，
   第三个参数 ``test`` 是设计中顶层模块的名称。

   要指定（需要检查的）属性，我们有两种选择：

   -  我们可以在 Verilog 设计的过程块或模块体中使用 Verilog 的 ``assert``
      语句，如 :numref:`specifying_property_assert` 所示。这是首选方案。

   -  我们可以使用一个名称以 ``safety`` 开头的单比特输出信号线。当属性
      满足时，该输出信号线的值需要被驱动为低电平，也就是说，求解器会尝试
      寻找使该 safety 引脚变为高电平的模型。这在
      :numref:`specifying_property_output` 中演示。

   .. code-block:: verilog
      :caption: 在 Verilog 设计中使用 ``assert`` 指定属性
      :name: specifying_property_assert

      module test(input clk, input rst, output y);

      reg [2:0] state;

      always @(posedge clk) begin
         if (rst || state == 3) begin
            state <= 0;
         end else begin
            assert(state < 3);
            state <= state + 1;
         end
      end

      assign y = state[2];

      assert property (y !== 1'b1);

      endmodule

   .. code-block:: verilog
      :caption: 在 Verilog 设计中使用输出信号线指定属性
      :name: specifying_property_output

      module test(input clk, input rst,
         output y, output safety1);

      reg [2:0] state;

      always @(posedge clk) begin
         if (rst || state == 3)
            state <= 0;
         else
            state <= state + 1;
      end

      assign y = state[2];

      assign safety1 = !(y !== 1'b1);

      endmodule

   我们可以在生成的 BTOR 文件上运行 `Boolector`_ ``1.4.1`` [1]_：

   .. _Boolector: http://fmv.jku.at/boolector/

   .. code:: sh

      $ boolector fsm.btor
      unsat

   我们也可以使用 `nuXmv`_，但它目前在 BTOR 设计上还不支持存储器。在
   nuXmv 的下一个版本中，我们将能够验证带有存储器的设计。

   .. _nuXmv: https://es-static.fbk.eu/tools/nuxmv/index.php

   详细流程


   Yosys 能够把 Verilog 设计综合到门级。我们希望在综合设计时保留寄存器和
   存储器。为此，我们描述了一个定制的 Yosys 综合流程，它也由
   ``verilog2btor.sh`` 脚本提供。:numref:`btor_script_memory` 展示了
   ``verilog2btor.sh`` 所执行的 Yosys 命令。

   .. code-block:: yoscrypt
      :caption: 带存储器的 BTOR 综合流程
      :name: btor_script_memory

      read_verilog -sv $1;
      hierarchy -top $3; hierarchy -libdir $DIR;
      hierarchy -check;
      proc; opt;
      opt_expr -mux_undef; opt;
      rename -hide;;;
      splice; opt;
      memory_dff -wr_only; memory_collect;;
      flatten;;
      memory_unpack;
      splitnets -driver;
      setundef -zero -undriven;
      opt;;;
      write_btor $2;

   下面逐行简要说明脚本中发生的事情：

   #. 读取输入文件。

   #. 设置层次中的顶层模块，并尝试自动读取第一行所读取文件中以 ``include``
      形式给出的文件。

   #. 检查设计层次。

   #. 把过程块转换为多路复用器（mux）和触发器。

   #. 从多路复用器中移除未定义（undef）信号。

   #. 隐藏所有未用作模块端口的信号名。

   #. 显式类型转换，即在电路中引入 slice 和 concat 单元。

   #. 把写存储器转换为同步存储器，并把存储器收集为多端口存储器。

   #. 展平设计，只得到一个模块。

   #. 分离读存储器和写存储器。

   #. 拆分被部分赋值的信号。

   #. 把未定义值设置为零值。

   #. 最后的优化 pass（处理流程）。

   #. 写出 BTOR 文件。

   关于上述命令的详细说明，请参阅 Yosys 文档，或运行
   ``yosys -h <command_name>``。

   前面给出的脚本可以很容易地修改为生成不含存储器的 BTOR 文件。做法是
   删除第 8 行和第 10 行，并在第 8 行引入新的 :cmd:ref:`memory` 命令。
   :numref:`btor_script_without_memory` 展示了修改后的 Yosys 脚本文件：

   .. code-block:: sh
      :caption: 不带存储器的 BTOR 综合流程
      :name: btor_script_without_memory

      read_verilog -sv $1;
      hierarchy -top $3; hierarchy -libdir $DIR;
      hierarchy -check;
      proc; opt;
      opt_expr -mux_undef; opt;
      rename -hide;;;
      splice; opt;
      memory;;
      flatten;;
      splitnets -driver;
      setundef -zero -undriven;
      opt;;;
      write_btor $2;

   示例


   下面是一个我们想转换为 BTOR 的 Verilog 设计示例：

   .. code-block:: verilog
      :caption: 示例 - Verilog 设计
      :name: example_verilog

      module array(input clk);

      reg [7:0] counter;
      reg [7:0] mem [7:0];

      always @(posedge clk) begin
         counter <= counter + 8'd1;
         mem[counter] <= counter;
      end

      assert property (!(counter > 8'd0) ||
         mem[counter - 8'd1] == counter - 8'd1);

      endmodule

   使用 :numref:`btor_memory` 中所示的脚本生成的、包含存储器的 BTOR 文件：

   .. code-block::
      :caption: 示例 - 转换后的带存储器 BTOR
      :name: btor_memory

      1 var 1 clk
      2 array 8 3
      3 var 8 $auto$rename.cc:150:execute$20
      4 const 8 00000001
      5 sub 8 3 4
      6 slice 3 5 2 0
      7 read 8 2 6
      8 slice 3 3 2 0
      9 add 8 3 4
      10 const 8 00000000
      11 ugt 1 3 10
      12 not 1 11
      13 const 8 11111111
      14 slice 1 13 0 0
      15 one 1
      16 eq 1 1 15
      17 and 1 16 14
      18 write 8 3 2 8 3
      19 acond 8 3 17 18 2
      20 anext 8 3 2 19
      21 eq 1 7 5
      22 or 1 12 21
      23 const 1 1
      24 one 1
      25 eq 1 23 24
      26 cond 1 25 22 24
      27 root 1 -26
      28 cond 8 1 9 3
      29 next 8 3 28

   以及由 :numref:`btor_without_memory` 中所示脚本得到的 BTOR 文件，该脚本
   把存储器展开为各个独立元素：

   .. code-block::
      :caption: 示例 - 转换后的带存储器 BTOR
      :name: btor_without_memory

      1 var 1 clk
      2 var 8 mem[0]
      3 var 8 $auto$rename.cc:150:execute$20
      4 slice 3 3 2 0
      5 slice 1 4 0 0
      6 not 1 5
      7 slice 1 4 1 1
      8 not 1 7
      9 slice 1 4 2 2
      10 not 1 9
      11 and 1 8 10
      12 and 1 6 11
      13 cond 8 12 3 2
      14 cond 8 1 13 2
      15 next 8 2 14
      16 const 8 00000001
      17 add 8 3 16
      18 const 8 00000000
      19 ugt 1 3 18
      20 not 1 19
      21 var 8 mem[2]
      22 and 1 7 10
      23 and 1 6 22
      24 cond 8 23 3 21
      25 cond 8 1 24 21
      26 next 8 21 25
      27 sub 8 3 16

      ...

      54 cond 1 53 50 52
      55 root 1 -54

      ...

      77 cond 8 76 3 44
      78 cond 8 1 77 44
      79 next 8 44 78

   限制


   BTOR 不支持存储器和寄存器的初始化，即它们会被隐式初始化为零值，因此在
   转换为 BTOR 时需要移除存储器的 initial 块。还应考虑 BTOR 不支持 Verilog
   的 ``x`` 或 ``z`` 值。

   另一件需要记住的事是，Yosys 会把多维存储器转换为一维存储器和地址
   译码器。因此越界的存储器访问可能产生意外的结果。

   结论


   使用所描述的流程，我们可以用 Yosys 从 Verilog 设计生成带存储器或不带
   存储器的字级验证基准。

   .. [1]
      较新版本的 Boolector 不支持时序模型。
      Boolector 1.4.1 可以用 picosat-951 构建。较新版本的
      picosat 具有不兼容的 API。
