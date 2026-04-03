# Qwen Nano Agent（可用于简历的 Agent 工程项目）

本项目基于 `learn-claude-code` 的分阶段架构思想（S0-S12），实现了一个可运行的 **Qwen Coding Agent Harness**。  
核心目标是：在不依赖重型框架的前提下，构建一套可扩展、可调试、可工程化落地的智能体执行系统。

---

## 一、项目定位（简历描述版）

- **项目名称**：Qwen Nano Agent（类 Claude Code 的本地工程智能体）
- **项目类型**：AI Agent / LLM Harness / 工程自动化
- **技术方向**：ReAct、Function Calling、Multi-Agent、任务编排、上下文压缩
- **模型与平台**：阿里云百炼 DashScope（OpenAI 兼容接口）
- **个人职责**：独立完成架构设计、核心循环开发、工具系统实现、任务调度与多 Agent 协作模块

---

## 二、简历可用亮点（可直接粘贴）

- 基于 Qwen 的 `tool_calls` 能力实现 ReAct 闭环，构建了 `思考 -> 调工具 -> 观察 -> 继续推理` 的执行引擎。
- 设计并实现多层任务执行体系：同步工具调用 + 后台线程任务 + 子 Agent 分派 + DAG 依赖任务编排。
- 实现上下文治理策略：微观压缩、阈值触发自动摘要、手动压缩指令，显著降低长会话 Token 膨胀风险。
- 构建多 Agent 协作能力：团队注册、任务派发、收件箱消息总线、审批协议流（request/approve/reject）。
- 引入任务隔离机制：基于 task_id 的 worktree 目录绑定/解绑，降低多任务并行时的上下文与文件污染风险。
- 完成统一工具注册中心（Schema + Handler），支持高扩展性与低耦合功能演进。
- **多步任务规划**: 集成了自我迭代的 `TodoManager`，强制大模型在处理复杂任务时遵循“单点进行中(in_progress)”原则，防止任务发散。
- **环境沙箱与安全拦截 (Human-in-the-loop)**: 实现了一套 `WORKSPACE` 路径安全限制，防止大模型越权读写系统文件。同时，在 Bash 命令执行层植入了**高危命令正则拦截机制**（如 `del`, `rm`, `format` 等），当触发危险操作时自动挂起，强制等待人类终端审批，确保系统绝对安全。
- **上下文微观压缩**: 针对工具返回过长（如读取大文件、报错堆栈过长）的问题，实现了 `micro_compact` 截断策略，防止 Token 爆炸。

---

## 三、架构设计

### 1) 执行主循环（Loop）
- 文件：`loop.py`
- 职责：维护消息历史、发起模型请求、执行工具、接收工具结果、控制步数与退出条件。
- 关键机制：
  - ReAct 执行闭环
  - todo nag 提醒（连续多轮未更新 todo 自动提醒）
  - 后台任务结果回注（下一轮推理前注入）
  - 自动/手动上下文压缩

### 2) 工具系统（Tool Registry）
- 文件：`tool_use.py`
- 职责：统一定义工具 JSON Schema 与 Python Handler 映射。
- 工具类型：
  - 基础工具：`bash`、`read_file`、`write_file`、`edit_file`
  - 规划工具：`todo`
  - 分派工具：`delegate_task`
  - 后台工具：`run_background`
  - 任务图工具：`dag_create`、`dag_update`、`dag_list`
  - 技能工具：`load_skill`、`reload_skills`
  - 团队工具：`team_register`、`team_assign`、`team_inbox`
  - 协议工具：`protocol_request`、`protocol_decide`、`protocol_get`
  - 自治与隔离工具：`autonomous_mode`、`worktree_bind`、`worktree_get`、`worktree_unbind`
  - 上下文工具：`compact_context`

### 3) 多 Agent 协作
- 文件：`subagent.py`、`agent_teams.py`、`team_protocols.py`
- 能力说明：
  - 主 Agent 可将分支任务委派给子 Agent（独立上下文）
  - 通过 MessageBus 进行成员消息收发
  - 通过 ProtocolManager 管理审批请求状态流

### 4) 任务与并发管理
- 文件：`dag_task_system.py`、`background_task.py`、`worktree_task_isolation.py`
- 能力说明：
  - DAG 任务依赖与级联解锁
  - 后台线程执行耗时命令并异步通知
  - task_id 与隔离工作目录绑定，完成后自动解绑

### 5) 上下文管理
- 文件：`context_compact.py`
- 三层压缩：
  - 微观压缩：旧工具长输出替换占位符
  - 自动压缩：Token 超阈值后摘要重构上下文
  - 手动压缩：模型主动调用 `compact_context`

---

## 四、模块清单

- `main.py`：CLI 入口与系统提示词初始化
- `loop.py`：ReAct 主循环
- `tool_use.py`：工具注册中心（Schema + Handler）
- `subagent.py`：子 Agent 执行引擎
- `todo_write.py`：任务列表管理器
- `background_task.py`：后台线程任务管理
- `dag_task_system.py`：DAG 任务依赖图
- `skills_loader.py`：技能加载器（扫描 SKILL.md）
- `agent_teams.py`：团队协作与消息总线
- `team_protocols.py`：审批协议管理
- `autonomous_agent.py`：自治模式状态机
- `worktree_task_isolation.py`：任务隔离目录映射
- `context_compact.py`：上下文压缩模块

---



---

## 六、快速开始

### 1) 创建环境并安装依赖

```bash
conda create -n qwen-agent python=3.11 -y
conda activate qwen-agent
pip install -r requirements.txt
```

### 2) 配置密钥

将 `.env.example` 复制为 `.env`，并写入你的 DashScope Key：

```env
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
```

### 3) 运行

```bash
python main.py
```

---

