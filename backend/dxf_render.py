"""Apply job geometry to a DXF using ezdxf (QCAD opens the result for PDF export)."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import ezdxf
from ezdxf import colors


def _ensure_block(doc: ezdxf.Drawing, name: str) -> None:
    if name not in doc.blocks:
        blk = doc.blocks.new(name)
        blk.add_line((0, 0), (100, 0), dxfattribs={"color": colors.RED})


def render_job_to_dxf(dxf_path: Path, job: dict[str, Any]) -> None:
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    doc.units = ezdxf.units.MM

    for bi in job.get("block_inserts", []):
        name = bi["name"]
        if name not in doc.blocks:
            _ensure_block(doc, name)
        ins = msp.add_blockref(name, (bi["x"], bi["y"]))
        ins.dxf.xscale = float(bi["sx"])
        ins.dxf.yscale = float(bi["sy"])
        ins.dxf.zscale = float(bi.get("sz", 1))
        ins.dxf.rotation = math.radians(float(bi.get("rot", 0)))

    for bi in job.get("parking_inserts", []):
        name = bi["name"]
        if name not in doc.blocks:
            _ensure_block(doc, name)
        ins = msp.add_blockref(name, (bi["x"], bi["y"]))
        ins.dxf.xscale = float(bi["sx"])
        ins.dxf.yscale = float(bi["sy"])
        ins.dxf.zscale = float(bi.get("sz", 1))
        ins.dxf.rotation = math.radians(float(bi.get("rot", 0)))

    for ln in job.get("lines", []):
        msp.add_line(
            (ln["x1"], ln["y1"]),
            (ln["x2"], ln["y2"]),
            dxfattribs={"color": colors.MAGENTA},
        )

    for t in job.get("texts", []):
        txt = msp.add_text(
            t["text"],
            height=float(t["height"]),
            dxfattribs={"color": colors.CYAN, "insert": (t["x"], t["y"])},
        )

    y0 = 42000
    x0 = 500
    for i, row in enumerate(job.get("table_rows", [])):
        y = y0 - i * 400
        line = f'{row["param"]}: {row["value"]}'
        msp.add_text(
            line,
            height=280,
            dxfattribs={"color": colors.YELLOW, "insert": (x0, y)},
        )

    for upd in job.get("block_param_updates", []):
        bname = upd["block_name"]
        sx = upd.get("sx")
        sy = upd.get("sy")
        for e in msp.query("INSERT"):
            if e.dxf.name.upper() != bname.upper():
                continue
            if sx is not None:
                e.dxf.xscale = float(sx)
            if sy is not None:
                e.dxf.yscale = float(sy)

    for dim in job.get("dimensions", []):
        if dim.get("kind") != "aligned":
            continue
        x1, y1 = dim["x1"], dim["y1"]
        x2, y2 = dim["x2"], dim["y2"]
        ox = float(dim["offset_x"])
        msp.add_line((x1, y1), (x2, y2), dxfattribs={"color": colors.GREEN})
        mx = (x1 + x2) / 2 + ox
        my = (y1 + y2) / 2
        msp.add_line((x2, y2), (mx, my), dxfattribs={"color": colors.GREEN, "linetype": "DASHED"})

    doc.saveas(dxf_path)
