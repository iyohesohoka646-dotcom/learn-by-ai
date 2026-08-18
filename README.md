# Learn by AI — An Adaptive Learning Skill

Learn by AI is a portable, evidence-led Agent Skill for long-term adaptive learning. It turns goals, learning materials, diagnostic answers, and prior progress into a sparse knowledge graph, a learner-state overlay, an append-only evidence log, and a precise cross-session checkpoint.

“Learn by AI” 是一个可移植、证据驱动的长期自适应学习 Skill。它把学习目标、资料、诊断回答和历史进度组织为局部知识图、学习者状态、追加式证据日志与跨会话检查点。

## Install / 安装

The runtime skill is the self-contained directory [`skill/learn-by-ai`](skill/learn-by-ai). Any Agent Skills-compatible client can install that directory directly.

通用安装方式是在克隆本仓库后，把 skill 复制到 Agent 的 skills 根目录：

```text
git clone https://github.com/iyohesohoka646-dotcom/learn-by-ai.git
cd learn-by-ai
```

```text
python install.py --target <your-agent-skills-directory>
```

For Codex, the installer can resolve `CODEX_HOME` (or the default `~/.codex`) automatically:

```text
python install.py --codex
```

If Python is unavailable, copy `skill/learn-by-ai` to `<your-agent-skills-directory>/learn-by-ai`. If an Agent supports installing a GitHub subdirectory, use `skill/learn-by-ai` as the package path.

The installer never overwrites an existing installation. Remove or rename the old `learn-by-ai` directory intentionally before reinstalling.

## Compatibility / 兼容性

- Uses the portable `SKILL.md` directory convention; the required frontmatter contains only `name` and `description`.
- Requires no model, API, MCP server, database, vector store, or vendor-specific tool.
- Uses ordinary file read/write operations for durable state.
- Includes an optional Python 3 initializer; agents without Python can initialize from the bundled templates using native file tools.
- Keeps optional OpenAI UI metadata in `agents/openai.yaml`; other platforms can ignore it without affecting the skill.

“任何平台”在这里指能够加载 `SKILL.md` 目录并允许 Agent 读写项目文件的平台。平台自己的 skills 根目录不同，因此安装器支持任意 `--target`，不把第三方路径硬编码为事实。

## What it does / 功能

- Initializes or resumes a durable learning project.
- Builds only the goal-relevant knowledge graph and prerequisite neighborhood.
- Selects sources by role instead of loading every material.
- Teaches through predictions, discriminating questions, worked examples, practice, and transfer.
- Locates the earliest reasoning breakpoint and remediates the shortest missing prerequisite chain.
- Updates mastery only from observable evidence and preserves uncertainty.
- Commits a checkpoint that can resume accurately in a new conversation.

Example prompts:

```text
Use $learn-by-ai to help me systematically learn probability theory from my textbooks.
Use $learn-by-ai to continue my learning project and start from the saved checkpoint.
用 $learn-by-ai 根据我的资料和目标，建立一套长期自适应学习计划并开始诊断。
```

## Repository layout

```text
learn-by-ai/
├── skill/learn-by-ai/    # Installable Agent Skill
├── install.py            # Cross-platform installer
├── tests/                # Standard-library validation
├── docs/                 # Design documentation
├── skill-package.json    # Distribution metadata
└── LICENSE
```

## Validate / 验证

```text
python -m unittest discover -s tests -v
```

The GitHub workflow runs the same tests on Windows, macOS, and Linux.

## License

MIT. The skill stores summaries and source locators, not copyrighted textbooks or full chapters.
