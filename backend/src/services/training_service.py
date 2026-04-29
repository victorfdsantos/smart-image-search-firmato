import requests


class TrainingService:

    def __init__(self, logger):
        self.logger = logger

    def train(self, image_ids: list[str], data_ids: list[str]) -> bool:
        try:
            resp = requests.post(
                "http://ai:9000/training",
                json={
                    "image_ids": image_ids,
                    "data_ids": data_ids,
                },
                timeout=600,
            )

            if resp.status_code == 200:
                self.logger.info("[Training] OK")
                return True

            self.logger.warning(f"[Training] Falhou: {resp.text}")
            return False

        except Exception as e:
            self.logger.error(f"[Training] Erro: {e}", exc_info=True)
            return False