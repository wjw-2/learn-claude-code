class TodoManager:
    """
    任务管理器：
    用于大模型(Agent)自我规划和管理复杂任务进度。
    核心规则：同一时间只能有一个任务处于 "in_progress" 状态。
    """
    def __init__(self):
        self.items = []

    def update(self, items: list) -> str:
        validated = []
        in_progress_count = 0
        
        for item in items:
            status = item.get("status", "pending")
            if status == "in_progress":
                in_progress_count += 1
                
            validated.append({
                "id": item.get("id", "unknown"),
                "text": item.get("text", "无描述"),
                "status": status
            })
            
        if in_progress_count > 1:
            return "更新失败: 一次只能有一个任务处于 in_progress (进行中) 状态，请重新调整并提交任务列表。"
            
        self.items = validated
        return f"任务列表更新成功！\n{self.render()}"

    def render(self) -> str:
        """渲染当前的任务列表状态"""
        if not self.items:
            return "当前没有任务。"
            
        lines = ["--- 当前 Todo 列表 ---"]
        for t in self.items:
            # 根据状态加个图标，看着更直观
            icon = " "
            if t['status'] == 'completed':
                icon = "✅"
            elif t['status'] == 'in_progress':
                icon = "⏳"
            elif t['status'] == 'pending':
                icon = "📝"
                
            lines.append(f"{icon} [{t['status'].upper()}] {t['id']}: {t['text']}")
        lines.append("----------------------")
        return "\n".join(lines)

# 实例化全局任务管理器供 tool_use.py 调用
TODO = TodoManager()
