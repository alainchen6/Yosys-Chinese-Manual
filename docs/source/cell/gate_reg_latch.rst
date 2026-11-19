.. role:: verilog(code)
   :language: Verilog

锁存器单元
----------


单元类型 `$_DLATCH_N_` 和 `$_DLATCH_P_` 表示 D 型锁存器。

.. table:: 基本锁存器的单元类型

   ======================================= =============
   Verilog                                 单元类型
   ======================================= =============
   :verilog:`always @* if (!E) Q <= D`     `$_DLATCH_N_`
   :verilog:`always @* if (E)  Q <= D`     `$_DLATCH_P_`
   ======================================= =============

单元类型 ``$_DLATCH_[NP][NP][01]_`` 实现带复位的 D 型锁存器。这些单元类型在
表中的取值对应下面的 Verilog 代码模板：

.. code-block:: verilog
   :force:

   always @*
      if (R == RST_LVL)
         Q <= RST_VAL;
      else if (E == EN_LVL)
         Q <= D;

.. table:: 门级逻辑网络的单元类型（带复位的锁存器）
   :name: tab:CellLib_gates_adlatch

   ============= ============== ============== ===============
   :math:`EnLvl` :math:`RstLvl` :math:`RstVal` 单元类型
   ============= ============== ============== ===============
   ``0``         ``0``          ``0``          `$_DLATCH_NN0_`
   ``0``         ``0``          ``1``          `$_DLATCH_NN1_`
   ``0``         ``1``          ``0``          `$_DLATCH_NP0_`
   ``0``         ``1``          ``1``          `$_DLATCH_NP1_`
   ``1``         ``0``          ``0``          `$_DLATCH_PN0_`
   ``1``         ``0``          ``1``          `$_DLATCH_PN1_`
   ``1``         ``1``          ``0``          `$_DLATCH_PP0_`
   ``1``         ``1``          ``1``          `$_DLATCH_PP1_`
   ============= ============== ============== ===============

单元类型 ``$_DLATCHSR_[NP][NP][NP]_`` 实现带置位和复位的 D 型锁存器。这些单元
类型在表中的取值对应下面的 Verilog 代码模板：

.. code-block:: verilog
   :force:

   always @*
      if (R == RST_LVL)
         Q <= 0;
      else if (S == SET_LVL)
         Q <= 1;
      else if (E == EN_LVL)
         Q <= D;

.. table:: 门级逻辑网络的单元类型（带置位和复位的锁存器）
   :name: tab:CellLib_gates_dlatchsr

   ============= ============== ============== =================
   :math:`EnLvl` :math:`SetLvl` :math:`RstLvl` 单元类型
   ============= ============== ============== =================
   ``0``         ``0``          ``0``          `$_DLATCHSR_NNN_`
   ``0``         ``0``          ``1``          `$_DLATCHSR_NNP_`
   ``0``         ``1``          ``0``          `$_DLATCHSR_NPN_`
   ``0``         ``1``          ``1``          `$_DLATCHSR_NPP_`
   ``1``         ``0``          ``0``          `$_DLATCHSR_PNN_`
   ``1``         ``0``          ``1``          `$_DLATCHSR_PNP_`
   ``1``         ``1``          ``0``          `$_DLATCHSR_PPN_`
   ``1``         ``1``          ``1``          `$_DLATCHSR_PPP_`
   ============= ============== ============== =================

单元类型 ``$_SR_[NP][NP]_`` 实现 SR 型锁存器。这些单元类型在表中的取值对应
下面的 Verilog 代码模板：

.. code-block:: verilog
   :force:

   always @*
      if (R == RST_LVL)
         Q <= 0;
      else if (S == SET_LVL)
         Q <= 1;

.. table:: 门级逻辑网络的单元类型（SR 锁存器）
   :name: tab:CellLib_gates_sr

   ============== ============== ==========
   :math:`SetLvl` :math:`RstLvl` 单元类型
   ============== ============== ==========
   ``0``          ``0``          `$_SR_NN_`
   ``0``          ``1``          `$_SR_NP_`
   ``1``          ``0``          `$_SR_PN_`
   ``1``          ``1``          `$_SR_PP_`
   ============== ============== ==========

.. autocellgroup:: reg_latch
   :members:
   :source:
   :linenos:
