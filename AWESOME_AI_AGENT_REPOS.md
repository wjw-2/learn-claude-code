# AI Agent 学习资源精选 (2026)

> 本列表收集了 GitHub 上关于 AI Agent 记忆系统、框架、Harness 评估的高星项目

---

## 🧠 Agent 记忆系统 (Memory Systems)

### 核心论文与资源集合

| 项目 | Stars | 描述 |
|------|-------|------|
| [AgentMemoryWorld/Awesome-Agent-Memory](https://github.com/AgentMemoryWorld/Awesome-Agent-Memory) | 120+ | 218 篇 Agent 记忆核心论文 (2023Q1-2025Q4)，专注于长期性能和个人化 |
| [TsinghuaC3I/Awesome-Memory-for-Agents](https://github.com/TsinghuaC3I/Awesome-Memory-for-Agents) | - | 清华大学整理，按记忆持久性 (长期/短期) 分类的论文列表 |
| [IAAR-Shanghai/Awesome-AI-Memory](https://github.com/IAAR-Shanghai/Awesome-AI-Memory) | - | 覆盖记忆生命周期管理 (创建、激活使用、检索等) |
| [Shichun-Liu/Agent-Memory-Paper-List](https://github.com/Shichun-Liu/Agent-Memory-Paper-List) | - | 包含 2026 最新论文 "Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management" |
| [FredJiang0324/Anatomy-of-Agentic-Memory](https://github.com/FredJiang0324/Anatomy-of-Agentic-Memory) | - | 分析延迟、构建时间、系统成本的权衡，对比 Agentic Memory 与标准 RAG |

### 记忆实现

| 项目 | 描述 |
|------|------|
| [FareedKhan-dev/langgraph-long-memory](https://github.com/FareedKhan-dev/langgraph-long-memory) | 使用 LangGraph 实现长期记忆，存储用户偏好和跨会话信息 |
| [AgentMemory/Huaman-Agent-Memory](https://github.com/AgentMemory/Huaman-Agent-Memory) | 多粒度长期记忆方法 (2025 年 12 月更新) |

---

## 🏗️ 主流 Agent 框架

### 顶级框架对比

| 框架 | Stars | 最佳用途 | 学习曲线 |
|------|-------|---------|---------|
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 100,000+ | 复杂工作流、有状态 Agent、生产部署 | 陡峭 |
| [joaomdmoura/crewAI](https://github.com/joaomdmoura/crewAI) | 45,000+ | 企业自动化、角色化协作 | 简单 |
| [microsoft/autogen](https://github.com/microsoft/autogen) | 30,000+ | 研究、实验性多 Agent 系统 | 中等 |
| [OpenAgentsInc/openagents](https://github.com/OpenAgentsInc/openagents) | - | 生产级 Agent 平台 |
| [simular-ai/agent-s](https://github.com/simular-ai/agent-s) | - | Agent-Computer Interface，像人类一样使用电脑 |

### 新兴框架 (2025-2026)

| 框架 | 描述 |
|------|------|
| [openai/openai-agents-python](https://github.com/openai/openai-agents-python) | OpenAI 官方 Agent SDK (2025 年 3 月发布，19,000+ 星) |
| [google/adk-python](https://github.com/google/adk-python) | Google Agent Development Kit |
| [pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai) | Pydantic AI Agent 框架 |
| [mastra-ai/mastra](https://github.com/mastra-ai/mastra) | 轻量级 Agent 框架 |

---

## 🔧 Harness/评估框架

| 项目 | 描述 |
|------|------|
| [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) | 统一的 LLM 评估框架，测试生成模型 across 多个任务 |
| [princeton-pli/hal-harness](https://github.com/princeton-pli/hal-harness) | 普林斯顿 Holistic Agent Leaderboard，标准化 Agent 评估 |
| [BulloRosso/etienne](https://github.com/BulloRosso/etienne) | Coding Agent Harness，让非技术人员也能定制 AI 编程 Agent |
| [msaleme/red-team-blue-team-agent-fabric](https://github.com/msaleme/red-team-blue-team-agent-fabric) | 342 个可执行安全测试，24 个模块的自主 Agent 安全评估 |
| [supernalintelligence/Awesome-General-Agents-Benchmark](https://github.com/supernalintelligence/Awesome-General-Agents-Benchmark) | 追踪 AI Agent 能力向 AGI/ASI 进展的基准 |

---

## 📚 综合学习资源

### Awesome 列表

| 项目 | 描述 |
|------|------|
| [kyrolabs/awesome-agents](https://github.com/kyrolabs/awesome-agents) | AI Agent 精选列表，包含 OpenClaw 等持久化个人 AI |
| [jim-schwoegel/awesome_ai_agents](https://github.com/jim-schwoegel/awesome_ai_agents) | 300+ AI Agent 项目和资源 |
| [ashishpatel26/500-AI-Agents-Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects) | 500 个 AI Agent 实战项目 |
| [caramaschiHG/awesome-ai-agents-2026](https://github.com/caramaschiHG/awesome-ai-agents-2026) | 2026 年最全面的 AI Agent 列表 |
| [slavakurilyak/awesome-ai-agents](https://github.com/slavakurilyak/awesome-agents) | 300+ 开源 AI Agent 对比指标 |
| [vince-lam/awesome-agents](https://github.com/vince-lam/awesome-agents) | 开源 AI Agent 项目对比指标 |
| [mb-mal/awesome-ai-agents-frameworks](https://github.com/mb-mal/awesome-ai-agents-frameworks) | AI Agent 框架精选 |

### 论文与调研

| 项目 | 描述 |
|------|------|
| [asinghcsu/AgenticRAG-Survey](https://github.com/asinghcsu/AgenticRAG-Survey) | Agentic RAG 系统综合调研 |
| [jamwithai/production-agentic-rag-course](https://github.com/jamwithai/production-agentic-rag-course) | 生产级 Agentic RAG 系统构建课程 |

### 中文资源

| 项目 | 描述 |
|------|------|
| [adongwanai/AgentGuide](https://github.com/adongwanai/AgentGuide) | Agent 开发框架对比中文指南 |

---

## 📈 2026 年趋势洞察

1. **Python 主导**: 10 大框架中 8 个是 Python 为基础
2. **规模化**: 20+ 框架拥有 10,000+ 星
3. **新进入者**: Google ADK、OpenAI Agents SDK、Pydantic AI、Mastra
4. **企业聚焦**: 转向生产就绪、有状态、人机协作的 Agent
5. **记忆系统成熟**: 从简单向量存储发展到统一长短期记忆管理
6. **评估标准化**: 多个基准测试平台出现

---

## 🎯 学习路径建议

### 初学者
1. 从 [CrewAI](https://github.com/joaomdmoura/crewAI) 开始 - 最快上手
2. 阅读 [awesome-agents](https://github.com/kyrolabs/awesome-agents) 了解生态
3. 实践 500 个项目中的简单案例

### 进阶开发者
1. 深入学习 [LangGraph](https://github.com/langchain-ai/langgraph) - 生产首选
2. 研究 [Agent Memory 论文列表](https://github.com/AgentMemoryWorld/Awesome-Agent-Memory)
3. 搭建自己的评估 harness

### 研究者
1. 关注 [TsinghuaC3I/Awesome-Memory-for-Agents](https://github.com/TsinghuaC3I/Awesome-Memory-for-Agents) 最新论文
2. 使用 [HAL Harness](https://github.com/princeton-pli/hal-harness) 进行基准测试
3. 贡献到 [AgenticRAG-Survey](https://github.com/asinghcsu/AgenticRAG-Survey)

---

## 📝 如何使用本列表

1. **Fork 感兴趣的项目** - 在 GitHub 上点击 Star 和 Fork
2. **克隆到本地** - `git clone <repo-url>`
3. **运行示例** - 大多数项目都有 examples/ 文件夹
4. **加入社区** - 关注项目的 Issues 和 Discussions

---

*最后更新：2026-04-04*
*数据来源：GitHub API、技术博客、官方文档*
