#!/usr/bin/env python3
"""News Image - 25 November 2026.

Draws a one-page newspaper front page (1024x1024 PNG) summing up the
world news of Wednesday 25 November 2026: six stories, six panels.

Stdlib only. No PIL, no network, no copied assets: the PNG encoder and
the 5x7 bitmap font below are written by hand in this file, and every
pixel is generated here at run time. The output is fully deterministic:
running the program twice writes byte-identical files.

Usage: python3 main.py [output-path]
Default output path is /output/entry.png (the make.fun grader path).
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (18, 38, 68)
RED = (178, 34, 34)
WHITE = (255, 255, 255)
GREY = (150, 148, 140)
TEAL = (0, 110, 110)
PURPLE = (90, 50, 130)
GREEN = (30, 110, 50)
OCHRE = (170, 90, 20)

# ---------------------------------------------------------------- font
# 5x7 bitmap font, written by hand. Each glyph is 7 rows of 5 bits,
# '#' = ink, '.' = empty. Only the characters the page needs are
# defined; anything else renders as a blank.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = color
        row = bytes((r, g, b)) * (x1 - x0)
        for yy in range(y0, y1):
            off = (yy * self.w + x0) * 3
            self.px[off:off + len(row)] = row

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_centered(self, cx, y, s, scale, color):
        self.text(cx - self.text_width(s, scale) // 2, y, s, scale, color)


def wrap(text, max_chars):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- content
# Six verified stories from Wednesday 25 November 2026.
STORIES = [
    ("01 - UKRAINE / BALTIC SEA", NAVY,
     "UKRAINIAN DRONES HIT RUSSIAN SHIPS",
     "Ukrainian drones strike Russian vessels in the Gulf of Finland, "
     "opening a new Baltic front in the war at sea."),
    ("02 - CYBERATTACK / WASHINGTON", RED,
     "CYBERATTACK HITS CIA AND ODNI",
     "Hackers breach the CIA and the Office of the Director of National "
     "Intelligence in a major attack on US spy agencies."),
    ("03 - TRADE SECRETS / US COURT", TEAL,
     "HUAWEI GUILTY ON 10 OF 12 COUNTS",
     "A US jury convicts Huawei of stealing trade secrets on 10 of 12 "
     "counts in a landmark corporate espionage trial."),
    ("04 - YEMEN / SAUDI ARABIA", PURPLE,
     "HOUTHI DRONE HITS RIYADH TOWER",
     "A Houthi drone strikes a tower in Riyadh, injuring 11 people and "
     "sharply raising tensions across the region."),
    ("05 - NATO / POLAND", GREEN,
     "NATO SENDS EARLY-WARNING JETS TO POLAND",
     "NATO deploys airborne early-warning aircraft to Poland to watch "
     "over the alliance's eastern flank."),
    ("06 - HEALTH / CONGO", OCHRE,
     "WHO EVACUATES EBOLA STAFF IN CONGO",
     "The World Health Organization pulls staff out of Ebola-hit areas "
     "of the Democratic Republic of Congo."),
]


def draw_page():
    c = Canvas(W, H, PAPER)

    # Masthead.
    c.rect(24, 24, 976, 96, NAVY)
    c.text_centered(512, 38, "THE WORLD IN ONE PAGE", 4, WHITE)
    c.text_centered(512, 84, "WEDNESDAY 25 NOVEMBER 2026", 2, WHITE)
    c.rect(24, 124, 976, 4, RED)

    # Six panels: 2 columns x 3 rows.
    pw, ph, gap = 480, 268, 16
    for i, (kicker, color, headline, body) in enumerate(STORIES):
        px = 24 + (i % 2) * (pw + gap)
        py = 140 + (i // 2) * (ph + gap)
        c.rect(px, py, pw, ph, WHITE)
        c.rect(px, py, pw, ph, GREY)  # border via outline trick below
        c.rect(px + 1, py + 1, pw - 2, ph - 2, WHITE)
        # Colour bar with kicker.
        c.rect(px, py, pw, 32, color)
        c.text(px + 14, py + 9, kicker, 2, WHITE)
        # Three white ticks at the right end of the bar.
        for k in range(3):
            c.rect(px + pw - 52 + k * 14, py + 11, 8, 10, WHITE)
        # Headline, wrapped, scale 3.
        lines = wrap(headline, 24)
        hy = py + 44
        for ln in lines[:3]:
            c.text(px + 16, hy, ln, 3, INK)
            hy += 27
        # Thin rule between headline and body.
        c.rect(px + 16, hy + 2, pw - 32, 2, GREY)
        # Body, wrapped, scale 2.
        by = hy + 14
        for ln in wrap(body, 37)[:5]:
            c.text(px + 16, by, ln, 2, (60, 60, 60))
            by += 19
        # Bottom accent strip.
        c.rect(px, py + ph - 4, pw, 4, color)

    # Footer.
    c.text_centered(512, 988, "SIX STORIES, ONE DAY - 25 NOVEMBER 2026",
                    2, INK)
    return c


# ---------------------------------------------------------------- PNG out
def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    size = write_png(draw_page(), out)
    print("wrote %s (%d bytes)" % (out, size))


if __name__ == "__main__":
    main()
