"""
Stage 1 — Planning agents
─────────────────────────
Curriculum Agent  reads an outline file (markdown or JSON) and outputs a
                  structured curriculum.json with ordered chapter descriptors.

Spec Agent        reads curriculum.json and outputs one spec-<id>.json per
                  chapter — a detailed blueprint the Writer Agent follows.

Checkpoint files:
  output/curriculum.json
  output/specs/<chapter-id>.json
"""
import json
import sys
from pathlib import Path

import llm
from config import OUTPUT_DIR, SPECS_DIR, MAX_TOKENS_PLAN
from prompts import PromptLoader

loader = PromptLoader()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _parse_json(text: str) -> dict:
    """Parse JSON, tolerating markdown fences and partial truncation."""
    # Strip markdown fences
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:] if lines[-1] != "```" else lines[1:-1])
    text = text.strip()

    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Extract first complete JSON object via brace matching
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

    # Re-raise with context so the caller can see the raw output
    raise ValueError(
        f"Could not parse JSON from LLM output. "
        f"First 200 chars: {text[:200]!r}"
    )


def _load_outline(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.dumps(json.loads(text), indent=2)
    return text


# ─────────────────────────────────────────────────────────────────────────────
# Curriculum Agent
# ─────────────────────────────────────────────────────────────────────────────

def run_curriculum_agent(outline_path: Path, resume: bool = False) -> dict:
    out_file = OUTPUT_DIR / "curriculum.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if resume and out_file.exists():
        print("[Curriculum Agent] ↩  Resuming — loaded existing curriculum.json")
        return json.loads(out_file.read_text())

    print(f"[Curriculum Agent] Reading outline: {outline_path}")
    system = loader.system("curriculum", shared=["course_rules"])
    user   = loader.user("curriculum", outline=_load_outline(outline_path))

    raw        = llm.call(system, user, role="planner", max_tokens=MAX_TOKENS_PLAN)
    curriculum = _parse_json(raw)

    out_file.write_text(json.dumps(curriculum, indent=2, ensure_ascii=False))
    n = len(curriculum["chapters"])
    print(f"[Curriculum Agent] ✓  {n} chapters → {out_file.relative_to(out_file.parent.parent)}")
    return curriculum


# ─────────────────────────────────────────────────────────────────────────────
# Spec Agent
# ─────────────────────────────────────────────────────────────────────────────

def run_spec_agent(curriculum: dict, resume: bool = False) -> list[dict]:
    SPECS_DIR.mkdir(parents=True, exist_ok=True)
    specs           = []
    curriculum_json = json.dumps(curriculum, indent=2)
    system          = loader.system("spec")

    for ch in curriculum["chapters"]:
        out_file = SPECS_DIR / f"{ch['id']}.json"

        if resume and out_file.exists():
            print(f"[Spec Agent]       ↩  {ch['id']} — loaded from cache")
            specs.append(json.loads(out_file.read_text()))
            continue

        print(f"[Spec Agent]       Speccing: {ch['title']!r}")
        user = loader.user(
            "spec",
            chapter=json.dumps(ch, indent=2),
            curriculum=curriculum_json,
        )
        raw  = llm.call(system, user, role="planner", max_tokens=MAX_TOKENS_PLAN)
        spec = _parse_json(raw)

        out_file.write_text(json.dumps(spec, indent=2, ensure_ascii=False))
        print(f"[Spec Agent]       ✓  {out_file.name}")
        specs.append(spec)

    return specs


# ─────────────────────────────────────────────────────────────────────────────
# Standalone entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse, os

    ap = argparse.ArgumentParser(description="Run Curriculum + Spec agents")
    ap.add_argument("--outline", default="outline.md")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--provider", choices=["anthropic", "ollama"], default=None)
    ap.add_argument("--ollama-model", default=None, metavar="MODEL")
    args = ap.parse_args()

    if args.provider:
        os.environ["LLM_PROVIDER"] = args.provider
    if args.ollama_model:
        for key in ("OLLAMA_PLANNER_MODEL", "OLLAMA_WRITER_MODEL", "OLLAMA_REVIEWER_MODEL"):
            os.environ[key] = args.ollama_model

    outline_path = Path(args.outline)
    if not outline_path.is_absolute():
        outline_path = Path(__file__).parent / outline_path
    if not outline_path.exists():
        sys.exit(f"Outline file not found: {outline_path}")

    curriculum = run_curriculum_agent(outline_path, resume=args.resume)
    run_spec_agent(curriculum, resume=args.resume)
