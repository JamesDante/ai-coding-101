"""
Shared configuration for the doc-generation pipeline.
All paths are resolved relative to this file so the scripts work
regardless of the working directory they are invoked from.

Provider selection:
  Set LLM_PROVIDER=anthropic (default) or LLM_PROVIDER=ollama in your env / .env file.
  Individual model names can also be overridden via environment variables.
"""
import os
from pathlib import Path

# ── Directory layout ──────────────────────────────────────────────────────────
SCRIPTS_DIR   = Path(__file__).parent
ROOT_DIR      = SCRIPTS_DIR.parent

# Docusaurus content targets
DOCS_EN_DIR   = ROOT_DIR / "docs"
DOCS_ZH_DIR   = (
    ROOT_DIR / "i18n" / "zh-Hans"
    / "docusaurus-plugin-content-docs" / "current"
)
SIDEBARS_FILE = ROOT_DIR / "sidebars.ts"

# Pipeline intermediate state (checkpointing)
OUTPUT_DIR  = SCRIPTS_DIR / "output"
SPECS_DIR   = OUTPUT_DIR / "specs"
REVIEW_DIR  = OUTPUT_DIR / "review"

# ── Anthropic models ──────────────────────────────────────────────────────────
ANTHROPIC_PLANNER_MODEL  = "claude-opus-4-8"
ANTHROPIC_WRITER_MODEL   = "claude-sonnet-4-6"
ANTHROPIC_REVIEWER_MODEL = "claude-sonnet-4-6"

# ── Ollama models ─────────────────────────────────────────────────────────────
# Override any of these with the corresponding env variable, e.g.:
#   OLLAMA_PLANNER_MODEL=llama3.1:70b python generate_site.py …
#
# Recommended models (pull with: ollama pull <name>):
#   llama3.1:8b       — fast, good for most tasks
#   llama3.1:70b      — higher quality, needs ~48 GB RAM
#   qwen2.5-coder:7b  — optimised for code generation
#   deepseek-r1:8b    — strong reasoning, good for planning
OLLAMA_BASE_URL      = "http://localhost:11434/v1"
OLLAMA_PLANNER_MODEL  = "gemma4:31b-it-q4_K_M"
OLLAMA_WRITER_MODEL   = "gemma4:26b-a4b-it-q4_K_M"
OLLAMA_REVIEWER_MODEL = "gemma4:26b-a4b-it-q4_K_M"

# ── Token budgets ─────────────────────────────────────────────────────────────
MAX_TOKENS_PLAN   = 8192   # curriculum + spec JSON
MAX_TOKENS_DOC    = 8192   # full MDX article
MAX_TOKENS_REVIEW = 6144   # review JSON (7 weighted dimensions + issues array)

# ── Quality gate ──────────────────────────────────────────────────────────────
MIN_REVIEW_SCORE = 7
