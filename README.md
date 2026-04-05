# Code Agent

基于 LangGraph + Qwen 的 AI 编程智能体，支持 CLI 和 Web 两种交互方式。

## 架构

```
.
├── main.py                 # CLI 入口 (REPL 交互)
├── server.py               # FastAPI 入口 (Web 服务)
├── index.html              # Web 前端 (聊天界面)
├── requirements.txt        # Python 依赖
├── .env                    # 环境变量 (DASHSCOPE_API_KEY)
├── agent/                  # 核心智能体模块
│   ├── graph.py            # LangGraph StateGraph 定义
│   ├── state.py            # Agent 状态定义
│   ├── tools.py            # 22 个工具定义 (bash, read, write, edit...)
│   └── subagent.py         # 子智能体委派
├── core/                   # 支撑系统
│   ├── tool_helpers.py     # 文件/Shell 操作 (带安全守卫)
│   ├── todo_write.py       # 任务列表管理
│   ├── background_task.py  # 后台任务管理器
│   ├── dag_task_system.py  # DAG 任务依赖系统
│   ├── skills_loader.py    # Skill 模板加载器
│   ├── agent_teams.py      # 多智能体团队管理
│   ├── team_protocols.py   # 协议审批系统
│   ├── autonomous_agent.py # 自治模式
│   └── worktree_task_isolation.py  # 工作区隔离
└── .skills/                # Skill 模板目录
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑 `.env` 文件：

```
DASHSCOPE_API_KEY=你的通义千问 API Key
```

### 3. 运行

**CLI 模式：**
```bash
python main.py
```

**Web 模式：**
```bash
python server.py
```
然后浏览器访问 http://127.0.0.1:9000

## 工具列表

| 类别 | 工具 |
|------|------|
| 文件/Shell | `bash`, `read_file`, `write_file`, `edit_file` |
| 任务管理 | `todo`, `dag_create`, `dag_update`, `dag_list` |
| 委派 | `delegate_task` |
| 后台 | `run_background` |
| Skills | `load_skill`, `reload_skills` |
| 团队 | `team_register`, `team_assign`, `team_inbox` |
| 协议 | `protocol_request`, `protocol_decide`, `protocol_get` |
| 自治 | `autonomous_mode` |
| 工作区 | `worktree_bind`, `worktree_unbind`, `worktree_get` |
| 上下文 | `compact_context` |

## Skills

项目内置 11 个 skill 模板（位于 `.skills/`）：

- `code-review` - 代码审查
- `debug` - 系统化调试
- `qa-testing` - QA 测试
- `dependency-audit` - 依赖管理
- `research` - 技术调研
- `shape-spec` - 需求规格
- `accessibility` - 无障碍审查
- `reflect` - 会话回顾
- `grooming` - 需求整理
- `security-audit` - 安全审计
- `study-skill` - 代码学习

## 技术栈

- **LLM**: 通义千问 (DashScope API)
- **Agent 框架**: LangGraph
- **LLM 封装**: LangChain
- **Web 框架**: FastAPI + uvicorn
