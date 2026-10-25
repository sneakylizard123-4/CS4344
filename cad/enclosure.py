"""Parametric enclosure for the CS4344 I2S DAC breakout.

Units are millimetres. The KiCad board STEP is exported with the board
bottom at Z=0, the top at Z=1.51 and Y pointing opposite to the PCB
editor. The board is placed at (7.4, 5.5, 4.2) in this model so the
3.5 mm jack face sits against the right-hand wall.

Requires CadQuery 2.x. Run from the repository root:

    python3 cad/enclosure.py
"""

from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

BOARD_STEP = HERE / "CS4344-assembly.step"

OUTER_W = 30.0
OUTER_D = 36.0
BASE_H = 17.0
LID_H = 2.4
WALL = 4.0
FLOOR = 1.6
CORNER_R = 3.0

BOARD_X = 7.4
BOARD_Y = 5.5
BOARD_Z = 4.2
BOARD_W = 18.5
BOARD_D = 25.0

LEDGE_TOP = BOARD_Z
LEDGE_BOTTOM = 2.6

POST_R = 2.2
SCREW_PILOT_R = 0.85
SCREW_CLEAR_R = 1.1
SCREW_HEAD_R = 2.1
SCREW_HEAD_DEPTH = 1.2
SCREW_POSITIONS = [(3.0, 3.0), (27.0, 3.0), (3.0, 33.0), (27.0, 33.0)]


def rounded_box(width, depth, height, radius):
    return (
        cq.Workplane("XY")
        .box(width, depth, height, centered=(False, False, False))
        .edges("|Z")
        .fillet(radius)
    )


def box_between(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).translate(
        ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0)
    )


def make_base():
    outer = rounded_box(OUTER_W, OUTER_D, BASE_H, CORNER_R)
    cavity = rounded_box(OUTER_W - 2 * WALL, OUTER_D - 2 * WALL, BASE_H - FLOOR, CORNER_R).translate(
        (WALL, WALL, FLOOR)
    )
    base = outer.cut(cavity)

    for x, y in SCREW_POSITIONS:
        post = cq.Workplane("XY").circle(POST_R).extrude(BASE_H - FLOOR).translate((x, y, FLOOR))
        base = base.union(post)

    for x, y in SCREW_POSITIONS:
        pilot = (
            cq.Workplane("XY")
            .circle(SCREW_PILOT_R)
            .extrude(BASE_H - 6.0)
            .translate((x, y, 6.0))
        )
        base = base.cut(pilot)

    base = base.union(box_between(WALL, 8.2, WALL, OUTER_D - WALL, LEDGE_BOTTOM, LEDGE_TOP))
    base = base.union(box_between(25.3, OUTER_W - WALL, WALL, OUTER_D - WALL, LEDGE_BOTTOM, LEDGE_TOP))
    base = base.union(box_between(WALL, OUTER_W - WALL, WALL, 6.0, LEDGE_BOTTOM, LEDGE_TOP))
    base = base.union(box_between(WALL, OUTER_W - WALL, 30.0, OUTER_D - WALL, LEDGE_BOTTOM, LEDGE_TOP))

    jack_opening = box_between(25.0, OUTER_W + 0.5, 20.0, 29.0, 5.4, 11.6)
    base = base.cut(jack_opening)

    return base


def make_lid():
    lid = rounded_box(OUTER_W, OUTER_D, LID_H, CORNER_R).translate((0, 0, BASE_H))

    for x, y in SCREW_POSITIONS:
        clearance = (
            cq.Workplane("XY")
            .circle(SCREW_CLEAR_R)
            .extrude(LID_H + 0.4)
            .translate((x, y, BASE_H - 0.2))
        )
        lid = lid.cut(clearance)
        counterbore = (
            cq.Workplane("XY")
            .circle(SCREW_HEAD_R)
            .extrude(SCREW_HEAD_DEPTH + 0.2)
            .translate((x, y, BASE_H + LID_H - SCREW_HEAD_DEPTH))
        )
        lid = lid.cut(counterbore)

    header_slot = box_between(8.2, 24.5, 5.8, 9.2, BASE_H - 0.2, BASE_H + LID_H + 0.2)
    lid = lid.cut(header_slot)

    lid = lid.union(box_between(4.5, 5.7, 6.0, 30.0, 15.0, BASE_H))
    lid = lid.union(box_between(6.0, 24.0, 30.8, 31.8, 15.0, BASE_H))

    hold_down = box_between(5.7, 7.3, 10.0, 17.0, 5.72, BASE_H)
    hold_down = hold_down.union(box_between(7.3, 8.2, 10.0, 17.0, 5.72, 6.05))
    lid = lid.union(hold_down)

    return lid


def make_screw():
    shaft = cq.Workplane("XY").circle(1.0).extrude(8.0).translate((0, 0, 11.4))
    head = cq.Workplane("XY").circle(1.9).extrude(1.4).translate((0, 0, BASE_H + LID_H))
    return shaft.union(head)


def make_assembly(base, lid):
    dx = BOARD_X - 31.5
    dy = BOARD_Y + 56.0
    dz = BOARD_Z
    board = cq.importers.importStep(str(BOARD_STEP)).translate((dx, dy, dz))

    assembly = base.union(lid).union(board)
    for x, y in SCREW_POSITIONS:
        assembly = assembly.union(make_screw().translate((x, y, 0)))

    return assembly


def main():
    base = make_base()
    lid = make_lid()
    assembly = make_assembly(base, lid)

    cq.exporters.export(base, str(HERE / "CS4344-enclosure-base.step"))
    cq.exporters.export(lid, str(HERE / "CS4344-enclosure-lid.step"))
    cq.exporters.export(base, str(HERE / "CS4344-enclosure-base.stl"))
    cq.exporters.export(lid, str(HERE / "CS4344-enclosure-lid.stl"))
    cq.exporters.export(assembly, str(HERE / "CS4344-full-assembly.step"))


if __name__ == "__main__":
    main()
