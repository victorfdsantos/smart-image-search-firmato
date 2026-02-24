from abc import ABC, abstractmethod


class BaseStorage(ABC):
    """
    Interface base para qualquer tipo de armazenamento.

    Implementações:
    - NASStorage
    - GCSStorage
    - S3Storage (futuro)
    """

    @abstractmethod
    def save(self, local_file: str, relative_path: str) -> str:
        """
        Salva arquivo no destino final.

        Parameters
        ----------
        local_file : str
            Caminho do arquivo local já processado.

        relative_path : str
            Caminho relativo padronizado (images_zone/...).

        Returns
        -------
        str
            Caminho final salvo.
        """
        pass