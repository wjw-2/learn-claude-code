import json

def micro_compact(messages: list, keep_recent_tool_results: int = 3) -> list:
    # 第一层：微观压缩
    # 仅保留最近 N 次工具输出的完整内容，更早的调用工具输出的长的内容替换为占位符，短的继续保存
    tool_indices = []
    for i, msg in enumerate(messages):
        if msg.get("role") == "tool" and isinstance(msg.get("content"), str):
            tool_indices.append(i)
    if len(tool_indices) <= keep_recent_tool_results:
        return messages
    for idx in tool_indices[:-keep_recent_tool_results]:
        content = messages[idx].get("content", "")
        if len(content) > 1000:
            messages[idx]["content"] = "[Previous tool output compacted]"  #把最近N轮之前的工具输出删除
    return messages


def estimate_tokens(messages: list) -> int:
    # 轻量估算：按“约 4 字符 ~= 1 token”粗略估算
    raw = json.dumps(messages, ensure_ascii=False)
    return max(1, len(raw) // 4)


def auto_compact(messages: list, summarize_fn) -> list:
    # 第二层：自动压缩
    # 当上下文过长时，调用 summarize_fn 生成摘要并重建短上下文
    summary = summarize_fn(messages)
    return [
        {"role": "system", "content": "以下是压缩后的会话摘要，请继续保持任务连续性。"},
        {"role": "user", "content": f"[Compressed Context]\n{summary}"},
        {"role": "assistant", "content": "已接收压缩摘要，继续执行。"},
    ]
