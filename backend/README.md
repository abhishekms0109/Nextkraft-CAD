# Nextkraft CAD backend

FastAPI service that turns form parameters into a DXF (via **ezdxf**) and renders **PDF** using **ezdxf + matplotlib** — no QCAD or AutoCAD needed at runtime.

## Prerequisites

- Python 3.11+
- Dependencies: `pip install -r requirements.txt`

## Template DXF

If `templates/parking_template.dxf` is missing, generate it:

```powershell
cd backend
python build_template.py
```

You can replace this file with your own DXF drawing (keep the same block names used in `parking_constants.py` or adjust the code).

## Run the API

From the `backend` folder:

```powershell
cd backend
uvicorn main:app --host 127.0.0.1 --port 8000
```

Check configuration:

```http
GET http://127.0.0.1:8000/api/health
```

Generate PDF (used by the Vite app via proxy):

```http
POST http://127.0.0.1:8000/api/generate
Content-Type: application/json

{"length_mm":5000,"width_mm":2500,"height_mm":25000,"suv_percent":40,"sedan_percent":60}
```

## Frontend (from repo root)

```powershell
npm run dev
```

Vite proxies `/api` to `http://127.0.0.1:8000`. Start **both** the backend and `npm run dev`, then submit the form; the PDF should download.

## Flow

1. `job_builder` uses `Function_Ref/Python_ref.py` (`calculate_parking`) and legacy geometry constants from `auto_parking_proposal.py`.
2. `dxf_render` writes all entities (blocks, text, labels, dimensions, table) into a copy of the template DXF.
3. `cad_service` renders the DXF to PDF using **ezdxf**'s matplotlib backend — pure Python, no external CAD application.
