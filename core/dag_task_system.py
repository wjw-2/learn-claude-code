import json
from pathlib import Path

class DAGTaskManager:
    """
    高级任务系统 (DAG Task System):
    每个任务作为一个独立的 JSON 文件存储。支持设置前置阻塞任务(blockedBy)。
    当一个任务完成时，系统会自动去其他任务的 blockedBy 列表中清除该任务ID，从而实现级联解锁。
    """
    def __init__(self, tasks_dir: str = ".tasks"):
        self.dir = Path(tasks_dir).resolve()
        self.dir.mkdir(exist_ok=True)

    def _get_next_id(self) -> int:
        max_id = 0
        for f in self.dir.glob("task_*.json"):
            try:
                task = json.loads(f.read_text(encoding='utf-8'))
                max_id = max(max_id, task.get("id", 0))
            except:
                pass
        return max_id + 1

    def save(self, task: dict):
        task_file = self.dir / f"task_{task['id']}.json"
        task_file.write_text(json.dumps(task, indent=2, ensure_ascii=False), encoding='utf-8')

    def load(self, task_id: int) -> dict:
        task_file = self.dir / f"task_{task_id}.json"
        if not task_file.exists():
            raise FileNotFoundError(f"找不到任务 ID: {task_id}")
        return json.loads(task_file.read_text(encoding='utf-8'))

    def create_task(self, subject: str, description: str = "", blocked_by: list = None) -> str:
        task_id = self._get_next_id()
        task = {
            "id": task_id,
            "subject": subject,
            "description": description,  
            "status": "pending",  #状态可以是 pending/in_progress/completed
            "blockedBy": blocked_by or [],  #前置阻塞任务 ID 列表，只有当这些任务都完成了，当前任务才能开始执行
            "owner": "Agent"  #未来可以扩展为具体的子 Agent 或团队成员
        }
        self.save(task)
        return f"创建高级任务成功:\n{json.dumps(task, indent=2, ensure_ascii=False)}"

    def _clear_dependency(self, completed_id: int):
        """核心逻辑：当任务完成时，去解锁依赖它的其他任务"""
        unlocked_tasks = []
        for f in self.dir.glob("task_*.json"):
            task = json.loads(f.read_text(encoding='utf-8'))
            if completed_id in task.get("blockedBy", []):
                task["blockedBy"].remove(completed_id)
                self.save(task)
                if not task["blockedBy"]:
                    unlocked_tasks.append(task['id'])
        return unlocked_tasks

    def update_task_status(self, task_id: int, status: str) -> str:
        try:
            task = self.load(task_id)
            if task["status"] == status:
                return f"任务 {task_id} 状态已经是 {status}，无需更改。"
                
            task["status"] = status
            self.save(task)
            
            result_msg = f"任务 {task_id} 状态已更新为: {status}。"
            
            # 如果任务被标记为完成，触发级联解锁
            if status == "completed":
                unlocked = self._clear_dependency(task_id)
                if unlocked:
                    result_msg += f"\n触发依赖解锁！以下任务现在可以开始执行了: {unlocked}"
                    
            return result_msg
        except Exception as e:
            return f"更新任务失败: {str(e)}"
            
    def list_tasks(self) -> str:
        tasks = []
        for f in self.dir.glob("task_*.json"):
            try:
                tasks.append(json.loads(f.read_text(encoding='utf-8')))
            except:
                pass
        if not tasks:
            return "当前没有高级任务。"
        
        # 按 ID 排序
        tasks.sort(key=lambda x: x["id"])
        
        lines = ["=== DAG 任务依赖图列表 ==="]
        for t in tasks:
            status_icon = "⏳" if t['status'] == 'pending' else "🏃" if t['status'] == 'in_progress' else "✅"
            block_info = f"(等待任务: {t['blockedBy']})" if t.get('blockedBy') else "(可立即执行)"
            lines.append(f"{status_icon} [ID:{t['id']}] {t['subject']} - 状态:{t['status']} {block_info}")
        return "\n".join(lines)

# 全局实例
DAG_TASKS = DAGTaskManager()
