"""Application configuration via environment variables."""
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# .env yükleme
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")

load_dotenv(ENV_PATH, override=True)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    database_url: str = Field(default="sqlite:///./bloom_local.db", validation_alias="DATABASE_URL")

    openai_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        validation_alias="AI_INTEGRATIONS_OPENAI_BASE_URL"
    )

    openai_api_key: str = Field(
        default="", 
        validation_alias="AI_INTEGRATIONS_OPENAI_API_KEY"
    )

    openai_model: str = Field(
        default="deepseek/deepseek-v4-flash:free",
        validation_alias="OPENAI_MODEL"
    )

    port: int = Field(default=8080, validation_alias="PORT")

    cag_ttl_seconds: int = 3600
    rag_top_k: int = 5


settings = Settings()

# ================ GUCLU TEMIZLEME ================
# Key'i hem env'den hem settings'den kontrol et
raw_key = (settings.openai_api_key or os.getenv("AI_INTEGRATIONS_OPENAI_API_KEY", "")).strip()

# Eger yanlislikla "Bearer " prefix'i ile kaydedilmisse temizle
if raw_key.lower().startswith("bearer "):
    raw_key = raw_key[7:].strip()

# Sadece ASCII karakterleri tut (gizli karakterleri temizle)
settings.openai_api_key = "".join(c for c in raw_key if 32 <= ord(c) <= 126).strip()

# Debug icin
print("="*60)
print(f"[CONFIG] .env yolu       : {ENV_PATH}")
print(f"[CONFIG] Base URL        : {settings.openai_base_url}")
print(f"[CONFIG] Model           : {settings.openai_model}")
print(f"[CONFIG] Key uzunlugu    : {len(settings.openai_api_key)}")
print(f"[CONFIG] Key (ilk 10)    : {settings.openai_api_key[:10]}...")
print("="*60)

if len(settings.openai_api_key) < 20:
    print("!!! [CONFIG] API KEY YUKLENEMEDI VEYA COK KISA !!!")
else:
    print(">>> [CONFIG] API Key basariyla yuklendi.")