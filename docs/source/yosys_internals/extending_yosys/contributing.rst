为 Yosys 贡献
=============


LLM 的使用
----------


在我们制定关于 Yosys 中 LLM 使用的完整政策之前，我们有一个
`YosysHQ 临时 LLM 政策
<https://blog.yosyshq.com/p/interim-yosyshq-llm-policy/>`_。作为一般规则：
请勿向我们 GitHub 项目提交包含 LLM 生成代码的拉取请求。

报告 bug
--------


报告得越好的 bug，我们修复得越快。好的 bug 报告是 `issue tracker`_ 上的
一个 issue，并包含以下信息：

.. _`issue tracker`: https://github.com/YosysHQ/yosys/issues

标题
~~~~


简要描述问题，例如：

   对含未定义输入的宽 mux 执行 techmap 时在 synth_xilinx 期间报错

+ 说明发生了什么（“报错”）
+ 给出受影响的命令（`techmap`）
+ 概述输入设计（“含未定义输入的宽 mux”）
+ 以及发现该问题时的上下文（“在 `synth_xilinx` 期间”）


复现步骤
~~~~~~~~


复现步骤应当是一个最小、完整且可验证的示例（`MVCE`_）。
在 bug 报告中提供 MVCE 会大幅提高他人能够帮助解决你的问题的可能性。
请确保你的报告输入不存在 `check` 命令报告的任何问题。
最小化设计的一种方法是使用 `bugpoint` 命令。
你可以在 :doc:`bugpoint 使用指南 </using_yosys/bugpoint>` 中了解更多。

理想情况下，复现步骤是一个代码块（以三个反引号开始和结束），其中包含
最小化后的设计（Verilog 或 RTLIL），随后是一个代码块，其中包含最小化后
的 yosys 脚本，或者是以代码格式（以单个反引号开始和结束）给出的 yosys
命令行调用。

.. code-block:: markdown

   min.v
   ```verilog
   // minimized Verilog design
   ```

   min.ys
   ```
   read_verilog min.v
   # minimum sequence of commands to reproduce error
   ```

   OR

   `yosys -p ': minimum sequence of commands;' min.v`


或者，你也可以提供单个代码块，其中以“here document”的形式包含最小化后
的设计，随后是复现该错误的命令序列：

.. code-block:: markdown

   ```
   read_rtlil <<EOF
   # minimized RTLIL design
   EOF
   # minimum sequence of commands
   ```


.. seealso:: 关于 heredoc 的更多用法，参见 :doc:`/using_yosys/more_scripting/load_design`。

不要忘记说明：

- 任何重要的环境变量或命令行选项
- 如果问题只在某个取值/设计范围内出现，该范围是什么
- 如果你使用外部工具（例如 ``valgrind``）来发现问题，说明所用工具的版本
  以及传给它的选项

.. warning::

   如果外部插件/工具与所报告的问题没有直接关系，请尽量不要在复现步骤中
   使用它们。这包括 GHDL 或 slang 这类前端插件；请改为对最小化后的设计
   使用 `write_rtlil`。这也包括 OpenLane 这类为 Yosys 提供封装层的工具；
   你应当把输入和复现步骤缩减到只涉及 Yosys 的部分。

.. _MVCE: https://stackoverflow.com/help/minimal-reproducible-example
.. _how-to guide for bugpoint: https://yosys.readthedocs.io/en/latest/using_yosys/bugpoint.html

预期行为
~~~~~~~~


描述如果 bug 已修复，我们按复现步骤操作时你期望看到的结果。

如果你有类似的设计/脚本不会触发该错误，请把它作为参考附在这里。如果
bug 是某个错误*本应*被报出却没有报出，请注明是否还有其他命令会给出类似
的错误信息。


实际行为
~~~~~~~~


描述你按复现步骤操作时实际看到的现象。

这可以包括：

* 任何错误信息
* 用 ``--trace`` 或 ``--debug`` 标志发现的与崩溃相关的任何细节
* 触发 bug 的那部分源代码

  * 如果可能，请使用 GitHub 上源代码的永久链接
  * 你可以浏览某个提交对应的源代码仓库，打开源文件，选中相关行（点击
    第一个相关行的行号，然后按住 shift 点击最后一个相关行的行号），点击
    出现的 ``...`` 并选择“Copy permalink”
  * 看起来应当类似
    ``https://github.com/YosysHQ/yosys/blob/<commit_hash>/path/to/file#L139-L147``
  * 点击“Preview”后应显示一个代码块，其中包含所指定的源代码行，并带有
    指向该提交下源文件的链接


补充细节
~~~~~~~~


任何你认为在验证或修复该 bug 时可能有帮助或相关的其他信息。

创建 issue 之后，任何补充细节都可以作为该 issue 的评论添加。你可以补充
说明你第一次遇到该 bug 时正在做什么。

如果这个 issue 是通过 fuzzer 发现的，务必注明这一点。
如果你已经最小化了脚本，可以考虑附上你使用的 `bugpoint` 脚本或原始脚本，
例如：

.. code-block:: markdown

   Minimized with
   ```
   read_verilog design.v
   # original sequence of commands prior to error
   bugpoint -script <failure.ys> -grep "<string>"
   write_rtlil min.il
   ```

   OR

   Minimized from
   `yosys -p ': original sequence of commands to produce error;' design.v`


如果可能，分享原始未最小化的设计也可能有帮助。
如果设计太大，无法放在评论中，可以考虑把它做成 `Gist`_。

.. _Gist: https://gist.github.com/

贡献代码
--------


重要的代码
~~~~~~~~~~


如果你要添加复杂功能，或修改 yosys 的核心部分，我们强烈建议你先在
`Discourse forum`_ 上讨论你的动机和方法。在解释你所构建内容的动机时，
请尽量明确、具体。此外，如果在动手写 C++ 之前先在论坛上讨论，你也许
一行代码都不用写就能解决问题！

评估 PR 时，我们依据相关性、优先级和质量，先看描述，再看代码。

在构建或修复某项内容之前，也请先搜索已有的 `issues`_。

我们有公开的 `developer 'jour fixe' (Dev JF) meetings`_，YosysHQ 和社区的
开发者会在那里一起讨论未解决的 issue 和 PR。这也是与我们讨论如何实现
较大 PR 的好地方。

.. _`developer 'jour fixe' (Dev JF) meetings`: https://docs.google.com/document/d/1SapA6QAsJcsgwsdKJDgnGR2mr97pJjV4eeXg_TVJhRU/edit?usp=sharing
.. _`Discourse forum`: https://yosyshq.discourse.group/
.. _`issues`: https://github.com/YosysHQ/yosys/issues

让代码清晰易懂
~~~~~~~~~~~~~~


只要投入足够的精力，任何代码的行为都能被弄懂到任意程度。但代码作者显然
最有条件让这件事尽可能容易。

Yosys 是一个历史悠久的项目，积累了大量 C 风格的代码，这些代码不是为了让
别人读而写的，只是为了运行。有机会时我们会一点点改进，但现状就是如此。
新增代码则应当干净得多。

应当清楚地描述所改动代码的目的和行为。你的改动应当恰好包含与该描述相符
的内容。这意味着：

* 不多不少——没有死代码，没有未记录在文档中的特性
* 不缺内容——如果某个东西只做了一半，那没问题，但你必须说清楚。例如，
  有些 pass（处理流程）只支持部分类型的单元

以下一些软件工程方法会有帮助：

* 用抽象来建模问题并隐藏细节

  * 尽量使用类型（用结构体而不是零散的变量），不一定非要以面向对象的
    方式
  * 使用函数、作用域、类型别名

* 在新的 pass 中，确保用连贯的注释说明其工作方式及原因的逻辑，并确保
  变量和类型命名与你描述中使用的术语一致。
* 实现的逻辑应当用数学或算法理论的术语来描述。正确性、终止性、计算
  复杂度。如果你是在为逻辑综合或图遍历等重新实现经典数据结构，要讲清楚。

* Yosys 中有多种用 use-def 索引遍历设计的方式（用于获取驱动源和被驱动
  信号）。它们各有优点，有时也有缺点。尽量不要重新实现这些
* 优先使用引用而不是指针，优先使用智能指针而不是裸指针
* 积极去重。函数内、pass 内、跨 pass，甚至与已有代码之间
* 优先把东西声明为 ``const``
* 优先使用基于范围的 for 循环而不是 C 风格循环

常见错误
~~~~~~~~


* 删除设计对象会使迭代器失效。请延迟删除，或持有一份指向设计对象的
  指针列表副本
* 删除信号线容易出问题，而且按设计只应由 ``opt_clean`` pass 来完成，所以
  不要自己删
* 遍历整个设计并检查对象是否被选中，比使用 ``selected_*`` 方法效率更低
* 如果修改模块接口，记得在最后调用 ``fixup_ports``

测试你的改动
~~~~~~~~~~~~


未经测试的代码无法维护。代码库层面不可避免的改动很可能会破坏任何未测试
的部分。测试还能帮助审查者了解代码改动在实际中的目的。

你的代码需要附带测试。如果是特性，测试应覆盖新增行为的代表性示例。如果
是 bug 修复，测试应能复现原来那个孤立的 bug。但在某些情况下，添加测试
并不可行。如果你无法提供测试，请说明这一决定。

对于更重要的代码改动（例如涉及 yosys 核心或更偏算法的改动）的内部，
优先用单元测试（:file:`tests/unit`）来做隔离测试。

测试套件的其余部分主要是在各种 Yosys 和 Tcl 脚本上运行 Yosys，这些脚本
会手工调用 Yosys 命令。关于我们测试套件的组织结构，参见
:doc:`/yosys_internals/extending_yosys/test_suites`。
编写测试的基本方法是在
:doc:`/using_yosys/more_scripting/selections` 中用 ``-assert-count``
检查某类对象或模式是否存在。

通常最好用 ``equiv_opt -assert`` 或类似的等价性检查，来证明被修改的 pass
对设计所做的改动保持等价。但有些代码本来就不打算保持等价。对于较大的
输入，证明等价有时会耗时长得不切实际。还要注意，``equiv_`` 系列的 pass
有些古怪，在特殊情况下甚至可能给出不正确的结果。

.. Changes to core parts of Yosys or passes that are included in synthesis flows
.. can change runtime and memory usage - for the better or for worse. This strongly
.. depends on the design involved. Such risky changes should then be benchmarked
.. with various designs.

.. TODO Emil benchmarking

编码风格
~~~~~~~~


Yosys 使用 C++20 编写。

一般情况下 Yosys 使用 ``int`` 而不是 ``size_t``。为避免隐式类型转换带来的
编译器警告，请始终使用 ``GetSize(foobar)`` 而不是 ``foobar.size()``。
（``GetSize()`` 定义在 :file:`kernel/yosys.h` 中）

顶层有一个 :file:`.clang-format` 文件用于自动格式化代码。Yosys 代码使用
制表符缩进。一个制表符宽 8 个字符，但尽量不要依赖这一点。语句在下一行
续行时额外缩进两个制表符。行可以任意长。一个好的经验法则是大约在第 150
列处换行。左花括号可以与打开该块的语句（if、switch、for、while、do）
放在同一行或下一行。对于较大的块，尤其是包含空行的块，请把左花括号单独
放一行。看到行尾空白就删掉。

除此之外，请遵循 `Linux Kernel Coding Style`_。

.. _Linux Kernel Coding Style: https://www.kernel.org/doc/Documentation/process/coding-style.rst

拉取请求（PR）
~~~~~~~~~~~~~~


如果你正在开发要加入 Yosys 的内容，或修复某些工作不太正常的地方，请
提交 `pull request (PR)`_。

一个公开的 PR（即使是草稿）会告诉大家你正在处理它，别人就不必再动手。
它也是就进行中的改动征求意见的有效方式。

我们用 `labels`_ 来帮助给 issue 和 PR 分类。如果某个标签看起来与你的工作
相关，请添加它；这也包括以 'status-' 开头的标签。'merge-' 标签由维护者
用来跟踪并沟通哪些 PR 已准备好、哪些还在等待合并；如果你不是维护者，请
不要使用这些标签。

.. _`pull request (PR)`: https://github.com/YosysHQ/yosys/pulls
.. _`labels`: https://github.com/YosysHQ/yosys/labels

Git 风格
~~~~~~~~


我们没有严格的提交信息风格。

一些风格提示：

* 如果你改动了已有代码，就顺便重构并补充文档，但要与功能改动分成不同的
  提交
* 优先使用按合理粒度组织的较小提交。Git 有很多特性，比如 fixup 提交、
  带 autosquash 的交互式 rebase

审查 PR
-------


审查 PR 是外部参与项目贡献的完全正当的方式！

谁来审查？
~~~~~~~~~~


YosysHQ GmbH 是一家以 YosysHQ 开源软件的利益为出发点做决策的公司，由
Yosys 的原作者 Claire Xenia Wolf 联合创立。在公司内部，我们会根据对所涉
主题的专长以及成员的时间安排来分配审查工作。不过，包括审查在内的决策
也有公司外部人员参与贡献。

如果你非常熟悉代码库的某一部分，我们很乐意尊重你的经验，让你来审查 PR。
我们喜欢的正式方式是通过 git 仓库中的 CODEOWNERS 文件。我们对代码所有者
的期望是活跃度和信任。关于活跃度：如果你只对某个 yosys pass 感兴趣，
比如仅限于写论文的那段时间，那么与其承诺做代码所有者、从而在日后各种
意想不到的时刻负责修复问题和审查他人的 PR，不如把精力放在为你提交的 PR
编写好的测试和文档上。如果你在代码库的某个部分产出很多但不是代码所有者，
我们仍然重视你的经验，可能会在 PR 中 @ 你。

事实上，代码所有权的目的是通过移除代码库中无人照管的部分来避免维护者
倦怠。如果你成为代码所有者后不再响应，将来我们可能会在移除方便、维护
代价高昂时决定移除这类代码。明确地把某些东西砍掉，比任由它“慢慢腐坏”
更尊重用户的时间。像 LLVM 或 Linux 这样更大的项目没有这类机制就无法
存续，但 Yosys 要小得多，而且存在一些默认的稳定性预期，我们会在合理
范围内尽量尊重。

.. TODO this deserves its own section elsewhere I think? But it would be distracting elsewhere

有时多位维护者都会添加审查评论。即使在个别时候可能产生分歧，这也被视为
健康的协作。如果已经有人正在审查某个 PR，其他人（甚至非维护者）也可以
本着协作精神留下评论，补充观察和不同视角。

如何审查
~~~~~~~~


首先，阅读上面关于贡献的所有内容。这些是作为审查者应当温和坚持的价值观。
它们按重要性排序，但需要明确的是：描述比代码更重要，描述设计的长篇评论
比零散的评论更重要，等等。

如果某个 PR 描述不清、不完整、测试无法通过，或者作者不再响应，请不要
感到有压力去通过逆向分析代码或替他们修复来接手其工作，除非有充分的理由
这么做。

如果 PR 作者提交了他们自己都没理解的 LLM 输出，他们将无法落实反馈意见。
也请把这考虑在内。我们并不禁止代码库中出现 LLM 代码，我们禁止的是糟糕
的代码。

审查者在审查时可能有不同的沟通风格——有人会做一次彻底的审查，有人则喜欢
先把基础问题过一遍再深入代码。一般来说，PR 可能会经历几轮修改请求和长
时间的讨论，但往往它们已经足够好，可以直接合并。

合并前 CI 必须全部通过。新贡献者的 PR 需要由维护者触发一次 CI 运行，之后
才会占用计算资源。在 GitHub 网页界面上只需点一下。我们在多种平台和编译器
上测试。Sanitizer 构建只在主分支上测试。
