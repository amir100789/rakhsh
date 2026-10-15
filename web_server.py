#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rakhsh Web Dashboard — Local HTTP interface for SOCKS / Core control
Port: 8080 (local only)
"""

import os, sys, subprocess, signal, time, json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = Path(__file__).parent.resolve()
CONFIG_DIR = Path.home() / ".config" / "rakhsh"
CORES = {
    "aether": {"label":"Aether (MASQUE)","binary_path":BASE_DIR/"bin"/"aether","protocols":["masque","wireguard","gool"]},
    "sing-box": {"label":"Sing-Box","binary_path":BASE_DIR/"bin"/"sing-box","protocols":["vless","trojan","reality"]},
    "xray": {"label":"XRay","binary_path":BASE_DIR/"bin"/"xray","protocols":["vless","trojan","reality"]},
}
PID_FILE = CONFIG_DIR / ".rakhsh.pid"

def is_running():
    if not PID_FILE.exists(): return False, None
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, 0)
        return True, pid
    except: return False, None

def get_active_core():
    p = CONFIG_DIR / ".active_core"
    return p.read_text().strip() if p.exists() else "aether"

def get_config(core):
    p = CORES[core]["binary_path"].parent.parent / "config" / (core + ".json")
    return json.loads(p.read_text()) if p.exists() else {}

# Simple HTML template
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="5">
<title>Rakhsh Web Dashboard</title>
<style>
body { font-family: system-ui, -apple-system, sans-serif; background: #0d1117; color: #e6edf3; max-width: 800px; margin: 40px auto; padding: 20px; }
.container { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 24px; }
h1 { font-size: 22px; margin-bottom: 4px; color: #58a6ff; }
.subtitle { color: #8b949e; font-size: 13px; margin-bottom: 24px; }
.status { display: flex; gap: 12px; align-items: center; margin-bottom: 16px; }
.badge { padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
.badge.running { background: #1a7f37; color: #3fb950; }
.badge.stopped { background: #da3633; color: #f85149; }
.core-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 24px; }
.card { background: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 16px; }
.card h3 { margin: 0 0 8px; font-size: 14px; }
.card p { margin: 0; font-size: 12px; color: #8b949e; }
.actions { display: flex; gap: 8px; flex-wrap: wrap; }
.actions a { display: inline-block; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 600; transition: .2s; }
.btn-start { background: #238636; color: #fff; }
.btn-start:hover { background: #2ea043; }
.btn-stop { background: #da3633; color: #fff; }
.btn-stop:hover { background: #f85149; }
.log-box { background: #010409; border: 1px solid #30363d; border-radius: 8px; padding: 12px; font-family: monospace; font-size: 11px; height: 160px; overflow-y: auto; white-space: pre-wrap; color: #7ee787; line-height: 1.4; }
.footer { margin-top: 24px; font-size: 11px; color: #6e7681; text-align: center; }
</style>
</head>
<body>
<div class="container">
  <h1>Rakhsh — Network Core Dashboard</h1>
  <div class="subtitle">Local Web Interface | SOCKS Proxy Port: 1819 | Auto-refresh: 5s</div>

  <div class="status">
    <span>Active Core:</span>
    <strong style="color:#58a6ff;">__ACTIVE_CORE__</strong>
    <span style="margin-left:8px;">|</span>
    <span>Process:</span>
    <span class="badge __RUNNING_CLASS__">__RUNNING_TEXT__</span>
    <span style="margin-left:8px;">|</span>
    <span>Port:</span>
    <span style="font-family:monospace; color:#f0f6fc;">1819</span>
    <span style="margin-left:8px;">|</span>
    <span>PID:</span>
    <span style="font-family:monospace; color:#f0f6fc;">__PID__</span>
  </div>

  <div class="core-grid">
    <div class="card">
      <h3>Aether (MASQUE / WG / Gool)</h3>
      <p>Binary: __AETHER_STATUS__</p>
      <div class="actions" style="margin-top:10px;">
        <a class="btn-start" href="/start?aether">Start</a>
      </div>
    </div>
    <div class="card">
      <h3>Sing-Box (VLESS / Reality)</h3>
      <p>Binary: __SINGBOX_STATUS__</p>
      <div class="actions" style="margin-top:10px;">
        <a class="btn-start" href="/start?sing-box">Start</a>
      </div>
    </div>
    <div class="card">
      <h3>XRay (VLESS / Reality / gRPC)</h3>
      <p>Binary: __XRAY_STATUS__</p>
      <div class="actions" style="margin-top:10px;">
        <a class="btn-start" href="/start?xray">Start</a>
      </div>
    </div>
  </div>

  <div class="actions">
    <a class="btn-stop" href="/stop">Stop Core</a>
    <a class="btn-start" style="background:#1f6feb;" href="/status">Refresh Status</a>
  </div>

  <h3 style="margin-top:24px; font-size:14px;">Live Log (last lines)</h3>
  <div class="log-box">__LOG_CONTENT__</div>

  <div class="footer">Rakhsh v1.0.0 | Bundled Cores | English Interface | Port 1819</div>
</div>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass  # suppress logs

    def do_GET(self):
        path = self.path
        active = get_active_core()
        running, pid = is_running()
        log_content = "No log file yet."
        log_path = CONFIG_DIR / ".rakhsh.log"
        if log_path.exists():
            log_content = "".join(log_path.read_text().splitlines()[-15:])

        # Handle actions
        if path.startswith("/start?"):
            core = path.split("?")[1].split("=")[-1]
            if core in CORES:
                # Execute start in background via subprocess
                subprocess.Popen([sys.executable, str(BASE_DIR / "rakhsh"), "--start", "--core", core], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        elif path == "/stop":
            kill_core()

        # Determine binary statuses
        def bin_status(name):
            bp = BASE_DIR / "bin" / name
            return "Present" if bp.exists() else "Missing"

        html = (HTML_TEMPLATE
            .replace("__ACTIVE_CORE__", active)
            .replace("__RUNNING_CLASS__", "running" if running else "stopped")
            .replace("__RUNNING_TEXT__", "Running" if running else "Stopped")
            .replace("__PID__", str(pid) if pid else "N/A")
            .replace("__AETHER_STATUS__", bin_status("aether"))
            .replace("__SINGBOX_STATUS__", bin_status("sing-box"))
            .replace("__XRAY_STATUS__", bin_status("xray"))
            .replace("__LOG_CONTENT__", log_content)
        )
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

def kill_core():
    running, pid = is_running()
    if running and pid:
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.5)
            try: os.kill(pid, 0); os.kill(pid, signal.SIGKILL)
            except ProcessLookupError: pass
        except: pass

def run_web(port=8080):
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"[Web] Dashboard running at http://localhost:{port}/")
    print(f"[Web] Access from browser or curl.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[Web] Stopped.")

if __name__ == "__main__":
    import argparse as ap
    p = ap.ArgumentParser()
    p.add_argument("--port", type=int, default=8080)
    args = p.parse_args()
    run_web(args.port)
