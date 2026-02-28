"""
Catalog Processor API
---------------------
Endpoint FastAPI para processamento de catálogo de produtos.
Consumido futuramente pelo Streamlit via requisição HTTP.

Execução:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import shutil
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from controllers.catalog_controller import CatalogController

app = FastAPI(
    title="Catalog Processor API",
    description="API para processamento e cadastro de catálogo de produtos Firmato Móveis.",
    version="1.0.0",
)

_TEMP_UPLOAD_DIR = Path("./tmp_uploads")
_TEMP_UPLOAD_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------

@app.post(
    "/catalog/register",
    summary="Cadastrar produtos a partir de planilha",
    description=(
        "Recebe um arquivo .xlsx com o catálogo de produtos, executa o fluxo de "
        "processamento de imagens (redimensionamento, conversão, hash, NAS e GCS) e "
        "atualiza os dados da planilha. Retorna estatísticas da execução."
    ),
    response_description="Estatísticas do processamento",
    tags=["Catalog"],
)
async def register_catalog(file: UploadFile = File(...)) -> JSONResponse:
    """
    Fluxo:
    1. Recebe a planilha .xlsx
    2. Salva temporariamente em disco
    3. Aciona o CatalogController
    4. Retorna o resultado
    """
    if not file.filename.endswith((".xlsx", ".xlsm")):
        raise HTTPException(
            status_code=400,
            detail=f"Formato inválido: '{file.filename}'. Apenas .xlsx ou .xlsm são aceitos.",
        )

    temp_path = _TEMP_UPLOAD_DIR / file.filename
    try:
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        controller = CatalogController()
        result = controller.register_from_spreadsheet(str(temp_path))

        if result.get("status") == "error":
            raise HTTPException(status_code=422, detail=result.get("message"))

        return JSONResponse(content=result, status_code=200)

    finally:
        # Limpa o upload temporário
        if temp_path.exists():
            temp_path.unlink()


@app.get("/health", tags=["System"], summary="Health check")
async def health_check():
    return {"status": "ok", "service": "catalog-processor"}


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
