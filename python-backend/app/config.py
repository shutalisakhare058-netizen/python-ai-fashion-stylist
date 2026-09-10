"""Application configuration loaded from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "AI Fashion Stylist"
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv(
        "ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"
    )
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fashion.db")
    # Comma-separated list of allowed CORS origins.
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")

    @property
    def demo_mode(self) -> bool:
        """Demo mode is active when no Anthropic API key is configured."""
        return not bool(self.ANTHROPIC_API_KEY)


settings = Settings()
