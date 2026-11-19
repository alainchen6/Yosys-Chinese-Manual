.. role:: verilog(code)
   :language: Verilog

组合单元（复合）
----------------


这些单元把两个或多个组合单元（简单）组合成一个单元。

.. table:: 门级组合单元（复合）的单元类型

   ======================================= =============
   Verilog                                 单元类型
   ======================================= =============
   :verilog:`Y = A & ~B`                   `$_ANDNOT_`
   :verilog:`Y = A | ~B`                   `$_ORNOT_`
   :verilog:`Y = ~((A & B) | C)`           `$_AOI3_`
   :verilog:`Y = ~((A | B) & C)`           `$_OAI3_`
   :verilog:`Y = ~((A & B) | (C & D))`     `$_AOI4_`
   :verilog:`Y = ~((A | B) & (C | D))`     `$_OAI4_`
   :verilog:`Y = ~(S ? B : A)`             `$_NMUX_`
   （见下文）                              `$_MUX4_`
   （见下文）                              `$_MUX8_`
   （见下文）                              `$_MUX16_`
   ======================================= =============

`$_MUX4_`、`$_MUX8_` 和 `$_MUX16_` 单元用于建模宽多路复用器，对应下面的
Verilog 代码：

.. code-block:: verilog
   :force:

   // $_MUX4_
   assign Y = T ? (S ? D : C) :
                  (S ? B : A);
   // $_MUX8_
   assign Y = U ? T ? (S ? H : G) :
                      (S ? F : E) :
                  T ? (S ? D : C) :
                      (S ? B : A);
   // $_MUX16_
   assign Y = V ? U ? T ? (S ? P : O) :
                          (S ? N : M) :
                      T ? (S ? L : K) :
                          (S ? J : I) :
                  U ? T ? (S ? H : G) :
                          (S ? F : E) :
                      T ? (S ? D : C) :
                          (S ? B : A);

.. autocellgroup:: comb_combined
   :members:
   :source:
   :linenos:
