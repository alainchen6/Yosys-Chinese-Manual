字级单元
--------


大多数 RTL 单元与 Verilog、VHDL 等 HDL 中提供的运算符非常相似。因此，以下各节使用
Verilog 运算符来定义 RTL 单元的行为。

注意，所有 RTL 单元都有表示输入和输出宽度的参数。当 pass（处理流程）修改 RTL 单元
时，必须始终使这些参数的值与连接到输入和输出的信号宽度保持一致。

RTL 单元的仿真模型可以在 Yosys 源码树的 :file:`techlibs/common/simlib.v` 文件中找到。

.. toctree::
   :maxdepth: 2

   /cell/word_unary
   /cell/word_binary
   /cell/word_mux
   /cell/word_reg
   /cell/word_mem
   /cell/word_fsm
   /cell/word_arith
   /cell/word_logic
   /cell/word_spec
   /cell/word_formal
   /cell/word_debug
   /cell/word_wire
