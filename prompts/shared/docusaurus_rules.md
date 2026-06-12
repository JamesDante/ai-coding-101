# Docusaurus MDX Rules

## Required front matter
Every MDX file must open with:
```
---
sidebar_position: <number>
title: "<string>"
description: "<one sentence>"
---
```

## Required sections (in order)
1. `## Learning Objectives` — bullet list of action-verb objectives
2. Content sections from the spec (## headings)
3. `## Exercise` — one hands-on task the reader can do right now
4. `## Summary` — 3–5 bullet recap of key takeaways
5. `## What's Next` — one sentence + link to the next chapter

## Code blocks
- Always include a language tag: ```bash  ```python  ```typescript
- Add a title for named files: ```python title="agent.py"
- Use ```bash title="Terminal" for shell commands

## Admonitions
:::tip    — helpful shortcut or best practice
:::note   — important clarification
:::warning — common mistake or gotcha
:::info   — background context

## Links
- Internal links: [text](../slug) — relative paths only, no absolute URLs
- External links: open in a new tab by appending {target="_blank"}
