from pathlib import Path


class SkillLoader:
    # skills_dir 指向技能目录，目录下每个子目录可放一个 SKILL.md
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        # 结构: {skill_name: {"meta": {...}, "body": "..."}}
        self.skills = {}
        self.reload()

    def parse_frontmatter(self, text: str):
        # 支持最常见的 frontmatter 形式:
        # ---
        # name: xxx
        # description: yyy
        # ---
        # 正文...
        if not text.startswith("---"):
            return {}, text
        parts = text.split("---", 2)
        if len(parts) < 3:
            return {}, text
        raw_meta = parts[1].strip().splitlines()
        body = parts[2].strip()
        meta = {}
        for line in raw_meta:
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")
        return meta, body

    def reload(self):
        # 重新扫描技能目录，适合在运行时热更新
        self.skills = {}
        if not self.skills_dir.exists():
            return
        for f in sorted(self.skills_dir.rglob("SKILL.md")):
            text = f.read_text(encoding="utf-8")
            meta, body = self.parse_frontmatter(text)
            name = meta.get("name", f.parent.name)
            self.skills[name] = {"meta": meta, "body": body}

    def get_descriptions(self) -> str:
        # 返回简短技能清单，用于注入 system prompt
        if not self.skills:
            return "No skills loaded."
        lines = []
        for name, skill in self.skills.items():
            desc = skill["meta"].get("description", "")
            lines.append(f"- {name}: {desc}")
        return "\n".join(lines)

    def get_content(self, name: str) -> str:
        # 返回技能正文，外层用标签包裹，便于模型理解边界
        skill = self.skills.get(name)
        if not skill:
            return f"Error: Skill {name} not found"
        return f"<skill name=\"{name}\">\n{skill['body']}\n</skill>"


SKILL_LOADER = SkillLoader(Path(".skills"))
