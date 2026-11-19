.. _sec:celllib_gates:

门级单元
--------


对于门级逻辑网络，使用不提供任何参数的固定功能单比特单元。

这些单元的仿真模型可以在 Yosys 源码树的 :file:`techlibs/common/simcells.v` 文件中找到。

在大多数情况下，门级逻辑网络是由 RTL 网络通过 techmap pass（处理流程）创建的。门级
逻辑网络中的触发器单元可以使用 dfflibmap pass 映射到 Liberty 文件中的物理触发器单元。
组合逻辑单元可以通过 ABC 使用 abc pass 映射到 Liberty 文件中的物理单元。

.. toctree::
   :maxdepth: 2

   /cell/gate_comb_simple
   /cell/gate_comb_combined
   /cell/gate_reg_ff
   /cell/gate_reg_latch
   /cell/gate_other
