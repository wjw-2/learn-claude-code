import os
import json
from openai import OpenAI
from context_compact import micro_compact

# 子 Agent 依然使用 Qwen 客户端
api_key = os.getenv("DASHSCOPE_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 子 Agent 也可以使用更轻量级的模型，比如 qwen-turbo，这里为了能力统一先用 qwen-plus
MODEL = "qwen-plus"

def run_subagent(prompt: str) -> str:
    """
    运行一个子智能体（Sub-agent）来完成特定的子任务。
    它有自己独立的上下文和思考循环，做完后会向主 Agent 汇报结果。
    """
    print(f"\n  [启动子 Agent] 🚀 接收到委派任务: {prompt[:50]}...")
    
    # 1. 初始化子 Agent 的独立消息列表
    sub_messages = [
        {
            "role": "system", 
            "content": "你是一个子智能体(Sub-Agent)。你的任务是专注且彻底地解决主 Agent 委派给你的特定任务。你需要自己思考并使用工具，完成后给出详细的总结汇报。"
        },
        {"role": "user", "content": prompt}
    ]
    
    # 为了避免循环依赖导入，我们在函数内部导入工具
    # 注意：子 Agent 可以复用主 Agent 的工具集，甚至可以定义自己专属的精简版工具集
    from tool_use import TOOL_HANDLERS, TOOLS_SCHEMA
    
    # 限制子 Agent 的最大执行步数
    max_steps = 10
    step = 0
    
    while step < max_steps:
        step += 1
        sub_messages = micro_compact(sub_messages)
        
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=sub_messages,
                tools=TOOLS_SCHEMA,
                temperature=0.2
            )
        except Exception as e:
            return f"子 Agent 运行出错 (API 调用失败): {e}"
            
        message = response.choices[0].message
        sub_messages.append(message.model_dump(exclude_none=True))
        
        # 如果子 Agent 没有调用工具，说明它认为任务已经完成了，返回最终总结
        if not message.tool_calls:
            print(f"  [子 Agent 任务完成] ✅ 正在向主 Agent 汇报...")
            return f"[子 Agent 汇报]\n{message.content}"
            
        # 如果需要调用工具，则子 Agent 自己去执行
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
                handler = TOOL_HANDLERS.get(func_name)
                
                if handler:
                    print(f"    └─ 子 Agent 正在使用工具 🔧 {func_name}")
                    output = handler(**args)
                else:
                    output = f"Error: 未知工具 {func_name}"
            except Exception as e:
                output = f"Error 执行工具 {func_name} 时发生错误: {str(e)}"
                
            sub_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": func_name,
                "content": str(output)
            })
            
    return "[子 Agent 汇报] 任务未能在规定步数内完成，被迫终止。请主 Agent 检查问题或重新拆分任务。"
