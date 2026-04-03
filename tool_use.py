import subprocess
import re
from pathlib import Path
from todo_write import TODO
from subagent import run_subagent
from background_task import BG_TASK_MANAGER
from dag_task_system import DAG_TASKS
from skills_loader import SKILL_LOADER
from agent_teams import TEAM
from team_protocols import PROTOCOLS
from autonomous_agent import AUTO_STATE
from worktree_task_isolation import WORKTREE_ISOLATION

WORKSPACE = Path(".").resolve()

# 危险命令黑名单正则表达式 (包含 Windows 和 Linux/Mac 的危险命令)
DANGEROUS_COMMANDS_PATTERN = re.compile(
    r"\b(del|rm|rmdir|format|mkfs|diskpart|shutdown|reboot|chmod|chown|kill|taskkill|wget|curl)\b",
    re.IGNORECASE
)

def _requires_human_approval(command: str) -> bool:
    """检查命令是否属于危险操作，如果是，则触发人工审批 (Human-in-the-loop)"""
    if DANGEROUS_COMMANDS_PATTERN.search(command):
        return True
    # 如果试图切换到系统根目录等高危操作
    if "cd /" in command or "cd \\" in command or "cd .." in command:
        return True
    return False

def save_path(p: str) -> Path:
    """路径沙箱：检查要操作的路径是否在工作区内，防止误读写系统文件"""
    path = (WORKSPACE / p).resolve()
    if not path.is_relative_to(WORKSPACE):
        raise ValueError(f"安全警告: 拒绝访问工作区外的路径: {p}")
    return path

def run_bash(command: str) -> str:
    """执行 Bash/命令行 指令，带有安全拦截机制"""
    # 1. 危险操作人工审批拦截
    if _requires_human_approval(command):
        print(f"\n⚠️  [安全拦截] Agent 试图执行高危命令: \033[91m{command}\033[0m")
        while True:
            confirm = input("是否允许执行？(y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                print("✅ 用户已授权执行。")
                break
            elif confirm in ['n', 'no']:
                print("❌ 用户已拒绝该命令。")
                return f"执行失败: 核心安全协议拦截。用户拒绝了执行危险命令 '{command}'。"
            else:
                print("请输入 y 或 n。")

    # 2. 实际执行
    try:
        # timeout=60 防止命令死循环卡住
        r = subprocess.run(command, shell=True, cwd=WORKSPACE, capture_output=True, text=True, timeout=60)
        output = r.stdout + "\n" + r.stderr
        return output.strip() or "命令执行成功，但没有输出任何内容。"
    except Exception as e:
        return f"执行失败: {str(e)}"


def run_read(path: str, limit: int = None) -> str:
    try:
        text = save_path(path).read_text(encoding="utf-8")
        lines = text.splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit]
        return "\n".join(lines)
    except Exception as e:
        return f"read error: {str(e)}"


def run_write(path: str, content: str) -> str:
    try:
        target = save_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"wrote {path}"
    except Exception as e:
        return f"write error: {str(e)}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        target = save_path(path)
        content = target.read_text(encoding="utf-8")
        if old_text not in content:
            return "edit error: old_text not found"
        target.write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
        return f"edited {path}"
    except Exception as e:
        return f"edit error: {str(e)}"


def run_dag_update(task_id: int, status: str) -> str:
    # 任务完成时自动解除 worktree 绑定，避免孤儿目录残留
    result = DAG_TASKS.update_task_status(task_id, status)
    if status == "completed":
        WORKTREE_ISOLATION.unbind(task_id)
    return result


TOOL_HANDLERS = {
    # 基础执行工具
    "bash": lambda **kw: run_bash(kw.get("command", "")),
    "read_file": lambda **kw: run_read(kw.get("path", ""), kw.get("limit")),
    "write_file": lambda **kw: run_write(kw.get("path", ""), kw.get("content", "")),
    "edit_file": lambda **kw: run_edit(kw.get("path", ""), kw.get("old_text", ""), kw.get("new_text", "")),
    # 规划与分工
    "todo": lambda **kw: TODO.update(kw.get("items", [])),
    "delegate_task": lambda **kw: run_subagent(kw.get("prompt", "")),
    # 后台与 DAG
    "run_background": lambda **kw: BG_TASK_MANAGER.run(kw.get("command", "")),
    "dag_create": lambda **kw: DAG_TASKS.create_task(kw.get("subject", ""), kw.get("description", ""), kw.get("blocked_by")),
    "dag_update": lambda **kw: run_dag_update(kw.get("task_id"), kw.get("status", "pending")),
    "dag_list": lambda **kw: DAG_TASKS.list_tasks(),
    # 技能与团队协议
    "load_skill": lambda **kw: SKILL_LOADER.get_content(kw.get("name", "")),
    "reload_skills": lambda **kw: (SKILL_LOADER.reload() or SKILL_LOADER.get_descriptions()),
    "team_register": lambda **kw: TEAM.register(kw.get("name", ""), kw.get("role", "member")),
    "team_assign": lambda **kw: TEAM.assign(kw.get("name", ""), kw.get("task", "")),
    "team_inbox": lambda **kw: TEAM.inbox(kw.get("name", "")),
    "protocol_request": lambda **kw: PROTOCOLS.request_approval(kw.get("requester", "agent"), kw.get("action", "")),
    "protocol_decide": lambda **kw: PROTOCOLS.decide(kw.get("request_id", ""), kw.get("decision", "reject")),
    "protocol_get": lambda **kw: PROTOCOLS.get(kw.get("request_id", "")),
    # 自治与隔离
    "autonomous_mode": lambda **kw: AUTO_STATE.enable() if kw.get("enabled", True) else AUTO_STATE.disable(),
    "worktree_bind": lambda **kw: WORKTREE_ISOLATION.bind(kw.get("task_id")),
    "worktree_unbind": lambda **kw: WORKTREE_ISOLATION.unbind(kw.get("task_id")),
    "worktree_get": lambda **kw: WORKTREE_ISOLATION.get(kw.get("task_id")),
    "compact_context": lambda **kw: "__MANUAL_COMPACT__",
}


# 提供给 Qwen/OpenAI function-calling 的工具模式定义
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "执行终端/命令行指令。可以用来运行代码、安装依赖、查看系统信息等。如果需要查看当前目录文件，可以使用 dir (Windows) 或 ls (Linux/Mac)。",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "要执行的命令"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edit file content with one replacement.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_text": {"type": "string"},
                    "new_text": {"type": "string"}
                },
                "required": ["path", "old_text", "new_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文件内容。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件的相对路径"},
                    "limit": {"type": "integer", "description": "最多读取几行（如果不传则读取全部）"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "load_skill",
            "description": "加载特定的技能模板(Skill)。比如当你需要某种特定领域的代码模板时，可以调用此工具获取。",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reload_skills",
            "description": "重新扫描并加载 skills 目录下的所有技能文件。",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "将内容写入本地文件。注意：这会覆盖原文件。如果是新建文件，也会自动创建所在目录。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件的相对路径"},
                    "content": {"type": "string", "description": "要写入的完整文本内容"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "team_register",
            "description": "注册一个团队成员(Teammate)。当需要多个专职 Agent 协作时使用。",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "role": {"type": "string"}},
                "required": ["name", "role"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "team_assign",
            "description": "向指定的团队成员发送消息/分配任务。",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "task": {"type": "string"}},
                "required": ["name", "task"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "team_inbox",
            "description": "查看团队消息收件箱，读取分配给你的任务或回复。",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "protocol_request",
            "description": "发起一个团队协议审批请求（如关机、执行敏感操作等）。",
            "parameters": {
                "type": "object",
                "properties": {"requester": {"type": "string"}, "action": {"type": "string"}},
                "required": ["requester", "action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "protocol_decide",
            "description": "审批/决断一个团队协议请求。",
            "parameters": {
                "type": "object",
                "properties": {"request_id": {"type": "string"}, "decision": {"type": "string", "enum": ["approve", "reject"]}},
                "required": ["request_id", "decision"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "protocol_get",
            "description": "查询指定的团队协议请求状态。",
            "parameters": {
                "type": "object",
                "properties": {"request_id": {"type": "string"}},
                "required": ["request_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "todo",
            "description": "管理任务列表(Todo List)。在执行复杂多步任务时，务必使用此工具来规划和跟踪进度。",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "description": "任务项列表。注意：每次必须且只能有一个任务状态为 in_progress。",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "任务的简短唯一标识，例如 'setup_db'"},
                                "text": {"type": "string", "description": "任务具体描述"},
                                "status": {"type": "string", "enum": ["pending", "in_progress", "completed"], "description": "任务当前状态"}
                            },
                            "required": ["id", "text", "status"]
                        }
                    }
                },
                "required": ["items"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delegate_task",
            "description": "委派一个复杂的子任务给 Sub-Agent 去执行。当你遇到一个需要多步探索、或者你不想让它弄乱你当前思考上下文的任务时，你可以把它外包给子智能体。子智能体执行完毕后会给你返回一份详细的报告。",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string", 
                        "description": "给子智能体的详细任务描述和要求"
                    }
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_background",
            "description": "在后台线程执行耗时较长的终端命令（如 npm install, pytest, 构建项目等）。这允许你不用死等命令结束，可以继续做其他事情。当命令执行完毕后，系统会自动把结果通知你。",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "要放到后台执行的 Bash 命令"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "dag_create",
            "description": "创建一个带有依赖关系的高级任务(DAG任务图)。适用于需要多步串行/并行协作的大型项目规划。",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "任务简述"},
                    "description": {"type": "string", "description": "任务详细说明"},
                    "blocked_by": {
                        "type": "array", 
                        "items": {"type": "integer"},
                        "description": "前置任务的 ID 列表。只有当这些任务完成时，本任务才能开始执行。"
                    }
                },
                "required": ["subject"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "dag_update",
            "description": "更新高级 DAG 任务的状态。当你把一个任务标记为 'completed' 时，系统会自动解锁依赖它的后续任务。",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "任务 ID"},
                    "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]}
                },
                "required": ["task_id", "status"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "dag_list",
            "description": "列出所有高级 DAG 任务的当前状态和依赖关系图。",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "autonomous_mode",
            "description": "启用或禁用自治模式(允许 Agent 在空闲时自动执行下一步)。动作只能是 'enable' 或 'disable'。",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["enable", "disable"]}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_bind",
            "description": "将任务绑定到一个隔离的工作区(worktree)。",
            "parameters": {
                "type": "object",
                "properties": {"task_id": {"type": "integer"}},
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_unbind",
            "description": "解绑并清理任务的工作区(worktree)。",
            "parameters": {
                "type": "object",
                "properties": {"task_id": {"type": "integer"}},
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_get",
            "description": "获取任务绑定的工作区(worktree)路径。",
            "parameters": {
                "type": "object",
                "properties": {"task_id": {"type": "integer"}},
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compact_context",
            "description": "请求手动压缩上下文历史。当对话过长时使用此工具。",
            "parameters": {"type": "object", "properties": {}}
        }
    },
]
