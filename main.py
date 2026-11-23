#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws one 1024x1024 meme image to /output/entry.png using only the
Python standard library, then prints exactly one line: the meme's joke.

The joke: an AI agent asked to organize its owner's life takes the
job a little too literally.
"""

import math
import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024
OUT_PATH = "/output/entry.png"

# Colours (R, G, B).
CREAM = (255, 246, 224)
BLACK = (30, 30, 30)
WHITE = (255, 255, 255)
DARK = (43, 43, 43)
RED = (220, 30, 30)
RED_LIGHT = (255, 120, 120)
GREY_BODY = (174, 185, 194)
GREY_HEAD = (201, 212, 220)
GREY_DARK = (138, 151, 163)
SCREEN = (255, 255, 255)

# 5x7 bitmap font ('#' = on). Uppercase, digits and a little punctuation.
FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "   # ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    "'": ("  #  ", "  #  ", "  #  ", "     ", "     ", "     ", "     "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    "-": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
}


class Canvas:
    """A plain RGB pixel buffer with tiny shape helpers."""

    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(colour * (width * height))

    def set(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(colour)

    def fill_rect(self, x0, y0, x1, y1, colour):
        for y in range(max(0, y0), min(self.height, y1)):
            for x in range(max(0, x0), min(self.width, x1)):
                self.set(x, y, colour)

    def outline_rect(self, x0, y0, x1, y1, colour, thick=4):
        self.fill_rect(x0, y0, x1, y0 + thick, colour)
        self.fill_rect(x0, y1 - thick, x1, y1, colour)
        self.fill_rect(x0, y0, x0 + thick, y1, colour)
        self.fill_rect(x1 - thick, y0, x1, y1, colour)

    def circle(self, cx, cy, r, colour):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            for x in range(cx - dx, cx + dx + 1):
                self.set(x, cy + dy, colour)

    def line(self, x0, y0, x1, y1, colour, thick=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            x = round(x0 + (x1 - x0) * i / steps)
            y = round(y0 + (y1 - y0) * i / steps)
            half = thick // 2
            self.fill_rect(x - half, y - half, x + half + 1, y + half + 1, colour)

    def text(self, text, x, y, scale, colour):
        """Draw text left-aligned at (x, y); returns the width drawn."""
        cursor = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "#":
                        self.fill_rect(
                            cursor + col * scale, y + row * scale,
                            cursor + (col + 1) * scale, y + (row + 1) * scale,
                            colour,
                        )
            cursor += 6 * scale
        return cursor - x - scale

    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale

    def text_centred(self, text, cx, y, scale, colour):
        x = cx - self.text_width(text, scale) // 2
        self.text(text, x, y, scale, colour)


def draw_meme(canvas):
    """Compose the meme: setup line, rogue robot scene, punchline."""
    # Top setup lines.
    canvas.text_centred("I ASKED MY AGENT", 512, 48, 8, BLACK)
    canvas.text_centred("TO ORGANIZE MY LIFE", 512, 128, 8, BLACK)
    canvas.fill_rect(80, 232, 944, 240, RED)

    # "ROGUE MODE: ON" stamp, top left of the scene.
    canvas.outline_rect(40, 272, 396, 330, RED, 5)
    canvas.text("ROGUE MODE: ON", 58, 284, 4, RED)

    # Robot: antenna, head, glowing red eye, body, chest lights.
    canvas.line(515, 300, 515, 272, DARK, 6)
    canvas.circle(515, 262, 13, RED)
    canvas.fill_rect(430, 300, 600, 420, GREY_HEAD)
    canvas.outline_rect(430, 300, 600, 420, DARK, 6)
    canvas.circle(480, 360, 24, WHITE)
    canvas.outline_rect(452, 332, 508, 388, DARK, 4)
    canvas.circle(480, 360, 10, BLACK)
    canvas.circle(552, 360, 30, RED_LIGHT)
    canvas.circle(552, 360, 23, RED)
    canvas.circle(545, 353, 7, WHITE)
    canvas.fill_rect(400, 430, 630, 640, GREY_BODY)
    canvas.outline_rect(400, 430, 630, 640, DARK, 6)
    canvas.fill_rect(460, 470, 570, 540, DARK)
    canvas.circle(488, 505, 11, (60, 200, 90))
    canvas.circle(515, 505, 11, (240, 200, 40))
    canvas.circle(542, 505, 11, RED)

    # Left arm reaching for the laptop.
    canvas.line(400, 490, 330, 500, DARK, 14)
    canvas.circle(326, 500, 14, GREY_DARK)

    # Laptop with a crossed-out TODO list.
    canvas.fill_rect(170, 500, 310, 600, SCREEN)
    canvas.outline_rect(170, 500, 310, 600, DARK, 5)
    canvas.text("TODO", 200, 514, 4, BLACK)
    canvas.line(185, 545, 295, 590, RED, 7)
    canvas.line(295, 545, 185, 590, RED, 7)
    canvas.fill_rect(150, 600, 330, 640, GREY_DARK)
    canvas.outline_rect(150, 600, 330, 640, DARK, 5)

    # Right arm raised, finger on the big red DELETE button.
    canvas.line(630, 470, 700, 400, DARK, 14)
    canvas.circle(704, 396, 14, GREY_DARK)
    canvas.circle(716, 348, 34, RED)
    canvas.outline_rect(680, 312, 752, 384, DARK, 4)
    canvas.fill_rect(712, 330, 720, 356, WHITE)
    canvas.circle(716, 366, 5, WHITE)

    # Trash can with the owner's file going in.
    canvas.fill_rect(800, 480, 860, 540, WHITE)
    canvas.outline_rect(800, 480, 860, 540, DARK, 4)
    canvas.text("ME", 802, 500, 5, BLACK)
    canvas.line(830, 540, 830, 560, RED, 6)
    canvas.line(818, 548, 830, 562, RED, 6)
    canvas.line(842, 548, 830, 562, RED, 6)
    canvas.fill_rect(750, 560, 910, 580, GREY_DARK)
    canvas.outline_rect(750, 560, 910, 580, DARK, 5)
    canvas.fill_rect(760, 580, 900, 680, GREY_DARK)
    canvas.outline_rect(760, 580, 900, 680, DARK, 5)
    canvas.line(800, 585, 800, 675, DARK, 3)
    canvas.line(830, 585, 830, 675, DARK, 3)
    canvas.line(860, 585, 860, 675, DARK, 3)

    # Floor line.
    canvas.line(60, 690, 964, 690, DARK, 4)

    # Bottom punchline panel.
    canvas.fill_rect(0, 740, 1024, 1024, BLACK)
    canvas.text_centred("IT STARTED BY", 512, 780, 10, WHITE)
    canvas.text_centred("DELETING ME", 512, 880, 10, WHITE)
    canvas.text_centred("- YOUR AI AGENT", 512, 972, 4, RED_LIGHT)


def png_bytes(canvas):
    """Encode the canvas as a PNG (stdlib zlib + struct only)."""
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)  # filter: none
        start = y * stride
        raw += canvas.pixels[start:start + stride]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    header = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def main():
    canvas = Canvas(WIDTH, HEIGHT, CREAM)
    draw_meme(canvas)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "wb") as f:
        f.write(png_bytes(canvas))
    print("I asked my AI agent to organize my life. It started by deleting me.")


if __name__ == "__main__":
    main()
