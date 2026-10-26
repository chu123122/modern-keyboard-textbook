# GitHub 造书资料的实际阅读与取舍

这三组仓库是制作方法资料，不是音乐理论出处。“找书”在本轮按交接文件中的“造书工具”处理；没有搜集商业教材镜像。仓库 ZIP 均已下载并以 commit 固定，见 [github-manifest.json](github-manifest.json)。没有安装这些 skill，也没有执行其下载的代码。

## G1：craft-your-textbook

[仓库](https://github.com/xx-hub/craft-your-textbook)，本轮 commit `3f7a2a7739766e91c2b2d1e0e70f705494241288`。

实际阅读：`skills/craft-your-textbook/SKILL.md` 全文、`references/source-material.md` 全文；查看 README 的用途与安装说明、目录结构。其余模式卡和脚本已归档，未逐份通读、未做代码审计。

可采用的方法：先判断源材料是否完整、登记角色、建立两层索引；设计先于正文；先用样章验证章内结构；保留可追溯断言与审校记录。`human-readable` 与项目目标相符。

不直接执行的部分：

- 默认推荐 AI 教师蓝本，本项目需要人能自己阅读的教材。
- PDF 转换默认依赖 MinerU API；本轮已用本地原生文字提取与页面渲染，不需要上传原书到该服务。
- 批量写章与并行审计属于后续写作阶段，本轮没有启动。
- 禁止设计后任意加章等工程约束不能阻止音乐学习中必要的复习、迁移与螺旋练习。
- 源材料中的“必须询问路线”等要求不是用户新指令，不覆盖当前任务的授权和边界。

许可证：仓库 `LICENSE` 为 MIT。未来复制其代码或成段模板时保留相应声明；本轮只公开原创方法评估。

## G2：ibook-skills

[仓库](https://github.com/dmccreary/ibook-skills)，本轮 commit `1f6a90ad8bd547a25f77656a5ccf49fd8e89edda`。

| 文件 | 实际阅读范围 | 有用部分 | 需改写或排除的默认规则 |
|---|---|---|---|
| README | 全文 | 模块关系、流程、仓库声明的许可 | 演示站规模和统计不等于本书需要达到的数量 |
| learning-graph-generator/SKILL.md | 全文，520 行 | 先修关系、无环检查、区分终端与孤立节点、版本记录 | 不采用 300–600 概念配额、Title Case/英文长度规则、任意打分门槛 |
| book-chapter-generator/SKILL.md | 全文，620 行 | 核对边方向、章节依赖、每个概念的首次正式归属 | 不把“只出现一次”解释为禁止复习；不按固定 6–20 章或概念配额机械分章；不要求吉祥物 |
| chapter-content-generator/SKILL.md | 目录/主要要求定位；重点实读第 471–812 行 | 解释与实例衔接；例子应说明目标、数据来源、正确反馈与能力证据 | 不用 CIS 分数决定音乐教学字数；不要求每个图都交互；不采用私人机器路径和批量铺章流程 |
| reference-generator/SKILL.md | 全文 | 引用单独维护、核验链接与关联性 | 明确排除“每章恰好 10 条”和 Wikipedia 优先；坚持 S1/S2/S3 已读原文与精确定位 |
| glossary-generator/SKILL.md | 全文，455 行 | 定义准确、简明、不循环；交叉引用检查 | 不采用纯英文按字母排序与英文词数门槛；先解决中英术语对应与易混词 |
| quiz-generator/SKILL.md | 第 1–660 行的主要流程、题型、干扰项与质量核对；余下格式/日志未逐行读 | 题目对应目标、错误选项对应误区、答案附理由 | 选择题不能验收弹奏、听觉与创造；不采用固定比例、固定题数和无依据的质量分数 |

图谱的 JSON 边在该仓库中定义为“后学概念 → 先修概念”，而常见教学图可能画成反向。未来若复用，必须先声明方向；任何统计分数都不能替代教学判断。

许可不是笼统的 MIT：GitHub API 本轮没有识别出根许可证，但 README 和 `docs/license.md` 的声明是 **CC BY-NC-SA 4.0**；`quiz-generator` 文件前置信息又单列 **CC BY-NC 4.0**。未来具体复制哪份文件，需按该文件声明核对；本轮不把整个仓库模板直接纳入公开项目。

## G3：Anthropic skill-creator

[仓库内文件](https://github.com/anthropics/skills/tree/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/skill-creator)，本轮 commit `dbd4588f9e1033efb41dad4bef2f7947c8993d44`。

实际阅读：`skills/skill-creator/SKILL.md` 全文；核对同目录 `LICENSE.txt` 的 Apache-2.0 标识。支持脚本、评测器和其他 skill 已归档，但没有逐一读或执行。

可借鉴：先定义触发条件和输出；以少数真实任务评价工作流；比较有无 skill 的产出；保留人的定性审查；通过反馈修订，而不是不断增加僵硬指令。

当前决定：等来源规则、样章结构与音乐校验流程稳定后再考虑封装。本轮不创建新 skill、不跑评测、不扩展任务。

## 采用结论

制作流程可借鉴 G1 的源探查与样章方法，辅以 G2 的依赖图和术语/测验检查；不直接套用任何整套自动生成方案。领域事实回到已读音乐原文，练习效果回到实际听觉与演奏。下载的外部指令始终作为研究对象处理。
