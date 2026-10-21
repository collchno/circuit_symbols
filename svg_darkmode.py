#!/usr/bin/env python3
"""Create dark-mode copies of SVG diagrams (e.g. saved from Inkscape).

Rules
  * black stroke/fill  -> white
  * fill/stroke none   -> left as none
  * unspecified fill   -> treated as black (SVG default), so becomes white
  * any other colour   -> lightness flipped (L -> 1 - L in HLS), hue and
                          saturation kept, so red stays red, light blue
                          becomes dark blue, white becomes black, etc.

Touches fill, stroke, stop-color, flood-color, lighting-color and color,
whether they appear as attributes, inside style="...", or in <style> blocks.
Works on the raw text, so symbols/defs/gradients/markers are all covered and
the rest of the file is left byte-for-byte alone.

Usage
  python3 svg_darkmode.py diagram.svg                 -> diagram_dark.svg
  python3 svg_darkmode.py a.svg b.svg --bg "#1e1e1e"  -> also adds a background
"""
import argparse
import colorsys
import re
from pathlib import Path

PROPS = ("fill", "stroke", "stop-color", "flood-color", "lighting-color", "color")

NAMED = {
    "black": (0, 0, 0), "white": (255, 255, 255), "red": (255, 0, 0),
    "green": (0, 128, 0), "blue": (0, 0, 255), "yellow": (255, 255, 0),
    "cyan": (0, 255, 255), "aqua": (0, 255, 255), "magenta": (255, 0, 255),
    "fuchsia": (255, 0, 255), "gray": (128, 128, 128), "grey": (128, 128, 128),
    "silver": (192, 192, 192), "maroon": (128, 0, 0), "navy": (0, 0, 128),
    "olive": (128, 128, 0), "purple": (128, 0, 128), "teal": (0, 128, 128),
    "orange": (255, 165, 0), "lime": (0, 255, 0), "brown": (165, 42, 42),
    "pink": (255, 192, 203), "darkgray": (169, 169, 169),
    "darkgrey": (169, 169, 169), "lightgray": (211, 211, 211),
    "lightgrey": (211, 211, 211),
}

# property name, separator (":" or "=" plus optional quote), colour value
PATTERN = re.compile(
    r"(?<![\w-])(" + "|".join(PROPS) + r")(\s*[:=]\s*[\"']?\s*)"
    r"(#[0-9a-fA-F]+|rgba?\([^)]*\)|[A-Za-z]+)"
)


def flip_rgb(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    r2, g2, b2 = colorsys.hls_to_rgb(h, 1 - l, s)
    return round(r2 * 255), round(g2 * 255), round(b2 * 255)


def flip_value(value):
    """Return the flipped colour string, or the input unchanged if it is not
    a colour we understand (none, currentColor, url(#grad), inherit, ...)."""
    low = value.strip().lower()
    alpha = None
    if low in NAMED:
        r, g, b = NAMED[low]
        fmt = "hex"
    elif low.startswith("#"):
        h = low[1:]
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) not in (6, 8):
            return value
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        alpha = h[6:] or None
        fmt = "hex"
    elif low.startswith("rgb"):
        nums = re.findall(r"[-+]?\d*\.?\d+%?", low[low.index("(") + 1:])
        if len(nums) < 3:
            return value

        def ch(x):
            v = float(x[:-1]) * 2.55 if x.endswith("%") else float(x)
            return max(0, min(255, round(v)))

        r, g, b = (ch(n) for n in nums[:3])
        alpha = nums[3] if len(nums) > 3 else None
        fmt = "rgb"
    else:
        return value

    r, g, b = flip_rgb(r, g, b)
    if fmt == "hex":
        return "#%02x%02x%02x%s" % (r, g, b, alpha or "")
    if alpha:
        return "rgba(%d, %d, %d, %s)" % (r, g, b, alpha)
    return "rgb(%d, %d, %d)" % (r, g, b)


def convert(text, bg=None):
    text = PATTERN.sub(lambda m: m.group(1) + m.group(2) + flip_value(m.group(3)), text)

    m = re.search(r"<svg\b[^>]*>", text, re.S)
    if not m:
        return text
    tag = m.group(0)
    new_tag = tag

    # Unspecified fill is black in SVG; make that inherit as white instead.
    if not re.search(r"(?<![\w-])fill\s*[:=]", tag):
        new_tag = new_tag.replace("<svg", '<svg fill="#ffffff"', 1)

    if bg:
        vb = re.search(r"viewBox\s*=\s*[\"']([^\"']+)", tag)
        if vb and len(vb.group(1).replace(",", " ").split()) >= 4:
            x, y, w, h = vb.group(1).replace(",", " ").split()[:4]
        else:
            x, y, w, h = "0", "0", "100%", "100%"
        new_tag += ('<rect id="dark-bg" x="%s" y="%s" width="%s" height="%s" '
                    'fill="%s" stroke="none"/>' % (x, y, w, h, bg))

    return text[:m.start()] + new_tag + text[m.end():]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="input SVG file(s)")
    ap.add_argument("--bg", help='add a background rect, e.g. "#1e1e1e"')
    ap.add_argument("--suffix", default="_dark", help="output suffix (default _dark)")
    args = ap.parse_args()

    for f in args.files:
        src = Path(f)
        dst = src.with_name(src.stem + args.suffix + src.suffix)
        dst.write_text(convert(src.read_text(encoding="utf-8"), args.bg), encoding="utf-8")
        print("%s -> %s" % (src, dst))


if __name__ == "__main__":
    main()
