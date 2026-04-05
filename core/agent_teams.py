from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class TeamMessage:
    # sender -> receiver 的最小消息单元
    sender: str  #发信者
    receiver: str  #收信者
    content: str  #消息内容
    request_id: str | None = None


class MessageBus:
    def __init__(self):
        # 每个成员一个收件箱队列
        self.inbox = defaultdict(list)

    def send(self, msg: TeamMessage):
        # 投递消息到 receiver 的收件箱
        self.inbox[msg.receiver].append(msg)

    def pop_all(self, receiver: str) -> List[TeamMessage]:
        # 取走收件箱所有任务，并清空收件箱，避免重复消费
        items = list(self.inbox.get(receiver, []))
        self.inbox[receiver].clear()
        return items


class TeammateManager:
    def __init__(self):
        # members 记录团队成员元信息，bus 负责消息流转
        self.members: Dict[str, Dict] = {}
        self.bus = MessageBus()

    def register(self, name: str, role: str):
        # 注册成员，默认空闲状态
        self.members[name] = {"role": role, "status": "idle"}
        return f"registered {name} as {role}"

    def assign(self, name: str, task: str):
        # 分派任务并投递到成员收件箱
        if name not in self.members:
            return f"unknown member: {name}"
        self.members[name]["status"] = "busy"
        self.bus.send(TeamMessage("manager", name, task))
        return f"assigned to {name}: {task}"

    def inbox(self, name: str):
        # 读取成员收件箱，用于 Agent 轮询任务
        msgs = self.bus.pop_all(name)
        if not msgs:
            return "no messages"
        return "\n".join([f"from={m.sender} content={m.content}" for m in msgs])


TEAM = TeammateManager()
