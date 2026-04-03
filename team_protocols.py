import uuid
from dataclasses import dataclass
from typing import Dict


@dataclass
class ApprovalRequest:
    # 统一的审批请求对象，便于跨 Agent 协议流转
    request_id: str
    requester: str
    action: str
    status: str

"""
角色	              核心职责
主 Agent（任务发布者）	拆解大任务为子任务、发布子任务到「任务池」、审批子 Agent 的领取请求（可选）、监控任务进度
子 Agent（任务执行者）	监听「任务池」、自动领取未被认领的子任务、执行任务、更新任务状态
任务管理器（核心中间件）	统一存储任务（ID、内容、状态、执行者等）、提供「发布 / 领取 / 更新 / 查询」接口（类比你的 ProtocolManager）
"""
class ProtocolManager:
    def __init__(self):
        # 内存态存储请求，后续可替换为持久化存储
        self.requests: Dict[str, ApprovalRequest] = {}

    def request_approval(self, requester: str, action: str):
        # 创建审批请求，返回 request_id 作为后续追踪键
        request_id = str(uuid.uuid4())[:8]
        req = ApprovalRequest(request_id, requester, action, "pending")
        self.requests[request_id] = req
        return f"approval request created: {request_id}"

    def decide(self, request_id: str, decision: str):
        # 统一处理 approve/reject
        req = self.requests.get(request_id)
        if not req:
            return "request not found"
        req.status = "approved" if decision == "approve" else "rejected"
        return f"{request_id} => {req.status}"

    def get(self, request_id: str):
        # 查询审批状态，便于 Agent 在后续步骤继续判断
        req = self.requests.get(request_id)
        if not req:
            return "request not found"
        return f"id={req.request_id} requester={req.requester} action={req.action} status={req.status}"


PROTOCOLS = ProtocolManager()
