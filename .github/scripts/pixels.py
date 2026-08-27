#!/usr/bin/env python3
"""Pixel-grid sprite engine. Grids are authored as text; runs of identical
pixels are merged into single rects so the SVG stays small."""

PAL = {
    # shared
    "B": "#241F1B", "W": "#FFFFFF", "K": "#2E2A24",
    # pikachu — light / mid / shade / tinted outline
    "1": "#FDEB8B", "Y": "#F7D02C", "2": "#DCA818", "3": "#7E590F",
    "R": "#F26A5E", "r": "#C4322A",
    # charmander
    "4": "#FFC08F", "O": "#F0894A", "5": "#CC6A34", "6": "#8A4419",
    "C": "#FCE7C0", "c": "#DDBE8B",
    "F": "#FF9B3D", "f": "#FFE066",
    # squirtle
    "7": "#A9E0F5", "S": "#5FB6E0", "8": "#3B87B4", "9": "#1F4E6B",
    "H": "#DCA868", "h": "#A87038", "i": "#6E4518",
    # bulbasaur
    "G": "#9BDBAF", "g": "#69B387", "j": "#33604A",
    "P": "#8FCE72", "p": "#5E9B4E", "q": "#35673A",
    # jigglypuff
    "J": "#FBC8DA", "u": "#E495B4", "v": "#A85C77",
    # psyduck
    "D": "#FBEC9E", "d": "#E0C55A", "E": "#E8A93F", "e": "#A87220",
    # ben 10 — omnitrix green
    "X": "#7CF03A", "x": "#4CB81C", "z": "#22600C",
    # heatblast
    "M": "#FF7A2B", "m": "#C4441A", "n": "#7A2208",
    "Q": "#FFD75E",
    # four arms
    "V": "#E8523C", "b": "#A32C1E", "N": "#5E1509",
    # diamondhead
    "I": "#9BE8C4", "I2": "#4FB88C",
    # scenery
    "T": "#7A5230", "t": "#5C3D24",
    "A": "#E9DCA0", "a": "#D6C489",
}

def norm(grid):
    """Pad ragged rows so a miscounted dot can never shift a sprite."""
    w = max(len(r) for r in grid)
    return [r.replace(" ", ".").ljust(w, ".") for r in grid]


def show(grid, title=""):
    """Terminal preview — iterate on shape without a browser."""
    if title:
        print(title)
    for row in norm(grid):
        print("".join(" " if c == "." else c for c in row))
    print()


def runs(grid, px, ox=0, oy=0):
    """Emit merged horizontal runs as rects."""
    out = []
    for r, row in enumerate(norm(grid)):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch in ". ":
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
    "...3............3.........",
    "...3B..........B3.........",
    "...3B..........B3.....33..",
    "...32..........23....3Y13.",
    "...3Y2........2Y3...3Y13..",
    "...3Y2........2Y3..3Y13...",
    "...3Y2.333333.2Y3.3YY13...",
    "...3Y33Y1111Y33Y3.3Y113...",
    "..3Y1111111111111Y33Y13...",
    "..3Y1BW111111BW11Y3.313...",
    "..3Y11111111111111Y3.33...",
    "..3YRr111331111RrY3.......",
    "..3Y2Rr1111111Rr2Y3.......",
    "...3Y21111111112Y3........",
    "....3321111111122 33......",
    ".....3Y211111112Y3........",
    "....3Y21111111112Y3.......",
    "....3Y23.....32Y3.........",
    ".....33.......33..........",
]
PIKA_B = PIKA_A[:16] + [
    "....3Y21111111112Y3.......",
    ".....3Y23...32Y3..........",
    "......33.....33...........",
]

# ------------------------------------------------------------- heatblast
HEAT_A = [
    "........QQQ.............",
    ".......QffQQ............",
    "......QfFFfQ............",
    ".....MffFFffM...........",
    "....MmFFFFFFmM..........",
    "....MmmFFFFmmM..........",
    "...nMmmMMMMmmMn.........",
    "...nMmmmmmmmmMn.........",
    "...nMmBWmmmBWmMn........",
    "...nMmmmmmmmmmMn........",
    "...nMmmMMMMMmmMn........",
    "....nMmmmmmmmMn.........",
    "..nMMmmmmmmmmmMMn.......",
    "..nMn.nMmmmmMn.nMn......",
    "......nMmmmmMn..........",
    "......nMMn.nMMn.........",
    "......nnn...nnn.........",
    "........................",
]
HEAT_B = HEAT_A[:15] + [
    "......nMmmMmMn..........",
    ".......nMMnMMn..........",
    ".......nnn.nnn..........",
]

# ------------------------------------------------------------- four arms
FOUR_A = [
    "........................",
    "....NNNNNNNN............",
    "...NVVVVVVVVN...........",
    "..NVVBWVVBWVVN..........",
    "..NVVVVVVVVVVN..........",
    "..NVVVbbbbVVVN..........",
    "..NVVBWVVBWVVN..........",
    "...NVVVVVVVVN...........",
    "NNNNVVVVVVVVNNNN........",
    "NVVVVVVVVVVVVVVN........",
    "NVVNNVVVVVVNNVVN........",
    "NNN..NVVVVN..NNN........",
    "NNN..NVVVVN..NNN........",
    "NVVNNVVVVVVNNVVN........",
    "NVVVVVVVVVVVVVVN........",
    "NNNNVVVVVVVVNNNN........",
    "....NVVN.NVVN...........",
    "....NNN...NNN...........",
]
FOUR_B = FOUR_A[:16] + [
    ".....NVVNVVN............",
    ".....NNN.NNN............",
]

# ------------------------------------------------------------- charmander
CHAR_A = [
    "..................FF....",
    ".................FfF....",
    "....66666666.....Ff.....",
    "...6O44444O6.....FF.....",
    "..6O44444444O6...F......",
    "..6O4BW44BW44O6.........",
    "..6O4444444444O6........",
    "..6O444666444O6.........",
    "...6O44444444O6.........",
    "....6O444444O6..........",
    "...6O44444444O6.........",
    "..6OCCCCCCCCO6..OO6.....",
    "..6CCCCCCCCCC6.OO6......",
    "..6CCCCCCCCCC6OO6.......",
    "..6OCCCCCCCCO6O6........",
    "...6OCCCCCCO6...........",
    "...6O5O6..6O5O6.........",
    "....666....666..........",
]
CHAR_B = CHAR_A[:15] + [
    "...6OCCCCCCO6...........",
    "....6O5OO5O6............",
    ".....66..66.............",
]

# --------------------------------------------------------------- squirtle
SQUI_A = [
    "........................",
    "....99999999............",
    "...9S7777777S9..........",
    "..9S777777777S9.........",
    "..9S7BW777BW77S9........",
    "..9S77777777777S9.......",
    "..9S777999777S9.........",
    "...9S7777777S9..........",
    "....9SSSSSS9............",
    "...ihhhhhhhhhi..........",
    "..ihHHCCCCCHHhi..SS9....",
    "..ihHCCCCCCCCHhi.SS9....",
    "..ihHCCCCCCCCHhiSS9.....",
    "..ihHHCCCCCHHhi9S9......",
    "...ihhhhhhhhhi..........",
    "....9SS9..9SS9..........",
    ".....99....99...........",
    "........................",
]
SQUI_B = SQUI_A[:14] + [
    "...ihhhhhhhhhi..........",
    "....9SS99SS9............",
    ".....999999.............",
    "........................",
]

# -------------------------------------------------------------- bulbasaur
BULB_A = [
    "........................",
    "........PPPPPP..........",
    ".......PpppppppP........",
    "......PpqqqqqqpP........",
    "....jjjjGGGGjjjj........",
    "...jGGGGGGGGGGGGj.......",
    "..jGGBWGGGGGGBWGGj......",
    "..jGGGGGGGGGGGGGGj......",
    "..jGGGGjjjjjGGGGGj......",
    "..jGGGGGGGGGGGGGGj......",
    "..jGggGGGGGGGGggGj......",
    "..jGGGGGGGGGGGGGGj......",
    "...jGGGGGGGGGGGGj.......",
    "..jGgjjGGGGGGjjgGj......",
    "..jGgj..jjjj..jgGj......",
    "...jj..........jj.......",
    "........................",
    "........................",
]
BULB_B = BULB_A[:13] + [
    "..jGGGjjGGGGjjGGGj......",
    "...jgj..jjjj..jgj.......",
    "....j..........j........",
    "........................",
    "........................",
]

# ------------------------------------------------------------- jigglypuff
JIGG_A = [
    "........................",
    "......JJJJ..............",
    ".....JuuuuJ.............",
    "....vvJJJJvv............",
    "...vJJJJJJJJv...........",
    "..vJJJJJJJJJJv..........",
    "..vJBWJJJJBWJJv.........",
    "..vJJJJJJJJJJJv.........",
    "..vJuuJJvvJJuuv.........",
    "..vJJJJJJJJJJJv.........",
    "...vJJJJJJJJJv..........",
    "....vJJJJJJJv...........",
    "....vJuv..vuJv..........",
    ".....vv....vv...........",
    "........................",
    "........................",
    "........................",
    "........................",
]
JIGG_B = JIGG_A[:12] + [
    "....vJJJJJJJv...........",
    ".....vJuvuJv............",
    "......vv.vv.............",
    "........................",
    "........................",
    "........................",
]

# ---------------------------------------------------------------- psyduck
PSY_A = [
    "........................",
    "....e...e...e...........",
    "....e...e...e...........",
    "....eeeeeeeee...........",
    "...eDDDDDDDDDe..........",
    "..eDDDDDDDDDDDe.........",
    "..eDDBDDDDDBDDe.........",
    "..eDDBDDDDDBDDe.........",
    "..eDDDDDDDDDDDe.........",
    "..eEEEEEEEEEEEe.........",
    "...eEEEEEEEEEe..........",
    "...eDDDDDDDDDe..........",
    "..eDDDDDDDDDDDe.........",
    "..eDdDDDDDDDdDe.........",
    "...eDDDDDDDDDe..........",
    "...eDDe...eDDe..........",
    "....ee.....ee...........",
    "........................",
]
PSY_B = PSY_A[:15] + [
    "...eDDDDDDDDDe..........",
    "....eDDeeDDe............",
    ".....ee..ee.............",
]

if __name__ == "__main__":
    for nm, g in (("PIKACHU", PIKA_A), ("HEATBLAST", HEAT_A),
                  ("FOUR ARMS", FOUR_A)):
        show(g, nm)
