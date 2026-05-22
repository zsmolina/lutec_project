from abc import ABC, abstractmethod

from openai import OpenAI

from app.config import Settings
from app.domain.enums import InvoiceFormat
from app.domain.models.invoice import FacturaEnergiaData
from app.services.excel_exporter import ColumnConfig


class InvoiceExtractor(ABC):
    format: InvoiceFormat

    @abstractmethod
    def crop_pdf_regions(self, pdf_bytes: bytes) -> list[str]: ...

    @abstractmethod
    def system_prompt(self) -> str: ...

    @property
    @abstractmethod
    def excel_column_config(self) -> list[ColumnConfig]: ...

    def extract(self, pdf_bytes: bytes, client: OpenAI, settings: Settings) -> FacturaEnergiaData:
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
            response_format=FacturaEnergiaData,
            temperature=settings.openai_temperature,
        )
        return completion.choices[0].message.parsed
