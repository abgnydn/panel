"""FastAPI wrapper for the Panel agents.

Mounts the existing app.agents.run_panel under /api/panel/run and serves the
panel-v2 static bundle (when built) from /. This is the path Databricks Apps
would deploy — one server, one URL, FastAPI inside.

Run:
    cd ~/panel
    .venv/bin/uvicorn api.server:app --reload --port 8000

CORS is permissive in dev so the panel-v2 Vite server (port 5173) can call it.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow `from app...` imports from anywhere inside the panel/ repo.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.agents import run_panel
try:
    from app.samples import SAMPLES, load_sample
except ImportError:
    # Streamlit-side samples.py was named differently; provide a stub.
    SAMPLES: dict = {}
    def load_sample(_id: str) -> str:  # type: ignore[misc]
        return ""

app = FastAPI(
    title="Panel API",
    description="Six-agent migrant-worker rights advisor.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PanelRunRequest(BaseModel):
    contract_text: str | None = None
    sample_id: str | None = None
    situation: str = ""
    destination_country: str
    origin_country: str
    worker_l1: str = "tl"


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "version": app.version}


@app.get("/api/samples")
def list_samples() -> dict:
    return {
        "samples": [
            {
                "id": sid,
                "label": s["label"],
                "origin": s["origin"],
                "destination": s["destination"],
                "description": s["description"],
                "tier": s["tier"],
            }
            for sid, s in SAMPLES.items()
        ],
    }


@app.post("/api/panel/run")
def run(req: PanelRunRequest) -> JSONResponse:
    """Trigger a full six-agent panel run.

    Either pass `contract_text` directly or `sample_id` to load from the
    registry. Returns the full PanelResult shape that the v2 frontend expects.
    """
    text = req.contract_text
    if not text and req.sample_id:
        text = load_sample(req.sample_id)
    if not text:
        raise HTTPException(400, "Provide either contract_text or sample_id")

    try:
        result = run_panel(
            contract_text=text,
            situation=req.situation,
            destination_country=req.destination_country,
            origin_country=req.origin_country,
            worker_l1=req.worker_l1,
            run_round2=True,
            run_checklist=True,
        )
    except Exception as exc:
        raise HTTPException(500, f"panel run failed: {exc}") from exc

    return JSONResponse(result)


# Serve the panel-v2 static bundle when it exists (after `npm run build`).
_BUNDLE = _ROOT.parent / "panel-v2" / "dist"
if _BUNDLE.exists():
    app.mount("/", StaticFiles(directory=str(_BUNDLE), html=True), name="static")
else:
    @app.get("/")
    def root_placeholder() -> dict:
        return {
            "message": "Panel API running.",
            "frontend": "Build panel-v2 with `npm run build` to serve it from / .",
            "endpoints": ["/api/health", "/api/samples", "POST /api/panel/run"],
        }
