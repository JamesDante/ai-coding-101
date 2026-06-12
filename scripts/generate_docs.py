"""
Stage 2 — Writer Agent  (English + Chinese)
────────────────────────────────────────────
For each spec, writes:
  EN → docs/<category?>/<slug>.mdx
  ZH → i18n/zh-Hans/docusaurus-plugin-content-docs/current/<category?>/<slug>.mdx

The Chinese pass receives the English doc as reference for faithful translation.
"""
import json
import sys
from pathlib import Path

import llm
from config import DOCS_EN_DIR, DOCS_ZH_DIR, SPECS_DIR, MAX_TOKENS_DOC
from prompts import PromptLoader

loader = PromptLoader()

# System prompts are assembled once at import time
_SYS_WRITER     = loader.system("writer",     shared=["docusaurus_rules", "style_guide"])
_SYS_TRANSLATOR = loader.system("translator", shared=["docusaurus_rules", "style_guide"])


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _doc_path(spec: dict, base_dir: Path) -> Path:
    slug     = spec["slug"]
    category = spec.get("category")
    return (base_dir / category / f"{slug}.mdx") if category else (base_dir / f"{slug}.mdx")


# ─────────────────────────────────────────────────────────────────────────────
# Writer Agent
# ─────────────────────────────────────────────────────────────────────────────

def write_chapter(spec: dict, resume: bool = False) -> tuple[Path, Path]:
    en_path   = _doc_path(spec, DOCS_EN_DIR)
    zh_path   = _doc_path(spec, DOCS_ZH_DIR)
    spec_json = json.dumps(spec, indent=2)

    # ── English ───────────────────────────────────────────────────────────────
    en_path.parent.mkdir(parents=True, exist_ok=True)
    if resume and en_path.exists():
        print(f"[Writer Agent]     ↩  EN cached: {en_path.relative_to(DOCS_EN_DIR.parent)}")
        en_doc = en_path.read_text(encoding="utf-8")
    else:
        print(f"[Writer Agent]     Writing EN: {en_path.relative_to(DOCS_EN_DIR.parent)}")
        en_doc = llm.call(
            _SYS_WRITER,
            loader.user("writer", spec=spec_json),
            role="writer",
            max_tokens=MAX_TOKENS_DOC,
        )
        en_path.write_text(en_doc, encoding="utf-8")
        print(f"[Writer Agent]     ✓  EN {en_path.name}")

    # ── Chinese ───────────────────────────────────────────────────────────────
    zh_path.parent.mkdir(parents=True, exist_ok=True)
    if resume and zh_path.exists():
        print(f"[Writer Agent]     ↩  ZH cached: {zh_path.relative_to(DOCS_ZH_DIR.parent)}")
    else:
        print(f"[Writer Agent]     Writing ZH: {zh_path.relative_to(DOCS_ZH_DIR.parent)}")
        zh_doc = llm.call(
            _SYS_TRANSLATOR,
            loader.user("translator", spec=spec_json, en_doc=en_doc),
            role="writer",
            max_tokens=MAX_TOKENS_DOC,
        )
        zh_path.write_text(zh_doc, encoding="utf-8")
        print(f"[Writer Agent]     ✓  ZH {zh_path.name}")

    return en_path, zh_path


def _inject_next_chapter_titles(specs: list[dict]) -> None:
    """Add next_chapter_title to each spec based on global ordering from disk."""
    # Build ordered list of all specs on disk to determine true neighbours
    all_specs_ordered: list[dict] = []
    if SPECS_DIR.exists():
        all_specs_ordered = [
            json.loads(f.read_text()) for f in sorted(SPECS_DIR.glob("*.json"))
        ]
    # Fall back to the passed list if disk has nothing (first run)
    if not all_specs_ordered:
        all_specs_ordered = specs

    # Build chapter_id → next title map from the full ordered set
    next_title_map: dict[str, str] = {}
    for i, s in enumerate(all_specs_ordered):
        if i + 1 < len(all_specs_ordered):
            next_title_map[s["chapter_id"]] = all_specs_ordered[i + 1]["title"]
        else:
            next_title_map[s["chapter_id"]] = "Graduation Project"

    for spec in specs:
        spec.setdefault(
            "next_chapter_title",
            next_title_map.get(spec["chapter_id"], ""),
        )


def run_writer_agent(specs: list[dict], resume: bool = False) -> list[dict]:
    _inject_next_chapter_titles(specs)
    results = []
    for spec in specs:
        en_path, zh_path = write_chapter(spec, resume=resume)
        results.append({
            "chapter_id":       spec["chapter_id"],
            "slug":             spec["slug"],
            "category":         spec.get("category"),
            "sidebar_position": spec["sidebar_position"],
            "title":            spec["title"],
            "en_path":          str(en_path),
            "zh_path":          str(zh_path),
        })
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Standalone entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse, os

    ap = argparse.ArgumentParser(description="Run Writer Agent")
    ap.add_argument("--resume", action="store_true")
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

    specs = [json.loads(f.read_text()) for f in sorted(SPECS_DIR.glob("*.json"))]
    if not specs:
        sys.exit("No spec JSON files in output/specs/")

    run_writer_agent(specs, resume=args.resume)
