.. role:: verilog(code)
   :language: Verilog

一元运算符
----------


所有一元 RTL 单元都有一个输入端口 ``A`` 和一个输出端口 ``Y``。它们还具有以下参数：

``A_SIGNED``
   如果输入 ``A`` 是有符号的，因而在需要时应进行符号扩展，则将该参数设为非零值。

``A_WIDTH``
   输入端口 ``A`` 的宽度。

``Y_WIDTH``
   输出端口 ``Y`` 的宽度。

.. table:: 一元运算符的单元类型及其对应的 Verilog 表达式。

   ================== ==============
   Verilog            单元类型
   ================== ==============
   :verilog:`Y =  ~A` `$not`
   :verilog:`Y =  +A` `$pos`
   :verilog:`Y =  -A` `$neg`
   :verilog:`Y =  &A` `$reduce_and`
   :verilog:`Y =  |A` `$reduce_or`
   :verilog:`Y =  ^A` `$reduce_xor`
   :verilog:`Y = ~^A` `$reduce_xnor`
   :verilog:`Y =  |A` `$reduce_bool`
   :verilog:`Y =  !A` `$logic_not`
   ================== ==============

对于输出逻辑值的一元单元（`$reduce_and`、`$reduce_or`、`$reduce_xor`、
`$reduce_xnor`、`$reduce_bool`、`$logic_not`），当 ``Y_WIDTH`` 参数大于 1 时，输出
会进行零扩展，只有最低位会发生变化。

注意，`$reduce_or` 和 `$reduce_bool` 通常表示相同的逻辑函数。但 `read_verilog` 前端
会在不同情况下生成它们。当使用前缀 ``|`` 运算符时会生成 `$reduce_or` 单元；当位向量
在 ``if`` 语句或 ``?:`` 表达式中用作条件时会生成 `$reduce_bool` 单元。

.. autocellgroup:: unary
   :members:
   :source:
   :linenos:
