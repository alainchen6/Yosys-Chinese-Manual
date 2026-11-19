.. _chapter:overview:

Yosys 内部
==========


.. todo:: 少些学术腔

Yosys 是一个可扩展的开源硬件综合工具。它面向的设计者需要一种易于上手、通用且与
厂商无关的综合工具；同时也面向在电子设计自动化（EDA）领域做研究的科研人员，他们
需要一种开放的综合框架，以便在复杂的真实设计上测试算法。

Yosys 可以综合 Verilog 2005 的很大一部分子集，并已在大量真实设计上测试过，包括
`OpenRISC 1200 CPU`_、`openMSP430 CPU`_、`OpenCores I2C master`_ 和 `k68 CPU`_。

.. todo:: 添加 RISC-V 核心示例

.. _OpenRISC 1200 CPU: https://github.com/openrisc/or1200

.. _openMSP430 CPU: http://opencores.org/projects/openmsp430

.. _OpenCores I2C master: http://opencores.org/projects/i2c

.. _k68 CPU: http://opencores.org/projects/k68

Yosys 用 C++ 编写，最低面向 C++20。本章介绍 Yosys 的一些基础数据结构。为了简单
起见，本章沿用 Yosys 实现中使用的 C++ 类型名，尽管本章只解释其背后的概念思路，
并且可以作为用任何语言实现类似系统的参考。

.. toctree::
   :maxdepth: 3

   flow/index
   formats/index
   extending_yosys/index
   techmap
   hashing
   idstring
