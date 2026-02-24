import shutil
from pathlib import Path
from infrastructure.storage.base_storage import BaseStorage


class NASStorage(BaseStorage):
    """
    Storage para filesystem/NAS interno.
    """

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)

    def save(self, local_file: str, relative_path: str) -> str:

        destination = self.root_path / relative_path

        destination.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(local_file, destination)

        return str(destination)