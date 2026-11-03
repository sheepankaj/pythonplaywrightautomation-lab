"""
Serve the pytest-html report over a local HTTP server and open it in the browser.
Equivalent to: npx playwright show-report

Usage: python scripts/show_report.py
"""

import http.server
import os
import pathlib
import socketserver
import sys
import threading
import webbrowser

PORT = 9323
REPORT_DIR = pathlib.Path(__file__).parent.parent / "reports"
REPORT_FILE = REPORT_DIR / "report.html"

if not REPORT_FILE.exists():
    print(f"No report found at {REPORT_FILE}. Run pytest first.")
    sys.exit(1)

os.chdir(REPORT_DIR)

handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), handler) as httpd:
    url = f"http://localhost:{PORT}/report.html"
    print(f"Report available at: {url}")
    print("Press Ctrl+C to stop the server.")
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
