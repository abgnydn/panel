"""Panel FastAPI server.

Mounted under a Databricks App. Same source code runs locally when launched
as `uvicorn app.api.server:app` from the panel/ repo root, OR inside a
Databricks App where the bundled app/ directory is itself the working dir.

The sys.path shim below makes sibling-package imports
(`from agents import ...`) work in both contexts.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make `from agents import ...` work in both deployment contexts.
_HERE = Path(__file__).resolve().parent    # .../app/api/
_APP_ROOT = _HERE.parent                    # .../app/
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agents import run_panel
try:
    from samples import SAMPLES, load as load_sample
except ImportError as _samples_err:
    print(f"[panel] samples import failed: {_samples_err}")
    SAMPLES = {}
    def load_sample(_id: str) -> str:
        return ""

try:
    import genie_client
    _GENIE_OK = True
except Exception as _e:  # pragma: no cover
    genie_client = None  # type: ignore
    _GENIE_OK = False

app = FastAPI(
    title="Panel API",
    description="Six-agent migrant-worker rights advisor.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173",
                   "https://panel-v2-nvg.pages.dev",
                   "https://panel-v2.pages.dev"],
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
            for sid, s in (SAMPLES or {}).items()
        ],
    }


class GenieQuery(BaseModel):
    question: str
    conversation_id: str | None = None


@app.post("/api/genie/query")
def genie_query(req: GenieQuery) -> JSONResponse:
    """Multi-turn Genie chat.

    If `conversation_id` is provided, continues that conversation (Genie keeps
    earlier turns as context). Otherwise starts a fresh one.

    Returns the NL answer + the SQL Genie generated + result rows +
    3 AI-suggested follow-up questions.
    """
    if not _GENIE_OK or not genie_client:
        raise HTTPException(503, "Genie client not available.")
    try:
        return JSONResponse(genie_client.ask(req.question, req.conversation_id))
    except Exception as exc:
        raise HTTPException(500, f"genie query failed: {exc}") from exc


@app.get("/api/genie/seed-questions")
def genie_seed() -> dict[str, list[str]]:
    """The starter questions that appear before any conversation has begun."""
    return {
        "questions": [
            "How many cases in the archive ended with the worker returning early?",
            "List the labor-code rules for passport retention across SA, MY, SG, HK, AE.",
            "Which ILO conventions has Saudi Arabia ratified?",
            "Count abuse-pattern outcomes grouped by clause topic and destination.",
            "Show 24-hour embassy hotlines for the Philippines and Indonesia corridors.",
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


# Serve the bundled panel-v2 static site from /
_STATIC = _APP_ROOT / "static"
_DEV_STATIC = _APP_ROOT.parent.parent / "panel-v2" / "dist"
_BUNDLE = _STATIC if _STATIC.exists() else _DEV_STATIC

if _BUNDLE.exists():
    app.mount("/", StaticFiles(directory=str(_BUNDLE), html=True), name="static")
else:
    @app.get("/")
    def root_placeholder() -> dict:
        return {
            "message": "Panel API running.",
            "frontend": "Run scripts/build_and_deploy.sh to bundle panel-v2 into app/static/",
            "endpoints": ["/api/health", "/api/samples", "POST /api/panel/run"],
        }
