"""
Configuration settings for PDFTool
"""

from pathlib import Path
from typing import Optional, List

try:
    from pydantic import BaseSettings, Field
except ImportError:
    # Fallback for environments without pydantic
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    def Field(default=None, env=None):
        return default


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application info
    app_name: str = Field(default="PDFTool", env="PDFTOOL_APP_NAME")
    version: str = Field(default="1.0.0", env="PDFTOOL_VERSION")
    debug: bool = Field(default=False, env="PDFTOOL_DEBUG")
    
    # File handling
    temp_dir: Path = Field(default=Path("temp"), env="PDFTOOL_TEMP_DIR")
    max_file_size: int = Field(default=100 * 1024 * 1024, env="PDFTOOL_MAX_FILE_SIZE")  # 100MB
    allowed_extensions: List[str] = Field(default=[".pdf"], env="PDFTOOL_ALLOWED_EXTENSIONS")
    
    # API settings
    api_host: str = Field(default="0.0.0.0", env="PDFTOOL_API_HOST")
    api_port: int = Field(default=8000, env="PDFTOOL_API_PORT")
    api_workers: int = Field(default=1, env="PDFTOOL_API_WORKERS")
    
    # Security
    upload_rate_limit: int = Field(default=10, env="PDFTOOL_UPLOAD_RATE_LIMIT")  # uploads per minute
    
    # Logging
    log_level: str = Field(default="INFO", env="PDFTOOL_LOG_LEVEL")
    log_file: Optional[Path] = Field(default=None, env="PDFTOOL_LOG_FILE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure temp directory exists
        self.temp_dir.mkdir(exist_ok=True)


# Global settings instance
settings = Settings()