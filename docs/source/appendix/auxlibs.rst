辅助库
======


Yosys 源码发行版中包含一些辅助库，它们会被编译进 Yosys，并可在插件中使用。

BigInt
------


``libs/bigint/`` 中的文件提供了一个对任意长度整数进行算术运算的库。
它由 Matt McCutchen 编写。

BigInt 库用于计算常量表达式，例如使用 kernel/consteval.h 中提供的
ConstEval 类。

另见：http://mattmccutchen.net/bigint/

dlfcn-win32
-----------


``dlfcn`` 库支持在运行时加载插件，而无需重新编译 Yosys。``libs/dlfcn-win32``
中的文件提供了 ``dlfcn`` 的 Windows 实现。

另见：https://github.com/dlfcn-win32/dlfcn-win32

ezSAT
-----


``libs/ezsat`` 中的文件提供了一个用于简化生成 SAT 求解器 CNF 公式的库。
它还包含 MiniSAT 的绑定。ezSAT 库由 C. Wolf 编写。它被 `sat` pass（处理流程）
使用。

fst
---


来自 `gtkwave`_ 的 ``libfst`` 文件包含在 ``libs/fst`` 中，用于支持从
GTKWave 开发的 FST 格式读取信号波形以及向该格式写入信号波形。这主要
用于 `sim` 命令。

.. _gtkwave: https://github.com/gtkwave/gtkwave

json11
------


若要从 JSON 读写设计，应使用 `read_json` 和 `write_json`。除此之外还有
`json11 library`_：

   json11 是一个用于 C++11 的微型 JSON 库，提供 JSON 解析和序列化。

这个库用于输出机器可读的统计信息（带 ``-json`` 标志的 `stat`）、使用 RPC
前端（`connect_rpc`），以及 yosys-witness 的 ``yw`` 格式。

.. _json11 library: https://github.com/dropbox/json11

MiniSAT
-------


``libs/minisat`` 中的文件提供了一个高性能 SAT 求解器，供 `sat` 命令使用。

SHA1
----


``libs/sha1/`` 中的文件提供了一个公有领域的 SHA1 实现，由 Steve Reid、
Bruce Guenter 和 Volker Grabsch 编写。它用于在特化参数化模块时生成唯一
名称。

.. _sec:SubCircuit:

SubCircuit
----------


``libs/subcircuit`` 中的文件提供了一个用于求解子电路同构问题的库。它由
C. Wolf 编写，基于 Ullmann 子图同构算法
:cite:p:`UllmannSubgraphIsomorphism`。它被 `extract` pass 使用。
