面向开发者的内部命令
--------------------


.. autocmdgroup:: internal
   :members:

编写命令帮助
------------


- 以 `chformal` 为例
- 下面是生成的帮助内容

.. _chformal autocmd:

.. autocmd:: chformal
   :noindex:

``formatted_help()`` 方法
~~~~~~~~~~~~~~~~~~~~~~~~~


- ``PrettyHelp::get_current()``
- ``PrettyHelp::set_group()``

  + 与 ``.. autocmdgroup:: <group>`` 一起使用
  + 可以指定分组并返回 false
  + 如果未设置分组，则会尝试使用 ``source_location``，并根据源文件路径
    指定分组

- 返回值

  + true 表示帮助内容已添加到当前的 ``PrettyHelp``
  + false 表示使用 ``Pass::help()``

- 添加内容

  + 帮助内容是一个由 ``ContentListing`` 节点组成的列表，每个节点都有类型、
    正文，以及自己的子 ``ContentListing`` 节点列表
  + ``PrettyHelp::get_root()`` 返回根 ``ContentListing``（``type="root"``）
  + ``ContentListing::{usage, option, codeblock, paragraph}`` 各自向当前节点
    添加一个 ``ContentListing``，其类型与方法名相同

    * 第一个参数是新节点的正文
    * ``usage`` 显示如何调用命令（即其“签名”）
    * ``paragraph`` 内容会格式化为一段文本，并自动添加换行
    * ``codeblock`` 内容按原样显示，可按需换行；它接受一个可选的
      ``language`` 参数，用于指定 RST 输出中代码语法高亮的语言（使用
      ``yoscrypt`` 可获得 yosys 脚本语法高亮）
    * ``option`` 列出命令的单个选项，通常以短横线（``-``）开头；它接受一个
      可选的第二个参数，用于添加一个段落节点作为描述

  + ``ContentListing::open_usage`` 创建并返回一个新的 usage 节点，可用于
    例如添加特定于命令某种用法的文本/选项
  + ``ContentListing::open_option`` 创建并返回一个新的 option 节点，可用于
    例如向选项的描述中添加多个段落
  + 段落被当作原始 RST 处理，因此可以像直接写在 RST 文件中那样使用行内格式
    和引用

.. literalinclude:: /generated/chformal.cc
   :language: c++
   :start-at: bool formatted_help()
   :end-before: void execute
   :caption: ``ChformalPass::formatted_help()``，出自 :file:`passes/cmds/chformal.cc`

将命令帮助导出为 json
~~~~~~~~~~~~~~~~~~~~~


- `help -dump-cmds-json cmds.json`

  + 为 Yosys 中注册的每条命令生成一个 ``ContentListing``
  + 如果 ``Pass::formatted_help()`` 未实现或返回 false，则尝试解析未格式化的
    ``Pass::help()`` 输出

    * 如果某行以四个空格开头，后跟命令名，再跟一个空格，则该行被解析为
      签名（usage 节点）
    * 如果某行有缩进且以短横线（``-``）开头，则该行被解析为选项
    * 其他内容都被解析为 codeblock，并根据缩进添加到根节点或当前选项

  + 命令名到 ``ContentListing`` 的字典

    * 对根节点中的每个节点递归使用 ``ContentListing::to_json()``
    * 根节点用于确定类定义的源位置
    * 包含在 pass 构造函数中设置的标志（例如由 ``Pass::experimental()``
      设置的 ``experimental_flag``）
    * 还包括标题（``Pass::Pass`` 中的 ``short_help`` 参数）、分组和类名

  + 分组名到该分组中命令列表的字典

- 由 sphinx autodoc 用于生成帮助内容

.. literalinclude:: /generated/cmds.json
   :language: json
   :start-at: "chformal": {
   :end-before: "chparam": {
   :caption: `chformal`，位于生成的 :file:`cmds.json` 中

.. note:: 综合命令脚本会做特殊处理

   如果帮助输出的最后一个块以字符串 `"The following commands are executed
   by this synthesis command:\n"` 开头，那么该代码块的其余部分会格式化为
   ``yoscrypt``（例如 `synth_ice40`）。需要注意的是，如果 ``script()`` 在
   第一个 ``check_label`` *之前* 对任何命令调用了 ``run()``，自动检测就会
   失效，并回退为未格式化的代码（例如 `synth_fabulous`）。

命令行渲染
~~~~~~~~~~


- 如果 ``Pass::formatted_help()`` 返回 true，则调用
  ``PrettyHelp::log_help()``

  + 遍历根节点的子节点并渲染为纯文本
  + 实际上与转换未格式化的 ``Pass::help()`` 文本的过程相反
  + 每行在 80 个字符处换行，同时保持缩进（由 :file:`kernel/log_help.cc` 中
    的 ``MAX_LINE_LEN`` 控制）
  + 每行按空格拆分为单词，如果某个单词以反引号开头并以反引号结尾，这些
    反引号会被去掉

- 如果返回 false，则调用 ``Pass::help()``，后者应直接调用 ``log()`` 来打印
  和格式化帮助文本

  + 如果未重写 ``Pass::help()``，则会显示一条关于缺少帮助的默认消息

.. literalinclude:: /generated/chformal.log
   :lines: 2-

由 autocmd 生成的 RST
~~~~~~~~~~~~~~~~~~~~~


- 下面是 ``autocmd``（:file:`docs/util/cmd_documenter.py` 中的
  ``YosysCmdDocumenter`` 类）为 `chformal` 命令生成的原始 RST 输出
- 标题会渲染为最近一个标题的子标题（参见上方 `chformal autocmd`_ 渲染在
  `编写命令帮助`_ 之下）
- ``.. cmd:def:: <cmd>`` 行会被索引，以便用 ``:cmd:ref:`` 指令进行交叉引用
  （上方的 `chformal autocmd`_ 使用了 ``:noindex:`` 选项，使 `chformal` 仍
  链接到正确位置）

  + ``:title:`` 选项控制鼠标悬停在 `chformal` 链接上时显示的文本

- 带有警告标志（实验性或内部）的命令会在所有帮助内容之前添加一个
  ``.. warning`` 块
- 如果命令没有 ``source_location``，则底部的 ``.. note`` 会改为链接到
  :doc:`/cmd/index_other`

.. autocmd_rst:: chformal
