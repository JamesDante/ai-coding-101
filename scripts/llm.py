"""
LLM provider abstraction
────────────────────────
Single entry point for all agent API calls.
Supports Anthropic (cloud) and Ollama (local) via a common interface.

Provider is selected by the LLM_PROVIDER environment variable:
  LLM_PROVIDER=anthropic   (default)
  LLM_PROVIDER=ollama

Model roles:
  "planner"  — curriculum + spec agents  (needs strong reasoning)
  "writer"   — writer + translator + fixer
  "reviewer" — reviewer agent

Usage:
  from llm import call
  text = call(system_prompt, user_prompt, role="writer", max_tokens=8192)
"""
import os
from abc import ABC, abstractmethod
from typing import Literal

Role = Literal["planner", "writer", "reviewer"]


# ─────────────────────────────────────────────────────────────────────────────
# Abstract backend
# ─────────────────────────────────────────────────────────────────────────────

class _Backend(ABC):
    @abstractmethod
    def complete(self, system: str, user: str, model: str, max_tokens: int) -> str: ...


# ─────────────────────────────────────────────────────────────────────────────
# Anthropic backend
# ─────────────────────────────────────────────────────────────────────────────

class _AnthropicBackend(_Backend):
    def __init__(self) -> None:
        import anthropic  # lazy import — not required if using Ollama
        self._client = anthropic.Anthropic()

    def complete(self, system: str, user: str, model: str, max_tokens: int) -> str:
        msg = self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return msg.content[0].text.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Ollama backend  (OpenAI-compatible endpoint)
# ─────────────────────────────────────────────────────────────────────────────

class _OllamaBackend(_Backend):
    def __init__(self, base_url: str) -> None:
        from openai import OpenAI  # lazy import
        self._client = OpenAI(
            base_url=base_url,
            api_key="ollama",  # required by the openai SDK; ignored by Ollama
        )

    def complete(self, system: str, user: str, model: str, max_tokens: int) -> str:
        resp = self._client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            max_tokens=max_tokens,
            temperature=0.2,   # lower temp for more deterministic structured output
        )
        return resp.choices[0].message.content.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Provider registry  (lazy-initialised singletons)
# ─────────────────────────────────────────────────────────────────────────────

_backends: dict[str, _Backend] = {}


def _get_backend() -> tuple[_Backend, dict[Role, str]]:
    """Return (backend, role→model_name mapping) for the active provider."""
    import config  # imported here to avoid circular dep during testing

    provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()

    if provider == "anthropic":
        if "anthropic" not in _backends:
            _backends["anthropic"] = _AnthropicBackend()
        models: dict[Role, str] = {
            "planner":  config.ANTHROPIC_PLANNER_MODEL,
            "writer":   config.ANTHROPIC_WRITER_MODEL,
            "reviewer": config.ANTHROPIC_REVIEWER_MODEL,
        }
        return _backends["anthropic"], models

    elif provider == "ollama":
        base_url = os.environ.get("OLLAMA_BASE_URL", config.OLLAMA_BASE_URL)
        key = f"ollama:{base_url}"
        if key not in _backends:
            _backends[key] = _OllamaBackend(base_url)
        models = {
            "planner":  os.environ.get("OLLAMA_PLANNER_MODEL",  config.OLLAMA_PLANNER_MODEL),
            "writer":   os.environ.get("OLLAMA_WRITER_MODEL",   config.OLLAMA_WRITER_MODEL),
            "reviewer": os.environ.get("OLLAMA_REVIEWER_MODEL", config.OLLAMA_REVIEWER_MODEL),
        }
        return _backends[key], models

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER={provider!r}. "
            "Supported values: 'anthropic', 'ollama'"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def call(system: str, user: str, role: Role, max_tokens: int) -> str:
    """
    Call the active LLM provider with the appropriate model for the given role.

    Args:
        system:     System prompt string.
        user:       User prompt string.
        role:       "planner" | "writer" | "reviewer"
        max_tokens: Maximum tokens in the response.

    Returns:
        The model's text response, stripped of leading/trailing whitespace.
    """
    backend, models = _get_backend()
    return backend.complete(system, user, models[role], max_tokens)


def active_provider() -> str:
    return os.environ.get("LLM_PROVIDER", "anthropic").lower()
