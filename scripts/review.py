"""
Stage 4 — Reviewer + Fixer Agents
───────────────────────────────────
Reviewer  reads each English MDX doc against its spec → review JSON (score + issues).
Fixer     for docs below MIN_REVIEW_SCORE: rewrites EN doc, then re-translates ZH.

Checkpoint files:
  output/review/<chapter-id>.json
"""
import json
import sys
from pathlib import Path

import llm
from config import (
    DOCS_EN_DIR, DOCS_ZH_DIR, SPECS_DIR, REVIEW_DIR,
    MAX_TOKENS_REVIEW, MAX_TOKENS_DOC,
    MIN_REVIEW_SCORE,
)
from prompts import PromptLoader

loader = PromptLoader()

_SYS_REVIEWER     = loader.system("reviewer",     shared=["docusaurus_rules"])
_SYS_FIXER        = loader.system("fixer",        shared=["docusaurus_rules", "style_guide"])
_SYS_RETRANSLATOR = loader.system("retranslator", shared=["docusaurus_rules"])


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _parse_json(text: str) -> dict:
    """Parse JSON from LLM output, tolerating markdown fences and truncation."""
    # Strip markdown fences
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:] if lines[-1] != "```" else lines[1:-1])
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Extract first JSON object via brace matching (handles trailing prose)
    depth, start = 0, -1
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start != -1:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    break

    # Truncation fallback: return a safe neutral review so pipeline continues
    import sys
    print(f"[WARNING] Could not parse review JSON — returning fallback. Raw: {text[:120]!r}",
          file=sys.stderr)
    return {
        "score": 5,
        "needs_fix": False,
        "issues": [],
        "strengths": [],
        "_parse_error": True,
    }


def _doc_path(spec: dict, base_dir: Path) -> Path:
    cat  = spec.get("category")
    slug = spec["slug"]
    return (base_dir / cat / f"{slug}.mdx") if cat else (base_dir / f"{slug}.mdx")


# ─────────────────────────────────────────────────────────────────────────────
# Reviewer Agent
# ─────────────────────────────────────────────────────────────────────────────

def review_chapter(spec: dict, resume: bool = False) -> dict:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    out_file = REVIEW_DIR / f"{spec['chapter_id']}.json"

    if resume and out_file.exists():
        print(f"[Reviewer Agent]   ↩  {spec['chapter_id']} — loaded from cache")
        return json.loads(out_file.read_text())

    en_path = _doc_path(spec, DOCS_EN_DIR)
    if not en_path.exists():
        print(f"[Reviewer Agent]   ⚠  Skipping {spec['chapter_id']} — EN doc not found")
        return {"chapter_id": spec["chapter_id"], "score": 0,
                "needs_fix": False, "issues": [], "strengths": []}

    print(f"[Reviewer Agent]   Reviewing: {spec['title']!r}")
    user = loader.user(
        "reviewer",
        spec=json.dumps(spec, indent=2),
        doc=en_path.read_text(encoding="utf-8"),
        threshold=str(MIN_REVIEW_SCORE),
    )
    raw    = llm.call(_SYS_REVIEWER, user, role="reviewer", max_tokens=MAX_TOKENS_REVIEW)
    review = _parse_json(raw)
    review.setdefault("chapter_id", spec["chapter_id"])   # always present
    review.setdefault("issues", [])
    review.setdefault("strengths", [])
    review["needs_fix"] = review["score"] < MIN_REVIEW_SCORE

    out_file.write_text(json.dumps(review, indent=2, ensure_ascii=False))
    flag = "⚠  needs fix" if review["needs_fix"] else "✓"
    print(f"[Reviewer Agent]   {flag}  score={review['score']}/10  {spec['chapter_id']}")
    return review


def run_reviewer_agent(specs: list[dict], resume: bool = False) -> list[dict]:
    return [review_chapter(spec, resume=resume) for spec in specs]


# ─────────────────────────────────────────────────────────────────────────────
# Fixer Agent
# ─────────────────────────────────────────────────────────────────────────────

def fix_chapter(spec: dict, review: dict) -> None:
    if not review["needs_fix"] or not review["issues"]:
        return

    en_path = _doc_path(spec, DOCS_EN_DIR)
    zh_path = _doc_path(spec, DOCS_ZH_DIR)
    if not en_path.exists():
        print(f"[Fixer Agent]      ⚠  Skipping {spec['chapter_id']} — EN doc missing")
        return

    # ── Fix English ───────────────────────────────────────────────────────────
    print(f"[Fixer Agent]      Fixing EN: {spec['title']!r}")
    fixed_en = llm.call(
        _SYS_FIXER,
        loader.user(
            "fixer",
            spec=json.dumps(spec, indent=2),
            issues=json.dumps(review["issues"], indent=2),
            doc=en_path.read_text(encoding="utf-8"),
        ),
        role="writer",
        max_tokens=MAX_TOKENS_DOC,
    )
    en_path.write_text(fixed_en, encoding="utf-8")
    print(f"[Fixer Agent]      ✓  EN fixed: {en_path.name}")

    # ── Re-translate Chinese ──────────────────────────────────────────────────
    zh_path.parent.mkdir(parents=True, exist_ok=True)
    current_zh = zh_path.read_text(encoding="utf-8") if zh_path.exists() else ""

    print(f"[Fixer Agent]      Re-translating ZH: {zh_path.name}")
    fixed_zh = llm.call(
        _SYS_RETRANSLATOR,
        loader.user("retranslator", en_doc=fixed_en, zh_doc=current_zh),
        role="writer",
        max_tokens=MAX_TOKENS_DOC,
    )
    zh_path.write_text(fixed_zh, encoding="utf-8")
    print(f"[Fixer Agent]      ✓  ZH re-translated: {zh_path.name}")


def run_fixer_agent(specs: list[dict], reviews: list[dict]) -> None:
    spec_map = {s["chapter_id"]: s for s in specs}
    fixed = 0
    for review in reviews:
        if review["needs_fix"]:
            spec = spec_map.get(review["chapter_id"])
            if spec:
                fix_chapter(spec, review)
                fixed += 1
    print(f"[Fixer Agent]      Fixed {fixed} chapter(s).")


# ─────────────────────────────────────────────────────────────────────────────
# Standalone entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse, os

    ap = argparse.ArgumentParser(description="Run Reviewer + Fixer agents")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--review-only", action="store_true")
    ap.add_argument("--provider", choices=["anthropic", "ollama"], default=None)
    ap.add_argument("--ollama-model", default=None, metavar="MODEL")
    args = ap.parse_args()

    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider
    if args.ollama_model:
        for key in ("OLLAMA_PLANNER_MODEL", "OLLAMA_WRITER_MODEL", "OLLAMA_REVIEWER_MODEL"):
            os.environ[key] = args.ollama_model

    if not SPECS_DIR.exists():
        sys.exit("No specs found — run generate_specs.py first.")

    specs   = [json.loads(f.read_text()) for f in sorted(SPECS_DIR.glob("*.json"))]
    reviews = run_reviewer_agent(specs, resume=args.resume)

    if not args.review_only:
        run_fixer_agent(specs, reviews)
