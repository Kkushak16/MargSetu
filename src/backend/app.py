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
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

frontend_public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public"))
if os.path.exists(frontend_public_dir):
    app.mount("/static", StaticFiles(directory=frontend_public_dir), name="static")

@app.get("/dashboard")
@app.get("/")
def root_dashboard():
    index_path = os.path.join(frontend_public_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(
            index_path,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return {
        "platform": "MargSetu",
        "problem_id": "SIH26002",
        "organization": "Ministry of Development of North Eastern Region (MDoNER)",
        "status": "online",
        "endpoints": {
            "routing": "/route-safe",
            "sync_up": "/api/v1/sync/up",
            "sync_down": "/api/v1/sync/down",
            "ml_predict": "/ml/predict",
            "health": "/health"
        }
    }


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
