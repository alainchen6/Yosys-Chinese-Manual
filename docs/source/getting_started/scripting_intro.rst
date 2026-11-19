在 Yosys 中编写脚本
-------------------


上一页我们走读了一个综合脚本，在交互式 Yosys shell 中逐条运行了其中的命令。
本页将介绍脚本文件格式，以及如何编写你自己的综合脚本。

Yosys 脚本文件通常使用 :file:`.ys` 扩展名，其中包含一组供 Yosys 按顺序执行的
命令。这些命令与上一页使用的命令相同，例如 `read_verilog` 和 `hierarchy`。

脚本解析
~~~~~~~~


与交互式 shell 一样，每条命令由命令名和可选的、以空白分隔的参数列表组成。
命令以换行符结束，井号 ``#`` 之后的任何内容都是注释（即会被忽略）。

也可以用分号 ``;`` 结束命令。当与 ``-p <command>`` 命令行选项配合使用时，这
一点尤其有用，其中 ``<command>`` 可以是一个包含多条命令、用分号分隔的字符串。
还可以用冒号 ``:`` 写行内注释，注释的结束标志是分号 ``;`` 或换行。

.. code-block::
   :caption: 使用 ``-p`` 选项

   $ yosys -p 'read_verilog fifo.v; :this is a comment; prep'

.. warning::

   分号后的空格是正确解析所必需的。例如，``log a;log b;`` 会输出
   ``a;log b``，而不是你可能预期的 ``a`` 和 ``b``。

Yosys 脚本中还可以使用的另一个特殊字符是感叹号 ``!``。感叹号之后的任何内容
都会作为 shell 命令执行。它只能以换行结束。任何分号、井号或其他特殊字符都会
传递给 shell。如果 shell 返回错误码，Yosys 会将其抛出。`exec` 提供了一种灵活
得多的命令执行方式，可以记录输出，并更好地控制何时产生错误。

.. warning::

   使用 ``yosys -p`` 选项时要小心。bash 等某些 shell 会在双引号字符串内进行
   替换，例如用 ``!`` 进行历史替换、用 ``$`` 进行变量替换；应改用单引号将
   字符串传给 Yosys，以避免替换。

综合入门脚本
~~~~~~~~~~~~


.. role:: yoscrypt(code)
   :language: yoscrypt

:doc:`/getting_started/example_synth` 中使用的所有图片和控制台输出都是由 Yosys
生成的，所用到的 Yosys 脚本文件位于
:file:`docs/source/code_examples/fifo`。如果你还没有看过，我们现在就来看其中
一些脚本文件。

.. literalinclude:: /code_examples/fifo/fifo.ys
   :language: yoscrypt
   :lineno-match:
   :start-at: echo on
   :end-before: design -reset
   :caption: :file:`fifo.ys` 的一节，用于生成 :ref:`addr_gen_example` 中使用的图片
   :name: fifo-ys

那里的第一条命令 :yoscrypt:`echo on` 使用 `echo` 打开命令回显。我们正是这样
生成 :ref:`hierarchy_output` 的代码清单的。打开命令回显会打印出
``yosys> hierarchy -top addr_gen`` 这一行，使输出看起来与交互式终端相同。
:yoscrypt:`hierarchy -top addr_gen` 当然就是我们正在演示的命令，其中还包括
运行后的输出文本和设计原理图图片。

我们曾在 `synth_ice40` 中接触到 `select`，现在进一步看看它。

.. _select_intro:

选择集简介
^^^^^^^^^^

`select` 命令用于修改和查看所选对象的列表：

.. literalinclude:: /code_examples/fifo/fifo.out
   :language: doscon
   :start-at: yosys> select
   :end-before: yosys> show

当我们调用 :yoscrypt:`select -module addr_gen` 时，我们把当前活动的选择集从
整个设计改为仅 ``addr_gen`` 模块。注意这如何把每条命令开头的 ``yosys`` 变成
``yosys [addr_gen]``。这表明此时运行的任何命令都 *只* 作用于 ``addr_gen``
模块。接着调用 :yoscrypt:`select -list`，会得到 ``addr_gen`` 模块中所有对象
的列表，包括模块本身，以及所有信号线、输入、输出、过程和单元。

接下来我们执行另一个选择：:yoscrypt:`select t:*`。其中 ``t:`` 部分表示按
*单元类型* 匹配，而 ``*`` 表示匹配任何内容。对于这个（非常简单的）选择，我们
试图找出所有单元，而不管它们的类型。当前活动选择集现在显示为
``[addr_gen]*``，表示这是 ``addr_gen`` 模块的某个子选择集。这样我们得到了
`$add` 和 `$eq` 单元，也就是我们想在 :ref:`addr_gen_hier` 图片中高亮的单元。

.. _select_new_cells:

我们可以用 :yoscrypt:`select -set` 给选择集命名。在我们的例子中，使用名字
``new_cells``，并告诉它使用当前选择集，即 ``%`` 符号所表示的选择集。之后
就可以通过 ``@new_cells`` 引用这个命名选择集，我们稍后会看到。然后我们清空
选择集，以便后续命令能在整个设计上操作。虽然本文档中我们把它拆了出来，但也
可以用一行完成：:yoscrypt:`select -set new_cells addr_gen/t:*`。如果我们知道
设计中只有一个模块，甚至可以省略 ``addr_gen/`` 部分。继续往下看
:ref:`fifo.ys 代码 <fifo-ys>`，可以看到
:yoscrypt:`select -set new_cells t:$mux t:*dff`。从这条命令还可以看到，选择集
不必局限于单条语句。

许多命令还支持可选的 ``[selection]`` 参数，用于覆盖当前选中的对象。例如，我们
可以调用 :yoscrypt:`clean addr_gen`，让 `clean` *只* 作用于 ``addr_gen`` 模块。

关于 select 框架的详细文档，可以在
:doc:`/using_yosys/more_scripting/selections` 中找到，或者查阅命令参考中的
:cmd:title:`select`。

.. _show_intro:

显示原理图
^^^^^^^^^^

虽然 `select` 命令非常有用，但有时亲眼看到设计本身是无可替代的。这就是 `show`
的用武之地。请注意，本文档只是 `show` 命令的简介，仅涵盖基础知识。更多信息，
包括不同符号含义的指南，请参阅 :ref:`interactive_show` 和
:doc:`/using_yosys/more_scripting/interactive_investigation` 页面。

.. figure:: /_images/code_examples/fifo/addr_gen_show.svg
   :class: width-helper invert-helper
   :name: addr_gen_show

   在 `hierarchy` 之后调用 :yoscrypt:`show addr_gen`

.. note::

   `show` 命令需要已安装可用的 `GraphViz`_ 和 `xdot`_ 才能显示实际的电路图。

.. _GraphViz: http://www.graphviz.org/
.. _xdot: https://github.com/jrfonseca/xdot.py

这是我们在 :file:`fifo.ys` 中调用的第一条 :yoscrypt:`show` 命令，
:ref:`如上面所见 <fifo-ys>`。如果查看这张图片对应的日志输出，会看到以下内容：

.. literalinclude:: /code_examples/fifo/fifo.out
   :language: doscon
   :start-at: -prefix addr_gen_show
   :end-before: yosys> show

用 :yoscrypt:`-format dot` 调用 `show`，表示我们希望输出 :file:`.dot` 文件，
而不是打开它来显示。:yoscrypt:`-prefix addr_gen_show` 选项表示希望文件名为
:file:`addr_gen_show.{*}`。记住，我们在 :file:`fifo.ys` 中这样做，是因为需要把
图片保存下来，用于你正在阅读的文档。但如果你只想在本地显示图片，可以跳过这
两个选项。``-format`` 选项内部会调用 GraphViz 的 ``dot`` 命令行程序，以转换成
:file:`.dot` 之外的其他格式。有关可用格式的更多信息，请查阅
`GraphViz output docs`_。

.. _GraphViz output docs: https://graphviz.org/docs/outputs/

.. note::

   如果你使用的是基于 POSIX 的 Yosys 版本（例如 Mac 或 Linux 版），xdot 会在
   后台打开，Yosys 可以继续使用。如果它仍然开着，之后调用 :yoscrypt:`show` 时
   会复用同一个 xdot 实例。

末尾的 ``addr_gen`` 表示我们只需要 ``addr_gen`` 模块，就像在
:ref:`select_intro` 中调用 :yoscrypt:`select -module addr_gen` 一样。最后一个
参数不必是模块名，它可以是任何有效的选择字符串。还记得我们
:ref:`给选择集命名<select_new_cells>` 并把它称为 ``new_cells`` 吗？我们在
:yoscrypt:`select -list` 的输出中看到它包含两个单元：一个 `$add` 和一个 `$eq`。
我们同样可以对那个选择集调用 `show`：

.. figure:: /_images/code_examples/fifo/new_cells_show.svg
   :class: width-helper invert-helper
   :name: new_cells_show

   调用 :yoscrypt:`show -notitle @new_cells`

如果没有命名选择集，我们也可以用 :yoscrypt:`show -notitle t:$add t:$eq` 得到
相同的输出。在那里加上 :yoscrypt:`-notitle` 标志，还可以去掉原本会自动添加的
``addr_gen`` 标题。最后两张图片都是为本简介添加的。下一张图片是我们在
:doc:`/getting_started/example_synth` 中看到的第一张图：显示完整的 ``addr_gen``
模块，同时高亮 ``@new_cells`` 和两个 ``PROC`` 块。为了实现这种高亮，我们使用
了 :yoscrypt:`-color` 选项：

.. figure:: /_images/code_examples/fifo/addr_gen_hier.svg
   :class: width-helper invert-helper

   调用 :yoscrypt:`show -color maroon3 @new_cells -color cornflowerblue p:* -notitle`

如 `show` 的 `help` 输出所述（或点击 `show` 链接），颜色以
:yoscrypt:`-color <color> <object>` 的形式指定。``<color>`` 部分的颜色名可在
`GraphViz color docs`_ 中找到。与可以接受任何选择字符串的最后一个 `show` 参数
不同，``<object>`` 部分必须是单个选择表达式或命名选择集。这意味着我们可以使用
``@new_cells``，但不能使用 ``t:$eq t:$add``。一般来说，如果命令将
``[selection]`` 列为最后一个参数，它可以是任何选择字符串。任何不是最后一个参数
的选择（例如选项中使用的选择）则必须是单个表达式。

.. _GraphViz color docs: https://graphviz.org/doc/info/colors

关于 `show` 的所有可用选项，请查阅命令参考中的 :cmd:title:`show`。

.. seealso:: :ref:`interactive_show`，见
   :doc:`/using_yosys/more_scripting/interactive_investigation` 页面。
