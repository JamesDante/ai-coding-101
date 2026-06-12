"""
Pipeline Orchestrator
─────────────────────
Runs all agents in sequence:

  Curriculum Agent  (generate_specs.py)
       ↓
  Spec Agent        (generate_specs.py)
       ↓
  Writer Agent      (generate_docs.py)   → docs/  +  i18n/zh-Hans/
       ↓
  Sidebar Builder   (build_sidebar.py)   → sidebars.ts + _category_.json
       ↓
  Reviewer Agent    (review.py)          → pass 1
       ↓
  Fixer Agent       (review.py)          → patches docs/ + i18n/zh-Hans/
       ↓
  Reviewer Agent    (review.py)          → pass 2 (post-fix verification)

Usage:
  # Anthropic (default)
  python generate_site.py --outline outline.md

  # Generate only chapter 1
  python generate_site.py --outline outline.md --chapters 1

  # Generate chapters 1-3
  python generate_site.py --outline outline.md --chapters 1-3

  # Generate chapters 1, 3, and 5
  python generate_site.py --outline outline.md --chapters 1,3,5

  # Mix of ranges and individual chapters
  python generate_site.py --outline outline.md --chapters 1-3,5,7-9

  # Local Ollama
  python generate_site.py --outline outline.md --provider ollama

  # Ollama with a specific model
  python generate_site.py --outline outline.md --provider ollama \
      --ollama-model qwen2.5-coder:7b

  # Resume a partial run
  python generate_site.py --outline outline.md --resume

  # Skip review/fix
  python generate_site.py --outline outline.md --skip-review

  # Only review + fix existing docs
  python generate_site.py --review-only

Environment variables:
  ANTHROPIC_API_KEY      required for --provider anthropic
  LLM_PROVIDER           alternative to --provider flag
  OLLAMA_BASE_URL        default: http://localhost:11434/v1
  OLLAMA_PLANNER_MODEL   default: llama3.1:8b
  OLLAMA_WRITER_MODEL    default: llama3.1:8b
  OLLAMA_REVIEWER_MODEL  default: llama3.1:8b
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

# ── Bootstrap: ensure scripts/ is on the path ────────────────────────────────
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from dotenv import load_dotenv
load_dotenv(SCRIPTS_DIR / ".env")          # load .env if present
load_dotenv(SCRIPTS_DIR.parent / ".env")   # also try repo root

from config import OUTPUT_DIR, SPECS_DIR

from generate_specs import run_curriculum_agent, run_spec_agent
from generate_docs  import run_writer_agent
from build_sidebar  import run_sidebar_agent
from review         import run_reviewer_agent, run_fixer_agent


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _banner(text: str) -> None:
    bar = "─" * 60
    print(f"\n{bar}\n  {text}\n{bar}")


def _check_env(provider: str) -> None:
    if provider == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit(
            "Error: ANTHROPIC_API_KEY not set.\n"
            "  export ANTHROPIC_API_KEY=sk-ant-...\n"
            "  or add it to scripts/.env"
        )
    if provider == "ollama":
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        try:
            import urllib.request
            urllib.request.urlopen(base_url.replace("/v1", ""), timeout=3)
        except Exception:
            sys.exit(
                f"Error: Ollama not reachable at {base_url}.\n"
                "  Make sure Ollama is running:  ollama serve\n"
                "  Then pull a model:           ollama pull llama3.1:8b"
            )


def _parse_chapter_filter(spec: str) -> set:
    """
    Parse a chapter-filter string into a set of 1-based chapter indices.

    Accepted formats (combinable with commas):
      "1"          -> {1}
      "1-3"        -> {1, 2, 3}
      "1,3,5"      -> {1, 3, 5}
      "1-3,5,7-9"  -> {1, 2, 3, 5, 7, 8, 9}
    """
    indices = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            indices.update(range(int(lo), int(hi) + 1))
        else:
            indices.add(int(part))
    return indices


def _apply_chapter_filter(chapters: list, filter_spec) -> list:
    """
    Return a filtered subset of chapters.
    Chapters are 1-indexed in the filter (first chapter = 1).
    Returns the original list when filter_spec is None.
    """
    if not filter_spec:
        return chapters
    indices = _parse_chapter_filter(filter_spec)
    filtered = [ch for i, ch in enumerate(chapters, start=1) if i in indices]
    if not filtered:
        sys.exit(
            f"Error: --chapters '{filter_spec}' matched no chapters "
            f"(curriculum has {len(chapters)} chapters)."
        )
    return filtered


def _load_specs(filter_spec=None) -> list:
    if not SPECS_DIR.exists():
        sys.exit("No specs found — run without --stages to start from scratch.")
    specs = [json.loads(f.read_text()) for f in sorted(SPECS_DIR.glob("*.json"))]
    if not specs:
        sys.exit("output/specs/ is empty.")
    if filter_spec:
        indices = _parse_chapter_filter(filter_spec)
        specs = [s for i, s in enumerate(specs, start=1) if i in indices]
        if not specs:
            sys.exit(f"Error: --chapters '{filter_spec}' matched no specs.")
    return specs


# ─────────────────────────────────────────────────────────────────────────────
# Stage runners
# ─────────────────────────────────────────────────────────────────────────────

def stage_plan(outline_path: Path, resume: bool, chapter_filter=None):
    _banner("Stage 1/4 — Curriculum Agent + Spec Agent")
    t0 = time.time()
    # Curriculum always runs in full (needed for spec cross-references)
    curriculum = run_curriculum_agent(outline_path, resume=resume)
    # Apply chapter filter before spec generation
    chapters_to_spec = _apply_chapter_filter(curriculum["chapters"], chapter_filter)
    if chapter_filter:
        n_total = len(curriculum["chapters"])
        n_sel   = len(chapters_to_spec)
        ids     = ", ".join(ch["id"] for ch in chapters_to_spec)
        print(f"  Chapter filter: {n_sel}/{n_total} chapters selected → {ids}")
    # Build a filtered curriculum for the spec agent
    filtered_curriculum = {**curriculum, "chapters": chapters_to_spec}
    specs = run_spec_agent(filtered_curriculum, resume=resume)
    print(f"  Done in {time.time() - t0:.1f}s")
    return curriculum, specs


def stage_write(specs: list, resume: bool) -> list:
    _banner("Stage 2/4 — Writer Agent  (EN + ZH)")
    t0 = time.time()
    results = run_writer_agent(specs, resume=resume)
    print(f"  Done in {time.time() - t0:.1f}s")
    return results


def stage_sidebar(chapter_results: list) -> None:
    _banner("Stage 3/4 — Sidebar Builder Agent")
    t0 = time.time()
    run_sidebar_agent(chapter_results)
    print(f"  Done in {time.time() - t0:.1f}s")


def stage_review(specs: list, resume: bool, fix: bool) -> None:
    _banner("Stage 4/5 — Reviewer Agent" + (" + Fixer Agent" if fix else ""))
    t0 = time.time()
    reviews = run_reviewer_agent(specs, resume=resume)

    chapters_fixed = []
    if fix:
        chapters_fixed = [r["chapter_id"] for r in reviews if r.get("needs_fix")]
        run_fixer_agent(specs, reviews)
    print(f"  Done in {time.time() - t0:.1f}s")

    # Print summary table
    print("\n  Review summary (pass 1):")
    print(f"  {'Chapter':<35} {'Score':>5}  {'Status'}")
    print(f"  {'─'*35}  {'─'*5}  {'─'*10}")
    for r in reviews:
        status = "→ fixing" if (r["needs_fix"] and fix) else ("needs fix" if r["needs_fix"] else "ok")
        print(f"  {r['chapter_id']:<35} {r['score']:>5}/10  {status}")

    # ── Pass 2: re-review only chapters that were fixed ──────────────────────
    if fix and chapters_fixed:
        _banner("Stage 5/5 — Re-Reviewer Agent  (post-fix verification)")
        t1 = time.time()
        fixed_specs = [s for s in specs if s["chapter_id"] in chapters_fixed]
        re_reviews = run_reviewer_agent(fixed_specs, resume=False)  # always fresh
        print(f"  Done in {time.time() - t1:.1f}s")

        print("\n  Review summary (pass 2 — post-fix):")
        print(f"  {'Chapter':<35} {'Score':>5}  {'Status'}")
        print(f"  {'─'*35}  {'─'*5}  {'─'*10}")
        for r in re_reviews:
            status = "still needs fix" if r["needs_fix"] else "✓ ok"
            print(f"  {r['chapter_id']:<35} {r['score']:>5}/10  {status}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="AI doc-generation pipeline for Docusaurus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument(
        "--outline", default="outline.md",
        help="Path to outline file (markdown or JSON). Default: outline.md",
    )
    ap.add_argument(
        "--chapters", default=None, metavar="RANGE",
        help=(
            "Only generate these chapters (1-based). "
            "Formats: '1', '1-3', '1,3,5', '1-3,5'. "
            "Curriculum always runs in full; spec/write/review stages are filtered."
        ),
    )
    ap.add_argument(
        "--resume", action="store_true",
        help="Skip stages whose output files already exist (checkpoint resume)",
    )
    ap.add_argument(
        "--skip-review", action="store_true",
        help="Skip the Reviewer and Fixer agents",
    )
    ap.add_argument(
        "--review-only", action="store_true",
        help="Only run Reviewer + Fixer on existing docs (requires cached specs)",
    )
    ap.add_argument(
        "--no-fix", action="store_true",
        help="Run Reviewer but do not apply fixes",
    )
    ap.add_argument(
        "--provider", choices=["anthropic", "ollama"], default=None,
        help="LLM provider (default: $LLM_PROVIDER or 'anthropic')",
    )
    ap.add_argument(
        "--ollama-model", default=None, metavar="MODEL",
        help="Set all three Ollama model slots to this model, e.g. qwen2.5-coder:7b",
    )
    ap.add_argument(
        "--ollama-url", default=None, metavar="URL",
        help="Ollama base URL (default: http://localhost:11434/v1)",
    )
    args = ap.parse_args()

    # ── Apply provider / model overrides to env so llm.py picks them up ──────
    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider
    if args.ollama_model:
        os.environ["OLLAMA_PLANNER_MODEL"]  = args.ollama_model
        os.environ["OLLAMA_WRITER_MODEL"]   = args.ollama_model
        os.environ["OLLAMA_REVIEWER_MODEL"] = args.ollama_model
    if args.ollama_url:
        os.environ["OLLAMA_BASE_URL"] = args.ollama_url

    provider = os.environ.get("LLM_PROVIDER", "anthropic")
    _check_env(provider)

    total_start = time.time()

    # ── review-only shortcut ──────────────────────────────────────────────────
    if args.review_only:
        specs = _load_specs(filter_spec=args.chapters)
        stage_review(specs, resume=args.resume, fix=not args.no_fix)
        print(f"\nPipeline complete in {time.time() - total_start:.1f}s")
        return

    # ── Full pipeline ─────────────────────────────────────────────────────────
    outline_path = Path(args.outline)
    if not outline_path.is_absolute():
        outline_path = SCRIPTS_DIR / outline_path
    if not outline_path.exists():
        sys.exit(
            f"Outline file not found: {outline_path}\n"
            f"Create it or pass --outline <path>"
        )

    _banner("AI Doc Generation Pipeline")
    print(f"  Outline  : {outline_path}")
    print(f"  Provider : {provider}")
    print(f"  Resume   : {args.resume}")
    print(f"  Chapters : {args.chapters or 'all'}")
    print(f"  Review   : {'skip' if args.skip_review else 'yes'}")

    # Stage 1: Plan (curriculum full, specs filtered)
    _curriculum, specs = stage_plan(outline_path, resume=args.resume,
                                    chapter_filter=args.chapters)

    # Stage 2: Write
    chapter_results = stage_write(specs, resume=args.resume)

    # Stage 3: Sidebar
    stage_sidebar(chapter_results)

    # Stage 4: Review + Fix
    if not args.skip_review:
        stage_review(specs, resume=args.resume, fix=not args.no_fix)

    elapsed = time.time() - total_start
    _banner(f"Pipeline complete in {elapsed:.1f}s")
    print(f"  EN docs  → docs/")
    print(f"  ZH docs  → i18n/zh-Hans/docusaurus-plugin-content-docs/current/")
    print(f"  Sidebar  → sidebars.ts (autogenerated)")
    print()


if __name__ == "__main__":
    main()
