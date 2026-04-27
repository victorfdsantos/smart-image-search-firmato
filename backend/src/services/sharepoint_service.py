"""
SharePointService — leitura e escrita da planilha de catálogo via Microsoft Graph API.

Fluxo de autenticação: Client Credentials (app-only).
Requer a variável de ambiente SHAREPOINT_CLIENT_SECRET.
"""

import logging
from typing import Optional
import requests
from config.settings import settings

class SharePointService:

    _TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    _GRAPH_BASE = "https://graph.microsoft.com/v1.0"

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._sp = settings.sharepoint
        self._token: Optional[str] = None

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def _get_token(self) -> str:
        if self._token:
            return self._token

        if not self._sp.client_secret:
            raise RuntimeError(
                "SHAREPOINT_CLIENT_SECRET não definida. "
                "Exporte a variável de ambiente antes de iniciar o serviço."
            )

        url = self._TOKEN_URL.format(tenant=self._sp.tenant_id)
        resp = requests.post(
            url,
            data={
                "grant_type": "client_credentials",
                "client_id": self._sp.client_id,
                "client_secret": self._sp.client_secret,
                "scope": "https://graph.microsoft.com/.default",
            },
            timeout=30,
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        self.logger.info("[SharePoint] Token obtido com sucesso.")
        return self._token

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._get_token()}"}

    def _get(self, url: str, **kwargs) -> dict:
        r = requests.get(url, headers=self._headers(), timeout=30, **kwargs)
        r.raise_for_status()
        return r.json()

    # ------------------------------------------------------------------
    # IDs do site / drive / item
    # ------------------------------------------------------------------

    def _site_id(self) -> str:
        data = self._get(
            f"{self._GRAPH_BASE}/sites/{self._sp.host}:/{self._sp.site_path}"
        )
        return data["id"]

    def _drive_id(self, site_id: str) -> str:
        data = self._get(f"{self._GRAPH_BASE}/sites/{site_id}/drives")
        return data["value"][0]["id"]

    def _item_id(self, site_id: str, drive_id: str) -> str:
        data = self._get(
            f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
            f"/root:/{self._sp.file_name}"
        )
        return data["id"]

    def _table_name(self, site_id: str, drive_id: str, item_id: str) -> str:
        data = self._get(
            f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
            f"/items/{item_id}/workbook/tables"
        )
        return data["value"][0]["name"]

    # ------------------------------------------------------------------
    # Leitura — retorna lista de dicts (linha = dict col→valor)
    # ------------------------------------------------------------------

    def read_catalog(self) -> list[dict]:
        """
        Lê todas as linhas da tabela Excel do SharePoint.
        Retorna uma lista de dicts onde cada chave é o cabeçalho da coluna.
        """
        self.logger.info("[SharePoint] Lendo catálogo...")
        site_id  = self._site_id()
        drive_id = self._drive_id(site_id)
        item_id  = self._item_id(site_id, drive_id)
        table    = self._table_name(site_id, drive_id, item_id)

        # Cabeçalhos
        header_data = self._get(
            f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
            f"/items/{item_id}/workbook/tables/{table}/headerRowRange"
        )
        headers: list[str] = header_data["values"][0]

        # Linhas (paginadas)
        rows: list[list] = []
        url = (
            f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
            f"/items/{item_id}/workbook/tables/{table}/rows"
        )
        while url:
            data = self._get(url)
            for row in data.get("value", []):
                rows.append(row["values"][0])
            url = data.get("@odata.nextLink")

        records = [dict(zip(headers, row)) for row in rows]
        self.logger.info(f"[SharePoint] {len(records)} linhas lidas.")
        return records

    # ------------------------------------------------------------------
    # Escrita — atualiza células específicas por ID de produto
    # ------------------------------------------------------------------

    def update_image_paths(self, updates: list[dict],) -> None:
        """
        Atualiza as colunas de caminho de imagem na planilha do SharePoint.
        `updates` é uma lista de dicts com Id_produto e os campos a atualizar.
        """
        if not updates:
            return

        self.logger.info(f"[SharePoint] Atualizando {len(updates)} linhas...")
        site_id  = self._site_id()
        drive_id = self._drive_id(site_id)
        item_id  = self._item_id(site_id, drive_id)
        table    = self._table_name(site_id, drive_id, item_id)

        # Busca índice das colunas de caminho
        header_data = self._get(
            f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
            f"/items/{item_id}/workbook/tables/{table}/headerRowRange"
        )
        headers: list[str] = header_data["values"][0]

        path_cols = {
            "Caminho_Imagem", "Chave_Especial"
        }

        col_index = {h: i for i, h in enumerate(headers) if h in path_cols}
        id_col_idx = headers.index("Id_produto") if "Id_produto" in headers else None

        if id_col_idx is None:
            self.logger.error("[SharePoint] Coluna Id_produto não encontrada.")
            return

        # Lê todas as linhas para encontrar os índices das linhas a atualizar
        rows_url = (
            f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
            f"/items/{item_id}/workbook/tables/{table}/rows"
        )
        all_rows = []
        url = rows_url
        while url:
            data = self._get(url)
            all_rows.extend(data.get("value", []))
            url = data.get("@odata.nextLink")

        # Monta mapa id_produto → índice da linha (0-based)
        id_to_row: dict[str, int] = {}
        for i, row in enumerate(all_rows):
            pid = str(row["values"][0][id_col_idx]).strip()
            id_to_row[pid] = i

        # Aplica os updates linha a linha
        session_url = (
            f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
            f"/items/{item_id}/workbook/createSession"
        )
        sess_resp = requests.post(
            session_url,
            headers={**self._headers(), "Content-Type": "application/json"},
            json={"persistChanges": True},
            timeout=30,
        )
        sess_resp.raise_for_status()
        session_id = sess_resp.json()["id"]
        sess_headers = {**self._headers(), "workbook-session-id": session_id}

        for upd in updates:
            pid = str(upd.get("Id_produto", "")).strip()
            if pid not in id_to_row:
                self.logger.warning(f"[SharePoint] Id {pid} não encontrado na planilha.")
                continue
            row_idx = id_to_row[pid]
            row_vals = list(all_rows[row_idx]["values"][0])

            for col_name, col_idx in col_index.items():
                if col_name in upd:
                    row_vals[col_idx] = upd[col_name]

            patch_url = (
                f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
                f"/items/{item_id}/workbook/tables/{table}"
                f"/rows/itemAt(index={row_idx})"
            )
            r = requests.patch(
                patch_url,
                headers={**sess_headers, "Content-Type": "application/json"},
                json={"values": [row_vals]},
                timeout=30,
            )
            if r.status_code not in (200, 204):
                self.logger.warning(
                    f"[SharePoint] Falha ao atualizar linha {row_idx} (Id={pid}): {r.text}"
                )

        # Fecha sessão
        requests.post(
            f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
            f"/items/{item_id}/workbook/closeSession",
            headers={**self._headers(), "workbook-session-id": session_id},
            timeout=30,
        )
        self.logger.info("[SharePoint] Atualização concluída.")