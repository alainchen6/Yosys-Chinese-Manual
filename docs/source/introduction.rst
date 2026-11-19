Yosys 是什么
============


Yosys 最初是 Claire Wolf 的本科毕业论文项目，目的是支持 CGRA（粗粒度可重构
架构）的综合。后来它扩展为更通用的综合研究基础设施。

现代 Yosys 完整支持 Verilog-2005 的可综合子集，并被称为“硬件综合领域的
GCC”。Yosys 可自由获取且以 `open source`_ 方式发布，既用于爱好者和商业应用，
也用于学术研究。

.. _open source: https://github.com/YosysHQ/yosys

.. note:: Yosys 以 ISC 许可证发布：

   宽松许可证允许人们在给予适当署名且无担保的前提下，对你的代码做任何事。
   ISC 许可证在功能上等同于 BSD 2-Clause 和 MIT 许可证，并删除了一些不再
   必要的措辞。

结合布局布线工具 `nextpnr`_，Yosys 可以用完全端到端的开源流程为某些 FPGA
编程（Lattice iCE40 和 ECP5）。它还负责 `OpenLane flow`_ 的综合部分，该流程
面向 SkyWater 130nm 开源 PDK，以实现完全开源的 ASIC 设计。Yosys 也能进行
形式化验证，并提供面向 `SMT2`_ 等求解器格式的后端。

.. _nextpnr: https://github.com/YosysHQ/nextpnr
.. _OpenLane flow: https://github.com/The-OpenROAD-Project/OpenLane
.. _SMT2: https://smtlib.cs.uiowa.edu/

Yosys 及与之配套的开源 EDA 生态目前由 `Yosys Headquarters`_ 维护，许多核心
开发者受雇于 `YosysHQ GmbH`_。商业扩展 `Tabby CAD Suite`_ 包含用于工业级
SystemVerilog 和 VHDL 支持的 Verific 前端、带 SVA 的形式化验证以及形式化
应用。

.. _Yosys Headquarters: https://github.com/YosysHQ
.. _YosysHQ GmbH: https://www.yosyshq.com/about
.. _Tabby CAD Suite: https://www.yosyshq.com/tabby-cad-datasheet

.. figure:: /_static/logo.png
    :class: width-helper

用 Yosys 能做什么
-----------------


- 读取并处理（大部分）现代 Verilog-2005 代码
- 对网表执行各种操作（RTL、逻辑、门级）
- 使用 ABC 进行逻辑优化和门映射

Yosys 的典型应用
~~~~~~~~~~~~~~~~


- 最终量产设计的综合
- 量产前综合（在投入其他工具之前试运行）
- 将全功能 Verilog 转换为简单 Verilog
- 将 Verilog 转换为其他格式（BLIF、BTOR 等）
- 演示综合算法（例如用于教学目的）
- 用于试验新算法的框架
- 用于构建自定义流程的框架（不限于综合，还包括形式化验证、逆向工程……）

Yosys 不能做的事
~~~~~~~~~~~~~~~~


- 处理 C/C++/SystemC 等高级语言
- 生成物理版图（布局布线）

  - 这一点请查看 `nextpnr`_

- 依赖内置的语法检查

  - 请改用 `verilator`_ 之类的外部工具

.. todo:: 补充用于 FPGA 的 nextpnr，考虑提及 openlane、vpr、coriolis

.. _nextpnr: https://github.com/YosysHQ/nextpnr
.. _verilator: https://www.veripool.org/verilator/

Yosys 家族
----------


如上所述，`YosysHQ`_ 不仅维护 Yosys，还维护围绕它构建的一整套工具。以下
顺序不分先后：

.. _YosysHQ: https://github.com/YosysHQ

用于形式化验证的 SBY
   Yosys 提供输入解析，并转换为求解器引擎所使用的格式。Yosys 还提供统一的
   见证（witness）框架，为原生不支持该功能的引擎提供覆盖轨迹（cover trace）
   和反例。`SBY source`_ | `SBY docs`_

.. _SBY source: https://github.com/YosysHQ/sby
.. _SBY docs: https://yosyshq.readthedocs.io/projects/sby

用于等价检查的 EQY
   除输入解析与准备之外，Yosys 还提供插件支持，使 EQY 能直接对设计进行
   操作。`EQY source`_ | `EQY docs`_

.. _EQY source: https://github.com/YosysHQ/eqy
.. _EQY docs: https://yosyshq.readthedocs.io/projects/eqy

用于变异覆盖率的 MCY
   Yosys 用于读取源设计、生成可最大化设计覆盖率的候选变异列表，然后执行
   选定的变异。`MCY source`_ | `MCY docs`_

.. _MCY source: https://github.com/YosysHQ/mcy
.. _MCY docs: https://yosyshq.readthedocs.io/projects/mcy

用于深层形式化轨迹的 SCY
   由于 SCY 生成并运行 SBY，Yosys 为 SCY 提供与 SBY 相同的功能。Yosys 还
   提供输出深层轨迹所需的轨迹拼接。`SCY source`_

.. _SCY source: https://github.com/YosysHQ/scy

原始论文摘要
------------


Yosys 文档的第一版是作为维也纳工业大学的本科毕业论文发表的 :cite:p:`BACC`。

:摘要:
	当今大多数数字设计都是用 HDL 代码（大多是 Verilog 或 VHDL）并借助 HDL
	综合工具完成的。

	在诸如为粗粒度单元库进行综合，或测试新的综合算法这样的特殊情况下，可能
	需要编写自定义的 HDL 综合工具，或为现有工具添加新功能。在这些情况下，
	若有一个可作为自定义工具基础的自由及开源软件（FOSS）综合工具，将会
	很有帮助。

	由于缺少这样的工具，我们开发了 Yosys Open SYnthesis Suite（Yosys）。
	本文档介绍该工具的设计与实现。目前 Yosys 的主要关注点在于数字综合的
	高层方面。Yosys 使用已有的 FOSS 逻辑综合工具 ABC 来执行高级门级优化。

	本文还包含基于真实设计的 Yosys 评估。结果表明，Yosys 可直接用于综合这类
	设计。这些测试中 Yosys 产生的结果已通过形式化验证成功验证，且质量与
	商业综合工具的结果相当。

Yosys 是一个 Verilog HDL 综合工具。这意味着它以行为级设计描述为输入，输出
设计的 RTL、逻辑门级或物理门级描述。Yosys 的主要优势在于行为级综合和 RTL
综合。Yosys 内提供了大量命令（综合 pass，即处理流程），可用于在行为级、RTL
和逻辑综合领域完成各种综合任务。Yosys 在设计上可扩展，因此是实现面向特定
任务的自定义综合工具的良好基础。

.. figure:: /_images/primer/levels_of_abstraction.svg
    :class: width-helper invert-helper
    :name: fig:Levels_of_abstraction

    Yosys 在抽象层次中的位置

开源 HDL 综合的优势
~~~~~~~~~~~~~~~~~~~


- 成本（同样适用于 ``free as in free beer`` 方案）：

  如今 180nm 工艺的一套掩模版成本远低于设计掩模版布局所需的设计工具成本。
  开源 ASIC 流程是实现 ASIC 级开源硬件的重要推动因素。

- 可用性与可复现性：

  如果你是发表论文的研究者，你会希望使用其他人也能使用的工具。即使大多数
  高校都能获得所有主流商业工具，你通常也无法方便地获得几年前某个研究项目
  所使用的那个版本。而使用开源工具，你甚至可以连同数据一起发布所用工具的
  源代码。

- 框架：

  Yosys 不只是一个工具。它是一个可作为其他开发基础的框架，因此研究者和
  黑客都无需重新发明基础功能。可扩展性是 Yosys 的设计目标之一。

- 一体化：

  由于 Yosys 的框架特性，越来越多的功能在一个工具中提供。Yosys 不仅可用于
  电路综合，还可用于形式化等价检查、SAT 求解和电路分析——这里只列举了少数
  其他应用领域。而使用专有软件时，每涉及一个这样的应用，都需要学习一个新
  工具。

- 教学工具：

  专有综合工具有时对其内部工作原理非常保密。它们往往是 ``black boxes``。
  Yosys 的内部实现非常开放，很容易观察综合的不同步骤。

Yosys 的历史
~~~~~~~~~~~~


.. todo:: 考虑为“Yosys 的历史”提供一个更通俗的版本

硬件描述语言（HDL）是一种用于描述电路的计算机语言。HDL 综合工具是一种
计算机程序，它的输入是用 HDL 编写的电路形式化描述，输出是实现给定电路的
网表。

目前，数字电路领域使用最广泛、支持最完善的 HDL 是 Verilog
:cite:p:`Verilog2005,VerilogSynth` 和
:abbr:`VHDL (VHSIC HDL，其中 VHSIC 是 Very-High-Speed Integrated Circuits 的首字母缩写)`
:cite:p:`VHDL,VHDLSynth`。两种 HDL 都用于测试与验证以及逻辑综合，因此各自
都有一组可综合的语言特性和一组不可综合的语言特性。本文只关注语言特性中的
可综合子集。

在近期关于异构粗粒度可重构逻辑的工作 :cite:p:`intersynth` 中，出现了对
面向特定应用的自定义 HDL 综合工具的需求。人们很快意识到，一个能理解
Verilog 或 VHDL 的综合工具，会比一个针对自定义 HDL 的综合工具更可取。若
已有 Verilog 或 VHDL 前端，那么编写所需附加功能并将其集成到现有工具中的
工作量，估计与编写一个支持极简自定义 HDL 的新工具大致相当。

所提出的自定义 HDL 综合工具应以自由及开源软件（FOSS）许可证授权。因此需要
一个现有的 FOSS Verilog 或 VHDL 综合工具作为构建基础。选择 Verilog 或 VHDL
的主要优势在于能够综合已有的 HDL 代码，并减轻电路设计者学习新语言的要求。
为了充分利用任何现有的 FOSS Verilog 或 VHDL 工具，此类工具必须提供可综合
HDL 子集的完整功能实现。

基本的 RTL 综合是一个已被充分理解的领域 :cite:p:`LogicSynthesis`。计算机
语言的词法分析、语法分析和处理 :cite:p:`Dragonbook` 是一个研究得很透彻的
领域。编写这类工具所需的全部信息早已公开可得，因此很可能存在一个具有
功能完整的 Verilog 或 VHDL 前端的 FOSS HDL 综合工具，可作为自定义 RTL
综合工具的基础。

由于作者更偏爱 Verilog 而非 VHDL，早期就决定采用 Verilog 而不用 VHDL [#]_。
于是对现有的 FOSS Verilog 综合工具进行了评估。评估结果非常糟糕。因此实现
了一个全新的 Verilog 综合工具，并推荐将其作为自定义综合工具的基础。本文档
讨论的正是这个工具。

.. [#]
   对 FOSS VHDL 工具的快速调查显示，FOSS VHDL 综合工具的情况同样不容乐观。
