"""
CatalogService — orquestra o pipeline completo de processamento do catálogo.

Fluxo de PRIMEIRO CARREGAMENTO (sem mirror CSV):
  1. Lê planilha via SharePoint API
  2. Para cada produto ativo com imagem na landing:
     a. Processa imagem → output/ e thumbnail/
     b. Cria data/{id}.json
  3. Constrói filters.json (índice de filtros)
  4. Atualiza planilha no SharePoint com caminhos das imagens
  5. Salva mirror CSV (espelho do estado atual)
  6. Dispara retreinamento de embeddings (via EmbeddingService)

Fluxo de RECARREGAMENTO (mirror CSV existente):
  1. Lê planilha via SharePoint API
  2. Compara com mirror CSV → DeltaResult
  3. Aplica mudanças (novas imagens, dados alterados, produtos removidos)
  4. Atualiza filters.json incrementalmente
  5. Atualiza planilha no SharePoint (apenas linhas alteradas)
  6. Salva mirror CSV atualizado
  7. Dispara retreinamento de embeddings apenas para IDs alterados

Garantia de zero-downtime:
  O retreinamento de embeddings usa arquivos de staging que só são trocados
  pelos de produção após o treino completo (swap atômico via os.replace).
  O app_state é atualizado em memória apenas após o swap.
  Enquanto o retreinamento ocorre, a API continua servindo os embeddings
  antigos sem interrupção.
"""

import logging
from pathlib import Path

from config.settings import settings
from services.filter_index_service import FilterIndexService
from services.image_service import ImageService
from services.mirror_service import DeltaResult, MirrorService
from services.product_data_service import ProductDataService
from services.sharepoint_service import SharePointService

_HASH_COLUMNS = [
    "Id_produto", "Nome_Produto", "Marca", "Categoria_Principal", "Subcategoria"
]


def _clean(val) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    return "" if s.lower() in ("nan", "none") else s


def _is_filename(val: str) -> bool:
    """True se o valor parece um nome de arquivo (sem barras)."""
    return bool(val) and "/" not in val and "\\" not in val


class CatalogService:

    def __init__(self, logger: logging.Logger, app_state: dict):
        self.logger = logger
        self.app_state = app_state
        self.sp = SharePointService(logger)
        self.mirror = MirrorService(logger)
        self.image = ImageService(logger)
        self.data = ProductDataService(logger)
        self.filter_index = FilterIndexService(logger)
        self.nas = settings.nas

    # ------------------------------------------------------------------
    # Ponto de entrada
    # ------------------------------------------------------------------

    def process(self) -> dict:
        stats = {
            "total_rows": 0,
            "new_products": 0,
            "images_updated": 0,
            "data_updated": 0,
            "removed": 0,
            "image_errors": 0,
            "retrain_clip_ids": [],
            "retrain_data_ids": [],
            "errors": [],
        }

        # 1. Lê planilha
        rows = self.sp.read_catalog()
        stats["total_rows"] = len(rows)

        # 2. Calcula delta
        delta = self.mirror.compute_delta(rows)

        is_first_load = not bool(self.mirror.load_mirror())

        if is_first_load:
            self.logger.info("[Catalog] PRIMEIRO CARREGAMENTO detectado.")
            self._process_first_load(rows, stats)
        else:
            self.logger.info("[Catalog] RECARREGAMENTO incremental.")
            self._process_delta(delta, stats)

        # 3. Garante que o mirror seja atualizado após processar
        # (rows já contém os caminhos atualizados nas posições certas
        #  porque atualizamos os dicts diretamente)
        self.mirror.save_mirror(rows)

        # 4. Retorna IDs para retreinamento (executado pelo controller)
        stats["retrain_clip_ids"] = delta.image_ids if not is_first_load else [
            _clean(r.get("Id_produto")) for r in rows
            if _clean(r.get("Id_produto")) and _clean(r.get("Status")).lower() == "ativo"
        ]
        stats["retrain_data_ids"] = delta.data_ids if not is_first_load else stats["retrain_clip_ids"]

        return stats

    # ------------------------------------------------------------------
    # Primeiro carregamento
    # ------------------------------------------------------------------

    def _process_first_load(self, rows: list[dict], stats: dict) -> None:
        sharepoint_updates: list[dict] = []

        for row in rows:
            pid = _clean(row.get("Id_produto"))
            if not pid:
                continue

            status = _clean(row.get("Status")).lower()

            # Gera hash / chave especial
            chave = ImageService.generate_hash(row, _HASH_COLUMNS)
            row["Chave_Especial"] = chave

            paths: dict = {}

            # Imagem principal
            img_col = _clean(row.get("Caminho_Imagem"))
            if img_col and _is_filename(img_col):
                source = self.image.find_in_landing(img_col)
                if source:
                    fname = ImageService.primary_filename(pid)
                    ok = self.image.process(source, fname)
                    if ok:
                        paths["caminho_output"]    = str(self.nas.output / fname)
                        paths["caminho_thumbnail"] = str(self.nas.thumbnail / fname)
                        row["Caminho_Imagem"] = paths["caminho_output"]
                        stats["new_products"] += 1
                    else:
                        stats["image_errors"] += 1
                else:
                    self.logger.warning(f"[Catalog] Id {pid}: imagem principal não encontrada na landing.")
                    stats["image_errors"] += 1

            # Cria JSON
            data_dict = self.data.row_to_dict(row)
            data_dict.update(paths)
            self.data.save(pid, data_dict)

            # Atualiza índice de filtros
            self.filter_index.upsert_product(
                int(float(pid)), row, is_active=(status == "ativo")
            )

            # Coleta atualização para o SharePoint
            upd = {"Id_produto": pid, "Chave_Especial": chave}
            if "Caminho_Imagem" in row:
                upd["Caminho_Imagem"] = row["Caminho_Imagem"]
            sharepoint_updates.append(upd)

        # Rebuild completo do índice de filtros (garante consistência)
        self.filter_index.build_from_rows(rows)

        # Atualiza SharePoint
        self.sp.update_image_paths(sharepoint_updates)

    # ------------------------------------------------------------------
    # Recarregamento incremental
    # ------------------------------------------------------------------

    def _process_delta(self, delta: DeltaResult, stats: dict) -> None:
        sharepoint_updates: list[dict] = []

        # — Produtos removidos —
        for pid in delta.removed_ids:
            self.data.mark_removed(pid)
            self.filter_index.remove_product(int(float(pid)))
            stats["removed"] += 1

        all_changed = {
            **delta.new_products,
            **delta.image_changed,
            **delta.data_changed,
        }

        for pid, row in all_changed.items():
            status = _clean(row.get("Status")).lower()
            existing = self.data.load(pid)
            is_new = existing is None
            paths: dict = {}

            chave = ImageService.generate_hash(row, _HASH_COLUMNS)
            row["Chave_Especial"] = chave

            # Processa imagem principal se mudou
            if pid in delta.new_products or pid in delta.image_changed:
                img_col = _clean(row.get("Caminho_Imagem"))
                if img_col and _is_filename(img_col):
                    # Remove imagem antiga se existia
                    if existing:
                        old_fname = ImageService.primary_filename(pid)
                        self.image.delete(old_fname)
                    source = self.image.find_in_landing(img_col)
                    if source:
                        fname = ImageService.primary_filename(pid)
                        ok = self.image.process(source, fname)
                        if ok:
                            paths["caminho_output"]    = str(self.nas.output / fname)
                            paths["caminho_thumbnail"] = str(self.nas.thumbnail / fname)
                            row["Caminho_Imagem"] = paths["caminho_output"]
                            if is_new:
                                stats["new_products"] += 1
                            else:
                                stats["images_updated"] += 1
                        else:
                            stats["image_errors"] += 1
                    else:
                        self.logger.warning(f"[Catalog] Id {pid}: imagem principal não encontrada.")
                        stats["image_errors"] += 1

            # Atualiza JSON
            data_dict = self.data.row_to_dict(row)
            merged = self.data.merge_paths(existing, paths) if paths else (existing or {})
            merged.update(data_dict)
            self.data.save(pid, merged)

            # Atualiza índice de filtros
            self.filter_index.upsert_product(
                int(float(pid)), row, is_active=(status == "ativo")
            )

            stats["data_updated"] += 1

            # Coleta para SharePoint
            upd = {"Id_produto": pid, "Chave_Especial": chave}
            if "Caminho_Imagem" in row:
                upd["Caminho_Imagem"] = row.get("Caminho_Imagem", "")
            sharepoint_updates.append(upd)

        self.sp.update_image_paths(sharepoint_updates)