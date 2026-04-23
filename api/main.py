"""FastAPI entrypoint. Exposes /query, /ingest, /documents."""

from pathlib import Path
from fastapi import FastAPI, HTTPException

from api.schemas import QueryRequest
from core.config import Config
from core.storage import Storage
from core.l1_engine import L1Engine
from core.multi_l_engine import MultiLEngine
from core.indexer import Indexer


def create_app(project_root: Path | None = None) -> FastAPI:
    cfg = Config(project_root=project_root) if project_root else Config()
    storage = Storage(data_dir=cfg.data_dir, documents_dir=cfg.documents_dir)

    app = FastAPI(title="NoRag", version="3.0")

    @app.post("/query")
    async def query(req: QueryRequest):
        mode = req.mode or cfg.default_mode
        if mode == "L1":
            engine = L1Engine(config=cfg, storage=storage)
            result = await engine.run(
                question=req.question,
                agent_forced=req.agent_hint,
                index_scope=req.index_scope,
            )
            return result.model_dump()
        elif mode == "MultiL":
            engine = MultiLEngine(config=cfg, storage=storage)
            result = await engine.run(
                question=req.question,
                preset=req.preset,
                max_layers=req.max_layers,
            )
            return result.model_dump()
        raise HTTPException(status_code=400, detail=f"Unknown mode: {mode}")

    @app.post("/ingest")
    async def ingest(doc_id: str, raw_text: str):
        indexer = Indexer(config=cfg, storage=storage)
        return await indexer.ingest(doc_id=doc_id, raw_text=raw_text)

    @app.get("/documents")
    def list_documents():
        docs = [p.stem for p in cfg.documents_dir.glob("*.md")
                if p.stem != ".gitkeep"]
        return {"documents": docs}

    return app


app = create_app()
