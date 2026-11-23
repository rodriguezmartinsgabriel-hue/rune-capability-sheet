"""Second wave: advanced Rune headless output formats and scripted situations."""

import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(r"C:\Users\gabri\Tools\game-dev\rune")
OUT = Path(r"C:\Users\gabri\AppData\Local\Temp\opencode\rune-media2")
OUT.mkdir(parents=True, exist_ok=True)

CARGO = str(Path.home() / ".cargo" / "bin" / "cargo.exe")
ENV = os.environ.copy()
ENV["PATH"] = str(Path.home() / ".cargo" / "bin") + os.pathsep + ENV.get("PATH", "")
ENV["Path"] = ENV["PATH"]

TAP = Path(r"C:\Users\gabri\AppData\Local\Temp\opencode\rune-tap.json")
KEYS = Path(r"C:\Users\gabri\AppData\Local\Temp\opencode\rune-tap-keys.json")
WHEEL = Path(r"C:\Users\gabri\AppData\Local\Temp\opencode\rune-wheel.json")
RESIZE = Path(r"C:\Users\gabri\AppData\Local\Temp\opencode\rune-resize.json")
BACKDROP = Path(r"C:\Users\gabri\AppData\Local\Temp\opencode\rune-bench\motion-bento.png")
S = ROOT / "examples" / "settings" / "scripts"


def j(name, pkg, args, out):
    return {"name": name, "pkg": pkg, "args": args, "out": [str(OUT / o) for o in out]}


JOBS = [
    j("hello_keys_pointer_mp4", "hello",
      ["--script", str(KEYS), "--video", "hello-keys.mp4", "--duration", "auto", "--fps", "60", "--keys", "--pointer"],
      ["hello-keys.mp4"]),
    j("hello_webm_vp9", "hello",
      ["--script", str(TAP), "--video", "hello.webm", "--duration", "auto", "--fps", "60"],
      ["hello.webm"]),
    j("hello_png_sequence", "hello",
      ["--script", str(TAP), "--out", "hello-frames/", "--every", "6", "--duration", "auto", "--fps", "60"],
      ["hello-frames"]),
    j("settings_light_theme_png", "settings",
      ["--scene", "light", "--theme", "light", "--snap", "settings-light-theme.png", "--size", "620x520", "--scale", "2"],
      ["settings-light-theme.png"]),
    j("settings_crop_png", "settings",
      ["--snap", "settings-crop.png", "--crop", "370,74,214,36", "--size", "620x520", "--scale", "2"],
      ["settings-crop.png"]),
    j("settings_tree_trace", "settings",
      ["--script", str(S / "demo.json"), "--tree", "settings-tree.json", "--trace", "settings-trace.jsonl", "--at", "mark:end", "--size", "620x520", "--scale", "2"],
      ["settings-tree.json", "settings-trace.jsonl"]),
    j("settings_resize_mp4", "settings",
      ["--script", str(RESIZE), "--video", "settings-resize.mp4", "--duration", "auto", "--fps", "60", "--size", "620x520", "--scale", "2"],
      ["settings-resize.mp4"]),
    j("frosted_wheel_mp4", "frosted-bar",
      ["--script", str(WHEEL), "--video", "frosted-wheel.mp4", "--duration", "auto", "--fps", "60"],
      ["frosted-wheel.mp4"]),
    j("showreel_mp4", "showreel",
      ["--video", "showreel.mp4", "--fps", "60", "--duration", "5"],
      ["showreel.mp4"]),
    j("launcher_desktop_mp4", "launcher",
      ["--desktop", str(BACKDROP), "--script", str(ROOT / "examples" / "launcher" / "scripts" / "demo.json"),
       "--video", "desktop.mp4", "--keys", "--pointer", "--size", "1440x900", "--fps", "60"],
      ["desktop.mp4"]),
    j("settings_list_scenes", "settings", ["--list-scenes"], []),
    j("hello_first_pixels", "hello", ["--first-pixels", "--snap", "hello-first.png"], ["hello-first.png"]),
]


def probe(path):
    if not path.exists() or path.suffix not in (".mp4", ".mov", ".webm"):
        return None
    try:
        p = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration,size",
             "-of", "json", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        if p.returncode == 0:
            return json.loads(p.stdout)
    except Exception:
        pass
    return None


def describe(path):
    if path.is_dir():
        files = sorted(path.glob("*.png"))
        return {"kind": "dir", "count": len(files),
                "bytes": sum(f.stat().st_size for f in files),
                "first": files[0].name if files else None,
                "last": files[-1].name if files else None}
    return {"kind": "file", "bytes": path.stat().st_size if path.exists() else None,
            "probe": probe(path)}


results = []
for job in JOBS:
    cmd = [CARGO, "run", "-q", "-p", job["pkg"], "--"] + job["args"]
    log = OUT / (job["name"] + ".log")
    t0 = time.perf_counter()
    try:
        p = subprocess.run(cmd, cwd=ROOT, env=ENV, capture_output=True, text=True, timeout=600)
        wall = (time.perf_counter() - t0) * 1000
        log.write_text(p.stdout + "\n" + p.stderr, encoding="utf-8", errors="replace")
        files = [{"name": Path(x).name, **describe(Path(x))} for x in job["out"]]
        rec = {"name": job["name"], "pkg": job["pkg"], "exit": p.returncode,
               "wall_ms": round(wall, 1), "files": files,
               "stdout_head": p.stdout[:800]}
        ok = p.returncode == 0 and all(
            (f["bytes"] if f["bytes"] is not None else 0) > 0 for f in files
        ) if files else p.returncode == 0
        status = "OK" if ok else "CHECK"
    except subprocess.TimeoutExpired as e:
        wall = (time.perf_counter() - t0) * 1000
        rec = {"name": job["name"], "pkg": job["pkg"], "exit": "TIMEOUT", "wall_ms": round(wall, 1), "files": []}
        log.write_text((e.stdout or "") + "\n" + (e.stderr or ""), encoding="utf-8", errors="replace")
        status = "TIMEOUT"
    results.append(rec)
    print(f"[{status:7s}] {job['name']:26s} exit={str(rec['exit']):7s} wall={rec['wall_ms']:9.1f} ms", flush=True)

(OUT / "bench-media2.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print("WROTE", OUT / "bench-media2.json", flush=True)
