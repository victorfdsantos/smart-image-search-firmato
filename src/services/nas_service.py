import logging
import shutil
from pathlib import Path
from typing import Optional
from config.settings import settings


class NasService:
    """
    Serviço responsável por operações no NAS.
    Atualmente usa sistema de arquivos local (caminho configurável em config.ini).
    No futuro pode ser adaptado para protocolos SMB/NFS/SFTP.
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.base_path = settings.nas.base_path
        self.organizer_columns = settings.nas.organizer_columns

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------

    def build_product_path(self, data_row: dict, product_id: int) -> Path:
        """
        Monta o caminho de destino no NAS.
        Estrutura: {base}/{col1}/{col2}/.../{ID}/
        """
        parts = [
            self._sanitize(str(data_row.get(col, "desconhecido")))
            for col in self.organizer_columns
        ]
        return self.base_path.joinpath(*parts, str(product_id))

    def _sanitize(self, value: str) -> str:
        """Sanitiza nome de pasta: remove/substitui caracteres inválidos."""
        invalid = r'\/:*?"<>|'
        for ch in invalid:
            value = value.replace(ch, "_")
        return value.strip().strip(".")[:100]  # limite de 100 chars

    # ------------------------------------------------------------------
    # Operações de arquivo
    # ------------------------------------------------------------------

    def save_image(self, source_path: Path, dest_folder: Path, filename: str) -> Optional[Path]:
        """
        Copia imagem para o NAS.
        Retorna o caminho final no NAS ou None em caso de erro.
        """
        try:
            dest_folder.mkdir(parents=True, exist_ok=True)
            dest_path = dest_folder / filename
            shutil.copy2(source_path, dest_path)
            self.logger.info(f"[NAS] Imagem salva: {dest_path}")
            return dest_path
        except Exception as exc:
            self.logger.error(
                f"[NAS] Erro ao salvar '{filename}' em '{dest_folder}': {exc}",
                exc_info=True,
            )
            return None

    def get_image(self, nas_path: str) -> Optional[Path]:
        """
        Retorna o Path de uma imagem no NAS se existir.
        Preparado para futura expansão (ex: download via protocolo).
        """
        try:
            path = Path(nas_path)
            if path.exists():
                self.logger.debug(f"[NAS] Imagem encontrada: {path}")
                return path
            self.logger.warning(f"[NAS] Imagem não encontrada: {path}")
            return None
        except Exception as exc:
            self.logger.error(f"[NAS] Erro ao buscar '{nas_path}': {exc}", exc_info=True)
            return None

    def delete_image(self, nas_path: str) -> bool:
        """Remove imagem do NAS. Retorna True em sucesso."""
        try:
            path = Path(nas_path)
            if path.exists():
                path.unlink()
                self.logger.info(f"[NAS] Imagem removida: {path}")
                return True
            self.logger.warning(f"[NAS] Imagem não encontrada para remoção: {path}")
            return False
        except Exception as exc:
            self.logger.error(
                f"[NAS] Erro ao remover '{nas_path}': {exc}", exc_info=True
            )
            return False