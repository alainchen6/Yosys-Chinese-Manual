流程概览
========


.. todo:: 少些学术腔

:numref:`图 %s <fig:Overview_flow>` 展示了 Yosys 内部简化的数据流。图中的矩形
表示程序模块，椭圆表示用于在程序模块之间交换设计数据的内部数据结构。

设计数据通过某个前端模块读入。面向 Verilog 和 VHDL 代码的高层 HDL 前端会生成
抽象语法树（AST），然后把它交给 AST 前端。注意，两个 HDL 前端使用相同的 AST
表示，这种表示足以覆盖 Verilog HDL 和 VHDL 语言。

随后 AST 前端把 AST 编译为 Yosys 的主要内部数据格式，即 RTL 中间语言（RTLIL）。
关于该格式更详细的说明见 :doc:`/yosys_internals/formats/rtlil_rep`。

RTLIL 数据结构还有一种文本表示，可以用 RTLIL 前端解析，详见
:doc:`/appendix/rtlil_text`。

接下来，可以用一系列 pass（处理流程）对设计数据进行变换，这些 pass 都作用于
设计的 RTLIL 表示。

最后，RTLIL 表示的设计会由某个后端转换回文本，即用 Verilog 后端生成 Verilog
网表，或用 RTLIL 后端以 RTLIL 前端能够理解的相同格式写出 RTLIL 数据。

除 AST 前端之外（它由高层 HDL 前端调用，用户不能直接调用），所有程序模块都由
用户调用（通常使用包含 Yosys 文本命令的综合脚本）。

通过以不同方式组合 pass 和/或向 Yosys 添加额外的 pass，可以让 Yosys 适应各种
应用。要做到这一点，关键在于：(1) 所有 pass 都作用于相同的数据结构（RTLIL）；
(2) 该数据结构足以表示综合不同阶段的设计。

.. figure:: /_images/internals/overview_flow.svg
	:class: width-helper invert-helper
	:name: fig:Overview_flow

	Yosys 简化的数据流（椭圆：数据结构，矩形：程序模块）
