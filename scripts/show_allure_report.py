"""
Serve the Allure report in the default browser.

Two modes:

  1. Local results (default) — uses 'allure serve' on reports/allure-results/
     Requires: Allure CLI + Java (see README for install steps)

       python scripts/show_allure_report.py

  2. Pre-built report from CI artifact — serves any allure-report directory over HTTP.
     No Allure CLI or Java needed. Use after downloading the 'allure-report'
     artifact from GitHub Actions and extracting it locally.

       python scripts/show_allure_report.py --report ~/Downloads/allure-report
"""

import argparse
import http.server
import os
import pathlib
import shutil
import socketserver
import subprocess
import sys
import threading
import webbrowser

DEFAULT_RESULTS_DIR = pathlib.Path(__file__).parent.parent / "reports" / "allure-results"
JAVA_HOME_CANDIDATES = [
    r"C:\Program Files\Microsoft\jdk-17.0.21.21-hotspot",
    r"C:\Program Files\Eclipse Adoptium",
    r"C:\Program Files\Java",
]
HTTP_PORT = 9324


def _find_java_home() -> str | None:
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


def _find_index_html(base: pathlib.Path) -> pathlib.Path | None:
    """
    Find index.html inside base, tolerating one extra nesting level.
    GitHub Actions zips sometimes extract as artifact-name/artifact-name/index.html.
    """
    if (base / "index.html").exists():
        return base
    # One level deeper — common when Windows extractor adds an extra folder
    for child in base.iterdir():
        if child.is_dir() and (child / "index.html").exists():
            return child
    return None


def serve_static_report(report_dir: pathlib.Path) -> None:
    """Serve a pre-built allure-report HTML directory over HTTP (no CLI/Java needed)."""
    if not report_dir.exists():
        print(f"Directory not found: {report_dir}")
        sys.exit(1)

    root = _find_index_html(report_dir)
    if root is None:
        contents = [p.name for p in report_dir.iterdir()] if report_dir.exists() else []
        print(f"Could not find index.html in {report_dir} or its subdirectories.")
        print(f"Contents of {report_dir}: {contents or '(empty)'}")
        print("Make sure you have fully extracted the allure-report artifact zip.")
        sys.exit(1)

    os.chdir(root)
    url = f"http://localhost:{HTTP_PORT}/index.html"
    print(f"Serving pre-built Allure report from: {root}")
    print(f"Opening at: {url}")
    print("Press Ctrl+C to stop the server.")

    with socketserver.TCPServer(("", HTTP_PORT), http.server.SimpleHTTPRequestHandler) as httpd:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nAllure server stopped.")


def serve_allure_results(results_dir: pathlib.Path) -> None:
    """Generate and serve Allure report from raw results using Allure CLI."""
    if not results_dir.exists() or not any(results_dir.iterdir()):
        print(f"No Allure results found at {results_dir}. Run pytest first.")
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
    print(f"Opening Allure report from {results_dir} ...")
    print("Press Ctrl+C to stop the server.")

    try:
        subprocess.run(f'allure serve "{results_dir}"', env=env, shell=True)
    except KeyboardInterrupt:
        print("\nAllure server stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Open the Allure report in a browser.")
    parser.add_argument(
        "--report",
        metavar="DIR",
        help="Path to a pre-built allure-report directory (e.g. downloaded from CI). "
        "Served over HTTP — no Allure CLI or Java required.",
    )
    args = parser.parse_args()

    if args.report:
        serve_static_report(pathlib.Path(args.report).expanduser().resolve())
    else:
        serve_allure_results(DEFAULT_RESULTS_DIR)
