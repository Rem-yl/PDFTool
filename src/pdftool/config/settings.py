"""
Configuration settings for PDFTool
"""

from pathlib import Path
from typing import Optional, List

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    try:
        from pydantic import BaseSettings, Field
    except ImportError:
        # Fallback for environments without pydantic
        class BaseSettings:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        def Field(default=None, **kwargs):
            return default


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application info
    app_name: str = Field(default="PDFTool")
    version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)  # uvicorn --reload
    
    # File handling
    temp_dir: Path = Field(default=Path("temp"))
    max_file_size: int = Field(default=100 * 1024 * 1024)  # 100MB
    allowed_extensions: List[str] = Field(default=[".pdf"])
    
    # API settings
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_workers: int = Field(default=1)
    
    # Security
    upload_rate_limit: int = Field(default=10)  # uploads per minute
    
    # Logging
    log_level: str = Field(default="INFO")
    log_file: Optional[Path] = Field(default=None)
    
    model_config = {
        "env_file": Path(__file__).parent.parent.parent.parent / ".env",
        "env_file_encoding": "utf-8",
        "env_prefix": "PDFTOOL_",
        "case_sensitive": False,
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure temp directory exists
        self.temp_dir.mkdir(exist_ok=True)


# Global settings instance
settings = Settings()