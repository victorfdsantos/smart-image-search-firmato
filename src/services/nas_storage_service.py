from pathlib import Path
import shutil


class NASStorageService:

    def __init__(self, root: Path):
        self.root = root

    def save(self, source: Path, relative_path: Path):

        destination = self.root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source, destination)

        return destination