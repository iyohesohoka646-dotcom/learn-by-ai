# Launch copy

Use these as starting points. Replace claims with real user evidence as it becomes available.

## English — short

Most AI tutors explain well, but they do not know when to advance, what evidence counts as mastery, or how to resume precisely in a new conversation.

I built **Learn by AI**, an open Agent Skill that adds a sparse knowledge graph, multidimensional learner state, append-only evidence, breakpoint-based remediation, and cross-session checkpoints to any skills-compatible agent.

Install:

```text
npx skills add iyohesohoka646-dotcom/learn-by-ai --skill learn-by-ai -g
```

GitHub: https://github.com/iyohesohoka646-dotcom/learn-by-ai

I would especially value feedback from educators, self-learners, and people testing skills across multiple agents.

## 中文 — 短帖

普通 AI 老师很会解释，但往往不知道什么时候该继续、什么证据才算掌握，也很难在新对话里准确续接。

我开源了 **Learn by AI**：一个可安装到多种 AI Agent 的长期自适应学习 Skill。它用局部知识图、多维掌握状态、追加式证据日志和检查点，决定继续、细化、补先修还是复习。

一条命令安装：

```text
npx skills add iyohesohoka646-dotcom/learn-by-ai --skill learn-by-ai -g
```

项目地址：https://github.com/iyohesohoka646-dotcom/learn-by-ai

欢迎老师、自学者和 Agent 工具开发者试用；最希望收到“它在哪一步判断错了”的具体反馈。

## Long-form opening

The hard part of AI tutoring is not generating another explanation. It is controlling the learning loop: selecting the next node, obtaining observable evidence, locating the first failed reasoning step, deciding when to review, and leaving enough durable state to resume without chat history.

Learn by AI packages that control loop as an open, inspectable Agent Skill rather than a new model, database, or tutoring app.

## Directory submission summary

**Name:** Learn by AI

**Category:** Education / Productivity / Agent Skills

**One line:** Turn any skills-compatible AI agent into an evidence-led adaptive tutor with durable cross-session learning state.

**Repository:** https://github.com/iyohesohoka646-dotcom/learn-by-ai

**Install:** `npx skills add iyohesohoka646-dotcom/learn-by-ai --skill learn-by-ai -g`

**License:** MIT
