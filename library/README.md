# 本地资料库说明

项目根目录下的 `.local-library/` 保存本轮实际下载的材料；这个目录被 Git 忽略，因此从公开仓库克隆后需要重新下载。

| 本地目录 | 内容 |
|---|---|
| `.local-library/raw/` | Berklee 三本手册，OMT2 PDF/XML/习题册，官网结构页和 PULSE PDF |
| `.local-library/omt-web/` | OMT2 当前目录链接的 150 个 HTML 快照 |
| `.local-library/omt-assets/` | 重点章节中可公开下载的官方图像、练习、谱例与部分音频 |
| `.local-library/github/` | 三组 GitHub 仓库的固定 commit ZIP，以及供阅读的文档/脚本副本 |
| `.local-library/text/` | 本地提取的 PDF/网页阅读副本；不能提交为原书转载 |
| `.local-library/visual-checks/` | 用于核对关键页面的渲染图；渲染不等于实际已查看 |
| `.local-inputs/` | 用户提供的交接原件，保留私人学习背景，不公开 |

`research/` 内各个 manifest 记录获取 URL、文件名、大小与 SHA-256。`reading-ledger.json` 单独记录实际读过的范围，未读附件仍只标为已下载。

本轮 OMT2 重点附件 426 项中有 4 项返回 404；原书有链接不代表该附件当前存在。媒体外链、MuseScore/YouTube/Spotify 的播放器和在线交互不保证离线可用。

不要把整个资料库拖进 GitHub 网页上传。应在公开仓库管理来源与笔记，让原文保留在本机。
