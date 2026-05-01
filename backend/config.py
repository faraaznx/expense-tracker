from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    gemini_api_key: str
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    database_url: str
    resend_api_key: str
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()
