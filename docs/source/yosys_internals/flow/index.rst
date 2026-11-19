内部流程
========


Yosys 由一个（通常很短的）综合脚本控制。

这些脚本包含三类命令：

- **前端**，读取输入文件（通常是 Verilog）；
- **Pass**，即处理流程，对内存中的设计执行变换；
- **后端**，把内存中的设计写入文件（支持多种格式：Verilog、BLIF、EDIF、SPICE、
  BTOR、. . .）。

.. toctree::
	:maxdepth: 3

	overview
	control_and_data
	verilog_frontend
