"""Configuration management for OpenProject MCP Server."""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging as early as possible
from utils.logging import configure_logging
configure_logging(os.getenv("MCP_LOG_LEVEL", "INFO"))


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # OpenProject configuration
        self.openproject_url: str = self._get_required_env("OPENPROJECT_URL")
        self.openproject_api_key: str = self._get_required_env("OPENPROJECT_API_KEY")
        self.openproject_host: Optional[str] = os.getenv("OPENPROJECT_HOST")  # Optional Host header override

        # MCP server configuration
        self.mcp_host: str = os.getenv("MCP_HOST", "localhost")
        self.mcp_port: int = int(os.getenv("MCP_PORT", "8080"))
        self.log_level: str = os.getenv("MCP_LOG_LEVEL", "INFO")
        
        # Optional performance settings
        self.cache_timeout: int = int(os.getenv("CACHE_TIMEOUT", "300"))
        self.pagination_size: int = int(os.getenv("PAGINATION_SIZE", "100"))
        self.max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
        
        # Validate configuration
        self._validate_config()
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error with helpful message."""
        value = os.getenv(key)
        if not value:
            if key == "OPENPROJECT_URL":
                raise ValueError(
                    "Required environment variable OPENPROJECT_URL is not set.\n"
                    "Please set it in your .env file:\n"
                    "  OPENPROJECT_URL=http://localhost:8080\n"
                    "  (Replace with your actual OpenProject URL)"
                )
            elif key == "OPENPROJECT_API_KEY":
                raise ValueError(
                    "Required environment variable OPENPROJECT_API_KEY is not set.\n"
                    "To get your API key:\n"
                    "  1. Login to your OpenProject instance\n"
                    "  2. Go to 'My Account' → 'Access Tokens'\n"
                    "  3. Click 'New token' and copy the 40-character key\n"
                    "  4. Set it in your .env file:\n"
                    "     OPENPROJECT_API_KEY=your_40_character_api_key_here"
                )
            else:
                raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def _validate_config(self) -> None:
        """Validate configuration values with detailed error messages."""
        # Validate OpenProject URL
        if not self.openproject_url.startswith(("http://", "https://")):
            raise ValueError(
                f"Invalid OPENPROJECT_URL: {self.openproject_url}\n"
                "OPENPROJECT_URL must start with http:// or https://\n"
                "Example: OPENPROJECT_URL=http://localhost:8080"
            )
        
        # Validate OpenProject API Key
        if len(self.openproject_api_key) < 20:
            raise ValueError(
                f"Invalid OPENPROJECT_API_KEY: {self.openproject_api_key}\n"
                "OPENPROJECT_API_KEY appears to be too short.\n"
                "OpenProject API keys are typically 40+ characters long.\n"
                "Please verify your API key from OpenProject → My Account → Access Tokens"
            )
        
        # Validate MCP Port
        if not (1 <= self.mcp_port <= 65535):
            raise ValueError(
                f"Invalid MCP_PORT: {self.mcp_port}\n"
                "MCP_PORT must be between 1 and 65535\n"
                "Recommended: 8080 (standard HTTP port)"
            )
        
        # Validate MCP Host
        if self.mcp_host not in ["localhost", "0.0.0.0", "127.0.0.1"]:
            raise ValueError(
                f"Invalid MCP_HOST: {self.mcp_host}\n"
                "MCP_HOST should be 'localhost' for local development or '0.0.0.0' for Docker containers"
            )
        
        # Validate Log Level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(
                f"Invalid MCP_LOG_LEVEL: {self.log_level}\n"
                f"Valid log levels are: {', '.join(valid_log_levels)}"
            )
        
        # Validate performance settings
        if self.cache_timeout < 60:
            raise ValueError(
                f"Invalid CACHE_TIMEOUT: {self.cache_timeout}\n"
                "CACHE_TIMEOUT should be at least 60 seconds (1 minute)"
            )
        
        if not (10 <= self.pagination_size <= 1000):
            raise ValueError(
                f"Invalid PAGINATION_SIZE: {self.pagination_size}\n"
                "PAGINATION_SIZE should be between 10 and 1000"
            )
        
        if not (1 <= self.max_retries <= 10):
            raise ValueError(
                f"Invalid MAX_RETRIES: {self.max_retries}\n"
                "MAX_RETRIES should be between 1 and 10"
            )


# Global settings instance
settings = Settings()
