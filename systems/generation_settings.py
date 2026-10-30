"""Shared generation settings intended to remain constant across systems."""

from dataclasses import dataclass
import os


DEFAULT_MODEL_NAME = "gemini-3.5-flash-lite"


@dataclass(frozen=True)
class GenerationSettings:
    model_name: str = DEFAULT_MODEL_NAME
    temperature: float = 0.0
    max_output_tokens: int = 1024
    request_timeout_seconds: int = 45
    max_retries: int = 2
    retry_backoff_seconds: float = 1.0

    def __post_init__(self):
        if not 0 <= self.max_retries <= 2:
            raise ValueError("max_retries must be between 0 and 2")
        if not 0.0 <= self.retry_backoff_seconds <= 30.0:
            raise ValueError("retry_backoff_seconds must be between 0 and 30 seconds")

    @classmethod
    def from_environment(cls):
        model_name = os.getenv("GEMINI_MODEL_NAME", DEFAULT_MODEL_NAME).strip()
        if not model_name:
            raise ValueError("GEMINI_MODEL_NAME must not be empty")
        try:
            temperature = float(os.getenv("GENERATION_TEMPERATURE", "0.0"))
        except ValueError as exc:
            raise ValueError("GENERATION_TEMPERATURE must be a number") from exc
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("GENERATION_TEMPERATURE must be between 0.0 and 2.0")
        try:
            max_output_tokens = int(os.getenv("MAX_OUTPUT_TOKENS", "1024"))
        except ValueError as exc:
            raise ValueError("MAX_OUTPUT_TOKENS must be an integer") from exc
        if max_output_tokens < 1:
            raise ValueError("MAX_OUTPUT_TOKENS must be greater than zero")
        try:
            request_timeout_seconds = int(os.getenv("GEMINI_REQUEST_TIMEOUT_SECONDS", "45"))
        except ValueError as exc:
            raise ValueError("GEMINI_REQUEST_TIMEOUT_SECONDS must be an integer") from exc
        if not 1 <= request_timeout_seconds <= 600:
            raise ValueError("GEMINI_REQUEST_TIMEOUT_SECONDS must be between 1 and 600")
        try:
            max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "2"))
        except ValueError as exc:
            raise ValueError("GEMINI_MAX_RETRIES must be an integer") from exc
        if not 0 <= max_retries <= 2:
            raise ValueError("GEMINI_MAX_RETRIES must be between 0 and 2")
        try:
            retry_backoff_seconds = float(os.getenv("GEMINI_RETRY_BACKOFF_SECONDS", "1.0"))
        except ValueError as exc:
            raise ValueError("GEMINI_RETRY_BACKOFF_SECONDS must be a number") from exc
        if not 0.0 <= retry_backoff_seconds <= 30.0:
            raise ValueError("GEMINI_RETRY_BACKOFF_SECONDS must be between 0 and 30 seconds")
        return cls(
            model_name, temperature, max_output_tokens, request_timeout_seconds,
            max_retries, retry_backoff_seconds,
        )
