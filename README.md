# 现代流行键盘中文自学教材 · 资料与写作准备

面向成人自学的 Contemporary / Pop Keyboard 项目，以 Pop/Rock、J-pop、ACG 的伴奏、听觉、基础即兴和乐队应用为目标。

[公开仓库](https://github.com/chu123122/modern-keyboard-textbook)

**当前阶段：下载、真实阅读、来源审查。此轮没有编写教材正文。**

## 本轮已经做了什么

- 下载 Berklee 三份官方手册：理论/和声/听觉 76 页、钢琴 90 页、电子音乐与声音设计 100 页，并阅读其全部可提取文字；关键谱例另作页面抽查。
- 下载 OMT2 整本 PDF（1,297 页）、官方 XML 导出、合并习题册（520 页），归档当前目录中的 150 个网页；实际阅读 **44 个重点章节及项目说明**，涉及基础、和弦、声部配置、流行节奏/织体/和声/曲式、Blues 与听觉方法。
- 下载上述重点章节引用的 422 个官方附件；4 个链接返回 404，明细保留在下载清单中。附件包括图像、PDF、可编辑乐谱及部分音频，并非全部已读或已听。
- 下载 PULSE 五课教案、五份视频转写、练习日志、问答与其他配套文件。已读五课教案与五份转写。
- 核对五门 Berklee 官方课程的公开结构、先修与指定教材。
- 固定并下载三组 GitHub 造书工具版本，实际阅读相关工作流并记录采用与排除项。

“读过”只按阅读账本声明的范围使用。没有声称 OMT2 全本通读、全部媒体听完、全部图谱审过、完成真人演奏验收或审计所有第三方代码。

## 从哪里开始看

| 文档 | 用途 |
|---|---|
| [阅读笔记](research/reading-notes.md) | 原书到底讲了什么、哪些可用、哪些不够 |
| [主题来源定位](research/source-mapping.md) | 44 个重点章节和项目说明的原文链接与逐项判断 |
| [阅读账本](research/reading-ledger.json) | 明确文字阅读、页面抽查和未验证媒体的范围 |
| [来源登记](research/source-registry.yaml) | 正文/结构/教学法/工具角色、许可与获取证据 |
| [能力覆盖矩阵](research/coverage-matrix.md) | 技能目标对应到已读原文，避免按书名推断覆盖 |
| [课程结构核对](research/syllabus-alignment.md) | Berklee 公开课程实际包含哪些技能 |
| [缺口报告](research/source-gaps.md) | 缺正文、缺示例、尚未读与未验证分别记录 |
| [原文疑点](research/source-issues.md) | 发现的分类、符号、版本与语境问题 |
| [GitHub 方法评估](research/github-review.md) | 三组造书工具的固定版本、实读范围与取舍 |
| [写作准备结论](research/writing-readiness.md) | 可以进入下一步的范围与验收边界 |
| [资料库说明](library/README.md) | 本地原始资料的位置与重建方式 |
| [状态与交接](research/STATUS.md) | 当前任务范围、完成结果与后续入口 |

## 核心原文

1. [Berklee Music Theory, Harmony & Ear Training Handbook](https://assets.online.berklee.edu/handbooks/berklee-online-music-theory-harmony-and-ear-training-handbook.pdf)：精选正文，用于听觉、节奏与和声补充。
2. [Berklee Piano Handbook](https://assets.online.berklee.edu/handbooks/berklee-online-piano-handbook.pdf)：键盘技术与和弦/配置节选。
3. [Open Music Theory V2](https://viva.pressbooks.pub/openmusictheory/)：连续理论骨架；以已读章节支持具体事实。

官网课程大纲只作技能规范；GitHub 项目只作制作方法。没有把付费书名、大纲或第三方笔记冒充已取得的音乐正文。

## 本地重建

需要 Python 3.10+。在虚拟环境中安装依赖后运行以下脚本；它们只将原文保存到本机的 `.local-library/`。

```bash
python -m venv .venv
# 激活虚拟环境后：
python -m pip install -r requirements.txt
python scripts/download_sources.py
python scripts/acquire_extended.py
python scripts/archive_web_chapters.py
python scripts/archive_pulse.py
python scripts/archive_omt_assets.py
python scripts/extract_sources.py
python scripts/validate_library.py
```

合并习题册的官网入口和本轮文件散列见 `research/workbook-manifest.json`。它是静态合并版，官网推荐优先使用各章末尾的当前习题。

网页、导出和仓库会更新。重新下载应单独保存新快照并比较散列；不要把旧阅读账本自动当作新版本已读记录。脚本和提取成功本身不会产生新的“已读”证据。

## 公开范围

原始资料、提取全文、原谱、第三方仓库 ZIP 和私人交接文件保存在 `.local-library/` / `.local-inputs/`，不提交 Git。公开仓库提供索引、原文链接、获取证据、原创研究记录和下载工具。详见 [RIGHTS.md](RIGHTS.md)。
