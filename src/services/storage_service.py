import logging
from pathlib import Path
from typing import Optional
from config.settings import settings


class StorageService:
    """
    Serviço responsável por operações no Google Cloud Storage (GCS).
    Requer a lib google-cloud-storage instalada e credenciais configuradas.
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.bucket_name = settings.gcs.bucket_name
        self.credentials_path = settings.gcs.credentials_path
        self.bucket_prefix = settings.gcs.bucket_prefix
        self.organizer_columns = settings.gcs.organizer_columns
        self._client = None
        self._bucket = None

    # ------------------------------------------------------------------
    # Conexão (lazy init)
    # ------------------------------------------------------------------

    def _get_client(self):
        """Inicializa o cliente GCS na primeira chamada (lazy)."""
        if self._client is not None:
            return self._client

        try:
            from google.cloud import storage as gcs
            from google.oauth2 import service_account

            if self.credentials_path.exists():
                credentials = service_account.Credentials.from_service_account_file(
                    str(self.credentials_path)
                )
                self._client = gcs.Client(credentials=credentials)
            else:
                # Tenta usar credenciais default do ambiente (GOOGLE_APPLICATION_CREDENTIALS)
                self._client = gcs.Client()

            self._bucket = self._client.bucket(self.bucket_name)
            self.logger.info(
                f"[GCS] Cliente inicializado. Bucket: {self.bucket_name}"
            )
            return self._client

        except ImportError:
            self.logger.error(
                "[GCS] Biblioteca 'google-cloud-storage' não instalada. "
                "Execute: pip install google-cloud-storage"
            )
            raise
        except Exception as exc:
            self.logger.error(
                f"[GCS] Falha ao inicializar cliente: {exc}", exc_info=True
            )
            raise

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------

    def build_blob_path(self, data_row: dict, product_id: int, filename: str) -> str:
        """
        Monta o caminho (blob name) dentro do bucket.
        Estrutura: {prefix}/{col1}/{col2}/.../{ID}/{filename}
        """
        parts = [
            self._sanitize(str(data_row.get(col, "desconhecido")))
            for col in self.organizer_columns
        ]
        path_parts = [self.bucket_prefix] + parts + [str(product_id), filename]
        return "/".join(p for p in path_parts if p)

    def _sanitize(self, value: str) -> str:
        """Remove caracteres problemáticos para paths de bucket GCS."""
        for ch in ["#", "[", "]", "?", "*"]:
            value = value.replace(ch, "_")
        return value.strip()[:100]

    # ------------------------------------------------------------------
    # Operações de arquivo
    # ------------------------------------------------------------------

    def upload_image(
        self, local_path: Path, blob_name: str
    ) -> Optional[str]:
        """
        Faz upload de imagem para o GCS.
        Retorna a URI gs:// em caso de sucesso, None em caso de erro.
        """
        try:
            client = self._get_client()
            blob = self._bucket.blob(blob_name)
            blob.upload_from_filename(str(local_path), content_type="image/jpeg")
            uri = f"gs://{self.bucket_name}/{blob_name}"
            self.logger.info(f"[GCS] Upload concluído: {uri}")
            return uri
        except Exception as exc:
            self.logger.error(
                f"[GCS] Erro no upload de '{local_path}' para '{blob_name}': {exc}",
                exc_info=True,
            )
            return None

    def get_image_url(self, blob_name: str) -> Optional[str]:
        """
        Retorna a URL pública (ou URI gs://) de uma imagem no bucket.
        Preparado para futura expansão (ex: signed URLs).
        """
        try:
            return f"gs://{self.bucket_name}/{blob_name}"
        except Exception as exc:
            self.logger.error(
                f"[GCS] Erro ao montar URL para '{blob_name}': {exc}", exc_info=True
            )
            return None

    def delete_image(self, blob_name: str) -> bool:
        """Remove imagem do bucket. Retorna True em sucesso."""
        try:
            client = self._get_client()
            blob = self._bucket.blob(blob_name)
            blob.delete()
            self.logger.info(f"[GCS] Blob removido: {blob_name}")
            return True
        except Exception as exc:
            self.logger.error(
                f"[GCS] Erro ao remover blob '{blob_name}': {exc}", exc_info=True
            )
            return False
