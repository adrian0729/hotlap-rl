"""Render the README's stills from the showcase page itself.

    uv run python scripts/showcase_stills.py

Serves ``docs/showcase/`` on a local port, opens the page in headless Chrome at fixed states
(``?view=<element>&c=<circuit>&t=<seconds>``, see the end of the page's script), trims each
screenshot to its content and writes ``docs/showcase/img/*.png``. Stills that show circuit
geometry get the TUMFTM attribution in a footer, as the repository's other committed figures
do. Needs ``docs/showcase/data.js`` (``scripts/showcase.py``), Google Chrome, and network
access for the page's web fonts.
"""

import argparse
import functools
import http.server
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs" / "showcase"
OUT = SITE / "img"
ATTRIBUTION = ("Track geometry: TUMFTM racetrack-database (LGPL-3.0). Replay of a registered "
               "run, simulated again for the page (post hoc).")
CHROME = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
          "google-chrome", "chromium", "chromium-browser")

# name, query, window (w, h), whether it shows circuit geometry (and so gets the footer)
SHOTS = [
    ("replay-spa", "view=screen&theme=dark&c=Spa&t=6.9", (1180, 760), True),
    ("replay-suzuka", "view=screen&theme=dark&c=Suzuka&t=12.0", (1180, 760), True),
    ("replay-crash", "view=screen&theme=dark&c=MexicoCity&t=999", (1180, 760), True),
    ("circuits", "view=picker&theme=light", (1180, 420), True),
    ("scoreboard", "view=scoreTable&theme=light", (980, 900), False),
    ("follow", "view=follow&theme=light", (760, 520), False),
    ("ladder", "view=ladder&theme=light", (760, 520), False),
    ("dial", "view=dial&theme=light", (1180, 420), False),
]


def find_chrome() -> str:
    for c in CHROME:
        if Path(c).exists() or shutil.which(c):
            return c
    raise SystemExit("Google Chrome was not found")


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve() -> tuple[http.server.ThreadingHTTPServer, int]:
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0),
                                          functools.partial(Quiet, directory=str(SITE)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def trim(im: Image.Image, pad: int) -> Image.Image:
    """Crop to the content: everything that differs from the bottom-right pixel's colour."""
    bg = Image.new(im.mode, im.size, im.getpixel((im.width - 1, im.height - 1)))
    box = ImageChops.difference(im, bg).getbbox()
    if box is None:
        return im
    return im.crop((max(0, box[0] - pad), max(0, box[1] - pad),
                    min(im.width, box[2] + pad), min(im.height, box[3] + pad)))


def font(size: int):
    for name in ("/System/Library/Fonts/Helvetica.ttc", "DejaVuSans.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def footer(im: Image.Image, text: str, scale: int) -> Image.Image:
    bg = im.getpixel((0, 0))
    h = 26 * scale
    out = Image.new("RGB", (im.width, im.height + h), bg)
    out.paste(im, (0, 0))
    dark = sum(bg[:3]) < 384
    ImageDraw.Draw(out).text((12 * scale, im.height + 6 * scale), text, font=font(11 * scale),
                             fill=(170, 176, 188) if dark else (95, 101, 113))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only", nargs="*", help="names of the stills to render (default: all)")
    ap.add_argument("--scale", type=int, default=2, help="device pixel ratio")
    args = ap.parse_args()
    if not (SITE / "data.js").exists():
        raise SystemExit("docs/showcase/data.js is missing: run scripts/showcase.py first")
    chrome, (srv, port) = find_chrome(), serve()
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        for name, query, (w, h), geometry in SHOTS:
            if args.only and name not in args.only:
                continue
            with tempfile.TemporaryDirectory() as tmp:
                raw = Path(tmp) / "shot.png"
                cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                       f"--user-data-dir={tmp}/profile", f"--window-size={w},{h}",
                       f"--force-device-scale-factor={args.scale}",
                       "--virtual-time-budget=9000", f"--screenshot={raw}",
                       f"http://127.0.0.1:{port}/index.html?{query}"]
                subprocess.run(cmd, check=True, capture_output=True, timeout=120)
                im = trim(Image.open(raw).convert("RGB"), pad=10 * args.scale)
            if geometry:
                im = footer(im, ATTRIBUTION, args.scale)
            im.save(OUT / f"{name}.png", optimize=True)
            print(f"{OUT / (name + '.png')}  {im.width}x{im.height}  "
                  f"{(OUT / (name + '.png')).stat().st_size / 1e3:.0f} kB", flush=True)
    finally:
        srv.shutdown()


if __name__ == "__main__":
    main()
