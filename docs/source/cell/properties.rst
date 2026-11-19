单元属性
--------


.. cell:defprop:: is_evaluable

   这些单元可以与 `eval` 命令配合使用。某些 pass（处理流程），例如 `opt_expr`，也
   可能对可求值的单元执行额外的优化。

.. cell:defprop:: x-aware

   某些 pass（处理流程）会把这些单元当作非 'x' 敏感单元处理。例如，在综合过程中，
   `$eqx` 通常会被当作 `$eq` 处理。

.. cell:defprop:: x-output

   这些单元即使所有输入都有定义，也可能产生 'x' 输出。例如，除数为零（``B``）的
   `$div` 单元输出未定义。

具有给定属性的单元列表请参阅 :ref:`propindex`。
