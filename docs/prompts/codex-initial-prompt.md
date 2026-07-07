# Codex 初始启动 Prompt

请在 Codex 中打开一个全新的 Git 仓库，然后粘贴以下 Prompt。

---

你现在是本项目的主开发 Agent。请先阅读以下文件，不要马上写代码：

- `README.md`
- `AGENTS.md`
- `docs/00-codex-handoff.md`
- `docs/01-prd.md`
- `docs/02-architecture.md`
- `docs/03-repo-structure.md`
- `docs/04-module-boundaries.md`
- `docs/06-live-state-machine.md`
- `docs/18-codex-issues.md`

阅读后请输出：

1. 你理解的系统目标。
2. 你理解的模块边界。
3. 第一阶段开发顺序。
4. 你将先实现的第一个 Issue。
5. 需要创建的文件清单。

然后从 `Issue 001：初始化 monorepo 与基础文档` 开始实现。

开发要求：

- 严格遵守 `AGENTS.md`。
- 不要一次性开发完整系统。
- 每次只完成当前 Issue。
- 不要接真实平台 API。
- 不要提交任何密钥。
- 所有外部能力先使用 Mock Provider。
- 每个模块必须有测试。
- 公共 API、事件、状态机变化必须同步更新文档。

完成后请给出：

- 修改文件列表。
- 如何运行。
- 如何测试。
- 当前未完成事项。
