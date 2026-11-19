# Yosys 中文文档

这是 [Yosys](https://github.com/YosysHQ/yosys) 官方文档的**非官方简体中文翻译**，目标是让中文读者在本地或 GitHub Pages 上阅读与官方结构一致的 Yosys 文档。

- 在线阅读：<https://alainchen6.github.io/Yosys-Chinese-Manual/>
- 官方英文文档：<https://yosyshq.readthedocs.io/projects/yosys/en/latest/>
- 上游仓库：<https://github.com/YosysHQ/yosys>
- 本翻译对应的上游文档快照：Yosys `0.71-dev`，`docs/source` 于 2026-11-20 拉取

> **以英文原文为准。** 翻译仅用于学习和参考；如果译文与英文原文不一致，或你发现内容已过时，请以官方文档为准。Yosys 的版本、命令和 API 可能随时变化。

## 范围与状态

- `docs/source/**/*.rst`：手写文档页面按官方源文件逐篇翻译。
- `docs/source/cmd/*.rst`：命令参考的分组页，仅翻译标题和说明；每条命令的
  help 文本由 Yosys 在构建时生成（`generated/cmds.json`），当前保留英文。
- `docs/source/cell/*.rst`：RTLIL 单元说明，按原文翻译。
- 图片、示例输出、`generated/` 下的 JSON 与源码片段来自上游，不翻译。
- 页面结构、Sphinx 主题（YosysHQ 的 `furo-ys`）、导航和交叉引用与官方一致。

## 本地构建

需要 Python 3.12+、git，以及能够访问 GitHub 的网络环境（`furo-ys` 主题从 GitHub 安装）。

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r docs/source/requirements.txt
sphinx-build -b html docs/source docs/build/html
```

打开 `docs/build/html/index.html` 即可预览。

## 目录

- `docs/source/`：与上游 `docs/source` 同构的文档源码
- `docs/source/generated/`：构建时需要的命令/单元 JSON 与源码片段（上游构建产物）
- `docs/source/_images/`：从官方文档取得的渲染图片
- `docs/source/code_examples/`：官方示例及其输出
- `docs/util/`：上游 Sphinx 扩展（`cmd`/`cell`/自定义指令）
- `TRANSLATION_GUIDE.md`：翻译规范与术语表
- `.github/workflows/pages.yml`：构建并发布 GitHub Pages

## 参与翻译

欢迎提交 PR 修正错译、漏译或过时内容。请先阅读
[`TRANSLATION_GUIDE.md`](TRANSLATION_GUIDE.md)，保持术语和 RST 结构一致。
翻译以 `docs/source` 下的英文源文件为参照，不要为了通顺而增删事实。

## 许可证与署名

Yosys 文档以 **ISC License** 发布，Copyright (C) 2012–2026 Claire Xenia Wolf 与
YosysHQ GmbH。本仓库的中文翻译是原文档的衍生作品，同样以 ISC License 提供；
原始英文文档的版权归上游作者所有。完整许可证文本见 [LICENSE](LICENSE)。

Yosys、YosysHQ 及相关名称为其各自权利人的商标。本仓库是非官方翻译，与
YosysHQ 没有隶属关系。
