"""FastAPI entry: POST /api/generate -> PDF bytes."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

from cad_service import run_generate_pdf
from config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nextkraft CAD API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateBody(BaseModel):
    length_mm: float = Field(gt=0)
    width_mm: float = Field(gt=0)
    height_mm: float = Field(gt=0)
    suv_percent: float = Field(gt=0)
    sedan_percent: float = Field(gt=0)


@app.get("/")
def root():
    """Avoid 404 when opening http://127.0.0.1:8000/ in the browser."""
    return {
        "service": "Nextkraft CAD API",
        "ui": "Run the Vite app (npm run dev) — usually http://localhost:5173",
        "docs": "/docs",
        "health": "/api/health",
        "generate_pdf": "POST /api/generate",
    }


@app.get("/api/health")
def health():
    try:
        s = get_settings()
        tpl = s.template_dxf
        return {
            "ok": True,
            "pdf_renderer": "ezdxf + matplotlib",
            "template_exists": tpl.is_file(),
            "template": str(tpl),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/generate")
def generate(body: GenerateBody):
    try:
        pdf = run_generate_pdf(
            length_mm=body.length_mm,
            width_mm=body.width_mm,
            height_mm=body.height_mm,
            suv_percent=body.suv_percent,
            sedan_percent=body.sedan_percent,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("generate failed")
        raise HTTPException(status_code=500, detail=str(e)) from e

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="nextkraft-parking.pdf"',
        },
    )


def _run_dev():
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(Path(__file__).resolve().parent)],
    )


if __name__ == "__main__":
    _run_dev()
