---
name: accessibility
description: 无障碍审查与修复。WCAG 2.2 AA 合规。使用场景："a11y", "accessibility", "无障碍", "屏幕阅读器"
---

# Accessibility (a11y)

无障碍审查、修复和验证。WCAG 2.2 AA 标准。

## 静态检查清单

### 反模式搜索
- `onClick` 在 div/span 上但无 role + tabIndex + onKeyDown
- `<img>` 无 alt 属性
- `<Button>` 只有图标无 aria-label
- `<input>` 或 `<select>` 无关联 label
- `tabindex > 0`
- `outline: none` 无替代聚焦样式

### 结构检查
- 地标元素：`<main>`, `<nav>`, `<header>`, `<footer>`
- 跳过链接作为第一个可聚焦元素
- 对话框聚焦管理和关闭时恢复
- `aria-required` 在必填字段上

## 修复优先级
1. **可访问名称** (关键) — 每个交互控件必须有名称
2. **键盘访问** (关键) — 不用 div 做按钮，所有元素 Tab 可达
3. **聚焦和对话框** (关键) — 模态框聚焦陷阱，关闭恢复
4. **语义** (高) — 优先原生元素而非 ARIA
5. **表单和错误** (高) — 用 aria-describedby 关联错误
6. **对比度和状态** (中) — 足够对比度，可见聚焦样式

## 规则
- 最小外科手术式修改，不重写大段 UI
- 优先原生 HTML 而非 ARIA workaround
- `<button>` 不用 `<div role="button">`
