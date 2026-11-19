最小化失败（或有缺陷）的设计
============================


.. TODO:: 等待 https://github.com/YosysHQ/yosys/pull/5068 合并

本文是一份操作指南，介绍如何将有问题的设计缩减到复现该问题所需的绝对最小规模。
它是 Stack Overflow 文章 `How to create a Minimal, Reproducible Example`_ 的 Yosys 专用替代方案，
适用于你的设计或 Yosys 本身出现问题的情况。

.. _How to create a Minimal, Reproducible Example: https://stackoverflow.com/help/minimal-reproducible-example

.. note::

   本指南假定你对 Yosys 有中等程度的熟悉，并且需要一定的解决问题的能力。


开始之前
--------


第一步（而且常常被忽视）是检查并 *阅读* 所有错误消息或警告。运行 Yosys 时传入
``-q`` 标志，就只会把警告和错误消息写入控制台。也不要只看最后一条消息，有些
警告会在问题发生之前就指出它。有些情况可能只被视为警告，例如同一信号存在多个
驱动源或存在逻辑环路，但它们在某些综合流程中会造成问题，在另一些流程中则不会。

Yosys 错误（以 ``ERROR:`` 开头的错误）可能会给出设计中的行号，或导致问题的对象
名称。如果是这样，你可能已经有足够的信息来解决问题，或者至少理解问题为什么会
发生。

.. note::

   如果还没有这样做，请尝试使用 `Yosys GitHub`_ 上的最新版本。你可能会发现
   问题已经修复了！即使没有，用两个不同版本进行测试也是确保可复现性的好方法。

.. _Yosys GitHub: https://github.com/YosysHQ/yosys

另一点需要注意的是，Yosys 通常不会对输入设计做严格检查以确保其有效。
`read_verilog` 前端尤其如此。建议你先用 `iverilog`_ 或 `verilator`_ 加载它，
因为无效的设计往往会导致意想不到的问题。

.. _iverilog: https://steveicarus.github.io/iverilog/
.. _verilator: https://www.veripool.org/verilator/

如果你使用的是自定义综合脚本，花点时间找出是哪个命令失败。在脚本开头调用
``echo on`` 会 `echo` 每条执行的命令；那么错误之前的最后一条 echo 就应该来自
错误发生的位置。查看失败命令的帮助消息；它是否表明支持有限，或者提到需要先
运行其他某个命令？你也可以在失败之前尝试调用 `check` 和/或 ``hierarchy -check``，
看看它们是否报告错误或警告。


用 bugpoint 最小化 RTLIL 设计
-----------------------------


Yosys 提供 `bugpoint` 命令，用于将失败的设计缩减为仍会导致失败的该设计的最小
部分。`bugpoint` 最初是为 Yosys 崩溃开发的，但也可用于会导致非致命错误的设计，
甚至用于使用 Yosys 脚本输出的其他工具中出现失败的情况。

.. note::

   在做出任何修改之前，务必备份你的代码（设计源码和 yosys 脚本）。即使代码
   本身并不重要，这也有助于避免在调试过程中“丢失”该错误。

我可以使用 bugpoint 吗？
~~~~~~~~~~~~~~~~~~~~~~~~


首先要注意的是，`bugpoint` 并非在 Yosys 的每个构建中都可用。由于该命令通过
调用外部进程来工作，它要求 Yosys 能够启动可执行文件。特别地，这意味着
`bugpoint` 无法在 WebAssembly 构建中使用，例如通过 YoWASP 提供的构建。检查你的
Yosys 构建最简单的方法是运行 ``yosys -h bugpoint``。如果 Yosys 显示了
`bugpoint` 的帮助文本，那么它就可以使用。

.. code-block:: console
   :caption: `bugpoint` 不可用

   $ yosys -h bugpoint

   -- Running command `help bugpoint' --
   No such command or cell type: bugpoint

接下来，你需要把加载设计与失败点分开；你的目标应当是通过运行
``yosys -s <load.ys> -s <failure.ys>`` 来复现失败。如果失败发生在加载设计时，
例如在 `read_verilog` 期间，你就需要自己最小化输入设计。请参阅下文
:ref:`using_yosys/bugpoint:最小化 verilog 设计` 的说明。

.. note::

   你也应该能够分别运行这两个脚本：先调用
   ``yosys -s <load.ys> -p 'write_rtlil design.il'``，然后调用
   ``yosys -s <failure.ys> design.il``。如果这样不行，可能意味着该失败无法从
   RTLIL 复现，那么 `bugpoint` 也无法工作。

这里所说的失败点，并不只是指 Yosys 中的崩溃或错误。``<failure.ys>`` 脚本也可以
是用户定义的失败，例如带某个 ``-assert-*`` 选项的 `select` 命令；一个可能用到
这种失败的情形是：某个 pass 本应移除某类单元，但存在某种边界情况导致该单元未
被移除。另一个用例是：最小化一个用 `equiv_opt` 命令会失败的设计，这暗示所讨论的
优化以某种方式改变了电路。

甚至可以将 `bugpoint` 用于 Yosys *外部* 的失败，方法是使用 ``<failure.ys>`` 中的
`exec` 命令。当 Yosys 输出无效设计，或某个其他工具与该设计不兼容时，这尤其
有用。务必使用 ``exec -expect-*`` 选项，以便正确检测通过/失败。可以多次调用
`exec`，甚至可以使用完整的 shell 脚本：

.. code-block:: yoscrypt

   exec -expect-return 1 --bash <script.sh>

最后一种可用于 `bugpoint` 的失败，是包装进程（wrapper process）返回的失败，例如
``valgrind`` 或 ``timeout``。在这种情况下，你调用的会是类似
``<wrapper> yosys -s <failure.ys> design.il`` 的东西。这里 Yosys 运行在一个包装
进程之下，该进程会检查某种失败状态，例如内存泄漏或运行时间过长。


我如何使用 bugpoint？
~~~~~~~~~~~~~~~~~~~~~


此时你应当已经具备：

1. 包含待最小化设计的 RTLIL 文件（本文称为 ``design.il``），或者用于加载它的
   Yosys 脚本 ``<load.ys>``；以及
2. 产生该失败并返回非零返回状态的 Yosys 脚本 ``<failure.ys>``。

现在运行 ``yosys -qq -s <failure.ys> design.il``，并记下打印出来的错误。这里
提供了一个模板脚本 ``<bugpoint.ys>`` 供你使用。务必用正确的文件名配置它，并且
只使用其中一种加载设计的方法。在 ``-grep`` 选项中填入刚刚打印的错误消息。如果
你使用包装进程来表示失败状态，请在 `bugpoint` 调用中加入
``-runner "<wrapper>"`` 选项。

.. code-block:: yoscrypt
   :caption: ``<bugpoint.ys>`` 模板脚本

   # Load design
   read_rtlil design.il
   ## OR
   script <load.ys>

   # Call bugpoint with failure
   bugpoint -script <failure.ys> -grep "<string>"

   # Save minimized design
   write_rtlil min.il

``-grep`` 选项用于搜索被测 Yosys 生成的日志文件。如果错误消息是由其他东西生成
的，例如包装进程或编译器 sanitizer，那么你应当改用 ``-err_grep``。对于操作系统
错误，例如 SEGFAULT，你也可以使用 ``-expect-return`` 来检查返回的错误码。

.. note::

   检查错误消息或返回状态是可选的，但强烈建议这样做。`bugpoint` 很容易通过
   创建命令本不打算处理的畸形设计而引入错误。如果有了某种检查错误的方法，
   `bugpoint` 就能确保复现的是 *正确的* 错误。当 ``<failure.ys>`` 包含多个命令时，
   这一点更为重要。

默认情况下，`bugpoint` 可以移除设计的任何部分。如果希望保留某些部分，例如因为
你已经知道它们与失败有关，可以使用 ``bugpoint_keep`` 属性。可以在 Verilog 中用
``(* bugpoint_keep *)``，在 RTLIL 中用 ``attribute \bugpoint_keep 1``，或在 Yosys
脚本中用 ``setattr -set bugpoint_keep 1 [selection]`` 来实现。也可以限制
`bugpoint` 只移除某些 *种类* 的对象，例如只移除整个模块或单元（模块的实例）。
关于可用选项的更多信息，请查看 ``help bugpoint`` 或 :cmd:title:`bugpoint`。

在某些情况下，在 `bugpoint` 之前使用 `setenv` 为所启动的进程设置环境变量也可能
有帮助。一个例子是 ``setenv UBSAN_OPTIONS halt_on_error=1``，用于你试图在未定义
行为上触发错误、但只希望子进程在出错时停止的场景。

.. note::

   以这种方式使用 `setenv` 可能影响也可能不影响当前进程。例如这里的
   ``UBSAN_OPTIONS halt_on_error`` 只影响子进程，:doc:`Yosys 环境变量</appendix/env_vars>`
   ``ABC`` 也是如此，因为它们只在启动时读取。而其他变量，例如
   ``YOSYS_NOVERIFIC`` 和 ``HOME``，则每次使用时都会求值。

完成配置后，你现在可以运行 ``yosys <bugpoint.ys>``。`bugpoint` 做的第一件事是
测试输入设计是否会失败。如果它没有失败，请确认你使用的是正确的 ``yosys``
可执行文件；除非提供了 ``-yosys`` 选项，否则它会使用 shell 默认的那个，而 *不是*
当前的 ``yosys``。如果你使用了 ``-runner`` 选项，可以尝试把 `bugpoint` 命令换成
``write_rtlil test.il``，然后在下一行写
``!<wrapper> yosys -s <failure.ys> test.il``，以检查它是否按预期工作并返回非零
状态。

.. seealso::

   关于脚本解析以及 ``!`` 用法的更多内容，请参阅
   :ref:`getting_started/scripting_intro:脚本解析`。

取决于设计的大小以及 ``<failure.ys>`` 的长度，`bugpoint` 可能需要一些时间；
记住，它会在设计的每次迭代中运行 ``yosys -s <failure.ys>``。设计越大，迭代次数
越多。``<failure.ys>`` 越长，每次迭代耗时越久。随着设计缩减、`bugpoint` 收敛，
每次迭代的耗时应当越来越少。当所有化简都已用尽、不再有可移除的对象时，脚本会
继续执行，最小化后的设计就可以保存了。


如何处理最小化后的设计？
~~~~~~~~~~~~~~~~~~~~~~~~


首先，检查最小化后的设计是否仍然失败。如果你没有用 `write_rtlil` 输出最小化
设计，这一点尤其重要。例如，如果你运行了下面的 :ref:`bugpoint_script`，那么
调用 ``yosys -s <failure.ys> min.v`` 应当仍以同样的方式失败。

.. code-block:: yoscrypt
   :caption: 示例 `bugpoint` 最小化器
   :name: bugpoint_script

   read_verilog design.v
   bugpoint -script <failure.ys>
   write_verilog min.v

`write_rtlil` 命令通常更可靠，因为 `bugpoint` 已经让那段确切的代码跑过了失败的
脚本。其他 ``write_*`` 命令会从 RTLIL 转换出去，然后在 ``read_*`` 时再转换回来，
这可能产生差异，导致设计不再失败。

.. note::

   仅仅用 ``write_*`` 的输出调用 Yosys（如 ``yosys -s <failure.ys> min.v``），
   并不保证会使用对应的 ``read_*``。关于这一点的更多内容，请参阅
   :doc:`/using_yosys/more_scripting/load_design`，或者用
   ``yosys -p 'read_verilog min.v' -s <failure.ys>`` 显式加载设计。

确认失败仍然出现后，请参阅 :ref:`using_yosys/bugpoint:定位问题` 了解
接下来该做什么。


最小化 Verilog 设计
-------------------


.. seealso::

   本节并非 Yosys 专用，因此你尽可使用其他指南，例如 Stack Overflow 的
   `How to create a Minimal, Reproducible Example`_。

务必检查所有错误或警告，看是否有消息能指出可能导致失败的源码行或对象名称，并在
修改源码之前先备份。如果你有多个源文件，应当先把它们缩减为单个文件。如果某个
特定文件读取失败，尝试移除其他所有内容，只关注那一个文件。如果你的源码使用了
``include`` 指令，请用所引用文件的内容替换它。

与可以使用 `bugpoint` 的 RTLIL 设计不同，Yosys 不提供任何用于最小化 Verilog 设计
的工具。你应当改用外部工具，例如 `C-Reduce`_（带 ``--not-c`` 标志）或
`sv-bugpoint`_。

.. _C-Reduce: https://github.com/csmith-project/creduce
.. _sv-bugpoint: https://github.com/antmicro/sv-bugpoint

C-Reduce
~~~~~~~~


简短介绍一下 C-Reduce 的用法：你需要一个会失败的源设计（``test.v``），以及某个用于
检查所调查错误的 shell 脚本（``test.sh``）。下面是一个 :ref:`egtest`，它使用
`logger` 和 ``-expect error "<string>" 1`` 选项来扮演类似 ``bugpoint -grep`` 的
角色，并使用 ``verilator`` 对代码做 lint 检查，确保它仍然有效。

.. code-block:: bash
   :caption: 用于 C-Reduce 的 test.sh 示例
   :name: egtest

   #!/usr/bin/env bash
   verilator --lint-only test.v &&/
   yosys -p 'logger -expect error "unsupported" 1; read_verilog test.v'

.. code-block:: verilog
   :caption: 输入 test.v

   module top(input clk, a, b, c, output x, y, z);
      always @(posedge clk) begin
         if (a == 1'b1)
            $stop;
      end
      assign x = a;
      assign y = a ^ b;
      assign z = c;
   endmodule

在这个例子中，``read_verilog test.v`` 给出的错误消息包含字符串 "unsupported"，
因为 ``$stop`` 系统任务只在 ``initial`` 块中受支持。通过调用
``creduce ./test.sh test.v --not-c``，我们可以把设计最小化到只剩导致失败的代码，
同时仍然是有效的 Verilog。

.. code-block:: verilog
   :caption: 输出 test.v

   module a;
   always begin $stop;
   end endmodule


sv-bugpoint
~~~~~~~~~~~


sv-bugpoint 的用法与 C-Reduce 非常相似，只是它要求提供一个输出目录，并且检查
脚本需要接受目标文件作为输入参数：``sv-bugpoint outDir/ test.sh test.v``

.. code-block:: bash
   :caption: 用于 sv-bugpoint 的 test.sh 示例

   #!/usr/bin/env bash
   verilator --lint-only $1 &&/
   yosys -p "logger -expect error \"unsupported\" 1; read_verilog $1"

注意，``yosys -p`` 的命令现在位于双引号（``"``）中，错误字符串两边的引号被转义了
（``\"``）。这是为了让 ``$1`` 参数替换正确工作所必需的。


手动完成
~~~~~~~~


如果由于某种原因你无法使用工具来最小化代码，你仍然可以手动完成。但这可能是
耗时的过程，需要大量迭代。在过程中的任何时候，你都可以检查是否有任何未使用或
完全未连接的东西（端口、信号线等）并将它们移除。如果某个特定模块导致了问题，
尝试把它设为顶层模块。任何参数都应修改其默认值，以匹配失败时的用法。

作为经验法则，尝试在每一步把东西大致分成两半，类似于“二分查找”。如果你的顶层
模块中有 10 个单元（模块的实例），并且完全不知道是什么导致问题，就把它们分成
两组，每组 5 个单元。对每组单元，尝试移除它们并看看失败是否仍然发生。如果移除
第一组后错误仍然出现，而移除第二组后错误消失，那么第一组就可以安全地移除。
如果某个模块不再有实例，就把它整个移除。对每个剩余的单元组重复此过程，直到每组
只剩 1 个单元，且在不使错误消失的前提下无法再移除任何单元。你也可以对设计中
仍然存在的每个模块重复此过程。

在最小化单元数量之后，对顶层模块中的过程块做同样的处理。然后对任何 generate 块
和组合逻辑块再做一次。记得检查是否有任何不再使用的端口或信号，并把它们也移除。
任何被写入但从未被读取的信号也可以移除。

.. note::

   取决于设计失败的位置，有些命令可能有助于找出设计中未使用的对象。
   `hierarchy` 会指出哪些模块被使用、哪些没有，但在移除未使用的模块之前要检查
   ``$paramod`` 模块。``debug clean`` 会列出每个模块中所有未使用的信号线，以及
   自动生成但未使用的单元（并给出生成它们的源码行号）。加上 ``-purge`` 标志还会
   包括通常被 `clean` 忽略的具名信号线。不过，当存在大量未使用的信号线时，通常
   更容易的做法是直接删除代码的某些部分，看看会发生什么。

接下来，尝试移除或减少赋值（``a = b``）和运算（``a + b``）。一个好的着手点是
检查是否有被读取但从未被写入的信号线/寄存器。尝试删除该信号声明，并把对它的
引用替换为 ``'0`` 或 ``'x``。对任何常量也这样做。尝试把字符串替换为数值，把宽
信号替换为更窄的信号，然后看错误是否仍然存在。

检查是否有可以化简的运算，例如把 ``a & '0`` 替换为 ``'0``。如果你有使能或复位
逻辑，尝试移除它并看看错误是否仍然出现。尝试把 ``if .. else`` 和 ``case`` 块缩减
为单个分支。即使这样不行，你可能仍然可以移除一些路径；从看起来不可达的分支
开始，再逐步推进。

.. note::

   在 `Yosys GitHub`_ 上分享代码时，请尽量让内容保持英文。声明和字符串应只
   使用字母 a-z 和数字 0-9，除非错误正是由所使用的名称/字符引起的。


定位问题
--------


在定位问题时，理解问题发生的条件非常有用。虽然偶尔会有影响大量设计的缺陷，但
Yosys 的改动会在各种设计和操作系统上进行测试，通常能在进入主分支之前发现这类
问题。那么，你的情况究竟有什么特别之处呢？

.. note::

   如果你能访问其他平台，也可以检查你的问题在那里是否可复现。有些问题可能
   特定于平台或 Yosys 的某个构建。

尝试把最小化后的设计放回其原始上下文中。你能用不同的方式实现同样的功能吗？
如果能，这种做法是否也有同样的问题？尝试对设计做小改动并看看会发生什么；虽然
`bugpoint` 可以缩减并化简设计，但它并不会做太多 *改变*。如果改变运算符会发生
什么，例如把左移（或 `$shl`）改为右移（或 `$shr`）？尝试看看问题是否与特定
参数、位宽或数值有关。

搜索 `the existing issues`_，看看是否已经有人提交了缺陷报告。这时，修改设计并
找出导致失败的边界条件就真正派上用场了。如果你更熟悉问题可能如何产生，可能更
容易找到相关 issue。如果针对问题的一种情况已有 issue，但你发现了其他情况，可以
在该 issue 下评论，帮助解决问题。如果还没有现存的或相关的 issue，请查看
:ref:`yosys_internals/extending_yosys/contributing:报告 bug` 的步骤。

.. _the existing issues: https://github.com/YosysHQ/yosys/issues

.. warning::

   如果你使用 fuzzer 来查找缺陷，请遵循
   :doc:`/yosys_internals/extending_yosys/advanced_bugpoint` 中的说明。如果你
   无法确定根本原因，**不要** 同时开启多个由 fuzzer 生成的 issue。如果被发现
   这样做，你的 issue 可能会在未经进一步调查的情况下被关闭。
