"""Generate PNG stills, strips, frame sequences and MP4/MOV videos with Rune headless runs."""

import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(r"C:\Users\gabri\Tools\game-dev\rune")
OUT = Path(r"C:\Users\gabri\AppData\Local\Temp\opencode\rune-media")
OUT.mkdir(parents=True, exist_ok=True)

CARGO = str(Path.home() / ".cargo" / "bin" / "cargo.exe")
ENV = os.environ.copy()
ENV["PATH"] = str(Path.home() / ".cargo" / "bin") + os.pathsep + ENV.get("PATH", "")
ENV["Path"] = ENV["PATH"]

S = ROOT / "examples" / "settings" / "scripts"
K = ROOT / "examples" / "kit-gallery" / "scripts"
L = ROOT / "examples" / "lab" / "scripts"
TAP = Path(r"C:\Users\gabri\AppData\Local\Temp\opencode\rune-tap.json")


def j(name, pkg, args, out_files):
    return {"name": name, "pkg": pkg, "args": args, "out": [str(OUT / o) for o in out_files]}


JOBS = [
    j("hello_toggle_mp4", "hello",
      ["--script", str(TAP), "--video", "hello-toggle.mp4", "--duration", "auto", "--fps", "60", "--keys"],
      ["hello-toggle.mp4"]),
    j("hello_toggle_mov", "hello",
      ["--script", str(TAP), "--video", "hello-toggle.mov", "--duration", "auto", "--fps", "60"],
      ["hello-toggle.mov"]),
    j("settings_scene_light", "settings", ["--scene", "light", "--snap", "settings-light.png", "--size", "620x520", "--scale", "2"], ["settings-light.png"]),
    j("settings_scene_dark", "settings", ["--scene", "dark", "--snap", "settings-dark.png", "--size", "620x520", "--scale", "2"], ["settings-dark.png"]),
    j("settings_scene_accent", "settings", ["--scene", "accent-pink", "--snap", "settings-accent.png", "--size", "620x520", "--scale", "2"], ["settings-accent.png"]),
    j("settings_demo_mp4", "settings",
      ["--script", str(S / "demo.json"), "--video", "settings-demo.mp4", "--duration", "auto", "--fps", "60", "--size", "620x520", "--scale", "2", "--keys"],
      ["settings-demo.mp4"]),
    j("settings_demo_strip", "settings",
      ["--script", str(S / "demo.json"), "--strip", "settings-strip.png", "--every", "12", "--cols", "5", "--size", "620x520", "--scale", "2"],
      ["settings-strip.png"]),
    j("kitgallery_combobox_mp4", "kit-gallery",
      ["--script", str(K / "combobox.json"), "--video", "kit-combobox.mp4", "--duration", "auto", "--fps", "60"],
      ["kit-combobox.mp4"]),
    j("kitgallery_modal_mp4", "kit-gallery",
      ["--script", str(K / "motion-focus-modal.json"), "--video", "kit-modal.mp4", "--duration", "auto", "--fps", "60"],
      ["kit-modal.mp4"]),
    j("lab_electric_mp4", "lab",
      ["--script", str(L / "electric.json"), "--video", "lab-electric.mp4", "--duration", "auto", "--fps", "60"],
      ["lab-electric.mp4"]),
    j("lab_pulses_mp4", "lab",
      ["--script", str(L / "pulses.json"), "--video", "lab-pulses.mp4", "--duration", "auto", "--fps", "60"],
      ["lab-pulses.mp4"]),
    j("frosted_scroll_mp4", "frosted-bar",
      ["--script", str(ROOT / "examples" / "frosted-bar" / "scroll.json"), "--video", "frosted-scroll.mp4", "--duration", "auto", "--fps", "60"],
      ["frosted-scroll.mp4"]),
    j("matched_zoom_mp4", "matched",
      ["--script", str(ROOT / "examples" / "matched" / "scripts" / "zoom.json"), "--video", "matched-zoom.mp4", "--duration", "auto", "--fps", "60"],
      ["matched-zoom.mp4"]),
    j("overlay_pill_png", "overlay-lab", ["--scene", "pill", "--snap", "overlay-pill.png"], ["overlay-pill.png"]),
    j("overlay_picker_png", "overlay-lab", ["--scene", "picker", "--size", "960x600", "--snap", "overlay-picker.png"], ["overlay-picker.png"]),
    j("motion_bento_ramp_png", "motion-bento",
      ["--seed", "7", "--ramp", "32:1024", "--frames", "bento-ramp.csv", "--snap", "bento-ramp-end.png", "--at", "29.6", "--size", "1440x900", "--scale", "2", "--fps", "120", "--duration", "30"],
      ["bento-ramp-end.png", "bento-ramp.csv"]),
]


def probe(path):
    if not path.exists():
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


results = []
for job in JOBS:
    args = [a.replace(str(OUT), str(OUT)) for a in job["args"]]
    cmd = [CARGO, "run", "-q", "-p", job["pkg"], "--"] + args
    log = OUT / (job["name"] + ".log")
    t0 = time.perf_counter()
    try:
        p = subprocess.run(cmd, cwd=ROOT, env=ENV, capture_output=True, text=True, timeout=420)
        wall = (time.perf_counter() - t0) * 1000
        log.write_text(p.stdout + "\n" + p.stderr, encoding="utf-8", errors="replace")
        files = []
        for name in job["out"]:
            f = Path(name)
            files.append({"name": f.name, "bytes": f.stat().st_size if f.exists() else None,
                          "probe": probe(f) if f.suffix in (".mp4", ".mov", ".webm") else None})
        rec = {"name": job["name"], "pkg": job["pkg"], "exit": p.returncode,
               "wall_ms": round(wall, 1), "files": files}
        status = "OK" if p.returncode == 0 and all(x["bytes"] for x in files) else "CHECK"
    except subprocess.TimeoutExpired as e:
        wall = (time.perf_counter() - t0) * 1000
        rec = {"name": job["name"], "pkg": job["pkg"], "exit": "TIMEOUT", "wall_ms": round(wall, 1), "files": []}
        log.write_text((e.stdout or "") + "\n" + (e.stderr or ""), encoding="utf-8", errors="replace")
        status = "TIMEOUT"
    results.append(rec)
    sizes = ",".join(str(x["bytes"]) for x in rec.get("files", []))
    print(f"[{status:7s}] {job['name']:26s} exit={str(rec['exit']):7s} wall={rec['wall_ms']:9.1f} ms bytes={sizes}", flush=True)

(OUT / "bench-media.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print("WROTE", OUT / "bench-media.json")
