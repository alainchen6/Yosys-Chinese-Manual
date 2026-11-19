综合详解
--------


综合通常可以分解为粗粒度综合和细粒度综合。我们在
:doc:`/getting_started/example_synth` 中已经看到：设计被加载并细化，然后经过
一系列粗粒度优化，最后映射到硬核模块和细粒度单元。Yosys 中的大多数命令要么
针对粗粒度表示，要么针对细粒度表示，只有少数命令同时兼容这两种状态。

`proc`、`fsm` 和 `memory` 等命令依赖粗粒度表示中的附加信息，以及 `wreduce`、
`share` 和 `alumacc` 等若干优化。`opt` 提供在两种状态下都有用的优化，而
`techmap` 用于把粗粒度单元转换为对应的细粒度表示。

单比特单元（逻辑门、触发器）以及 LUT、半加器和全加器构成了细粒度表示的主体，
并且是 `abc`\ /`abc9`、`simplemap`、`dfflegalize` 和 `memory_map`
等命令所必需的。

.. toctree::
   :maxdepth: 3

   synth
   proc
   fsm
   memory
   opt
   techmap_synth
   extract
   abc
   cell_libs
