#!/usr/bin/env python3
"""Pixel-grid sprite engine. Grids are authored as text; runs of identical
pixels are merged into single rects so the SVG stays small."""

PAL = {
    "K": "#2E2A24",   # outline
    "Y": "#F7D02C", "D": "#D9A216",          # pikachu
    "R": "#E8483C", "B": "#221E1A", "W": "#FFFFFF",
    "O": "#F0894A", "o": "#C96B33", "C": "#FBD9A5",   # charmander
    "F": "#FF9B3D", "f": "#FFE066",                   # flame
    "S": "#5FB6E0", "s": "#3E8CB8",                   # squirtle blue
    "H": "#C98A4B", "h": "#9C6634",                   # shell
    "G": "#7DC48E", "g": "#4F9268",                   # bulbasaur
    "P": "#7BB661", "p": "#4A7A3F",                   # bulb
    "L": "#8FE07A", "l": "#5AA84B",                   # grass
    "T": "#7A5230", "t": "#5C3D24",                   # trunk
    "N": "#3E8F52", "n": "#2F7040",                   # leaves
    "A": "#E9DCA0", "a": "#D6C489",                   # path
}


def show(grid, title=""):
    """Terminal preview — iterate on shape without a browser."""
    if title:
        print(title)
    for row in grid:
        print("".join(" " if c == "." else c for c in row))
    print()


def runs(grid, px, ox=0, oy=0):
    """Emit merged horizontal runs as rects."""
    out = []
    for r, row in enumerate(grid):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch == ".":
                c += 1
                continue
            n = 1
            while c + n < len(row) and row[c + n] == ch:
                n += 1
            out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>'
                       % (ox + c * px, oy + r * px, n * px, px,
                          PAL.get(ch, "#f0f")))
            c += n
    return "".join(out)


# ---------------------------------------------------------------- pikachu
PIKA_A = [
    "...B............B.........",
    "...BB..........BB......KYK",
    "...KB..........BK.....KYYK",
    "...KYB........BYK....KYYK.",
    "...KYK........KYK...KYYK..",
    "...KYK........KYK..KYYK...",
    "...KYK.KKKKKK.KYK.KYYYYYK.",
    "...KYYKKYYYYKKYYKKYYYYYYK.",
    "..KYYYYYYYYYYYYYYKKKYYYK..",
    "..KYYBWYYYYYYBWYYK.KYYK...",
    "..KYYYYYYYYYYYYYYKKYYK....",
    "..KYRRYYYKKYYYRRYKKYK.....",
    "..KYRRYYYYYYYYRRYKKK......",
    "...KYYYYYYYYYYYYK.........",
    "....KKYYYYYYYYKK..........",
    ".....KYYYYYYYYK...........",
    "....KYYYYYYYYYYK..........",
    "....KYYK....KYYK..........",
    ".....KK......KK...........",
]

# frame B: legs together — the classic two-frame overworld walk
PIKA_B = PIKA_A[:16] + [
    "....KYYYYYYYYYYK..........",
    ".....KYYK..KYYK...........",
    "......KK....KK............",
]

# -------------------------------------------------------------- charmander
CHAR_A = [
    "..................FF....",
    ".................FfF....",
    "....KKKKKKKK.....Ff.....",
    "...KOOOOOOOOK....FF.....",
    "..KOOOOOOOOOOK...F......",
    "..KOBWOOOOBWOOK.........",
    "..KOOOOOOOOOOOK.........",
    "..KOOOKKKKOOOOK.........",
    "...KOOOOOOOOOK..........",
    "....KOOOOOOOK...........",
    "...KOOOOOOOOOK..........",
    "..KOOCCCCCCOOK..OOK.....",
    "..KOCCCCCCCCOK.OOK......",
    "..KOCCCCCCCCOKOOK.......",
    "..KOOCCCCCCOOKOK........",
    "...KOOCCCCOOK...........",
    "...KOOK..KOOK...........",
    "....KK....KK............",
]
CHAR_B = CHAR_A[:15] + [
    "...KOOCCCCOOK...........",
    "....KOOKKOOK............",
    ".....KK..KK.............",
]

# ---------------------------------------------------------------- squirtle
SQUI_A = [
    "........................",
    "....KKKKKKKK............",
    "...KSSSSSSSSK...........",
    "..KSSSSSSSSSSK..........",
    "..KSBWSSSSBWSSK.........",
    "..KSSSSSSSSSSSK.........",
    "..KSSSKKKKSSSSK.........",
    "...KSSSSSSSSSK..........",
    "....KSSSSSSSK...........",
    "...KHHHHHHHHHK..........",
    "..KHhhCCCCChhHK..SSK....",
    "..KHhCCCCCCCChHK.SSK....",
    "..KHhCCCCCCCChHKSSK.....",
    "..KHhhCCCCChhHKSK.......",
    "...KHHHHHHHHHK..........",
    "....KSSK..KSSK..........",
    ".....KK....KK...........",
    "........................",
]
SQUI_B = SQUI_A[:14] + [
    "...KHHHHHHHHHK..........",
    "....KSSKKSSK............",
    ".....KKKK...............",
    "........................",
]

# --------------------------------------------------------------- bulbasaur
BULB_A = [
    "........................",
    "........PPPPPP..........",
    ".......PppppppP.........",
    "......PpPPPPPPpP........",
    "....KKKKGGGGKKKK........",
    "...KGGGGGGGGGGGGK.......",
    "..KGGBWGGGGGGBWGGK......",
    "..KGGGGGGGGGGGGGGK......",
    "..KGGGGKKKKKGGGGGK......",
    "..KGGGGGGGGGGGGGGK......",
    "..KGgGGGGGGGGGGgGK......",
    "..KGGGGGGGGGGGGGGK......",
    "...KGGGGGGGGGGGGK.......",
    "..KGGKKGGGGGGKKGGK......",
    "..KGGK..KKKK..KGGK......",
    "...KK..........KK.......",
    "........................",
    "........................",
]
BULB_B = BULB_A[:13] + [
    "..KGGGKKGGGGKKGGGK......",
    "...KGK..KKKK..KGK.......",
    "....K..........K........",
    "........................",
    "........................",
]

# -------------------------------------------------------------- jigglypuff
JIGG_A = [
    "........................",
    "......JJJJ..............",
    ".....JjjjjJ.............",
    "....KKJJJJKK............",
    "...KJJJJJJJJK...........",
    "..KJJJJJJJJJJK..........",
    "..KJBWJJJJBWJJK.........",
    "..KJJJJJJJJJJJK.........",
    "..KJjjJJKKJJjjK.........",
    "..KJJJJJJJJJJJK.........",
    "...KJJJJJJJJJK..........",
    "....KJJJJJJJK...........",
    "....KJJK..KJJK..........",
    ".....KK....KK...........",
    "........................",
    "........................",
    "........................",
    "........................",
]
JIGG_B = JIGG_A[:12] + [
    "....KJJJJJJJK...........",
    ".....KJJKJJK............",
    "......KK.KK.............",
    "........................",
    "........................",
    "........................",
]

# ----------------------------------------------------------------- psyduck
PSY_A = [
    "........................",
    "....K...K...K...........",
    "....K...K...K...........",
    "....KKKKKKKKK...........",
    "...KYYYYYYYYYK..........",
    "..KYYYYYYYYYYYK.........",
    "..KYYKYYYYYKYYK.........",
    "..KYYKYYYYYKYYK.........",
    "..KYYYYYYYYYYYK.........",
    "..KEEEEEEEEEEEK.........",
    "...KEEEEEEEEEK..........",
    "...KYYYYYYYYYK..........",
    "..KYYYYYYYYYYYK.........",
    "..KYYYYYYYYYYYK.........",
    "...KYYYYYYYYYK..........",
    "...KYYK...KYYK..........",
    "....KK.....KK...........",
    "........................",
]
PSY_B = PSY_A[:15] + [
    "...KYYYYYYYYYK..........",
    "....KYYKKYYK............",
    ".....KK..KK.............",
]

if __name__ == "__main__":
    for nm, g in (("JIGGLYPUFF", JIGG_A), ("PSYDUCK", PSY_A)):
        show(g, nm)
