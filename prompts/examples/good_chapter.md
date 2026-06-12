---
sidebar_position: 1
title: "Prompt Engineering for Code"
description: "Learn to write effective prompts that get Claude to produce correct, maintainable code on the first try."
---

## Learning Objectives

By the end of this chapter you will be able to:
- Write a prompt that specifies language, constraints, and expected output format.
- Apply the Context-Task-Format (CTF) pattern to any coding request.
- Use role prompting to steer Claude's output style.
- Spot and fix the three most common prompting mistakes.

---

## Why Prompts Matter

The quality of Claude's output is directly tied to the quality of your prompt.
Here is the same request written two ways:

```bash title="Terminal — vague prompt"
claude "fix the bug"
```

```bash title="Terminal — specific prompt"
claude "In this TypeScript Express handler (Node 20), the response sometimes sends twice.
Identify the cause and return only the corrected function — no explanation needed."
```

The second prompt names the language, version, symptom, and desired output format.
Claude has everything it needs to produce a precise, usable answer.

## The CTF Pattern

CTF stands for **Context → Task → Format**.

| Part    | Question it answers          | Example                              |
|---------|------------------------------|--------------------------------------|
| Context | What is the environment?     | "In a Python 3.12 FastAPI project…"  |
| Task    | What do you want done?       | "…write a JWT auth middleware…"      |
| Format  | How should the output look?  | "…return only the class, no imports" |

Applied together:

```bash title="Terminal"
claude "In a Python 3.12 FastAPI project, write a JWT auth middleware that reads
the Bearer token from the Authorization header and raises HTTPException(401) on failure.
Return only the class definition, no imports or test code."
```

:::tip
Save your best prompts in a `prompts/` folder. Treat them like code — version-control them
and reuse them across projects.
:::

## Role Prompting

Prefixing your prompt with a persona focuses Claude's response style.

```bash title="Terminal"
claude "Act as a senior Python engineer doing a code review.
Review this function for naming conventions, edge cases, and performance.
Flag issues as ERROR / WARNING / SUGGESTION."
```

Without the role prefix, Claude gives a generic review.
With it, Claude flags Python-specific conventions (snake_case, type hints, etc.).

## Common Mistakes

**1. Missing language or version**
Bad: "Write a function that parses dates."
Fix: "In JavaScript (ES2022), write a function that parses ISO 8601 date strings…"

**2. No output format specified**
Bad: "Explain this code."
Fix: "Explain this code in 3 bullet points, each under 15 words."

**3. Two tasks in one prompt**
Bad: "Refactor this function and write tests for it."
Fix: Two separate prompts — refactor first, then ask for tests on the refactored version.

:::warning
Never ask Claude to "fix my code" without including the code.
Always paste the relevant snippet directly in the prompt.
:::

## Exercise

Take any function from a project you are currently working on and write three versions
of a prompt for it using CTF:
1. A refactor request.
2. A code review.
3. A documentation request.

Compare Claude's outputs and note which CTF formulation produced the most useful result.

## Summary

- Specific prompts produce specific results — always include language, version, and constraints.
- The **CTF pattern** (Context → Task → Format) is the fastest way to improve output quality.
- Role prompting shapes Claude's tone and focus without changing what it knows.
- One task per prompt — split complex requests into steps.

## What's Next

In the next chapter, [Working with Claude Code CLI](../claude-code-cli), you will explore
the full set of CLI commands, slash commands, and memory files that make Claude Code
a first-class tool in your daily workflow.
