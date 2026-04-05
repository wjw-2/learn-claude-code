class AutonomousState:
    def __init__(self):
        # idle_rounds 记录连续“无工具调用”轮次，用于触发自治策略
        self.idle_rounds = 0
        # auto_mode 打开后，允许 Agent 在空闲时自动做下一步动作
        self.auto_mode = False

    def enable(self):  #开启自治模式后，Agent 会在每轮结束时根据 idle_rounds 判断是否需要自动调用工具或调整策略，以避免陷入思考死循环
        self.auto_mode = True
        return "autonomous mode enabled"

    def disable(self):  #关闭自治模式后，Agent 将不再自动调整策略，完全依赖工具调用来推动任务进展
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
