"""
Step decorator for test reporting — works with both pytest-html and Allure.

Two usage patterns, same API:

  1. Method decorator on page-object / API-client classes:
        @step("Login with credentials")
        def login(self, username, password): ...

  2. Context manager inside test methods:
        with step("Assert app logo is visible"):
            expect(page.locator(".app_logo")).to_be_visible()

Steps are tracked simultaneously in:
  - A thread-local registry → rendered as an HTML table in the pytest-html report
  - allure.step()           → rendered as expandable steps in the Allure report
"""

import functools
import threading
from collections.abc import Callable
from typing import Any

_registry = threading.local()


def _get_steps() -> list[dict]:
    if not hasattr(_registry, "steps"):
        _registry.steps = []
    return _registry.steps


def reset_steps() -> None:
    _registry.steps = []


def get_current_steps() -> list[dict]:
    return list(_get_steps())


class step:
    """
    Named step — use as @step("title") decorator or with step("title"): context manager.
    Feeds both the pytest-html inline table and the Allure step hierarchy.
    """

    def __init__(self, title: str) -> None:
        self.title = title
        self._entry: dict | None = None
        self._allure_ctx: Any | None = None

    # ── decorator usage ────────────────────────────────────────────────────
    def __call__(self, func: Callable) -> Callable:
        title = self.title

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with step(title):
                return func(*args, **kwargs)

        return wrapper

    # ── context-manager usage ──────────────────────────────────────────────
    def __enter__(self) -> "step":
        # pytest-html tracking
        self._entry = {"name": self.title, "status": "passed", "error": None}
        _get_steps().append(self._entry)

        # Allure tracking (transparent — no-op if allure-pytest is not installed)
        try:
            import allure  # type: ignore[import-untyped]

            self._allure_ctx = allure.step(self.title)
            self._allure_ctx.__enter__()
        except ImportError:
            pass

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None and self._entry is not None:
            self._entry["status"] = "failed"
            self._entry["error"] = str(exc_val)

        if self._allure_ctx is not None:
            self._allure_ctx.__exit__(exc_type, exc_val, exc_tb)

        return False  # never suppress exceptions
