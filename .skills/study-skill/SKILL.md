---
name: "study-skill"
description: "Explains a code file in a structured learning style. Invoke when user asks to learn unfamiliar code, architecture, or APIs."
---

# Study Skill

## Goal
Help the user quickly understand unfamiliar code with clear structure, key ideas, and practical takeaways.

## When To Use
- User says they do not understand a file, function, or module.
- User asks for architecture walkthrough or interview-style explanation.
- User wants line-by-line interpretation of key code blocks.

## Workflow
1. Summarize what the file does in one sentence.
2. Split explanation into: inputs, outputs, core flow, and edge cases.
3. Explain naming and design choices in plain language.
4. Provide a small example of how data changes across the flow.
5. End with 3 learning checkpoints the user can self-test.

## Output Template
Use this structure:

### 1) 一句话总结
...

### 2) 核心流程
- 步骤 A:
- 步骤 B:
- 步骤 C:

### 3) 关键代码点
- 函数/类名:
- 作用:
- 为什么这样写:

### 4) 容易出错的地方
- ...

### 5) 自测问题
1. ...
2. ...
3. ...

## Constraints
- Keep terms consistent with current codebase naming.
- Prefer concrete examples over abstract definitions.
- Avoid adding unrelated theory.
