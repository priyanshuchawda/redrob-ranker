from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import candidates, compare, evaluation, exports, ranking, trust_audit


app = FastAPI(title="EvidenceGraph Ranker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "EvidenceGraph Ranker API"}


@app.get("/api/demo-data")
def demo_data() -> dict:
    return ranking.service.get_demo_data()


app.include_router(ranking.router, prefix="/api")
app.include_router(candidates.router, prefix="/api")
app.include_router(compare.router, prefix="/api")
app.include_router(evaluation.router, prefix="/api")
app.include_router(exports.router, prefix="/api")
app.include_router(trust_audit.router, prefix="/api")

