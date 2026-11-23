"""Build the perf profile and run Rune's built-in headless micro-benchmarks."""

import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(r"C:\Users\gabri\Tools\game-dev\rune")
OUT = Path(r"C:\Users\gabri\AppData\Local\Temp\opencode\rune-perf")
OUT.mkdir(parents=True, exist_ok=True)

CARGO = str(Path.home() / ".cargo" / "bin" / "cargo.exe")
ENV = os.environ.copy()
ENV["PATH"] = str(Path.home() / ".cargo" / "bin") + os.pathsep + ENV.get("PATH", "")
ENV["Path"] = ENV["PATH"]

BIN = ROOT / "target" / "perf" / "examples"

PINCH_RE = re.compile(
    r"METRIC mode=(\S+) cards=(\d+) metric=(\S+) median=([\d.]+) p95=([\d.]+) n=(\d+)"
)
UPLOAD_RE = re.compile(
    r"scene=(\S+) cpu_us=([\d.]+) kinstr=([\d.]+) frame_us=([\d.]+) buffers_per_frame=([\d.]+)"
)


def run(cmd, name, env=None, timeout=900):
    log = OUT / (name + ".log")
    t0 = time.perf_counter()
    try:
        p = subprocess.run(cmd, cwd=ROOT, env=env or ENV, capture_output=True, text=True, timeout=timeout)
        text = p.stdout + "\n" + p.stderr
        log.write_text(text, encoding="utf-8", errors="replace")
        return {"exit": p.returncode, "wall_ms": round((time.perf_counter() - t0) * 1000, 1), "text": text}
    except subprocess.TimeoutExpired as e:
        text = (e.stdout or "") + "\n" + (e.stderr or "")
        log.write_text(text, encoding="utf-8", errors="replace")
        return {"exit": "TIMEOUT", "wall_ms": round((time.perf_counter() - t0) * 1000, 1), "text": text}


report = {"builds": [], "runs": []}

print("building perf binaries...", flush=True)
builds = [
    ["cargo_build_rune_examples", [CARGO, "build", "--profile", "perf", "-p", "rune",
                                   "--example", "pinch_bench", "--example", "upload_bench",
                                   "--features", "frame-profile,test-gpu-counters"]],
    ["cargo_build_rune_light", [CARGO, "build", "--profile", "perf", "-p", "rune-light",
                                "--example", "frame_bench", "--features", "test-gpu-counters"]],
    ["cargo_build_motion_bento", [CARGO, "build", "--profile", "perf", "-p", "motion-bento"]],
]
for name, cmd in builds:
    r = run(cmd, name)
    report["builds"].append({"name": name, "exit": r["exit"], "wall_ms": r["wall_ms"]})
    print(f"build {name}: exit={r['exit']} wall={r['wall_ms']} ms", flush=True)
    if r["exit"] != 0:
        print(r["text"][-2000:], flush=True)

# Pinch: 120-frame pinch on 2000 cards, rebuild vs live_only.
r = run([str(BIN / "pinch_bench.exe"), "--samples", "9", "--cards", "2000"], "pinch_bench")
pinch = []
for m in PINCH_RE.finditer(r["text"]):
    pinch.append({"mode": m.group(1), "cards": int(m.group(2)), "metric": m.group(3),
                  "median": float(m.group(4)), "p95": float(m.group(5)), "n": int(m.group(6))})
report["runs"].append({"name": "pinch_bench", "exit": r["exit"], "wall_ms": r["wall_ms"], "metrics": pinch})
print(f"pinch_bench: exit={r['exit']} metrics={len(pinch)} wall={r['wall_ms']} ms", flush=True)

# Upload: 2000-instance frame, steady vs scroll.
upload_env = ENV.copy()
upload_env["UPLOAD_FRAMES"] = "300"
r = run([str(BIN / "upload_bench.exe")], "upload_bench", env=upload_env)
upload = []
for m in UPLOAD_RE.finditer(r["text"]):
    upload.append({"scene": m.group(1), "cpu_us": float(m.group(2)), "kinstr": float(m.group(3)),
                   "frame_us": float(m.group(4)), "buffers_per_frame": float(m.group(5))})
report["runs"].append({"name": "upload_bench", "exit": r["exit"], "wall_ms": r["wall_ms"], "metrics": upload})
print(f"upload_bench: exit={r['exit']} metrics={len(upload)} wall={r['wall_ms']} ms", flush=True)

# Lighting/FX frame recording cost.
r = run([str(BIN / "frame_bench.exe")], "frame_bench")
report["runs"].append({"name": "frame_bench", "exit": r["exit"], "wall_ms": r["wall_ms"],
                       "raw": r["text"][-6000:]})
print(f"frame_bench: exit={r['exit']} wall={r['wall_ms']} ms", flush=True)

# Motion-bento stress: ramp and a fixed load, live values vs naive rebuild.
MB = ROOT / "target" / "perf" / "motion-bento.exe"
mb_jobs = [
    ("bento_ramp", ["--seed", "7", "--ramp", "32:1024", "--frames", str(OUT / "ramp.csv"),
                    "--metrics", str(OUT / "ramp-metrics.json"), "--snap", str(OUT / "ramp-end.png"),
                    "--at", "29.6", "--size", "1440x900", "--scale", "2", "--fps", "120", "--duration", "30"]),
    ("bento_live_256", ["--seed", "7", "--load", "256", "--frames", str(OUT / "live256.csv"),
                        "--metrics", str(OUT / "live256-metrics.json"), "--fps", "120", "--duration", "8"]),
    ("bento_naive_256", ["--seed", "7", "--load", "256", "--naive", "--frames", str(OUT / "naive256.csv"),
                         "--metrics", str(OUT / "naive256-metrics.json"), "--fps", "120", "--duration", "8"]),
]
for name, args in mb_jobs:
    if not MB.exists():
        report["runs"].append({"name": name, "exit": "SKIP", "reason": "motion-bento perf binary missing"})
        continue
    r = run([str(MB)] + args, name)
    report["runs"].append({"name": name, "exit": r["exit"], "wall_ms": r["wall_ms"],
                           "raw_tail": r["text"][-1500:]})
    print(f"{name}: exit={r['exit']} wall={r['wall_ms']} ms", flush=True)

(OUT / "bench-perf.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("WROTE", OUT / "bench-perf.json", flush=True)
