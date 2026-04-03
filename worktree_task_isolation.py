from pathlib import Path
import json


class WorktreeTaskIsolation:
    def __init__(self, base_dir: str = ".worktrees"):
        # 每个 task 绑定一个独立工作目录，避免并行任务互相污染
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(exist_ok=True)
        # task_id -> worktree_path 的映射文件
        self.map_file = self.base_dir / "task_map.json"
        if not self.map_file.exists():
            self.map_file.write_text("{}", encoding="utf-8")

    def _load_map(self):
        return json.loads(self.map_file.read_text(encoding="utf-8"))

    def _save_map(self, data):
        self.map_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def bind(self, task_id: int):
        # 绑定任务到工作目录；已绑定则直接返回
        data = self._load_map()
        if str(task_id) in data:
            return f"task {task_id} already bound to {data[str(task_id)]}"
        worktree = self.base_dir / f"task_{task_id}"
        worktree.mkdir(exist_ok=True)
        data[str(task_id)] = str(worktree)
        self._save_map(data)
        return f"bound task {task_id} -> {worktree}"

    def unbind(self, task_id: int):
        # 任务完成后解除绑定
        data = self._load_map()
        path = data.pop(str(task_id), None)
        self._save_map(data)
        return f"unbound task {task_id} ({path})"

    def get(self, task_id: int):
        # 查询绑定结果，便于上层调度
        data = self._load_map()
        return data.get(str(task_id), "not bound")


WORKTREE_ISOLATION = WorktreeTaskIsolation()
