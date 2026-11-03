"""
Serve the Allure report via a local server and open it in the default browser.
Equivalent to: npx playwright show-report (but for Allure)

Requirements:
  Allure CLI:  npm install -g allure-commandline
  Java 11+:    winget install --id Microsoft.OpenJDK.17

Usage: python scripts/show_allure_report.py
"""

import os
import pathlib
import shutil
import subprocess
import sys

RESULTS_DIR = pathlib.Path(__file__).parent.parent / "reports" / "allure-results"
JAVA_HOME_CANDIDATES = [
    r"C:\Program Files\Microsoft\jdk-17.0.21.21-hotspot",
    r"C:\Program Files\Eclipse Adoptium",
    r"C:\Program Files\Java",
]


def _find_java_home() -> str | None:
    """Return a clean JAVA_HOME path (no trailing slash), or None if not found."""
    existing = os.environ.get("JAVA_HOME", "").rstrip("\\/")
    if existing and pathlib.Path(existing, "bin", "java.exe").exists():
        return existing
    for candidate in JAVA_HOME_CANDIDATES:
        p = pathlib.Path(candidate)
        if (p / "bin" / "java.exe").exists():
            return str(p)
        for sub in sorted(p.iterdir(), reverse=True) if p.is_dir() else []:
            if (sub / "bin" / "java.exe").exists():
                return str(sub)
    return None


if not RESULTS_DIR.exists() or not any(RESULTS_DIR.iterdir()):
    print(f"No Allure results found at {RESULTS_DIR}. Run pytest first.")
    sys.exit(1)

if shutil.which("allure") is None:
    print("Allure CLI not found. Install it:")
    print("  npm install -g allure-commandline")
    sys.exit(1)

java_home = _find_java_home()
if java_home is None:
    print("Java not found. Install it:")
    print("  winget install --id Microsoft.OpenJDK.17")
    sys.exit(1)

env = os.environ.copy()
env["JAVA_HOME"] = java_home
env["PATH"] = str(pathlib.Path(java_home) / "bin") + os.pathsep + env.get("PATH", "")

print(f"Using JAVA_HOME: {java_home}")
print(f"Opening Allure report from {RESULTS_DIR} ...")
print("Press Ctrl+C to stop the server.")

try:
    # shell=True is required on Windows to run .cmd files (allure is allure.cmd)
    subprocess.run(
        f'allure serve "{RESULTS_DIR}"',
        env=env,
        shell=True,
    )
except KeyboardInterrupt:
    print("\nAllure server stopped.")
