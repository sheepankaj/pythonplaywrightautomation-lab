import pathlib
import platform
import sys
from collections.abc import Iterator

import pytest
from dotenv import load_dotenv
from pytest_html import extras as html_extras  # type: ignore[import-untyped]

from framework.utils.step_decorator import get_current_steps, reset_steps

load_dotenv()

_ROOT = pathlib.Path(__file__).parent


def pytest_configure() -> None:
    # 'reports/' holds pytest-html and allure-results;
    # 'test-results/' is managed by pytest-playwright for traces/screenshots/videos
    (_ROOT / "reports").mkdir(exist_ok=True)


def pytest_sessionfinish() -> None:
    """Write allure environment.properties so the Allure home page shows system info."""
    allure_dir = _ROOT / "reports" / "allure-results"
    if not allure_dir.exists():
        return
    env_file = allure_dir / "environment.properties"
    with env_file.open("w", encoding="utf-8") as f:
        f.write(f"Python={sys.version.split()[0]}\n")
        f.write(f"Platform={platform.system()} {platform.release()}\n")
        f.write("UI.Base.URL=https://www.saucedemo.com\n")
        f.write("API.Base.URL=https://petstore.swagger.io/v2\n")


def pytest_html_report_title(report) -> None:  # type: ignore[no-untyped-def]
    report.title = "Playwright Automation Test Report"


@pytest.fixture(autouse=True)
def _reset_steps() -> Iterator[None]:
    """Clear the step registry before each test so steps don't bleed between tests."""
    reset_steps()
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport():  # type: ignore[no-untyped-def]
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    steps = get_current_steps()
    if not steps:
        return

    rows = "".join(
        f"<tr>"
        f'<td style="padding:6px 14px;border:1px solid #ddd;width:40px">{i}</td>'
        f'<td style="padding:6px 14px;border:1px solid #ddd">{s["name"]}</td>'
        f'<td style="padding:6px 14px;border:1px solid #ddd;font-weight:bold;'
        f'color:{"#2d6a4f" if s["status"] == "passed" else "#c0392b"}">'
        f"{s['status'].upper()}</td>"
        f'<td style="padding:6px 14px;border:1px solid #ddd;color:#c0392b;font-size:0.85em">'
        f"{s['error'] or ''}</td>"
        f"</tr>"
        for i, s in enumerate(steps, 1)
    )

    html = (
        '<table style="width:100%;border-collapse:collapse;margin:8px 0;font-family:monospace;font-size:0.9em">'
        "<thead><tr>"
        '<th style="padding:8px 14px;background:#1b4332;color:#fff;text-align:left">#</th>'
        '<th style="padding:8px 14px;background:#1b4332;color:#fff;text-align:left">Step</th>'
        '<th style="padding:8px 14px;background:#1b4332;color:#fff;text-align:left">Status</th>'
        '<th style="padding:8px 14px;background:#1b4332;color:#fff;text-align:left">Error</th>'
        "</tr></thead>"
        f"<tbody>{rows}</tbody>"
        "</table>"
    )

    extra = getattr(report, "extras", [])
    extra.append(html_extras.html(html))
    report.extras = extra


@pytest.fixture(scope="session")
def base_url() -> str:
    return "https://www.saucedemo.com"
