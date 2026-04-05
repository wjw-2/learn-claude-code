import re
import subprocess
from pathlib import Path


WORKSPACE = Path(".").resolve()

DANGEROUS_COMMANDS_PATTERN = re.compile(
    r"\b(del|rm|rmdir|format|mkfs|diskpart|shutdown|reboot|chmod|chown|kill|taskkill|wget|curl)\b",
    re.IGNORECASE,
)


def _requires_human_approval(command: str) -> bool:
    if DANGEROUS_COMMANDS_PATTERN.search(command):
        return True
    if "cd /" in command or "cd \\" in command or "cd .." in command:
        return True
    return False


def save_path(p: str) -> Path:
    path = (WORKSPACE / p).resolve()
    if not path.is_relative_to(WORKSPACE):
        raise ValueError(f"安全警告: 拒绝访问工作区外的路径: {p}")
    return path


def run_bash(command: str) -> str:
    if _requires_human_approval(command):
        print(f"\n[SECURITY] Agent attempted dangerous command: \033[91m{command}\033[0m")
        while True:
            confirm = input("Allow execution? (y/n): ").strip().lower()
            if confirm in ["y", "yes"]:
                print("[OK] User authorized execution.")
                break
            elif confirm in ["n", "no"]:
                print("[DENIED] User rejected the command.")
                return f"Execution failed: security protocol rejected dangerous command '{command}'."
            else:
                print("Please enter y or n.")

    try:
        r = subprocess.run(
            command, shell=True, cwd=WORKSPACE, capture_output=True, text=True, timeout=60
        )
        output = r.stdout + "\n" + r.stderr
        return output.strip() or "命令执行成功，但没有输出任何内容。"
    except Exception as e:
        return f"执行失败: {str(e)}"


def run_read(path: str, limit: int = None) -> str:
    try:
        text = save_path(path).read_text(encoding="utf-8")
        lines = text.splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit]
        return "\n".join(lines)
    except Exception as e:
        return f"read error: {str(e)}"


def run_write(path: str, content: str) -> str:
    try:
        target = save_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"wrote {path}"
    except Exception as e:
        return f"write error: {str(e)}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        target = save_path(path)
        content = target.read_text(encoding="utf-8")
        if old_text not in content:
            return "edit error: old_text not found"
        target.write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
        return f"edited {path}"
    except Exception as e:
        return f"edit error: {str(e)}"
