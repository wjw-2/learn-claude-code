import os

from langchain_core.messages import SystemMessage, trim_messages
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from agent.state import CodeAgentState
from agent.tools import ALL_TOOLS
from core.background_task import BG_TASK_MANAGER


def _build_llm():
    """构建 DashScope (Qwen) 配置的 LLM 实例。"""
    return ChatOpenAI(
        model="qwen3.6-plus",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature=0.2,
    )


SYSTEM_PROMPT = (
    "你是一个强大的 AI 编程助手和系统控制终端。\n"
    "你可以使用 bash/read_file/write_file/edit_file 完成工程任务。\n"
    "复杂任务先用 todo；耗时命令优先 run_background；分支探索优先 delegate_task。\n"
    "需要多任务依赖时使用 dag_create/dag_update/dag_list。\n"
    "需要技能模板时使用 load_skill；需要团队协作时使用 team_* 与 protocol_*。\n"
    "需要隔离工作目录时使用 worktree_bind/worktree_get/worktree_unbind。\n"
    "在回答问题时，请一步步思考，利用工具去验证你的想法。"
)


def _inject_background_notifications(state: CodeAgentState) -> CodeAgentState:
    """将后台任务的结果注入消息流."""
    notifs = BG_TASK_MANAGER.drain_notifications()
    if notifs:
        notif_lines = []
        for n in notifs:
            result_preview = n["result"][:1000] if len(n["result"]) > 1000 else n["result"]
            notif_lines.append(
                f"[bg:{n['task_id']}] 状态:{n['status']} 结果:\n{result_preview}"
            )
        notif_text = "\n".join(notif_lines)
        print(f"  [BackgroundTask] Injected {len(notifs)} task results into context.")

        # Inject as a user-like system message
        from langchain_core.messages import HumanMessage

        bg_msg = HumanMessage(
            content=f"<background-results>\n系统提示：以下是你之前派发的后台任务的执行结果：\n{notif_text}\n</background-results>"
        )
        return {"messages": [bg_msg]}
    return {}


def _manage_context(state: CodeAgentState) -> CodeAgentState:
    """当对话记录过长时，自动截断消息。保留系统消息及最近的消息以控制在 token 预算内."""
    messages = state["messages"]

    # 仅保留系统消息和最近的25条消息，以保持在token预算内
    MAX_MESSAGES = 25
    if len(messages) > MAX_MESSAGES:
        system_msgs = [m for m in messages[:1] if isinstance(m, SystemMessage)]
        recent = messages[-MAX_MESSAGES + (1 if system_msgs else 0):]
        trimmed = system_msgs + recent
        return {"messages": trimmed}
    return {}


def _agent_node(state: CodeAgentState) -> CodeAgentState:
    """LLM 代理节点：接收消息，决定是调用工具还是响应。"""
    llm = _build_llm().bind_tools(ALL_TOOLS)
    messages = state["messages"]

    # 如果不存在系统消息，则在前面添加系统提示
    has_system = any(isinstance(m, SystemMessage) for m in messages)
    if not has_system:
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm.invoke(messages)
    return {"messages": [response]}


def _check_manual_compact(state: CodeAgentState) -> CodeAgentState:
    """检查是否有任何工具结果请求手动上下文压缩。 """
    messages = state["messages"]
    # 检查最近的工具消息是否存在 __MANUAL_COMPACT__ 标记
    for msg in reversed(messages[-10:]):
        if hasattr(msg, "content") and isinstance(msg.content, str):
            if "__MANUAL_COMPACT__" in msg.content:
                # 将工具输出替换为更简洁的消息
                msg.content = msg.content.replace("__MANUAL_COMPACT__", "上下文已压缩。")
                break

    # 大幅修剪消息历史以释放上下文空间，保留系统消息和最近的消息以控制在 token 预算内
    system_msgs = [m for m in messages[:1] if isinstance(m, SystemMessage)]
    recent = messages[-15:]
    trimmed = system_msgs + recent
    return {"messages": trimmed}


def build_graph():
    """构建并编译代码代理的 LangGraph StateGraph。"""
    builder = StateGraph(CodeAgentState)

    tool_node = ToolNode(ALL_TOOLS)

    # Add nodes
    builder.add_node("background_inject", _inject_background_notifications)
    builder.add_node("manage_context", _manage_context)
    builder.add_node("agent", _agent_node)
    builder.add_node("tools", tool_node)
    builder.add_node("check_compact", _check_manual_compact)

    # Edges
    builder.add_edge(START, "background_inject")
    builder.add_edge("background_inject", "manage_context")
    builder.add_edge("manage_context", "agent")
    builder.add_conditional_edges(
        "agent",
        tools_condition,
        {"tools": "tools", END: END},
    )
    builder.add_edge("tools", "check_compact")
    builder.add_edge("check_compact", "background_inject")

    # Compile with checkpointer
    checkpointer = MemorySaver()
    graph = builder.compile(checkpointer=checkpointer)

    return graph


# 全局实例
agent_graph = build_graph()
