from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import upload, analyze, provenance, result
from app.db import init_db

app = FastAPI(title="ASTITVA API", version="0.1.0")

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


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
async def root():
    return {"status": "VeriTrace backend running"}

from app.services import blockchain_service

@app.get("/health")
async def health():
    return {
        "backend": "ok",
        "chain_up": blockchain_service.is_chain_up(),
        "contract_deployed": blockchain_service.contract_deployed(),
    }