"""Stage every generated Rune artifact into a static site folder."""

import shutil
from pathlib import Path

BASE = Path(r"C:\Users\gabri\AppData\Local\Temp\opencode")
SITE = BASE / "rune-sheet-site"
ASSETS = SITE / "assets"
REPO = Path(r"C:\Users\gabri\Tools\game-dev\rune")

for d in ["bench", "frames", "generated", "fx", "light", "lab", "kit", "scenes", "reports", "src"]:
    (ASSETS / d).mkdir(parents=True, exist_ok=True)


def cp(src, dest):
    src = Path(src)
    if not src.exists():
        print("MISSING", src)
        return
    shutil.copy2(src, ASSETS / dest)
    print("OK", dest, src.stat().st_size)


for p in sorted((BASE / "rune-bench").glob("*.png")):
    cp(p, "bench/" + p.name)
for p in sorted((BASE / "rune-sheet").glob("*.png")):
    cp(p, "frames/" + p.name)

for name in [
    "grain-compose.png", "grain-compose.mp4", "rune-tree.json", "rune-tap.json",
    "bench-apps.json", "bench-apps.csv",
]:
    p = BASE / name
    if p.exists():
        cp(p, "generated/" + name)
for d in ["rune-bench", "rune-media", "rune-media2", "rune-perf"]:
    for p in sorted((BASE / d).glob("bench-*.json")):
        cp(p, "reports/" + d + "-" + p.name)
for p in sorted((BASE / "rune-bench").glob("*.csv")):
    cp(p, "reports/" + p.name)

for name in [
    "hello-toggle.mp4", "hello-toggle.mov", "settings-light.png", "settings-dark.png",
    "settings-accent.png", "settings-demo.mp4", "kit-combobox.mp4", "kit-modal.mp4",
    "lab-electric.mp4", "lab-pulses.mp4", "frosted-scroll.mp4", "matched-zoom.mp4",
    "overlay-pill.png", "overlay-picker.png",
]:
    cp(REPO / name, "generated/" + name)

fx = ["glow.png", "fire.png", "liquid-metal-strip.png", "grain-gradient.png",
      "dither.png", "distort.png", "electric.png", "fluted-glass.png", "mesh-gradient.png"]
for n in fx:
    cp(REPO / "demo/fx" / n, "fx/" + n)

for n in ["flashlight.png", "godrays.png", "raised.png", "emissive.png"]:
    cp(REPO / "demo/light" / n, "light/" + n)
for n in ["lens.png", "flashlight.png", "keys.png", "pulses.png"]:
    cp(REPO / "demo/lab" / n, "lab/" + n)
for n in ["diff-split-dark.png", "index-dark.png"]:
    cp(REPO / "demo/kit" / n, "kit/" + n)
for n in ["metal.png", "glass.png", "light.png"]:
    cp(REPO / "target/site-scenes" / n, "scenes/" + n)

cp(REPO / "demo/rune.mp4", "generated/rune-reel.mp4")
cp(REPO / "crates/rune/examples/grain_compose.rs", "src/grain_compose.rs")
cp(REPO / "examples/hello/src/main.rs", "src/hello_main.rs")

total = sum(p.stat().st_size for p in ASSETS.rglob("*") if p.is_file())
print("TOTAL_BYTES", total, "FILES", len([p for p in ASSETS.rglob("*") if p.is_file()]))
print("SITE", SITE)
