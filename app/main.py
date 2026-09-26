from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import upload, analyze, provenance, result

app = FastAPI(title="VeriTrace API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, tags=["upload"])
app.include_router(analyze.router, tags=["analyze"])
app.include_router(provenance.router, tags=["provenance"])
app.include_router(result.router, tags=["result"])


@app.get("/")
async def root():
    return {"status": "VeriTrace backend running"}