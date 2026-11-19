.. role:: verilog(code)
   :language: Verilog

二元运算符
~~~~~~~~~~


所有二元 RTL 单元都有两个输入端口 ``A`` 和 ``B`` 以及一个输出端口 ``Y``。它们还具有
以下参数：

``A_SIGNED``
   如果输入 ``A`` 是有符号的，因而在需要时应进行符号扩展，则将该参数设为非零值。

``A_WIDTH``
   输入端口 ``A`` 的宽度。

``B_SIGNED``
   如果输入 ``B`` 是有符号的，因而在需要时应进行符号扩展，则将该参数设为非零值。

``B_WIDTH``
   输入端口 ``B`` 的宽度。

``Y_WIDTH``
   输出端口 ``Y`` 的宽度。

.. table:: 二元运算符的单元类型及其对应的 Verilog 表达式。

   ======================= =============== ======================= ===========
   Verilog                 单元类型        Verilog                 单元类型
   ======================= =============== ======================= ===========
   :verilog:`Y = A  & B`   `$and`          :verilog:`Y = A ** B`   `$pow`
   :verilog:`Y = A  | B`   `$or`           :verilog:`Y = A <  B`   `$lt`
   :verilog:`Y = A  ^ B`   `$xor`          :verilog:`Y = A <= B`   `$le`
   :verilog:`Y = A ~^ B`   `$xnor`         :verilog:`Y = A == B`   `$eq`
   :verilog:`Y = A << B`   `$shl`          :verilog:`Y = A != B`   `$ne`
   :verilog:`Y = A >> B`   `$shr`          :verilog:`Y = A >= B`   `$ge`
   :verilog:`Y = A <<< B`  `$sshl`         :verilog:`Y = A >  B`   `$gt`
   :verilog:`Y = A >>> B`  `$sshr`         :verilog:`Y = A  + B`   `$add`
   :verilog:`Y = A && B`   `$logic_and`    :verilog:`Y = A  - B`   `$sub`
   :verilog:`Y = A || B`   `$logic_or`     :verilog:`Y = A  * B`   `$mul`
   :verilog:`Y = A === B`  `$eqx`          :verilog:`Y = A  / B`   `$div`
   :verilog:`Y = A !== B`  `$nex`          :verilog:`Y = A  % B`   `$mod`
   ``N/A``                 `$shift`        ``N/A``                 `$divfloor`
   ``N/A``                 `$shiftx`       ``N/A``                 `$modfloor`
   ======================= =============== ======================= ===========

`$shl` 和 `$shr` 单元实现逻辑移位，而 `$sshl` 和 `$sshr` 单元实现算术移位。`$shl`
和 `$sshl` 单元实现相同的操作。这四个单元都把第二个操作数解释为无符号数，并要求
``B_SIGNED`` 为零。

还有两个额外的移位运算符单元并不直接对应 Verilog 中的任何运算符：`$shift` 和
`$shiftx`。如果第二个操作数为正（或无符号），`$shift` 单元执行右逻辑移位；如果为负，
则执行左逻辑移位。`$shiftx` 单元执行与 `$shift` 单元相同的操作，但空出的位位置用
undef（x）位填充，并且对应于 Verilog 的索引部分选择（indexed part-select）表达式。

对于输出逻辑值的二元单元（`$logic_and`、`$logic_or`、`$eqx`、`$nex`、`$lt`、
`$le`、`$eq`、`$ne`、`$ge`、`$gt`），当 ``Y_WIDTH`` 参数大于 1 时，输出会进行零扩展，
只有最低位会发生变化。

除法和取模单元提供两种舍入模式。原始的 `$div` 和 `$mod` 单元基于截断除法，对应于
Verilog ``/`` 和 ``%`` 运算符的语义。`$divfloor` 和 `$modfloor` 单元表示向下取整除法
和向下取整取模，后者对应于 Python 中的 ``%`` 运算符。不同语义之间的并列比较见下表。

.. table:: 除法和取模单元不同舍入模式的比较。

   | 除法      | 结果   |          截断         |        向下取整       |

   |           |        | $div      | $mod      | $divfloor | $modfloor |

   | -10 / 3   | -3.3   | -3        |        -1 | -4        |  2        |

   | 10 / -3   | -3.3   | -3        |         1 | -4        | -2        |

   | -10 / -3  |  3.3   |  3        |        -1 |  3        | -1        |

   | 10 / 3    |  3.3   |  3        |         1 |  3        |  1        |


.. autocellgroup:: binary
   :members:
   :source:
   :linenos:
