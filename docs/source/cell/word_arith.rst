粗粒度算术
----------


.. todo:: 补充关于 `$alu`、`$fa`、`$macc_v2` 和 `$lcu` 单元的信息。

`$macc` 单元类型表示广义的乘加运算。该单元是纯组合逻辑。它输出把一串乘积和其他注入的
求和项相加的结果。

.. code-block::

   Y = 0 +- a0factor1 * a0factor2 +- a1factor1 * a1factor2 +- ...
        + B[0] + B[1] + ...

A 端口由成对拼接的乘法器输入（“因子”）组成。长度为零的 factor2 充当常量 1，使
factor1 成为简单的求和项。

在这段伪代码中，``u(foo)`` 表示长度为 foo 位的无符号整数。

.. code-block::

   struct A {
      u(CONFIG.mul_info[0].factor1_len) a0factor1;
      u(CONFIG.mul_info[0].factor2_len) a0factor2;
      u(CONFIG.mul_info[1].factor1_len) a1factor1;
      u(CONFIG.mul_info[1].factor2_len) a1factor2;
      ...
   };


单元的 ``CONFIG`` 参数决定单元端口 ``A`` 的布局。CONFIG 参数携带以下信息：

.. code-block::

   struct CONFIG {
      u4 num_bits;
      struct mul_info {
         bool is_signed;
         bool is_subtract;
         u(num_bits) factor1_len;
         u(num_bits) factor2_len;
      }[num_ports];
   };

B 是一组拼接起来的 1 位宽无符号整数，同样要参与求和。

.. autocellgroup:: arith
   :members:
   :source:
   :linenos:
