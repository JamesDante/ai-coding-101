"""
PromptLoader — reads prompt files from prompts/ and renders templates.

Directory layout expected:
  prompts/
    system/   <agent>.md          system prompt for each agent
    user/     <agent>.md          user prompt template (uses {{variable}} placeholders)
    shared/   <name>.md           reusable context blocks
    examples/ <name>.md|yaml      few-shot examples

Template syntax:
  Use {{variable_name}} in .md files for substitution.
  Plain JSON/YAML curly braces are safe — they use single {}.

Usage:
  from prompts import PromptLoader
  loader = PromptLoader()

  system = loader.system("writer", shared=["style_guide", "docusaurus_rules"])
  user   = loader.user("writer", spec=spec_json)
"""
from pathlib import Path


PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class PromptLoader:
    def __init__(self, prompts_dir: Path = PROMPTS_DIR):
        self.dir = prompts_dir

    # ── Loaders ───────────────────────────────────────────────────────────────

    def system(self, name: str, shared: list[str] | None = None) -> str:
        """
        Load a system prompt.
        If shared is given, append those shared context files below a separator.
        """
        parts = [self._read("system", name)]
        if shared:
            for s in shared:
                parts.append(f"\n\n---\n# {s.replace('_', ' ').title()}\n")
                parts.append(self._read("shared", s))
        return "".join(parts).strip()

    def user(self, name: str, **kwargs: str) -> str:
        """
        Load and render a user prompt template.
        kwargs are substituted for {{key}} placeholders.
        """
        template = self._read("user", name)
        return self._render(template, **kwargs)

    def shared(self, name: str) -> str:
        """Load a shared context file as a plain string."""
        return self._read("shared", name)

    def example(self, name: str) -> str:
        """Load an example file (any extension)."""
        # Try exact match first, then search by stem
        direct = self.dir / "examples" / name
        if direct.exists():
            return direct.read_text(encoding="utf-8")
        matches = list((self.dir / "examples").glob(f"{name}.*"))
        if not matches:
            raise FileNotFoundError(f"Example not found: {name!r}")
        return matches[0].read_text(encoding="utf-8")

    # ── Internal ──────────────────────────────────────────────────────────────

    def _read(self, subdir: str, name: str) -> str:
        path = self.dir / subdir / f"{name}.md"
        if not path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {path}\n"
                f"Expected: prompts/{subdir}/{name}.md"
            )
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _render(template: str, **kwargs: str) -> str:
        """Replace {{key}} with the corresponding value from kwargs."""
        for key, value in kwargs.items():
            template = template.replace("{{" + key + "}}", value)
        return template.strip()
