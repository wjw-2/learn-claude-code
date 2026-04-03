import threading
import uuid
import subprocess
from pathlib import Path

# 将工作区限制在当前目录
WORKSPACE = Path(".").resolve()

class BackgroundTaskManager:
    """
    后台任务系统 (Background Tasks):
    允许 Agent 将耗时的命令（如 npm install, pytest）丢到后台子线程运行，
    主线程可以继续对话。跑完后结果会注入到消息历史中。
    """
    def __init__(self):
        self.tasks = {}
        self.notification_queue = []
        self._lock = threading.Lock()

    def run(self, command: str) -> str:
        """启动一个后台任务"""
        # 同样引入危险操作拦截（因为 _requires_human_approval 定义在 tool_use 中，这里简单复刻或直接在此处询问）
        import re
        DANGEROUS_COMMANDS_PATTERN = re.compile(
            r"\b(del|rm|rmdir|format|mkfs|diskpart|shutdown|reboot|chmod|chown|kill|taskkill|wget|curl)\b",
            re.IGNORECASE
        )
        if DANGEROUS_COMMANDS_PATTERN.search(command) or "cd .." in command or "cd /" in command or "cd \\" in command:
            print(f"\n⚠️  [后台任务安全拦截] Agent 试图在后台执行高危命令: \033[91m{command}\033[0m")
            while True:
                confirm = input("是否允许后台执行？(y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    print("✅ 用户已授权执行。")
                    break
                elif confirm in ['n', 'no']:
                    print("❌ 用户已拒绝该命令。")
                    return f"执行失败: 用户拒绝了后台执行危险命令 '{command}'。"
                else:
                    print("请输入 y 或 n。")

        task_id = str(uuid.uuid4())[:8]
        self.tasks[task_id] = {"status": "running", "command": command}
        
        thread = threading.Thread(
            target=self._execute, args=(task_id, command), daemon=True)
        thread.start()
        
        return f"后台任务 [bg:{task_id}] 已启动。你可以继续执行其他操作，任务完成后系统会自动通知你。"

    def _execute(self, task_id, command):
        """在子线程中实际执行命令"""
        try:
            r = subprocess.run(command, shell=True, cwd=WORKSPACE,
                capture_output=True, text=True, timeout=300)
            output = r.stdout + "\n" + r.stderr
        except subprocess.TimeoutExpired:
            output = "Error: Timeout (300s)"
        except Exception as e:
            output = f"Error: {str(e)}"
            
        with self._lock:
            # 截断超长输出，防止撑爆 Token
            self.notification_queue.append({
                "task_id": task_id, 
                "status": "completed", 
                "result": output.strip()[:1000] or "执行成功，无输出"
            })
            self.tasks[task_id]["status"] = "completed"

    def drain_notifications(self) -> list:
        """排空通知队列，获取所有已完成的任务结果"""
        with self._lock:
            notifs = list(self.notification_queue)
            self.notification_queue.clear()
            return notifs

# 实例化全局后台任务管理器
BG_TASK_MANAGER = BackgroundTaskManager()
