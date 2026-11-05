#!/usr/bin/env python3
"""Prepare H5 skin + dummy assets for docs/h5/drill-cam-v1.0.html.

Sources (outside the repo, do not copy the originals in):
  素材/左右手/咏春_右手_立掌.png   -> docs/h5/hand-skin-L.png
  素材/左右手/咏春_左手_立掌.png   -> docs/h5/hand-skin-R.png
  素材/木桩/wingchun-dummy-assets/01_front_full.png -> docs/h5/dummy-front.jpg

Left/right swap is intentional: the delivered hands show the palm toward the
viewer, so the "right hand" silhouette matches what a first-person left hand
looks like. Filenames stay put so the HTML references keep working.

Usage:
  python3 tools/prepare_h5_assets.py            # write assets + print anchors
  python3 tools/prepare_h5_assets.py --check    # only print anchors/sizes
"""

from __future__ import annotations

import argparse
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "docs" / "h5"

SRC_HANDS = {
    # output stem -> (source path, note)
    "L": Path("/Users/dawn80s/Documents/viture_sports/素材/左右手/咏春_右手_立掌.png"),
    "R": Path("/Users/dawn80s/Documents/viture_sports/素材/左右手/咏春_左手_立掌.png"),
}
SRC_DUMMY = Path(
    "/Users/dawn80s/Documents/viture_sports/素材/木桩/wingchun-dummy-assets/01_front_full.png"
)

HAND_MAX_SIDE = 768
HAND_PAD = 2  # transparent margin kept around the content box

# background key for the hand plates: light gray wall = low saturation, mid/high brightness
BG_SAT_MAX = 0.20
BG_BRIGHT_MIN = 0.32
FEATHER_RADIUS = 1.2


def log(msg: str) -> None:
    print(msg, flush=True)


def flood_bg(candidate: np.ndarray) -> np.ndarray:
    """Return the background mask = candidate pixels connected to the border."""
    h, w = candidate.shape
    seen = np.zeros((h, w), dtype=bool)
    queue: deque[tuple[int, int]] = deque()

    for x in range(w):
        for y in (0, h - 1):
            if candidate[y, x] and not seen[y, x]:
                seen[y, x] = True
                queue.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if candidate[y, x] and not seen[y, x]:
                seen[y, x] = True
                queue.append((y, x))

    while queue:
        y, x = queue.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and candidate[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                queue.append((ny, nx))
    return seen


def key_background(rgb: np.ndarray) -> np.ndarray:
    """rgb uint8 HxWx3 -> alpha uint8 HxW (255 = keep)."""
    a = rgb.astype(np.float32) / 255.0
    mx = a.max(axis=2)
    mn = a.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1e-6)
    candidate = (sat < BG_SAT_MAX) & (mx > BG_BRIGHT_MIN)
    bg = flood_bg(candidate)
    alpha = np.where(bg, 0.0, 1.0).astype(np.float32) * 255.0

    # 1-2px feather: one soft blur of the binary edge keeps the rim from stair-stepping
    feather = Image.fromarray(alpha.astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(FEATHER_RADIUS)
    )
    return np.asarray(feather)


def content_box(alpha: np.ndarray) -> tuple[int, int, int, int]:
    solid = alpha > 16
    rows = np.where(solid.any(axis=1))[0]
    cols = np.where(solid.any(axis=0))[0]
    if rows.size == 0 or cols.size == 0:
        raise RuntimeError("empty alpha after keying")
    return int(cols.min()), int(rows.min()), int(cols.max()) + 1, int(rows.max()) + 1


def hand_anchors(alpha: np.ndarray) -> dict:
    """Palm contact + forearm root, normalized inside the cropped plate."""
    h, w = alpha.shape
    solid = alpha > 32

    def band_centroid(v0: float, v1: float) -> tuple[float, float]:
        y0, y1 = int(round(h * v0)), int(round(h * v1))
        y1 = max(y1, y0 + 1)
        band = solid[y0:y1]
        ys, xs = np.nonzero(band)
        if xs.size == 0:
            return 0.5, (v0 + v1) / 2
        return float(xs.mean() / (w - 1)), float((ys.mean() + y0) / (h - 1))

    palm_x, palm_y = band_centroid(0.16, 0.30)
    root_x, root_y = band_centroid(0.94, 1.0)
    wrist_x, wrist_y = band_centroid(0.34, 0.42)
    return {
        "w": w,
        "h": h,
        "palmX": round(palm_x, 4),
        "palmY": round(palm_y, 4),
        "wristX": round(wrist_x, 4),
        "wristY": round(wrist_y, 4),
        "rootX": round(root_x, 4),
        "rootY": round(root_y, 4),
    }


def prep_hand(side: str, src: Path, write: bool) -> dict:
    im = Image.open(src).convert("RGB")
    rgb = np.asarray(im)
    alpha = key_background(rgb)
    x0, y0, x1, y1 = content_box(alpha)

    pad = HAND_PAD
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(im.width, x1 + pad)
    y1 = min(im.height, y1 + pad)

    plate = np.dstack([rgb, alpha])[y0:y1, x0:x1]
    out = Image.fromarray(plate)

    scale = HAND_MAX_SIDE / max(out.width, out.height)
    new_size = (max(1, round(out.width * scale)), max(1, round(out.height * scale)))
    out = out.resize(new_size, Image.LANCZOS)

    anchors = hand_anchors(np.asarray(out)[:, :, 3])
    target = OUT_DIR / f"hand-skin-{side}.png"
    if write:
        target.parent.mkdir(parents=True, exist_ok=True)
        # keep a plain RGBA PNG: palette+transparency renders with ragged rims in Safari
        out.save(target, optimize=True)
    kb = target.stat().st_size / 1024 if target.exists() else 0
    size_note = f"  {kb:.0f}KB" if write else ""
    log(f"[hand {side}] {src.name} -> {target.name}  {new_size[0]}x{new_size[1]}{size_note}")
    anchors["side"] = side
    anchors["file"] = target.name
    return anchors


def prep_dummy(src: Path, write: bool) -> dict:
    im = Image.open(src).convert("RGB")
    if im.size != (1728, 1117):
        im = im.resize((1728, 1117), Image.LANCZOS)
    target = OUT_DIR / "dummy-front.jpg"
    if write:
        target.parent.mkdir(parents=True, exist_ok=True)
        im.save(target, "JPEG", quality=82, optimize=True, progressive=True)
    kb = target.stat().st_size / 1024 if target.exists() else 0
    log(f"[dummy] {src.name} -> {target.name}  {im.width}x{im.height}  {kb:.0f}KB")
    return {"file": target.name, "w": im.width, "h": im.height}


def print_anchors(hands: list[dict], dummy: dict) -> None:
    log("")
    log("/* ---- anchors printed by tools/prepare_h5_assets.py (paste into the HTML) ---- */")
    log("// normalised inside each cropped skin plate (0..1, y down)")
    for h in hands:
        log(
            "HAND_ANCHOR.{side} = {{ palmX: {palmX:.4f}, palmY: {palmY:.4f}, "
            "wristX: {wristX:.4f}, wristY: {wristY:.4f}, rootX: {rootX:.4f}, rootY: {rootY:.4f} }};"
            " // {w}x{h} {file}".format(**h)
        )
    log("")
    log("// dummy-front.jpg: wooden dummy geometry, normalised on the photo itself")
    log("DUMMY_ART = {")
    log("  trunkX: 0.5150,          // centre line of the trunk")
    log("  top: 0.0600,             // rounded top of the trunk")
    log("  base: 0.9850,            // floor line under the base frame")
    log("  ru:  { x: 0.6000, y: 0.2320 },  // viewer-right upper arm tip (armRU)")
    log("  mid: { x: 0.5200, y: 0.4430 },  // middle arm tip (armMid)")
    log("};")
    log("")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="print anchors only, do not write files")
    args = ap.parse_args()
    write = not args.check

    missing = [str(p) for p in list(SRC_HANDS.values()) + [SRC_DUMMY] if not p.exists()]
    if missing:
        for m in missing:
            log(f"missing source: {m}")
        return 1

    hands = [prep_hand(side, src, write) for side, src in SRC_HANDS.items()]
    dummy = prep_dummy(SRC_DUMMY, write)
    print_anchors(hands, dummy)
    return 0


if __name__ == "__main__":
    sys.exit(main())
