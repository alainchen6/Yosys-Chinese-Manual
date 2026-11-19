# Yosys 中文文档翻译规范

本仓库是 [Yosys 官方文档](https://yosyshq.readthedocs.io/projects/yosys/en/latest/)
的简体中文翻译。翻译对象是上游 `docs/source` 的 reStructuredText 源文件；
页面结构、主题和导航与官方保持一致。

## 总则

- **忠实**：不增删事实、数字、版本号、限制条件；不把不确定的内容“润色”掉。
- **术语一致**：优先使用下方术语表；同一概念全仓库只用一个译法。
- **RST 结构不动**：只翻译可见文字。所有指令、角色、标签、目标、引用键、
  代码、路径、URL、命令名、参数名、表格边框、图片路径保持原样。
- **简洁的技术书面中文**：避免口语和营销腔；`you` 译为“你”，`we` 译为“我们”。
- **不添加译者注**，不添加“本文由……”之类的话；需要说明的放 README。

## 必须原样保留

1. 代码块、`literalinclude`、`code-block`、`yoscrypt`、`yoterm` 的内容，
   包括缩进和空行。
2. 行内代码（双反引号）里的命令、选项、信号名、文件名、路径、RTLIL 标识符。
3. RST 指令名、选项名，例如 `.. figure::`、`:caption:`、`:name:`、
   `.. toctree::`、`:maxdepth:`。
4. 角色名与目标：`:doc:`、`:ref:`、`:numref:`、`:file:`、`:cmd:`、
   `:cell:`、`autoref` 的反引号内容。只翻译角色的显示文字，不改目标，例如
   `` :doc:`/introduction` `` 保持不变，但 `:doc:` 前面/后面的普通文字要翻译。
5. 交叉引用目标、标签（`.. _label:`）、锚点、引用键（`[ABC]_`、`[@...]`）。
6. 数学公式、表格中的数字、单位、版本号、Git SHA、URL。
7. 图片路径（本仓库已把通配符改成明确扩展名，不要改回 `.*`）。
8. 列表/表格的缩进和空行；不要重排表格列。

## 标题与下划线

- 标题文字翻译成中文。
- 标题下的 `====`、`----`、`~~~~`、`^^^^` 等下划线**长度至少等于标题的字符数**
  （中文一个汉字算一个字符）。可以比标题长，不要短。
- 不确定时复制原下划线并把长度补到标题长度以上。

## 段落和换行

- 按原文段落翻译；普通段落可以按 80–100 字符左右换行，不要求与英文逐行对应。
- 列表项、表格单元格、`.. note::` / `.. warning::` 等 admonition 内部的
  内容同样翻译。
- 保留空行数量的大致结构（两个段落之间一个空行，指令与内容之间一个空行）。

## 术语表

| 英文 | 中文 | 说明 |
|---|---|---|
| synthesis / synthesize | 综合 | |
| pass | pass（处理流程） | Yosys 的 pass 是命令类别；首次出现写“pass（处理流程）”，后文可只用 `pass` |
| cell | 单元 | RTLIL 单元；代码中的 `$add` 等保持 |
| coarse-grain / fine-grain | 粗粒度 / 细粒度 | |
| RTLIL | RTLIL | 不翻译 |
| netlist | 网表 | |
| net | 网络 | 电气网络 |
| wire | 信号线 | RTLIL 的 wire 是信号线，不是 PCB 导线 |
| module | 模块 | |
| design | 设计 | |
| selection | 选择集 | |
| techmap | 技术映射（techmap） | 首次出现可注英文 |
| technology library / techlib | 工艺库 | |
| frontend / backend | 前端 / 后端 | |
| attribute | 属性 | |
| parameter | 参数 | |
| signal | 信号 | |
| driver | 驱动源 | |
| bit / vector | 位 / 向量 | |
| latch | 锁存器 | |
| flip-flop | 触发器 | |
| mux / multiplexer | 多路复用器 | |
| FSM | 有限状态机（FSM） | |
| ABC | ABC | 工具名 |
| SMT | SMT | |
| formal verification | 形式化验证 | |
| equivalence | 等价 | |
| optimization | 优化 | |
| flatten | 展平 | |
| hierarchy | 层次 | |
| process block | 过程块 | |
| memory | 存储器 | |
| port | 端口 | |
| pin | 引脚 | |
| instance | 实例 | |
| simulation | 仿真 | |
| script | 脚本 | |
| shell | shell | 交互式命令解释器 |
| subcircuit | 子电路 | |
| top module | 顶层模块 | |
| blackbox / whitebox | 黑盒 / 白盒 | |
| extract | 提取 | |
| map | 映射 | |
| share | 共享 | |
| merge | 合并 | |
| simplify | 化简 | |
| keep | 保留 | |
| bugpoint | bugpoint | 工具名不翻译 |
| Yosys | Yosys | |
| YosysHQ | YosysHQ | |
| yoscrypt / yoterm | yoscrypt / yoterm | 角色名保留 |
| Read the Docs | Read the Docs | |
| command reference | 命令参考 | |
| Appendix | 附录 | |
| table of contents | 目录 | |

## 文件范围

- 翻译 `docs/source/**/*.rst` 中的全部文件。
- `docs/source/cmd/*.rst` 是命令参考的分组页，大多只有标题和 toctree；
  翻译标题和简短说明即可。命令本身的帮助文本由 `generated/cmds.json`
  在构建时生成，不在翻译范围内。
- `docs/source/cell/*.rst` 是手写的 RTLIL 单元说明，需要完整翻译。
- 不要翻译 `docs/source/generated/`、`_images/`、`_downloads/`、
  `code_examples/`、`literature.bib`、`conf.py`。
- 如果原文有 `.. todo::`，保留指令并翻译内容；构建时会隐藏。

## 质量检查

翻译后运行：

```bash
/tmp/ysvenv/bin/sphinx-build -b html -q docs/source docs/build/html
```

以 0 个 warning 为目标；至少不能新增“未翻译的标题/指令错误”。
