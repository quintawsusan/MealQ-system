from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MealQ API"
    environment: str = "development"
    debug: bool = True

    database_url: str = "sqlite:///./mealq.db"

    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    flow_poll_interval_seconds: int = 2
    
    BREVO_API_KEY: str
    BREVO_SENDER_EMAIL: str
    BREVO_SENDER_NAME: str = "MealQ"

    app_base_url: str = "http://localhost:8000"

    email_verification_required: bool = True
    verification_token_expire_hours: int = 24
    password_reset_token_expire_minutes: int = 30

    seed_admin_email: str = ""
    seed_admin_password: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()