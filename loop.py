import os
import json
from openai import OpenAI
from tool_use import TOOL_HANDLERS, TOOLS_SCHEMA
from context_compact import micro_compact, estimate_tokens, auto_compact
from background_task import BG_TASK_MANAGER
from autonomous_agent import AUTO_STATE

# 初始化 Qwen 客户端 (通过 DashScope 的 OpenAI 兼容接口)
api_key = os.getenv("DASHSCOPE_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 推荐使用 qwen-plus 或 qwen-max 以获得更好的 Agent 推理能力
MODEL = "qwen-plus"

def _summarize_messages(messages: list) -> str:
    # 用同一个模型做“会话摘要器”，供 auto_compact 调用
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是会话压缩器。请保留目标、已完成操作、未完成事项、关键路径和错误。"},
            {"role": "user", "content": json.dumps(messages, ensure_ascii=False)[:80000]},
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content or "summary unavailable"

def agent_loop(query: str, messages: list) -> str:
    """
    核心 ReAct 循环：思考 -> 调用工具 -> 观察 -> 再次思考
    """
    # 1. 放入用户新的指令
    messages.append({"role": "user", "content": query})
    
    # 限制最大执行步数，防止陷入死循环
    max_steps = 15
    step = 0
    rounds_since_todo = 0
    
    while step < max_steps:
        step += 1
        # 压缩上下文，防止长文本撑爆 Token 限制
        messages = micro_compact(messages)   #处理后只保留最近3轮的工具输出内容
        if estimate_tokens(messages) > 12000:
            # 第二层压缩：超过阈值后自动转摘要上下文
            messages[:] = auto_compact(messages, _summarize_messages)
        
        # === 核心逻辑补充：在每次思考前，检查后台任务队列 ===
        bg_notifs = BG_TASK_MANAGER.drain_notifications()
        if bg_notifs:
            notif_text = "\n".join(f"[bg:{n['task_id']}] 状态:{n['status']} 结果:\n{n['result']}" for n in bg_notifs)
            messages.append({
                "role": "user",
                "content": f"<background-results>\n系统提示：以下是你之前派发的后台任务的执行结果：\n{notif_text}\n</background-results>"
            })
            print(f"  [后台任务完成] 🔔 已将 {len(bg_notifs)} 个后台任务结果注入上下文。")
            
        try:
            # 2. 调用大模型进行思考和决策
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS_SCHEMA,
                temperature=0.2
            )
        except Exception as e:
            return f"API 调用失败，请检查网络和 API Key: {e}"
            
        message = response.choices[0].message
        
        # 3. 将大模型的回复存入上下文（这是 OpenAI 格式的硬性要求：必须包含 tool_calls）
        messages.append(message.model_dump(exclude_none=True))  #排除空值，避免浪费算力
        
        # 4. 判断是否需要调用工具。如果没有 tool_calls，说明大模型认为任务已完成
        if not message.tool_calls:
            # 没有工具调用，视为本轮任务收敛
            AUTO_STATE.tick(had_tool_call=False)
            return message.content
            
        # 5. 执行大模型请求调用的工具
        had_tool_call = False
        manual_compact_requested = False
        for tool_call in message.tool_calls:
            had_tool_call = True
            func_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
                handler = TOOL_HANDLERS.get(func_name)
                
                if handler:
                    print(f"  [Agent 正在执行工具] 🔧 {func_name}: {args}")
                    output = handler(**args)
                    if func_name == "todo":
                        rounds_since_todo = 0
                    if func_name == "compact_context" or output == "__MANUAL_COMPACT__":
                        manual_compact_requested = True
                else:
                    output = f"Error: 未知工具 {func_name}"
            except Exception as e:
                output = f"Error 执行工具 {func_name} 时发生错误: {str(e)}"
                
            # 6. 把工具的执行结果追加到消息列表中 (role="tool")，进入下一轮思考
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": func_name,
                "content": str(output)
            })
        AUTO_STATE.tick(had_tool_call=had_tool_call)
        rounds_since_todo += 1  #防迷失，陷入局部陷阱
        if rounds_since_todo >= 3:
            # todo nag：连续多轮未更新 todo 时注入提醒
            messages.append({
                "role": "user",
                "content": "<reminder>Update your todos.</reminder>",
            })
            rounds_since_todo = 0
        if manual_compact_requested:
            # 第三层压缩：模型手动请求 compact_context 时立即摘要
            messages[:] = auto_compact(messages, _summarize_messages)
            
    return "已达到最大执行步数 (15步)，任务被迫终止。"
