class AutonomousState:
    def __init__(self):
        # idle_rounds 记录连续“无工具调用”轮次，用于触发自治策略
        self.idle_rounds = 0
        # auto_mode 打开后，允许 Agent 在空闲时自动做下一步动作
        self.auto_mode = False

    def enable(self):
        self.auto_mode = True
        return "autonomous mode enabled"

    def disable(self):
        self.auto_mode = False
        return "autonomous mode disabled"

    def tick(self, had_tool_call: bool):
        # 每轮循环更新一次空闲计数
        if had_tool_call:
            self.idle_rounds = 0
        else:
            self.idle_rounds += 1
        return self.idle_rounds


AUTO_STATE = AutonomousState()
