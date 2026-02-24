from pathlib import Path
from google.cloud import storage

from infrastructure.storage.base_storage import BaseStorage


class GCSStorage(BaseStorage):
    """
    Storage para Google Cloud Storage.
    """

    def __init__(self, bucket_name: str):
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def save(self, local_file: str, relative_path: str) -> str:
        """
        Faz upload do arquivo para o GCS mantendo o mesmo path.
        """

        local_file = Path(local_file)

        blob = self.bucket.blob(relative_path)

        blob.upload_from_filename(str(local_file))

        return f"gs://{self.bucket.name}/{relative_path}"