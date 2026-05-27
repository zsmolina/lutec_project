"""Base común para extractores Afinia (esquema y extracción IA)."""

from openai import OpenAI
from pydantic import BaseModel

from app.config import Settings
from app.domain.enums import InvoiceFormat
from app.domain.models.invoice import FacturaEnergiaData
from app.services.excel_exporter import ColumnConfig
from app.services.extraction.base import InvoiceExtractor


class AfiniaInvoiceExtractor(InvoiceExtractor):
    """Usa esquema Pydantic Afinia (anclajes visuales) y normaliza a FacturaEnergiaData."""

    _response_model: type[BaseModel]

    @property
    def response_model(self) -> type[BaseModel]:
        return self._response_model

    def extract(
        self,
        pdf_bytes: bytes,
        client: OpenAI,
        settings: Settings,
    ) -> FacturaEnergiaData:
        crops = self.crop_pdf_regions(pdf_bytes)
        payload: list[dict] = [{"type": "text", "text": self.system_prompt()}]
        for img_b64 in crops:
            payload.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"},
                }
            )

        completion = client.beta.chat.completions.parse(
            model=settings.openai_model,
            messages=[{"role": "user", "content": payload}],
            response_format=self.response_model,
            temperature=settings.openai_temperature,
        )
        parsed = completion.choices[0].message.parsed
        raw = parsed.model_dump()
        if raw.get("tipo_consumo_calculado") is None:
            raw["tipo_consumo_calculado"] = ""
        if raw.get("propiedad_activo") is None:
            raw["propiedad_activo"] = ""
        return FacturaEnergiaData.model_validate(raw)
