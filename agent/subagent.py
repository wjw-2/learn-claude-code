import os

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


def _build_sub_agent_llm():
    """Build LLM instance for sub-agent with DashScope config."""
    return ChatOpenAI(
        model=os.getenv("DASHSCOPE_MODEL", "qwen3.5-plus"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature=0.2,
    )


def run_subagent(prompt: str) -> str:
    """
    运行一个子智能体（Sub-agent）来完成特定的子任务。
    它有自己独立的上下文和思考循环，做完后会向主 Agent 汇报结果。
    """
    print(f"\n  [SubAgent] Received task: {prompt[:50]}...")

    # Lazy import to avoid circular dependency with agent.tools
    from agent.tools import ALL_TOOLS

    llm = _build_sub_agent_llm()

    sub_agent = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        prompt="你是一个子智能体(Sub-Agent)。你的任务是专注且彻底地解决主 Agent 委派给你的特定任务。你需要自己思考并使用工具，完成后给出详细的总结汇报。",
    )

    result = sub_agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]},
    )

    # Extract the final assistant message
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content and not getattr(msg, "tool_calls", None):
            print(f"  [SubAgent] Task done, reporting to main agent...")
            return f"[子 Agent 汇报]\n{msg.content}"

    print(f"  [SubAgent] Task done, reporting to main agent...")
    return "[子 Agent 汇报] 子 Agent 执行完毕，但未找到最终回复内容。"
