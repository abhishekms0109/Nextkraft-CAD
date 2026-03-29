"""Build a JSON job for the QCAD runner from UI parameters (replaces Excel)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import ezdxf

from parking_constants import (
    DEFAULT_BLOCK_PARAMS,
    DIM_Y_START,
    DIMENSION_OFFSET_X,
    GROUND_BLOCK,
    GROUND_BLOCK_HEIGHT,
    LABEL_LINE_LENGTH,
    LABEL_TEXT_HEIGHT,
    MACHINE_ROOM_BLOCK,
    PARKING_BLOCK,
    PARKING_SCALE_X,
    PLACE_HOLDER,
    SEDAN_BLOCK,
    SEDAN_BLOCK_HEIGHT,
    SEDAN_SPACING,
    SUV_BLOCK,
    SUV_BLOCK_HEIGHT,
    SUV_SPACING,
    SUV_START_X,
    SUV_START_Y,
)
from parking_ref import calculate_parking


def _find_inserts(dxf_path: Path, block_name: str) -> list[dict[str, float]]:
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    out: list[dict[str, float]] = []
    for e in msp.query("INSERT"):
        if e.dxf.name.upper() == block_name.upper():
            x, y, z = e.dxf.insert
            out.append({"x": float(x), "y": float(y), "z": float(z)})
    return out


def build_job(
    *,
    length_mm: float,
    width_mm: float,
    height_mm: float,
    suv_percent: float,
    sedan_percent: float,
    working_dxf: Path,
    pdf_output: Path,
    block_params: dict[str, dict[str, float | None]] | None = None,
) -> dict[str, Any]:
    if suv_percent <= 0 or sedan_percent <= 0:
        raise ValueError("SUV and Sedan percentages must be greater than zero.")

    calc = calculate_parking(length_mm, width_mm, height_mm, suv_percent, sedan_percent)
    suv_levels = max(0, int(calc["suv_levels"]))
    sedan_levels = max(0, int(calc["sedan_levels"]))

    levels = {
        "SUV_LEVEL": suv_levels,
        "SEDAN_LEVEL": sedan_levels,
        "SUV_SLOT": SUV_SPACING,
        "SEDAN_SLOT": SEDAN_SPACING,
    }

    suv_height = levels["SUV_SLOT"]
    sedan_height = levels["SEDAN_SLOT"]
    suv_scale_y = suv_height / SUV_BLOCK_HEIGHT
    sedan_scale_y = sedan_height / SEDAN_BLOCK_HEIGHT

    block_inserts: list[dict[str, Any]] = []

    # Ground
    block_inserts.append(
        {"name": GROUND_BLOCK, "x": 0, "y": 0, "sx": 1, "sy": 1, "sz": 1, "rot": 0}
    )

    y = GROUND_BLOCK_HEIGHT
    for _i in range(suv_levels):
        block_inserts.append(
            {
                "name": SUV_BLOCK,
                "x": 0,
                "y": y,
                "sx": 1,
                "sy": suv_scale_y,
                "sz": 1,
                "rot": 0,
            }
        )
        y += suv_height

    if sedan_levels == 0 and suv_levels > 0:
        machine_y = y - suv_height
        block_inserts.append(
            {
                "name": MACHINE_ROOM_BLOCK,
                "x": 0,
                "y": machine_y,
                "sx": 1,
                "sy": 1,
                "sz": 1,
                "rot": 0,
            }
        )
    elif sedan_levels > 0:
        for _i in range(sedan_levels):
            block_inserts.append(
                {
                    "name": SEDAN_BLOCK,
                    "x": 0,
                    "y": y,
                    "sx": 1,
                    "sy": sedan_scale_y,
                    "sz": 1,
                    "rot": 0,
                }
            )
            y += sedan_height

        last_height = sedan_height if sedan_levels > 0 else suv_height
        machine_y = y - last_height
        block_inserts.append(
            {
                "name": MACHINE_ROOM_BLOCK,
                "x": 0,
                "y": machine_y,
                "sx": 1,
                "sy": 1,
                "sz": 1,
                "rot": 0,
            }
        )

    parking_inserts: list[dict[str, Any]] = []
    try:
        for p in _find_inserts(working_dxf, PLACE_HOLDER):
            parking_inserts.append(
                {
                    "name": PARKING_BLOCK,
                    "x": p["x"],
                    "y": p["y"],
                    "sx": PARKING_SCALE_X,
                    "sy": 1,
                    "sz": 1,
                    "rot": 0,
                }
            )
    except Exception:
        parking_inserts = []

    texts: list[dict[str, Any]] = []
    lines: list[dict[str, Any]] = []

    suv_spacing = levels["SUV_SLOT"]
    sedan_spacing = levels["SEDAN_SLOT"]
    suv_num = levels["SUV_LEVEL"]
    sedan_num = levels["SEDAN_LEVEL"]

    for i in range(suv_num):
        yy = SUV_START_Y + i * suv_spacing
        label = f"{i + 1}F"
        texts.append(
            {"x": SUV_START_X, "y": yy, "height": LABEL_TEXT_HEIGHT, "text": label}
        )
        ln_y = yy - LABEL_TEXT_HEIGHT / 2 - 100
        x1 = SUV_START_X - LABEL_LINE_LENGTH / 2
        x2 = SUV_START_X + LABEL_LINE_LENGTH / 2
        lines.append({"x1": x1, "y1": ln_y, "x2": x2, "y2": ln_y})

    sedan_start_y = SUV_START_Y + suv_spacing * suv_num
    for i in range(sedan_num):
        yy = sedan_start_y + i * sedan_spacing
        label = f"{suv_num + i + 1}F"
        texts.append(
            {"x": SUV_START_X, "y": yy, "height": LABEL_TEXT_HEIGHT, "text": label}
        )
        ln_y = yy - LABEL_TEXT_HEIGHT / 2 - 100
        x1 = SUV_START_X - LABEL_LINE_LENGTH / 2
        x2 = SUV_START_X + LABEL_LINE_LENGTH / 2
        lines.append({"x1": x1, "y1": ln_y, "x2": x2, "y2": ln_y})

    dim_end = (
        DIM_Y_START
        + 3000
        + suv_spacing * suv_num
        + sedan_spacing * sedan_num
        + 4200
    )
    dimensions = [
        {
            "kind": "aligned",
            "x1": 0,
            "y1": DIM_Y_START,
            "x2": 0,
            "y2": dim_end,
            "offset_x": DIMENSION_OFFSET_X,
        }
    ]

    table_rows: list[tuple[str, str]] = [
        ("Length Available (mm)", f"{length_mm:g}"),
        ("Width Available (mm)", f"{width_mm:g}"),
        ("Height Available (mm)", f"{height_mm:g}"),
        ("SUV %", f"{suv_percent:g}"),
        ("Sedan %", f"{sedan_percent:g}"),
        ("SUV levels", str(suv_levels)),
        ("Sedan levels", str(sedan_levels)),
        ("SUV cars", str(calc["suv_cars"])),
        ("Sedan cars", str(calc["sedan_cars"])),
        ("Total cars", str(calc["total_cars"])),
        ("Actual SUV %", str(calc["actual_suv_percent"])),
        ("Actual Sedan %", str(calc["actual_sedan_percent"])),
    ]

    params = dict(block_params or DEFAULT_BLOCK_PARAMS)
    block_param_updates: list[dict[str, Any]] = []
    for blk, vals in params.items():
        vx = vals.get("X")
        vy = vals.get("Y")
        block_param_updates.append(
            {
                "block_name": blk,
                "sx": (float(vx) / 100.0) if vx is not None else None,
                "sy": (float(vy) / 100.0) if vy is not None else None,
            }
        )

    return {
        "version": 1,
        "working_dxf": str(working_dxf.resolve()),
        "pdf_output": str(pdf_output.resolve()),
        "block_inserts": block_inserts,
        "parking_inserts": parking_inserts,
        "texts": texts,
        "lines": lines,
        "dimensions": dimensions,
        "table_rows": [{"param": a, "value": b} for a, b in table_rows],
        "block_param_updates": block_param_updates,
    }
