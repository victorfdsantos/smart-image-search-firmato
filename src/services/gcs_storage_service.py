from google.cloud import storage
from pathlib import Path


class GCSStorageService:

    def __init__(self, bucket_name: str | None = None):

        self.bucket_name = bucket_name
        self._client = None
        self._bucket = None

    def save(self, source: Path, relative_path: Path):

        if not self.bucket_name:
            return None

        if not self._client:
            self._client = storage.Client()
            self._bucket = self._client.bucket(self.bucket_name)

        blob = self._bucket.blob(str(relative_path))
        blob.upload_from_filename(str(source))

        return f"gs://{self.bucket_name}/{relative_path}"