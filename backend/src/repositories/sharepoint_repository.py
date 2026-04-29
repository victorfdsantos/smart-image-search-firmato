import logging
from typing import Optional
import requests
from config.settings import settings


class SharePointRepository:

    _TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    _GRAPH_BASE = "https://graph.microsoft.com/v1.0"

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._sp = settings.sharepoint
        self._token: Optional[str] = None

    # ---------------- AUTH ----------------

    def _get_token(self) -> str:
        if self._token:
            return self._token

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
        return self._token

    def _headers(self):
        return {"Authorization": f"Bearer {self._get_token()}"}

    def _get(self, url: str):
        r = requests.get(url, headers=self._headers(), timeout=30)
        r.raise_for_status()
        return r.json()

    # ---------------- METADATA ----------------

    def _get_ids(self):
        site = self._get(
            f"{self._GRAPH_BASE}/sites/{self._sp.host}:/{self._sp.site_path}"
        )
        site_id = site["id"]

        drive = self._get(f"{self._GRAPH_BASE}/sites/{site_id}/drives")
        drive_id = drive["value"][0]["id"]

        item = self._get(
            f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
            f"/root:/{self._sp.file_name}"
        )
        item_id = item["id"]

        tables = self._get(
            f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
            f"/items/{item_id}/workbook/tables"
        )
        table = tables["value"][0]["name"]

        return site_id, drive_id, item_id, table

    # ---------------- READ ----------------

    def list_rows(self) -> list[dict]:
        site_id, drive_id, item_id, table = self._get_ids()

        headers = self._get(
            f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
            f"/items/{item_id}/workbook/tables/{table}/headerRowRange"
        )["values"][0]

        rows = []
        url = (
            f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
            f"/items/{item_id}/workbook/tables/{table}/rows"
        )

        while url:
            data = self._get(url)
            for r in data.get("value", []):
                rows.append(r["values"][0])
            url = data.get("@odata.nextLink")

        return [dict(zip(headers, r)) for r in rows]

    # ---------------- UPDATE (UNITÁRIO) ----------------

    def update_row(self, product_id: str, fields: dict) -> None:
        site_id, drive_id, item_id, table = self._get_ids()

        header_data = self._get(
            f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
            f"/items/{item_id}/workbook/tables/{table}/headerRowRange"
        )
        headers = header_data["values"][0]

        id_col_idx = headers.index("Id_produto")

        # busca todas linhas
        rows = self._get(
            f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
            f"/items/{item_id}/workbook/tables/{table}/rows"
        )["value"]

        target_idx = None
        for i, row in enumerate(rows):
            if str(row["values"][0][id_col_idx]) == str(product_id):
                target_idx = i
                break

        if target_idx is None:
            self.logger.warning(f"[SP] ID {product_id} não encontrado")
            return

        row_values = list(rows[target_idx]["values"][0])

        for k, v in fields.items():
            if k in headers:
                row_values[headers.index(k)] = v

        patch_url = (
            f"{self._GRAPH_BASE}/sites/{site_id}/drives/{drive_id}"
            f"/items/{item_id}/workbook/tables/{table}"
            f"/rows/itemAt(index={target_idx})"
        )

        requests.patch(
            patch_url,
            headers={**self._headers(), "Content-Type": "application/json"},
            json={"values": [row_values]},
            timeout=30,
        )