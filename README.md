# 从第一段旋律到独奏一首歌

现代流行键盘中文自学教材。先学习用一台琴同时演奏旋律与伴奏，逐步独立准备喜欢的歌曲，再衔接乐队中的键盘角色。

[公开仓库](https://github.com/chu123122/modern-keyboard-textbook)

**当前版本：v0.1 首稿，2026-10-27。16章正文、导读与附录，配24组原创五线谱、分手播放、合成参考音频、MIDI与MusicXML。**

## 读书入口

- [印刷阅读版 PDF](book/现代流行键盘_初稿.pdf)
- [离线阅读版 HTML](book/index.html)：下载整个仓库后打开；内置目录、分手示范、减速和资源下载，不依赖在线脚本。
- [分章正文](book/chapters/)与[合并 Markdown](book/完整正文.md)
- [原创谱例与音频](book/assets/)；乐谱符号解释和学习方法见导读及各章。

基础顺序为键盘与谱表→节奏→读谱→双手配合→第一首小曲→调与音阶→三和弦→连接与转位→独奏伴奏→声音与踏板→律动→小调→七和弦→独立学曲→乐队→练习与MIDI。听觉和曲目应用从开头并行。

伯克利官方 PDF 为主要参考；OMT2 已读章节核对理论，正式课程大纲核对目标与顺序。补充课程只采用国外资料；停止泛化补源。Integrated Musicianship 未取得、未实读，不列为本版依据。Bill Hilton讲义只作辅助。

本版为首稿。合成音频不是钢琴家录音；程序与浏览器检查不能替代真人演奏、动作适配、听觉审查或试教。目标曲《ただ君に晴れ》提供正式谱本入口和迁移步骤，未收录该曲完整乐谱或编造原曲分析。

## 资料准备记录

- 下载 Berklee 三份官方手册：理论/和声/听觉 76 页、钢琴 90 页、电子音乐与声音设计 100 页，并阅读其全部可提取文字；关键谱例另作页面抽查。
- 下载 OMT2 整本 PDF（1,297 页）、官方 XML 导出、合并习题册（520 页），归档当前目录中的 150 个网页；实际阅读 **44 个重点章节及项目说明**，涉及基础、和弦、声部配置、流行节奏/织体/和声/曲式、Blues 与听觉方法。
- 下载上述重点章节引用的 422 个官方附件；4 个链接返回 404，明细保留在下载清单中。附件包括图像、PDF、可编辑乐谱及部分音频，并非全部已读或已听。
- 下载 PULSE 五课教案、五份视频转写、练习日志、问答与其他配套文件。已读五课教案与五份转写。
- 核对五门 Berklee 官方课程的公开结构、先修与指定教材。
- 固定并下载三组 GitHub 造书工具版本，实际阅读相关工作流并记录采用与排除项。
- 补充归档 Bill Hilton 官方免费讲义21份、66页，已读可提取说明文字并抽查关键页面；视频未完整观看。取得记录与散列见 `research/supplemental-courses-manifest.json`。

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

原始资料、提取全文、原谱、第三方仓库 ZIP 和私人交接文件保存在 `.local-library/` / `.local-inputs/`，不提交 Git。公开仓库提供原创教材及配套示例、索引、原文链接、获取证据、原创研究记录和制作工具。详见 [RIGHTS.md](RIGHTS.md)。

## 构建与验证教材

```bash
python -m pip install -r requirements-book.txt
python scripts/build_book.py
python scripts/validate_book.py
```

印刷 PDF 与浏览器检查可运行 `node scripts/check_book_browser.cjs`，需要 Playwright 和可用的 Chromium/Edge；通过 `BOOK_BROWSER_EXECUTABLE` 指定浏览器。Node 依赖由使用者的环境提供，不将本机运行库提交仓库。

写作取舍见 [writing-plan.md](research/writing-plan.md)，实际范围与限制见 [book-review.md](research/book-review.md)，机器检查见 [book-validation.json](research/book-validation.json)。
