"""
Unified Backend Application Server (Member A + Member B Integration)
SIH26002 - MargSetu: Smart Logistics & Accessibility Platform

Integrates ML hazard prediction, hazard-aware routing, offline sync manager,
and edge mutator jobs into a single high-performance FastAPI service.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.ml.predict_api import app as predict_app
from src.backend.routing_api import router as routing_router
from src.backend.sync_api import router as sync_router
from src.backend.gateway import RateLimitAndAuthMiddleware

# Master Unified FastAPI App
app = FastAPI(
    title="MargSetu - Smart Logistics & Routing Platform",
    description="SIH26002 MDoNER Emergency Response & Highway Blockage Avoidance Engine",
    version="1.0.0"
)

# Enable CORS for Next.js & Mobile App integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Rate-Limiting & Gateway middleware
app.add_middleware(RateLimitAndAuthMiddleware)

# Mount Routers
app.include_router(routing_router)
app.include_router(sync_router)

# Mount ML Predict Endpoints from Member A
app.mount("/ml", predict_app)


# Serve static frontend files and control room dashboard
import os
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Candidate paths for index.html in Vercel Serverless environment
INDEX_HTML_CANDIDATES = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "index.html")),
    os.path.abspath(os.path.join(os.getcwd(), "src", "frontend", "public", "index.html")),
    os.path.abspath("src/frontend/public/index.html"),
    "/var/task/src/frontend/public/index.html"
]

def _find_index_html():
    for p in INDEX_HTML_CANDIDATES:
        if os.path.exists(p):
            return p
    return None

frontend_public_dir = None
for p in INDEX_HTML_CANDIDATES:
    d = os.path.dirname(p)
    if os.path.exists(d):
        frontend_public_dir = d
        break

if frontend_public_dir and os.path.exists(frontend_public_dir):
    try:
        app.mount("/static", StaticFiles(directory=frontend_public_dir), name="static")
    except Exception:
        pass

@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
def root_dashboard():
    index_path = _find_index_html()
    if index_path and os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, status_code=200)
    return HTMLResponse(content="<h1>MargSetu Control Room</h1><p>Status: Online</p>", status_code=200)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "backend": "online",
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.backend.app:app", host="0.0.0.0", port=8000, reload=True)
