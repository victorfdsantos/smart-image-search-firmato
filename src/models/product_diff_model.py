"""
Dataclasses que representam o resultado de uma comparação Excel vs JSON.
São o contrato de dados entre DiffService e CatalogService —
nenhum dos dois precisa conhecer os detalhes internos do outro.

ProductDiff         → estado completo de um produto após o diff
"""

from dataclasses import dataclass, field
from models.secondary_image_diff_model import SecondaryImageDiff
from typing import Optional


@dataclass
class ProductDiff:
    """
    Resultado completo da comparação Excel vs JSON para um produto.
    Preenchido pelo DiffService e consumido pelo CatalogService.

    Dados brutos da linha do Excel (row_dict) NÃO fazem parte do diff —
    são responsabilidade do CatalogService que já os possui.
    """
    product_id: int

    # --- Estado geral ---
    is_new_product: bool = False

    # --- Imagem principal ---
    primary_excel_value: Optional[str] = None
    primary_json_nas_path: Optional[str] = None
    primary_json_bucket_uri: Optional[str] = None
    primary_is_new: bool = False
    primary_is_changed: bool = False

    # --- Imagens secundárias ---
    secondaries: list[SecondaryImageDiff] = field(default_factory=list)

    # --- Colunas organizadoras do NAS ---
    nas_path_changed: bool = False

    # --- Campos de dados (non-image) ---
    data_fields_changed: bool = False
    changed_data_fields: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Helpers de consulta
    # ------------------------------------------------------------------

    @property
    def has_any_change(self) -> bool:
        return (
            self.is_new_product
            or self.primary_is_new
            or self.primary_is_changed
            or self.nas_path_changed
            or self.data_fields_changed
            or any(s.is_new or s.is_changed or s.is_deleted for s in self.secondaries)
        )

    @property
    def secondary_changes(self) -> list[SecondaryImageDiff]:
        return [s for s in self.secondaries if s.is_new or s.is_changed]

    @property
    def secondary_deletions(self) -> list[SecondaryImageDiff]:
        return [s for s in self.secondaries if s.is_deleted]