"""Generate backend/templates/parking_template.dxf with required block definitions."""

from __future__ import annotations

import sys
from pathlib import Path

import ezdxf
from ezdxf import colors

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "templates" / "parking_template.dxf"

BLOCKS = [
    "GROUND_LEVEL_BLOCK",
    "SUV_BLOCK",
    "SEDAN_BLOCK",
    "MACHINE_ROOM_BLOCK",
    "PLACE_HOLDER",
    "PARKING_BLOCK",
    "PALLET_DYN_BLOCK",
    "COUNTER_WEIGHT_DYN_BLOCK",
    "TRANSPORTER_DYN_BLOCK",
    "RCC_BRACKET_DYN_BLOCK",
    "RCC_DYN_BLOCK",
]


def main() -> None:
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.MM
    for name in BLOCKS:
        blk = doc.blocks.new(name)
        blk.add_line((0, 0), (2000, 0), dxfattribs={"color": colors.WHITE})
        blk.add_line((2000, 0), (2000, 1000), dxfattribs={"color": colors.WHITE})
        blk.add_line((2000, 1000), (0, 1000), dxfattribs={"color": colors.WHITE})
        blk.add_line((0, 1000), (0, 0), dxfattribs={"color": colors.WHITE})

    msp = doc.modelspace()
    msp.add_blockref("PLACE_HOLDER", (8000, 5000))
    for nm, pt in [
        ("PALLET_DYN_BLOCK", (3000, 3000)),
        ("COUNTER_WEIGHT_DYN_BLOCK", (4000, 3000)),
        ("TRANSPORTER_DYN_BLOCK", (5000, 3000)),
        ("RCC_BRACKET_DYN_BLOCK", (6000, 3000)),
        ("RCC_DYN_BLOCK", (7000, 3000)),
    ]:
        msp.add_blockref(nm, pt)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(OUT)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
    sys.exit(0)
