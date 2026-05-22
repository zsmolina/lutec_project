from openai import OpenAI

from app.config import Settings, get_settings


def create_openai_client(settings: Settings | None = None) -> OpenAI:
    cfg = settings or get_settings()
    if not cfg.openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY no está configurada. Defínala en backend/.env o variables de entorno."
        )
    return OpenAI(api_key=cfg.openai_api_key.get_secret_value())
