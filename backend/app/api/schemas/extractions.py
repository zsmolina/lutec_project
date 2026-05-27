from pydantic import BaseModel, Field


class InvoiceOutcomeResponse(BaseModel):
    filename: str
    success: bool
    nic: str | None = None
    error: str | None = None
    format_detected: str | None = None
    format_label: str | None = None


class BatchJobCreatedResponse(BaseModel):
    job_id: str
    status: str
    retailer: str
    retailer_label: str
    format: str
    format_label: str
    total: int = 0


class BatchJobStatusResponse(BaseModel):
    job_id: str
    status: str
    retailer: str
    retailer_label: str
    format: str
    format_label: str
    total: int = 0
    processed: int = 0
    succeeded: int = 0
    failed: int = 0
    current_file: str | None = None
    error: str | None = None
    outcomes: list[InvoiceOutcomeResponse] = Field(default_factory=list)
    download_ready: bool = False
