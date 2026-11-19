.. role:: verilog(code)
   :language: Verilog

触发器单元
----------


单元类型 `$_DFF_N_` 和 `$_DFF_P_` 表示 D 型触发器。

.. table:: 基本触发器的单元类型

   ======================================= =============
   Verilog                                 单元类型
   ======================================= =============
   :verilog:`always @(negedge C) Q <= D`   `$_DFF_N_`
   :verilog:`always @(posedge C) Q <= D`   `$_DFF_P_`
   ======================================= =============

单元类型 ``$_DFFE_[NP][NP]_`` 实现带使能的 D 型触发器。这些单元类型在表中的
取值对应下面的 Verilog 代码模板。

.. code-block:: verilog
   :force:

   always @(CLK_EDGE C)
      if (EN == EN_LVL)
         Q <= D;


.. table:: 门级逻辑网络的单元类型（带使能的触发器）
   :name: tab:CellLib_gates_dffe

   ================== ============= ============
   :math:`ClkEdge`    :math:`EnLvl` 单元类型
   ================== ============= ============
   :verilog:`negedge` ``0``         `$_DFFE_NN_`
   :verilog:`negedge` ``1``         `$_DFFE_NP_`
   :verilog:`posedge` ``0``         `$_DFFE_PN_`
   :verilog:`posedge` ``1``         `$_DFFE_PP_`
   ================== ============= ============

单元类型 ``$_DFF_[NP][NP][01]_`` 实现带异步复位的 D 型触发器。这些单元类型在
表中的取值对应下面的 Verilog 代码模板，其中若 ``RST_LVL`` 为 ``1``，则
``RST_EDGE`` 为 ``posedge``，否则为 ``negedge``。

.. code-block:: verilog
   :force:

   always @(CLK_EDGE C, RST_EDGE R)
      if (R == RST_LVL)
         Q <= RST_VAL;
      else
         Q <= D;

单元类型 ``$_SDFF_[NP][NP][01]_`` 实现带同步复位的 D 型触发器。这些单元类型在
表中的取值对应下面的 Verilog 代码模板：

.. code-block:: verilog
   :force:

   always @(CLK_EDGE C)
      if (R == RST_LVL)
         Q <= RST_VAL;
      else
         Q <= D;

.. table:: 门级逻辑网络的单元类型（带复位的触发器）
   :name: tab:CellLib_gates_adff

   ================== ============== ============== ===========================
   :math:`ClkEdge`    :math:`RstLvl` :math:`RstVal` 单元类型
   ================== ============== ============== ===========================
   :verilog:`negedge` ``0``          ``0``          `$_DFF_NN0_`, `$_SDFF_NN0_`
   :verilog:`negedge` ``0``          ``1``          `$_DFF_NN1_`, `$_SDFF_NN1_`
   :verilog:`negedge` ``1``          ``0``          `$_DFF_NP0_`, `$_SDFF_NP0_`
   :verilog:`negedge` ``1``          ``1``          `$_DFF_NP1_`, `$_SDFF_NP1_`
   :verilog:`posedge` ``0``          ``0``          `$_DFF_PN0_`, `$_SDFF_PN0_`
   :verilog:`posedge` ``0``          ``1``          `$_DFF_PN1_`, `$_SDFF_PN1_`
   :verilog:`posedge` ``1``          ``0``          `$_DFF_PP0_`, `$_SDFF_PP0_`
   :verilog:`posedge` ``1``          ``1``          `$_DFF_PP1_`, `$_SDFF_PP1_`
   ================== ============== ============== ===========================

单元类型 ``$_DFFE_[NP][NP][01][NP]_`` 实现带异步复位和使能的 D 型触发器。这些
单元类型在表中的取值对应下面的 Verilog 代码模板，其中若 ``RST_LVL`` 为 ``1``，
则 ``RST_EDGE`` 为 ``posedge``，否则为 ``negedge``。

.. code-block:: verilog
   :force:

   always @(CLK_EDGE C, RST_EDGE R)
      if (R == RST_LVL)
         Q <= RST_VAL;
      else if (EN == EN_LVL)
         Q <= D;

单元类型 ``$_SDFFE_[NP][NP][01][NP]_`` 实现带同步复位和使能的 D 型触发器，其中
复位优先于使能。这些单元类型在表中的取值对应下面的 Verilog 代码模板：

.. code-block:: verilog
   :force:

   always @(CLK_EDGE C)
      if (R == RST_LVL)
         Q <= RST_VAL;
      else if (EN == EN_LVL)
         Q <= D;

单元类型 ``$_SDFFCE_[NP][NP][01][NP]_`` 实现带同步复位和使能的 D 型触发器，其中
使能优先于复位。这些单元类型在表中的取值对应下面的 Verilog 代码模板：

.. code-block:: verilog
   :force:

   always @(CLK_EDGE C)
      if (EN == EN_LVL)
         if (R == RST_LVL)
            Q <= RST_VAL;
         else
            Q <= D;


.. table:: 门级逻辑网络的单元类型（带复位和使能的触发器）
   :name: tab:CellLib_gates_adffe

   ================== ============== ============== ============= =================================================
   :math:`ClkEdge`    :math:`RstLvl` :math:`RstVal` :math:`EnLvl` 单元类型
   ================== ============== ============== ============= =================================================
   :verilog:`negedge` ``0``          ``0``          ``0``         `$_DFFE_NN0N_`, `$_SDFFE_NN0N_`, `$_SDFFCE_NN0N_`
   :verilog:`negedge` ``0``          ``0``          ``1``         `$_DFFE_NN0P_`, `$_SDFFE_NN0P_`, `$_SDFFCE_NN0P_`
   :verilog:`negedge` ``0``          ``1``          ``0``         `$_DFFE_NN1N_`, `$_SDFFE_NN1N_`, `$_SDFFCE_NN1N_`
   :verilog:`negedge` ``0``          ``1``          ``1``         `$_DFFE_NN1P_`, `$_SDFFE_NN1P_`, `$_SDFFCE_NN1P_`
   :verilog:`negedge` ``1``          ``0``          ``0``         `$_DFFE_NP0N_`, `$_SDFFE_NP0N_`, `$_SDFFCE_NP0N_`
   :verilog:`negedge` ``1``          ``0``          ``1``         `$_DFFE_NP0P_`, `$_SDFFE_NP0P_`, `$_SDFFCE_NP0P_`
   :verilog:`negedge` ``1``          ``1``          ``0``         `$_DFFE_NP1N_`, `$_SDFFE_NP1N_`, `$_SDFFCE_NP1N_`
   :verilog:`negedge` ``1``          ``1``          ``1``         `$_DFFE_NP1P_`, `$_SDFFE_NP1P_`, `$_SDFFCE_NP1P_`
   :verilog:`posedge` ``0``          ``0``          ``0``         `$_DFFE_PN0N_`, `$_SDFFE_PN0N_`, `$_SDFFCE_PN0N_`
   :verilog:`posedge` ``0``          ``0``          ``1``         `$_DFFE_PN0P_`, `$_SDFFE_PN0P_`, `$_SDFFCE_PN0P_`
   :verilog:`posedge` ``0``          ``1``          ``0``         `$_DFFE_PN1N_`, `$_SDFFE_PN1N_`, `$_SDFFCE_PN1N_`
   :verilog:`posedge` ``0``          ``1``          ``1``         `$_DFFE_PN1P_`, `$_SDFFE_PN1P_`, `$_SDFFCE_PN1P_`
   :verilog:`posedge` ``1``          ``0``          ``0``         `$_DFFE_PP0N_`, `$_SDFFE_PP0N_`, `$_SDFFCE_PP0N_`
   :verilog:`posedge` ``1``          ``0``          ``1``         `$_DFFE_PP0P_`, `$_SDFFE_PP0P_`, `$_SDFFCE_PP0P_`
   :verilog:`posedge` ``1``          ``1``          ``0``         `$_DFFE_PP1N_`, `$_SDFFE_PP1N_`, `$_SDFFCE_PP1N_`
   :verilog:`posedge` ``1``          ``1``          ``1``         `$_DFFE_PP1P_`, `$_SDFFE_PP1P_`, `$_SDFFCE_PP1P_`
   ================== ============== ============== ============= =================================================

单元类型 ``$_DFFSR_[NP][NP][NP]_`` 实现带异步置位和复位的 D 型触发器。这些单元
类型在表中的取值对应下面的 Verilog 代码模板，其中若 ``RST_LVL`` 为 ``1``，则
``RST_EDGE`` 为 ``posedge``，否则为 ``negedge``；若 ``SET_LVL`` 为 ``1``，则
``SET_EDGE`` 为 ``posedge``，否则为 ``negedge``。

当置位和复位同时有效时，状态和输出未定义。由于可综合 Verilog 的限制，
Verilog 代码模型并不对应这种情况。

.. code-block:: verilog
   :force:

   always @(CLK_EDGE C, RST_EDGE R, SET_EDGE S)
      if (R == RST_LVL)
         Q <= 0;
      else if (S == SET_LVL)
         Q <= 1;
      else
         Q <= D;

.. table:: 门级逻辑网络的单元类型（带置位和复位的触发器）
   :name: tab:CellLib_gates_dffsr

   ================== ============== ============== ==============
   :math:`ClkEdge`    :math:`SetLvl` :math:`RstLvl` 单元类型
   ================== ============== ============== ==============
   :verilog:`negedge` ``0``          ``0``          `$_DFFSR_NNN_`
   :verilog:`negedge` ``0``          ``1``          `$_DFFSR_NNP_`
   :verilog:`negedge` ``1``          ``0``          `$_DFFSR_NPN_`
   :verilog:`negedge` ``1``          ``1``          `$_DFFSR_NPP_`
   :verilog:`posedge` ``0``          ``0``          `$_DFFSR_PNN_`
   :verilog:`posedge` ``0``          ``1``          `$_DFFSR_PNP_`
   :verilog:`posedge` ``1``          ``0``          `$_DFFSR_PPN_`
   :verilog:`posedge` ``1``          ``1``          `$_DFFSR_PPP_`
   ================== ============== ============== ==============

单元类型 ``$_DFFSRE_[NP][NP][NP][NP]_`` 实现带异步置位、复位和使能的 D 型
触发器。这些单元类型在表中的取值对应下面的 Verilog 代码模板，其中若
``RST_LVL`` 为 ``1``，则 ``RST_EDGE`` 为 ``posedge``，否则为 ``negedge``；
若 ``SET_LVL`` 为 ``1``，则 ``SET_EDGE`` 为 ``posedge``，否则为 ``negedge``。

当置位和复位同时有效时，状态和输出未定义。由于可综合 Verilog 的限制，
Verilog 代码模型并不对应这种情况。

.. code-block:: verilog
   :force:

   always @(CLK_EDGE C, RST_EDGE R, SET_EDGE S)
      if (R == RST_LVL)
         Q <= 0;
      else if (S == SET_LVL)
         Q <= 1;
      else if (E == EN_LVL)
         Q <= D;


.. table:: 门级逻辑网络的单元类型（带置位、复位和使能的触发器）
   :name: tab:CellLib_gates_dffsre

   ================== ============== ============== ============= ================
   :math:`ClkEdge`    :math:`SetLvl` :math:`RstLvl` :math:`EnLvl` 单元类型
   ================== ============== ============== ============= ================
   :verilog:`negedge` ``0``          ``0``          ``0``         `$_DFFSRE_NNNN_`
   :verilog:`negedge` ``0``          ``0``          ``1``         `$_DFFSRE_NNNP_`
   :verilog:`negedge` ``0``          ``1``          ``0``         `$_DFFSRE_NNPN_`
   :verilog:`negedge` ``0``          ``1``          ``1``         `$_DFFSRE_NNPP_`
   :verilog:`negedge` ``1``          ``0``          ``0``         `$_DFFSRE_NPNN_`
   :verilog:`negedge` ``1``          ``0``          ``1``         `$_DFFSRE_NPNP_`
   :verilog:`negedge` ``1``          ``1``          ``0``         `$_DFFSRE_NPPN_`
   :verilog:`negedge` ``1``          ``1``          ``1``         `$_DFFSRE_NPPP_`
   :verilog:`posedge` ``0``          ``0``          ``0``         `$_DFFSRE_PNNN_`
   :verilog:`posedge` ``0``          ``0``          ``1``         `$_DFFSRE_PNNP_`
   :verilog:`posedge` ``0``          ``1``          ``0``         `$_DFFSRE_PNPN_`
   :verilog:`posedge` ``0``          ``1``          ``1``         `$_DFFSRE_PNPP_`
   :verilog:`posedge` ``1``          ``0``          ``0``         `$_DFFSRE_PPNN_`
   :verilog:`posedge` ``1``          ``0``          ``1``         `$_DFFSRE_PPNP_`
   :verilog:`posedge` ``1``          ``1``          ``0``         `$_DFFSRE_PPPN_`
   :verilog:`posedge` ``1``          ``1``          ``1``         `$_DFFSRE_PPPP_`
   ================== ============== ============== ============= ================

.. todo:: 带异步加载的触发器，``$_ALDFFE?_[NP]{2,3}_``

.. autocellgroup:: reg_ff
   :members:
   :source:
   :linenos:
