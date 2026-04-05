---
name: dependency-audit
description: 依赖管理。分析、测试、升级项目依赖。一个 PR 搞定，不是 47 个版本 bump。使用场景："upgrade deps", "dependency audit", "检查依赖"
---

# Dependency Audit

分析、测试、升级依赖。

## 工作流

### Phase 0: 基线
运行项目完整测试套件。测试失败则 **停止**——不能区分是升级导致的还是基线就有问题。

### Phase 1: 发现
检测项目生态并运行审计：

| 生态 | 检查命令 |
|------|---------|
| Python | `pip list --outdated` + `pip-audit` |
| Node | `npm outdated` + `npm audit` |

分类过时依赖：
- **Patch** (1.2.3 → 1.2.4): 安全，直接升级
- **Minor** (1.2.3 → 1.3.0): 通常安全，快速扫 Changelog
- **Major** (1.2.3 → 2.0.0): 需要完整分析，可能有破坏性变更

列出所有已知 CVE 及严重程度。

### Phase 2: 分析
对非 Patch 升级和安全标记的依赖分析：
- **Changelog**: 读更新日志，标记破坏性变更
- **可达性**: CVE 影响的函数是否被项目调用
- **行为变更**: API 表面变化、安装脚本、权限变更

### Phase 3: 升级
按风险顺序升级：
1. Patches → 一次全部，单个 commit
2. 安全修复 → 每个 fix 一个 commit
3. Minors → 按生态分组
4. Majors → 每个包一个 commit（方便 bisect）

### Phase 4: 测试
每组升级后运行测试套件。失败的包回退并记录原因。

## 注意事项
- 无 lockfile 不升级（无法 reproducible diff）
- 不批量升级所有包（无法 bisect）
- 重大版本无迁移指南 → 升级给人工决策
- 检查传递依赖（直接依赖升级可能拉入传递依赖的大版本）
