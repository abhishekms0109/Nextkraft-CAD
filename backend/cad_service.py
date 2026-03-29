"""Generate parking DXF and render to PDF using ezdxf + matplotlib (no QCAD needed)."""

from __future__ import annotations

import json
import logging
import shutil
import tempfile
from pathlib import Path

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import Settings, get_settings
from dxf_render import render_job_to_dxf
from job_builder import build_job

logger = logging.getLogger(__name__)


def _dxf_to_pdf(dxf_path: Path, pdf_path: Path) -> None:
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp)
    ax.set_aspect("equal")
    ax.autoscale()
    ax.axis("off")
    fig.savefig(str(pdf_path), format="pdf", bbox_inches="tight", pad_inches=0.25, dpi=150)
    plt.close(fig)


def run_generate_pdf(
    *,
    length_mm: float,
    width_mm: float,
    height_mm: float,
    suv_percent: float,
    sedan_percent: float,
    settings: Settings | None = None,
) -> bytes:
    settings = settings or get_settings()
    template = settings.template_dxf
    if not template.is_file():
        raise FileNotFoundError(
            f"Template DXF missing: {template}. Run: python build_template.py"
        )

    parent = settings.temp_parent or Path(tempfile.gettempdir())
    parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="nextkraft_", dir=parent))
    try:
        working_dxf = work / "drawing.dxf"
        shutil.copy2(template, working_dxf)
        pdf_path = work / "output.pdf"
        job = build_job(
            length_mm=length_mm,
            width_mm=width_mm,
            height_mm=height_mm,
            suv_percent=suv_percent,
            sedan_percent=sedan_percent,
            working_dxf=working_dxf,
            pdf_output=pdf_path,
        )
        job_path = work / "job.json"
        job_path.write_text(json.dumps(job, indent=2), encoding="utf-8")

        render_job_to_dxf(working_dxf, job)
        _dxf_to_pdf(working_dxf, pdf_path)

        if not pdf_path.is_file():
            raise RuntimeError("PDF was not created after rendering.")
        return pdf_path.read_bytes()
    finally:
        try:
            shutil.rmtree(work, ignore_errors=True)
        except OSError:
            pass
