import time
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse

from models.catalog_models import ProcessCatalogResponse
from services.catalog_service import CatalogService
from services.startup_service import StartupService
from utils.logger import setup_logger

_TEMP_UPLOAD_DIR = Path("./tmp_uploads")
_TEMP_UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter(prefix="/catalog", tags=["Catalog"])

ENDPOINT_NAME = "catalog_register"


@router.post(
    "/register",
    response_model=ProcessCatalogResponse,
    summary="Processa catálogo do SharePoint e retreina embeddings",
    description="""
        Fluxo completo de sincronização do catálogo:
        
        1. Lê planilha do SharePoint via Microsoft Graph API  
        2. Compara com o mirror CSV para detectar mudanças  
        3. Processa imagens novas/alteradas → output/ e thumbnail/  
        4. Atualiza data/{id}.json para cada produto modificado  
        5. Reconstrói/atualiza o índice de filtros (filters.json)  
        6. Atualiza a planilha no SharePoint com os caminhos das imagens  
        7. Salva o mirror CSV com o estado atual  
        8. Retreina embeddings CLIP + ST + BM25 de forma atômica (zero-downtime):  
        - Os novos embeddings são escritos em staging  
        - Só após o treino completo os arquivos são trocados atomicamente  
        - O app_state é atualizado em memória após o swap  
        - Enquanto retreina, a API continua servindo os embeddings antigos  
        """,
)
async def register_catalog(request: Request) -> JSONResponse:
    logger = setup_logger("catalog_process")
    t0 = time.time()
 
    # 1. Processamento do catálogo (imagens, JSONs, filtros, SharePoint, mirror)
    try:
        svc = CatalogService(logger, request.app.state.__dict__)
        stats = svc.process()
    except Exception as exc:
        logger.error(f"[Catalog] Falha crítica no processamento: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
 
    elapsed = round(time.time() - t0, 2)
    logger.info(f"[Catalog] Processo total: {elapsed}s")
 
    return JSONResponse(content={
        "status":          "success" if not stats.get("errors") else "partial",
        "elapsed_seconds": elapsed,
        **stats
    })


@router.post(
    "/retrain",
    summary="Reexecuta o StartupService (rebuild thumbnails + reload embeddings + CLIP)",
)
async def retrain(request: Request) -> JSONResponse:
    logger = setup_logger("retrain")
    logger.info("Retreinamento solicitado — reexecutando StartupService.")
    try:
        startup = StartupService(logger)
        startup.run(request.app.state.__dict__)
        logger.info("StartupService concluído com sucesso.")
        return JSONResponse(content={"status": "success"}, status_code=200)
    except Exception as exc:
        logger.error(f"Erro no retreinamento: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get(
    "/latest-log",
    summary="Download do log mais recente do catalog_register",
)
async def latest_log() -> FileResponse:
    from config.settings import settings

    logs_dir = settings.general.logs_path
    logs = sorted(
        logs_dir.glob("catalog_register_*.log"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not logs:
        raise HTTPException(status_code=404, detail="Nenhum log encontrado.")

    latest = logs[0]
    return FileResponse(
        path=latest,
        media_type="text/plain",
        filename=latest.name,
        headers={"Content-Disposition": f"attachment; filename={latest.name}"},
    )

@router.get(
    "/status",
    summary="Estado atual dos embeddings em memória",
)
async def status(request: Request) -> JSONResponse:
    state = request.app.state.__dict__
 
    clip_emb = state.get("clip_embeddings")
    text_emb = state.get("text_embeddings")
    metadata = state.get("embeddings_metadata")
 
    return JSONResponse(content={
        "clip_embeddings_shape": list(clip_emb.shape) if clip_emb is not None else None,
        "text_embeddings_shape": list(text_emb.shape) if text_emb is not None else None,
        "metadata_count":        len(metadata) if metadata else 0,
        "bm25_available":        state.get("bm25") is not None,
        "clip_model_loaded":     state.get("clip_model") is not None,
        "st_model_loaded":       state.get("st_model") is not None,
    })