from langchain_core.tools import tool

from core.tool_helpers import run_bash, run_read, run_write, run_edit
from core.todo_write import TODO
from core.background_task import BG_TASK_MANAGER
from core.dag_task_system import DAG_TASKS
from core.skills_loader import SKILL_LOADER
from core.agent_teams import TEAM
from core.team_protocols import PROTOCOLS
from core.autonomous_agent import AUTO_STATE
from core.worktree_task_isolation import WORKTREE_ISOLATION
from agent.subagent import run_subagent


@tool
def bash(command: str) -> str:
    """执行终端/命令行指令。可以用来运行代码、安装依赖、查看系统信息等。如果需要查看当前目录文件，可以使用 dir (Windows) 或 ls (Linux/Mac)。"""
    return run_bash(command)


@tool
def read_file(path: str, limit: int = None) -> str:
    """读取本地文件内容。"""
    return run_read(path, limit)


@tool
def write_file(path: str, content: str) -> str:
    """将内容写入本地文件。注意：这会覆盖原文件。如果是新建文件，也会自动创建所在目录。"""
    return run_write(path, content)


@tool
def edit_file(path: str, old_text: str, new_text: str) -> str:
    """Edit file content with one replacement."""
    return run_edit(path, old_text, new_text)


@tool
def todo(items: list[dict]) -> str:
    """管理任务列表(Todo List)。在执行复杂多步任务时，务必使用此工具来规划和跟踪进度。注意：每次必须且只能有一个任务状态为 in_progress。"""
    return TODO.update(items)


@tool
def delegate_task(prompt: str) -> str:
    """委派一个复杂的子任务给 Sub-Agent 去执行。当你遇到一个需要多步探索、或者你不想让它弄乱你当前思考上下文的任务时，你可以把它外包给子智能体。子智能体执行完毕后会给你返回一份详细的报告。"""
    return run_subagent(prompt)


@tool
def run_background(command: str) -> str:
    """在后台线程执行耗时较长的终端命令（如 npm install, pytest, 构建项目等）。这允许你不用死等命令结束，可以继续做其他事情。当命令执行完毕后，系统会自动把结果通知你。"""
    return BG_TASK_MANAGER.run(command)


@tool
def dag_create(subject: str, description: str = "", blocked_by: list[int] = None) -> str:
    """创建一个带有依赖关系的高级任务(DAG任务图)。适用于需要多步串行/并行协作的大型项目规划。"""
    return DAG_TASKS.create_task(subject, description, blocked_by)


@tool
def dag_update(task_id: int, status: str) -> str:
    """更新高级 DAG 任务的状态。当你把一个任务标记为 'completed' 时，系统会自动解锁依赖它的后续任务。"""
    result = DAG_TASKS.update_task_status(task_id, status)
    if status == "completed":
        WORKTREE_ISOLATION.unbind(task_id)
    return result


@tool
def dag_list() -> str:
    """列出所有高级 DAG 任务的当前状态和依赖关系图。"""
    return DAG_TASKS.list_tasks()


@tool
def load_skill(name: str) -> str:
    """加载特定的技能模板(Skill)。比如当你需要某种特定领域的代码模板时，可以调用此工具获取。"""
    return SKILL_LOADER.get_content(name)


@tool
def reload_skills() -> str:
    """重新扫描并加载 skills 目录下的所有技能文件。"""
    SKILL_LOADER.reload()
    return SKILL_LOADER.get_descriptions()


@tool
def team_register(name: str, role: str) -> str:
    """注册一个团队成员(Teammate)。当需要多个专职 Agent 协作时使用。"""
    return TEAM.register(name, role)


@tool
def team_assign(name: str, task: str) -> str:
    """向指定的团队成员发送消息/分配任务。"""
    return TEAM.assign(name, task)


@tool
def team_inbox(name: str) -> str:
    """查看团队消息收件箱，读取分配给你的任务或回复。"""
    return TEAM.inbox(name)


@tool
def protocol_request(requester: str, action: str) -> str:
    """发起一个团队协议审批请求（如关机、执行敏感操作等）。"""
    return PROTOCOLS.request_approval(requester, action)


@tool
def protocol_decide(request_id: str, decision: str) -> str:
    """审批/决断一个团队协议请求。"""
    return PROTOCOLS.decide(request_id, decision)


@tool
def protocol_get(request_id: str) -> str:
    """查询指定的团队协议请求状态。"""
    return PROTOCOLS.get(request_id)


@tool
def autonomous_mode(enabled: bool = True) -> str:
    """启用或禁用自治模式(允许 Agent 在空闲时自动执行下一步)。"""
    if enabled:
        return AUTO_STATE.enable()
    return AUTO_STATE.disable()


@tool
def worktree_bind(task_id: int) -> str:
    """将任务绑定到一个隔离的工作区(worktree)。"""
    return WORKTREE_ISOLATION.bind(task_id)


@tool
def worktree_unbind(task_id: int) -> str:
    """解绑并清理任务的工作区(worktree)。"""
    return WORKTREE_ISOLATION.unbind(task_id)


@tool
def worktree_get(task_id: int) -> str:
    """获取任务绑定的工作区(worktree)路径。"""
    return WORKTREE_ISOLATION.get(task_id)


@tool
def compact_context() -> str:
    """请求手动压缩上下文历史。当对话过长时使用此工具。"""
    return "__MANUAL_COMPACT__"


# All tools list for binding to the LLM
ALL_TOOLS = [
    bash,
    read_file,
    write_file,
    edit_file,
    todo,
    delegate_task,
    run_background,
    dag_create,
    dag_update,
    dag_list,
    load_skill,
    reload_skills,
    team_register,
    team_assign,
    team_inbox,
    protocol_request,
    protocol_decide,
    protocol_get,
    autonomous_mode,
    worktree_bind,
    worktree_unbind,
    worktree_get,
    compact_context,
]
