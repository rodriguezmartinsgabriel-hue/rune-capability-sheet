"""Run Rune example apps headlessly and collect the frame stats they print."""

import csv
import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(r"C:\Users\gabri\Tools\game-dev\rune")
OUT = Path(r"C:\Users\gabri\AppData\Local\Temp\opencode\rune-bench")
OUT.mkdir(parents=True, exist_ok=True)

CARGO = str(Path.home() / ".cargo" / "bin" / "cargo.exe")
ENV = os.environ.copy()
ENV["PATH"] = str(Path.home() / ".cargo" / "bin") + os.pathsep + ENV.get("PATH", "")
ENV["Path"] = ENV["PATH"]

APPS = [
    "hello",
    "settings",
    "kit-gallery",
    "knobs",
    "motion-bento",
    "odometer",
    "shapes",
    "live-values",
    "glass-panel",
    "frosted-bar",
    "playground",
    "site-scenes",
    "showreel",
    "todo",
    "background",
    "video-tiles",
]

FRAME_RE = re.compile(
    r"rune: (\d+) frames at ([\d.]+) fps, gpu init ([\d.]+) ms, "
    r"first frame ([\d.]+) ms, frame cpu mean ([\d.]+) ms "
    r"p50 ([\d.]+) p95 ([\d.]+) max ([\d.]+), (\d+) instances"
)
SCENE_RE = re.compile(
    r"animating frames (\d+) .*?at-rest frames (\d+) .*?layout nodes (\d+), glyphs (\d+)"
)

rows = []
for app in APPS:
    snap = OUT / (app + ".png")
    log = OUT / (app + ".log")
    cmd = [CARGO, "run", "-q", "-p", app, "--", "--snap", str(snap)]
    t0 = time.perf_counter()
    try:
        p = subprocess.run(cmd, cwd=ROOT, env=ENV, capture_output=True, text=True, timeout=300)
        wall = (time.perf_counter() - t0) * 1000
        text = p.stdout + "\n" + p.stderr
        log.write_text(text, encoding="utf-8", errors="replace")
        m = FRAME_RE.search(text)
        s = SCENE_RE.search(text)
        rec = {
            "app": app,
            "exit": p.returncode,
            "wall_ms": round(wall, 1),
            "frames": int(m.group(1)) if m else None,
            "fps": float(m.group(2)) if m else None,
            "gpu_init_ms": float(m.group(3)) if m else None,
            "first_frame_ms": float(m.group(4)) if m else None,
            "cpu_mean_ms": float(m.group(5)) if m else None,
            "cpu_p50_ms": float(m.group(6)) if m else None,
            "cpu_p95_ms": float(m.group(7)) if m else None,
            "cpu_max_ms": float(m.group(8)) if m else None,
            "instances": int(m.group(9)) if m else None,
            "layout_nodes": int(s.group(3)) if s else None,
            "glyphs": int(s.group(4)) if s else None,
            "png_bytes": snap.stat().st_size if snap.exists() else None,
        }
    except subprocess.TimeoutExpired as e:
        wall = (time.perf_counter() - t0) * 1000
        rec = {"app": app, "exit": "TIMEOUT", "wall_ms": round(wall, 1)}
        log.write_text((e.stdout or "") + "\n" + (e.stderr or ""), encoding="utf-8", errors="replace")
    rows.append(rec)
    print(
        f"{app:16s} exit={str(rec.get('exit')):7s} "
        f"first={str(rec.get('first_frame_ms')):8s} ms "
        f"instances={str(rec.get('instances')):6s} "
        f"nodes={str(rec.get('layout_nodes')):5s} "
        f"glyphs={str(rec.get('glyphs')):5s} "
        f"wall={rec.get('wall_ms')} ms",
        flush=True,
    )

(OUT / "bench-apps.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
fields = [
    "app", "exit", "wall_ms", "frames", "fps", "gpu_init_ms", "first_frame_ms",
    "cpu_mean_ms", "cpu_p50_ms", "cpu_p95_ms", "cpu_max_ms", "instances",
    "layout_nodes", "glyphs", "png_bytes",
]
with (OUT / "bench-apps.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k) for k in fields})

print("WROTE", OUT / "bench-apps.json")
print("WROTE", OUT / "bench-apps.csv")
