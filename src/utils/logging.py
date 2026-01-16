"""Structured logging configuration for OpenProject MCP Server."""
import structlog
import logging
import sys
from typing import Any, Dict, Optional


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Configure standard library logging to stderr for MCP compatibility
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=getattr(logging, log_level.upper())
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def log_api_request(logger: structlog.BoundLogger, method: str, url: str, **kwargs: Any) -> None:
    """Log an API request with structured data.
    
    Args:
        logger: Structlog logger instance
        method: HTTP method
        url: Request URL
        **kwargs: Additional context data
    """
    logger.info(
        "API request initiated",
        method=method,
        url=url,
        **kwargs
    )


def log_api_response(logger: structlog.BoundLogger, method: str, url: str, status_code: int, **kwargs: Any) -> None:
    """Log an API response with structured data.
    
    Args:
        logger: Structlog logger instance
        method: HTTP method
        url: Request URL
        status_code: HTTP status code
        **kwargs: Additional context data
    """
    logger.info(
        "API request completed",
        method=method,
        url=url,
        status_code=status_code,
        **kwargs
    )


def log_tool_run(logger: structlog.BoundLogger, tool_name: str, success: bool, *args: Any, **kwargs: Any) -> None:
    """Log tool execution with structured data.
    
    Args:
        logger: Structlog logger instance
        tool_name: Name of the executed tool
        success: Whether execution was successful
        *args: Variable positional arguments (ignored)
        **kwargs: Additional context data
    """
    logger.info(
        "Tool execution completed",
        tool_name=tool_name,
        success=success,
        **kwargs
    )


def log_error(logger: structlog.BoundLogger, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log an error with structured data and context.
    
    Args:
        logger: Structlog logger instance
        error: Exception that occurred
        context: Additional context about the error
    """
    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        **(context or {})
    }
    
    logger.error(
        "Error occurred",
        **error_context,
        exc_info=True
    )


