import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIRECTORY = PROJECT_ROOT / "logs"
LOG_FILE_PATH = LOG_DIRECTORY / "job_match_agent.log"

MAX_LOG_FILE_BYTES = 2 * 1024 * 1024
BACKUP_LOG_COUNT = 3

LOGGER_NAME = "job_match_agent"


def configure_logging() -> logging.Logger:
    """
    Configure rotating file and console logging.

    The logger is configured only once, even when Streamlit
    reruns the application.
    """

    LOG_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger = logging.getLogger(
        LOGGER_NAME
    )

    logger.setLevel(
        logging.INFO
    )

    logger.propagate = False

    if logger.handlers:
        return logger

    log_formatter = logging.Formatter(
        (
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        filename=LOG_FILE_PATH,
        maxBytes=MAX_LOG_FILE_BYTES,
        backupCount=BACKUP_LOG_COUNT,
        encoding="utf-8",
    )

    file_handler.setLevel(
        logging.INFO
    )

    file_handler.setFormatter(
        log_formatter
    )

    console_handler = logging.StreamHandler()

    console_handler.setLevel(
        logging.WARNING
    )

    console_handler.setFormatter(
        log_formatter
    )

    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )

    logger.info(
        "Application logging initialized."
    )

    return logger


def get_logger(
    module_name: str = LOGGER_NAME,
) -> logging.Logger:
    """
    Return a child logger for one application module.
    """

    configure_logging()

    return logging.getLogger(
        f"{LOGGER_NAME}.{module_name}"
    )


def sanitize_context(
    context: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Remove sensitive or excessively large values before logging.

    CV text, job-description text, credentials, secrets and
    generated application documents must not be stored in logs.
    """

    if not context:
        return {}

    sensitive_terms = {
        "cv_text",
        "job_text",
        "password",
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "private_key",
        "credentials",
        "credential",
        "secret",
        "email_body",
        "cover_letter",
        "tailored_cv",
        "authorization",
    }

    safe_context: dict[str, Any] = {}

    for key, value in context.items():
        normalized_key = str(
            key
        ).lower()

        if any(
            sensitive_term in normalized_key
            for sensitive_term in sensitive_terms
        ):
            safe_context[key] = "[REDACTED]"
            continue

        if isinstance(
            value,
            str,
        ) and len(value) > 500:
            safe_context[key] = (
                value[:500]
                + "... [TRUNCATED]"
            )

        else:
            safe_context[key] = value

    return safe_context


def log_exception(
    logger: logging.Logger,
    error: Exception,
    message: str,
    context: dict[str, Any] | None = None,
) -> None:
    """
    Log an exception with sanitized diagnostic context.
    """

    safe_context = sanitize_context(
        context
    )

    logger.error(
        (
            "%s | Error type: %s | "
            "Details: %s | Context: %s"
        ),
        message,
        type(error).__name__,
        str(error),
        safe_context,
        exc_info=True,
    )


def log_event(
    logger: logging.Logger,
    message: str,
    context: dict[str, Any] | None = None,
) -> None:
    """
    Log a normal application event.
    """

    safe_context = sanitize_context(
        context
    )

    logger.info(
        "%s | Context: %s",
        message,
        safe_context,
    )


def get_log_file_path() -> Path:
    """
    Return the absolute active log-file path.
    """

    configure_logging()

    return LOG_FILE_PATH.resolve()


def get_recent_log_lines(
    line_limit: int = 300,
) -> list[str]:
    """
    Return the most recent lines from the active log file.
    """

    configure_logging()

    if not LOG_FILE_PATH.exists():
        return []

    try:
        lines = LOG_FILE_PATH.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines()

    except OSError:
        return []

    safe_limit = max(
        1,
        min(
            int(line_limit),
            5000,
        ),
    )

    return lines[
        -safe_limit:
    ]


def get_log_text(
    line_limit: int = 1000,
) -> str:
    """
    Return recent log content as one text string.
    """

    return "\n".join(
        get_recent_log_lines(
            line_limit=line_limit
        )
    )


def clear_log_file() -> None:
    """
    Clear the active log file.

    Rotated backup files are preserved.
    """

    configure_logging()

    LOG_FILE_PATH.write_text(
        "",
        encoding="utf-8",
    )

    logger = get_logger(
        "logging_service"
    )

    logger.info(
        "The active log file was cleared."
    )


def get_log_information() -> dict[str, Any]:
    """
    Return metadata about the active log file.
    """

    configure_logging()

    exists = LOG_FILE_PATH.exists()

    return {
        "path": str(
            LOG_FILE_PATH.resolve()
        ),
        "exists": exists,
        "size_bytes": (
            LOG_FILE_PATH.stat().st_size
            if exists
            else 0
        ),
        "backup_count": (
            BACKUP_LOG_COUNT
        ),
        "maximum_file_size_bytes": (
            MAX_LOG_FILE_BYTES
        ),
    }