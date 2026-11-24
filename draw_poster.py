#!/usr/bin/env python3
"""Draw 'The World in One Day' - a one-page newspaper poster summing up the
world news of Tuesday, 24 November 2026.

Standard library only. No network, no fonts on disk: text is rendered from a
small 5x7 bitmap font defined below, and the PNG is encoded by hand with
zlib. Output is deterministic: the same input always produces the same bytes.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (248, 244, 236)
INK = (20, 20, 20)
BODY = (54, 50, 44)
RED = (178, 38, 29)
RULE = (198, 190, 174)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- font -----
# 5x7 bitmap font, uppercase + digits + common punctuation. Each glyph is
# seven rows of five characters; '#' is ink, '.' is empty.
FONT = {
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.#.#", "#..##"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (no trailing space)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# -------------------------------------------------------------- canvas -----
class Canvas:
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bg * (width * height))

    def _set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            base = (yy * self.w + x) * 3
            for xx in range(w):
                i = base + xx * 3
                self.px[i] = color[0]
                self.px[i + 1] = color[1]
                self.px[i + 2] = color[2]

    def text(self, s, x, y, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                glyph = FONT["?"]
            for r in range(7):
                row = glyph[r]
                for c in range(5):
                    if row[c] == "#":
                        self.rect(cx + c * scale, y + r * scale, scale, scale, color)
            cx += 6 * scale

    def text_centered(self, s, cx, y, scale, color):
        self.text(s, cx - text_width(s, scale) // 2, y, scale, color)


def png_chunk(kind, data):
    chunk = struct.pack(">I", len(data)) + kind + data
    chunk += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return chunk


def encode_png(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    out = b"\x89PNG\r\n\x1a\n"
    out += png_chunk(b"IHDR", ihdr)
    out += png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += png_chunk(b"IEND", b"")
    return out


# ------------------------------------------------------------- stories ----
# Six stories of Tuesday, 24 November 2026, verified against multiple news
# wires the same day. Headlines stay short; summaries stay factual.
STORIES = [
    {
        "kicker": "WORLD COURT",
        "headline": "MYANMAR GUILTY OF ROHINGYA GENOCIDE",
        "summary": "THE ICJ RULES MYANMAR COMMITTED GENOCIDE AGAINST THE "
        "ROHINGYA IN 2017, A FIRST FOR THE WORLD COURT.",
    },
    {
        "kicker": "WAR AT SEA",
        "headline": "UKRAINE SAYS IT SANK RUSSIAN WARSHIP OFF LIBYA",
        "summary": "KYIV SAYS NAVAL DRONES SANK A RUSSIAN CORVETTE AT "
        "BENGHAZI; LIBYA SAYS IT WAS HEAVILY DAMAGED.",
    },
    {
        "kicker": "CLIMATE",
        "headline": "COP31 TALKS COLLAPSE WITH NO DEAL",
        "summary": "AFTER 50 HOURS OF OVERTIME, 90 NATIONS REJECT A "
        "TEXT THAT NEVER NAMES FOSSIL FUELS.",
    },
    {
        "kicker": "TECH",
        "headline": "NVIDIA REINSTATES JENSEN HUANG AS CEO",
        "summary": "THE BOARD RESTORES ITS FOUNDER 11 DAYS AFTER HE QUIT, "
        "AS THE U.S. BLACKLISTS A CHIP FIRM.",
    },
    {
        "kicker": "MIDDLE EAST",
        "headline": "U.S. SANCTIONS IRAN'S SHADOW BANKING NETWORK",
        "summary": "TREASURY TARGETS NEARLY 30 EXCHANGE HOUSES AS GULF "
        "TENSIONS RISE AND RUBIO MEETS QATAR.",
    },
    {
        "kicker": "LATIN AMERICA",
        "headline": "MEXICO CAPTURES 'EL CHAPO ISIDRO' WITH U.S. HELP",
        "summary": "A U.S. DRONE HELPED CATCH THE DRUG LORD IN SINALOA. "
        "MEXICO WILL TRY HIM AT HOME.",
    },
]

MASTHEAD = "THE WORLD IN ONE DAY"
DATE_LINE = "TUESDAY, 24 NOVEMBER 2026"
FOOTER = "SIX STORIES FROM TUESDAY, 24 NOVEMBER 2026"


def draw_poster():
    cv = Canvas(W, H, PAPER)

    # Thin frame around the whole page.
    cv.rect(16, 16, W - 32, 2, RULE)
    cv.rect(16, H - 18, W - 32, 2, RULE)
    cv.rect(16, 16, 2, H - 32, RULE)
    cv.rect(W - 18, 16, 2, H - 32, RULE)

    # ---- masthead ----
    cv.rect(36, 36, 952, 6, RED)
    cv.text_centered(MASTHEAD, W // 2, 56, 7, INK)
    # Date line in red, flanked by two small red diamonds.
    date_w = text_width(DATE_LINE, 4)
    dx = (W - date_w) // 2
    cv.rect(dx - 34, 128, 12, 12, RED)
    cv.rect(dx + date_w + 22, 128, 12, 12, RED)
    cv.text(DATE_LINE, dx, 120, 4, RED)
    # Double rule under the header.
    cv.rect(36, 158, 952, 3, INK)
    cv.rect(36, 164, 952, 2, RED)

    # ---- story grid: 2 columns x 3 rows ----
    col_x = (36, 524)
    row_y = (182, 450, 718)
    cell_w, cell_h = 464, 248

    # Dividers between cells.
    cv.rect(512, 182, 2, 784, RULE)
    cv.rect(36, 439, 952, 2, RULE)
    cv.rect(36, 707, 952, 2, RULE)

    for i, story in enumerate(STORIES):
        x = col_x[i % 2]
        y = row_y[i // 2]
        # Kicker bar.
        cv.rect(x, y, cell_w, 26, RED)
        cv.text(story["kicker"], x + 10, y + 6, 2, WHITE)
        # Headline, wrapped to the cell width.
        head_lines = wrap_text(story["headline"], cell_w - 16, 4)
        hy = y + 38
        for line in head_lines:
            cv.text(line, x + 8, hy, 4, INK)
            hy += 32
        # Summary, wrapped to the cell width.
        sum_lines = wrap_text(story["summary"], cell_w - 16, 3)
        sy = hy + 8
        for line in sum_lines:
            cv.text(line, x + 8, sy, 3, BODY)
            sy += 24
        if sy > y + cell_h:
            raise ValueError("story %d overflows its cell" % (i + 1))

    # ---- footer ----
    cv.rect(36, 976, 952, 2, INK)
    cv.text_centered(FOOTER, W // 2, 986, 2, BODY)

    return encode_png(cv)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = "/output" if os.path.isdir("/output") else "out"
    os.makedirs(out_dir, exist_ok=True)
    data = draw_poster()
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
