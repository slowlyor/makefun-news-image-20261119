#!/usr/bin/env python3
"""News-image entry for 19 November 2026.

Draws a 1024x1024 newspaper-style front page summing up the day's
world news. Standard library only, deterministic, no network, no files.
"""
import os
import struct
import zlib

W, H = 1024, 1024

CREAM = (247, 242, 231)
INK = (18, 18, 18)
RED = (176, 42, 32)
BLUE = (31, 78, 121)
TEAL = (14, 110, 110)
GOLD = (184, 134, 11)
GREY = (110, 105, 95)
LIGHT = (232, 226, 212)
WHITE = (255, 255, 255)
SKY = (168, 208, 224)
SUN = (232, 150, 40)
GREEN = (46, 125, 50)

# 5x7 bitmap font: each glyph is 7 rows of 5 characters.
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ";": ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    "-": ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "=": ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    "*": ["00000", "10101", "01110", "11111", "01110", "10101", "00000"],
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[i * 3:i * 3 + 3] = bytes(bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def box(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def disc_ring(self, cx, cy, r, c, t=3):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d <= r * r:
                    self.set(xx, yy, c)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        # Fill a triangle by scanline interpolation.
        ys = sorted([y0, y1, y2])
        for y in range(ys[0], ys[2] + 1):
            xs = []
            for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2), (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if min(ay, by) <= y <= max(ay, by):
                    xs.append(ax + (bx - ax) * (y - ay) / (by - ay))
            if len(xs) >= 2:
                for x in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(x, y, c)

    def text(self, s, x, y, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == "1":
                        self.rect(cx + col * scale, y + r * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def centered(self, s, y, scale, c, x0=0, x1=None):
        if x1 is None:
            x1 = self.w
        w = self.text_w(s, scale)
        self.text(s, x0 + (x1 - x0 - w) // 2, y, scale, c)

    def wrap(self, s, scale, maxw):
        words = s.split(" ")
        lines, cur = [], ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if self.text_w(trial, scale) <= maxw:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def bar_chart(cv, x, y, w, h, vals, cols, labels=None):
    cv.box(x - 4, y - 4, w + 8, h + 8, INK, 1)
    n = len(vals)
    bw = w // n
    mx = max(vals)
    for i, v in enumerate(vals):
        bh = int(v / mx * (h - 6))
        cv.rect(x + i * bw + 3, y + h - bh, bw - 6, bh, cols[i % len(cols)])
    if labels:
        for i, lb in enumerate(labels):
            cv.text(lb, x + i * bw + 3, y + h + 8, 1, INK)


def draw_skyline(cv, x, y, w, h):
    # Sunset sky, sun, buildings, sea strip, palm.
    cv.rect(x, y, w, h, SKY)
    cv.circle(x + w - 70, y + 52, 34, SUN)
    cv.disc_ring(x + w - 70, y + 52, 40, SUN, 3)
    heights = [0.55, 0.8, 0.45, 0.95, 0.65, 0.85, 0.5, 0.75]
    bw = w // len(heights)
    for i, f in enumerate(heights):
        bh = int(h * 0.62 * f)
        bx = x + i * bw + 2
        cv.rect(bx, y + h - 46 - bh, bw - 4, bh + 46, INK)
        for wy in range(4):
            for wx in range(2):
                cv.rect(bx + 5 + wx * 12, y + h - 40 - bh + 8 + wy * 16, 5, 6, GOLD)
    cv.rect(x, y + h - 46, w, 46, TEAL)
    cv.line(x, y + h - 30, x + w, y + h - 30, WHITE, 2)
    cv.line(x, y + h - 14, x + w, y + h - 14, WHITE, 2)
    # Palm tree at left.
    cv.line(x + 26, y + h - 46, x + 26, y + h - 120, GREEN, 4)
    for dx, dy in ((-34, -18), (-20, -30), (0, -34), (20, -28), (34, -14)):
        cv.line(x + 26, y + h - 120, x + 26 + dx, y + h - 120 + dy, GREEN, 3)


def icon_chart(cv, x, y, s):
    vals = [0.55, 0.8, 1.0]
    cols = [BLUE, TEAL, RED]
    for i, v in enumerate(vals):
        bh = int(44 * v)
        cv.rect(x + i * 20, y + 46 - bh, 14, bh, cols[i])
    cv.line(x - 4, y + 48, x + 64, y + 48, INK, 2)


def icon_globe(cv, x, y, s):
    cv.circle(x + 32, y + 24, 24, BLUE)
    cv.circle(x + 32, y + 24, 24, INK)  # placeholder overwritten below
    cv.disc_ring(x + 32, y + 24, 24, INK, 2)
    cv.circle(x + 32, y + 24, 22, BLUE)
    cv.line(x + 10, y + 24, x + 54, y + 24, WHITE, 2)
    cv.line(x + 32, y + 4, x + 32, y + 44, WHITE, 2)
    cv.rect(x + 22, y + 12, 20, 8, GREEN)
    cv.rect(x + 28, y + 30, 16, 8, GREEN)


def icon_scales(cv, x, y, s):
    cv.line(x + 32, y + 2, x + 32, y + 44, INK, 3)
    cv.line(x + 8, y + 8, x + 56, y + 8, INK, 3)
    cv.line(x + 8, y + 8, x + 4, y + 28, INK, 2)
    cv.line(x + 8, y + 8, x + 12, y + 28, INK, 2)
    cv.line(x + 56, y + 8, x + 52, y + 28, INK, 2)
    cv.line(x + 56, y + 8, x + 60, y + 28, INK, 2)
    cv.tri(x - 2, y + 28, x + 18, y + 28, x + 8, y + 38, GOLD)
    cv.tri(x + 46, y + 28, x + 66, y + 28, x + 56, y + 38, GOLD)
    cv.rect(x + 24, y + 44, 16, 4, INK)


def icon_rocket(cv, x, y, s):
    cv.tri(x + 32, y + 2, x + 20, y + 26, x + 44, y + 26, RED)
    cv.rect(x + 20, y + 26, 24, 14, INK)
    cv.tri(x + 20, y + 26, x + 10, y + 40, x + 20, y + 40, RED)
    cv.tri(x + 44, y + 26, x + 54, y + 40, x + 44, y + 40, RED)
    cv.tri(x + 28, y + 40, x + 36, y + 40, x + 32, y + 52, GOLD)


def icon_tank(cv, x, y, s):
    cv.rect(x + 8, y + 26, 40, 14, INK)
    cv.line(x + 40, y + 30, x + 62, y + 24, INK, 4)
    cv.rect(x + 16, y + 12, 24, 14, TEAL)
    for i in range(5):
        cv.circle(x + 14 + i * 8, y + 44, 4, INK)


def icon_bridge(cv, x, y, s):
    cv.line(x + 2, y + 40, x + 62, y + 40, INK, 3)
    cv.line(x + 14, y + 40, x + 14, y + 8, INK, 3)
    cv.line(x + 50, y + 40, x + 50, y + 8, INK, 3)
    cv.line(x + 14, y + 8, x + 50, y + 8, INK, 3)
    for i in range(5):
        cv.line(x + 14 + i * 9, y + 8, x + 14 + i * 9, y + 40, GREY, 1)
    cv.tri(x + 26, y + 40, x + 38, y + 40, x + 32, y + 22, RED)


def icon_coin(cv, x, y, s):
    cv.circle(x + 32, y + 24, 22, GOLD)
    cv.disc_ring(x + 32, y + 24, 22, INK, 2)
    cv.text("45", x + 20, y + 14, 2, INK)


def icon_dish(cv, x, y, s):
    cv.line(x + 12, y + 46, x + 40, y + 20, INK, 3)
    cv.tri(x + 40, y + 6, x + 58, y + 14, x + 48, y + 30, BLUE)
    cv.circle(x + 52, y + 12, 3, RED)
    cv.line(x + 12, y + 46, x + 4, y + 52, INK, 3)
    cv.line(x + 12, y + 46, x + 22, y + 52, INK, 3)


ICONS = {
    "chart": icon_chart, "globe": icon_globe, "scales": icon_scales,
    "rocket": icon_rocket, "tank": icon_tank, "bridge": icon_bridge,
    "coin": icon_coin, "dish": icon_dish,
}

CARDS = [
    ("MARKETS", "ANTHROPIC DEBUTS", "ON NASDAQ AS ANT",
     "PRICED AT $83. $81.3BN RAISED, THE LARGEST US IPO EVER.", "chart"),
    ("DIPLOMACY", "TRUMP, XI, PUTIN", "MEET IN SHENZHEN",
     "FIRST TRILATERAL OF THE THREE LEADERS, AT APEC.", "globe"),
    ("JUSTICE", "WORLD COURT RULES", "ON ROHINGYA CASE",
     "ICJ JUDGMENT IN THE HAGUE: GAMBIA V. MYANMAR.", "scales"),
    ("GULF", "IRAN HITS US BASE", "IN KUWAIT",
     "KUWAIT AND BAHRAIN SAY THEY INTERCEPTED DRONES.", "rocket"),
    ("GAZA", "ISRAELI TANKS CROSS", "THE YELLOW LINE",
     "FIRST GROUND OPERATION SINCE THE CEASEFIRE.", "tank"),
    ("UKRAINE", "CRIMEA BRIDGE HIT", "AGAIN",
     "TRAFFIC SUSPENDED AFTER A NEW ATTACK, OFFICIALS SAY.", "bridge"),
    ("EUROPE", "EU PLANS 45BN EURO", "UKRAINE LOAN",
     "20BN BUDGET, 25BN ARMS. REPAID ONLY IF RUSSIA PAYS.", "coin"),
    ("SPACE", "NASA MARKS VOYAGER", "LIGHT-DAY MARK",
     "PROBE NOW 16.1BN MILES OUT. SIGNALS TAKE A DAY.", "dish"),
]


def draw_card(cv, x, y, w, h, kicker, h1, h2, sub, icon):
    cv.rect(x, y, w, h, WHITE)
    cv.box(x, y, w, h, INK, 2)
    cv.text(kicker, x + 12, y + 10, 2, RED)
    cv.text(h1, x + 12, y + 32, 3, INK)
    cv.text(h2, x + 12, y + 56, 3, INK)
    lines = cv.wrap(sub, 2, w - 118)
    for i, ln in enumerate(lines[:2]):
        cv.text(ln, x + 12, y + 88 + i * 16, 2, INK)
    ICONS[icon](cv, x + w - 84, y + h - 66, 1)


def main():
    cv = Canvas(W, H, CREAM)
    # Masthead.
    cv.centered("THE WORLD IN ONE PAGE", 26, 2, GREY)
    cv.rect(24, 56, 976, 66, INK)
    cv.centered("THURSDAY 19 NOVEMBER 2026", 74, 5, WHITE)
    cv.rect(24, 130, 976, 3, INK)
    cv.centered("NINE STORIES THAT DEFINED THE DAY", 140, 2, RED)

    # Hero story: GTA VI.
    hx, hy, hw, hh = 24, 162, 976, 252
    cv.rect(hx, hy, hw, hh, WHITE)
    cv.box(hx, hy, hw, hh, INK, 3)
    cv.text("HERO STORY  *  CULTURE", hx + 16, hy + 14, 2, RED)
    cv.text("VICE CITY OPENS", hx + 16, hy + 38, 5, INK)
    cv.text("GTA VI ROLLS OUT", hx + 16, hy + 80, 5, INK)
    cv.text("WORLDWIDE TODAY", hx + 16, hy + 122, 5, RED)
    for i, ln in enumerate([
        "AFTER 13 YEARS, ROCKSTAR'S",
        "GAME UNLOCKS AT MIDNIGHT",
        "IN EACH MARKET, FROM NEW",
        "ZEALAND AROUND THE GLOBE.",
    ]):
        cv.text(ln, hx + 16, hy + 168 + i * 15, 2, INK)
    # Numbers strip.
    cv.rect(hx + 16, hy + 226, 520, 2, INK)
    cv.text("99 METACRITIC  *  16M PRE-SOLD  *  $1.5BN", hx + 16, hy + 234, 2, BLUE)
    draw_skyline(cv, hx + 560, hy + 14, 400, 224)

    # Cards grid: 2 columns x 4 rows.
    cw, chh, gx, gy = 480, 128, 16, 12
    for i, (kicker, h1, h2, sub, icon) in enumerate(CARDS):
        col, row = i % 2, i // 2
        x = 24 + col * (cw + gx)
        y = 426 + row * (chh + gy)
        draw_card(cv, x, y, cw, chh, kicker, h1, h2, sub, icon)

    # Footer.
    cv.rect(24, 984, 976, 2, INK)
    cv.centered("SOURCES: REUTERS, BBC, NASA, ICJ, EUROPEAN COMMISSION  *  19 NOVEMBER 2026", 992, 1, GREY)

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "./out")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    data = encode_png(cv)
    with open(path, "wb") as f:
        f.write(data)


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])

    def chunk(kind, payload):
        c = struct.pack(">I", len(payload)) + kind + payload
        c += struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


if __name__ == "__main__":
    main()
