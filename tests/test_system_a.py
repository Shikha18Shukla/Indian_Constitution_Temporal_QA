"""System A tests use mocked generation callbacks; no API key or network required."""

import json
import os
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from systems.generation_settings import GenerationSettings
from systems.system_a import (
    ApiRequestError,
    ConnectionTimeoutError,
    GeminiResponse,
    MissingApiKeyError,
    NetworkRequestError,
    RateLimitError,
    TransientApiError,
    generate_with_gemini,
    run_experiment,
)


class FakeGenerator:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def __call__(self, prompt, settings, api_key):
        self.calls.append((prompt, settings, api_key))
        if self.error:
            raise self.error
        return self.response


class FakeHttpError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.status_code = code
        super().__init__(message)


@contextmanager
def fake_genai_responses(outcomes):
    captured = {"calls": 0}

    class FakeModels:
        def generate_content(self, **kwargs):
            captured["calls"] += 1
            outcome = outcomes[captured["calls"] - 1]
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome

    class FakeClient:
        def __init__(self, api_key, http_options):
            captured["api_key"] = api_key
            captured["http_options"] = http_options
            self.models = FakeModels()

    class FakeConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeHttpOptions:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeRetryOptions:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    google_module = ModuleType("google")
    google_module.__path__ = []
    genai_module = ModuleType("google.genai")
    genai_module.Client = FakeClient
    types_module = ModuleType("google.genai.types")
    types_module.GenerateContentConfig = FakeConfig
    types_module.HttpOptions = FakeHttpOptions
    types_module.HttpRetryOptions = FakeRetryOptions
    genai_module.types = types_module
    google_module.genai = genai_module
    fake_modules = {"google": google_module, "google.genai": genai_module, "google.genai.types": types_module}
    with patch.dict(sys.modules, fake_modules), \
         patch("systems.system_a.time.sleep") as sleep, \
         patch("systems.system_a.random.uniform", return_value=0.25) as jitter:
        yield captured, sleep, jitter


class SystemATests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.output_path = Path(self.temp_dir.name) / "system_a" / "runs.jsonl"
        self.settings = GenerationSettings("gemini-test-model", 0.0, 512)

    def run_one(self, generator, api_key="test-key"):
        return run_experiment(
            question_id="Q-001",
            question="What does Article 21A provide?",
            reference_date="2020-01-01",
            settings=self.settings,
            api_key=api_key,
            generate=generator,
            output_path=self.output_path,
            timestamp="2026-10-30T00:00:00Z",
        )

    def read_records(self):
        return [json.loads(line) for line in self.output_path.read_text(encoding="utf-8").splitlines()]

    def test_success_sends_only_question_and_date_prompt_and_saves_record(self):
        generator = FakeGenerator("Article 21A provides for free and compulsory education.")
        result = self.run_one(generator)
        self.assertEqual(len(generator.calls), 1)
        prompt, settings, api_key = generator.calls[0]
        self.assertIn("Reference date: 2020-01-01", prompt)
        self.assertIn("Question: What does Article 21A provide?", prompt)
        self.assertNotIn("retriev", prompt.lower())
        self.assertNotIn("corpus", prompt.lower())
        self.assertEqual(settings, self.settings)
        self.assertEqual(api_key, "test-key")
        self.assertEqual(result["raw_answer"], generator.response)
        self.assertFalse(result["retrieval_used"])
        self.assertFalse(result["web_access_used"])
        self.assertEqual(self.read_records(), [result])

    def test_records_missing_api_key_attempt(self):
        with self.assertRaises(MissingApiKeyError):
            self.run_one(FakeGenerator("should not run"), api_key=None)
        record = self.read_records()[0]
        self.assertIsNone(record["raw_answer"])
        self.assertEqual(record["run_status"], "failed")
        self.assertIn("GEMINI_API_KEY", record["error_message"])

    def test_records_rate_limit_error_and_raises_clear_error(self):
        with self.assertRaises(RateLimitError):
            self.run_one(FakeGenerator(error=RateLimitError("quota exceeded")))
        record = self.read_records()[0]
        self.assertEqual(record["run_status"], "failed")
        self.assertIn("quota exceeded", record["error_message"])

    def test_records_other_api_failure_and_raises_clear_error(self):
        with self.assertRaises(ApiRequestError):
            self.run_one(FakeGenerator(error=RuntimeError("service unavailable")))
        record = self.read_records()[0]
        self.assertEqual(record["run_status"], "failed")
        self.assertIn("service unavailable", record["error_message"])

    def test_records_timeout_failure(self):
        with self.assertRaises(ConnectionTimeoutError):
            self.run_one(FakeGenerator(error=TimeoutError("request deadline exceeded")))
        record = self.read_records()[0]
        self.assertEqual(record["run_status"], "failed")
        self.assertIn("timed out", record["error_message"])

    def test_records_network_failure(self):
        with self.assertRaises(NetworkRequestError):
            self.run_one(FakeGenerator(error=ConnectionError("connection reset")))
        record = self.read_records()[0]
        self.assertEqual(record["run_status"], "failed")
        self.assertIn("network request failed", record["error_message"])

    def test_record_has_required_experiment_fields_and_settings(self):
        result = self.run_one(FakeGenerator("answer"))
        expected = {
            "question_id", "question", "reference_date", "system_name", "model_name",
            "prompt", "raw_answer", "run_timestamp", "temperature", "max_output_tokens",
            "retrieval_used", "web_access_used",
        }
        self.assertTrue(expected.issubset(result))
        self.assertEqual(result["model_name"], "gemini-test-model")
        self.assertEqual(result["temperature"], 0.0)
        self.assertEqual(result["max_output_tokens"], 512)

    def test_rejects_invalid_reference_date_before_call(self):
        generator = FakeGenerator("answer")
        with self.assertRaises(ValueError):
            run_experiment("Q-1", "Question", "2020-02-30", self.settings, "key", generator, self.output_path)
        self.assertEqual(generator.calls, [])
        self.assertFalse(self.output_path.exists())

    def test_default_model_and_environment_override(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(GenerationSettings.from_environment().model_name, "gemini-3.5-flash-lite")
        with patch.dict(os.environ, {"GEMINI_MODEL_NAME": "gemini-custom-flash"}, clear=True):
            self.assertEqual(GenerationSettings.from_environment().model_name, "gemini-custom-flash")

    def test_gemini_35_flash_lite_uses_generate_content_without_temperature_or_tools(self):
        captured = {}

        class FakeModels:
            def generate_content(self, **kwargs):
                captured.update(kwargs)
                return SimpleNamespace(text="mocked Gemini 3.8 response")

        class FakeClient:
            def __init__(self, api_key, http_options):
                captured["api_key"] = api_key
                captured["http_options"] = http_options
                self.models = FakeModels()

        class FakeGenerateContentConfig:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        class FakeHttpOptions:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        class FakeHttpRetryOptions:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        google_module = ModuleType("google")
        google_module.__path__ = []
        genai_module = ModuleType("google.genai")
        genai_module.Client = FakeClient
        types_module = ModuleType("google.genai.types")
        types_module.GenerateContentConfig = FakeGenerateContentConfig
        types_module.HttpOptions = FakeHttpOptions
        types_module.HttpRetryOptions = FakeHttpRetryOptions
        genai_module.types = types_module
        google_module.genai = genai_module
        fake_modules = {
            "google": google_module,
            "google.genai": genai_module,
            "google.genai.types": types_module,
        }
        settings = GenerationSettings("gemini-3.5-flash-lite", 0.4, 512)
        with patch.dict(sys.modules, fake_modules):
            answer = generate_with_gemini("question prompt", settings, "test-key")

        self.assertEqual(answer, "mocked Gemini 3.8 response")
        self.assertEqual(captured["model"], "gemini-3.5-flash-lite")
        self.assertEqual(captured["contents"], "question prompt")
        self.assertEqual(captured["config"].kwargs, {"max_output_tokens": 512})
        self.assertEqual(captured["http_options"].kwargs["timeout"], 45000)
        self.assertEqual(captured["http_options"].kwargs["retry_options"].kwargs, {"attempts": 1})
        self.assertNotIn("tools", captured["config"].kwargs)

    def test_gemini_35_flash_lite_run_logs_temperature_as_not_sent(self):
        settings = GenerationSettings("gemini-3.5-flash-lite", 0.4, 512)
        result = run_experiment(
            "Q-3", "Question", "2020-01-01", settings, "test-key",
            generate=FakeGenerator("answer"), output_path=self.output_path,
        )
        self.assertIsNone(result["temperature"])

    def test_request_timeout_is_configurable(self):
        with patch.dict(os.environ, {"GEMINI_REQUEST_TIMEOUT_SECONDS": "32"}, clear=True):
            settings = GenerationSettings.from_environment()
        self.assertEqual(settings.request_timeout_seconds, 32)

    def test_retry_settings_are_configurable_and_capped_at_two_retries(self):
        with patch.dict(os.environ, {
            "GEMINI_MAX_RETRIES": "1",
            "GEMINI_RETRY_BACKOFF_SECONDS": "2.5",
        }, clear=True):
            settings = GenerationSettings.from_environment()
        self.assertEqual(settings.max_retries, 1)
        self.assertEqual(settings.retry_backoff_seconds, 2.5)
        with patch.dict(os.environ, {"GEMINI_MAX_RETRIES": "3"}, clear=True):
            with self.assertRaisesRegex(ValueError, "between 0 and 2"):
                GenerationSettings.from_environment()

    def test_503_retries_once_then_succeeds_and_keeps_attempt_telemetry(self):
        outcomes = [FakeHttpError(503, "503 UNAVAILABLE: high demand"), SimpleNamespace(text="recovered")]
        with fake_genai_responses(outcomes) as (captured, sleep, jitter):
            answer = generate_with_gemini("prompt", self.settings, "test-key")
        self.assertEqual(answer, "recovered")
        self.assertIsInstance(answer, GeminiResponse)
        self.assertEqual(answer.attempt_count, 2)
        self.assertEqual(answer.error_details[0]["status_code"], 503)
        self.assertEqual(captured["calls"], 2)
        sleep.assert_called_once_with(0.25)
        jitter.assert_called_once_with(0.0, 1.0)
        self.assertEqual(captured["http_options"].kwargs["timeout"], 45000)
        self.assertEqual(captured["http_options"].kwargs["retry_options"].kwargs, {"attempts": 1})

    def test_504_retries_once_then_succeeds(self):
        outcomes = [FakeHttpError(504, "504 DEADLINE_EXCEEDED: temporary"), SimpleNamespace(text="recovered")]
        with fake_genai_responses(outcomes) as (captured, sleep, _):
            answer = generate_with_gemini("prompt", self.settings, "test-key")
        self.assertEqual(answer, "recovered")
        self.assertEqual(answer.attempt_count, 2)
        self.assertEqual(answer.error_details[0]["status_label"], "DEADLINE_EXCEEDED")
        self.assertEqual(captured["calls"], 2)
        sleep.assert_called_once_with(0.25)

    def test_transient_retries_are_exhausted_after_two_retries(self):
        outcomes = [FakeHttpError(503, "503 UNAVAILABLE: busy") for _ in range(3)]
        with fake_genai_responses(outcomes) as (captured, sleep, _):
            with self.assertRaises(TransientApiError) as raised:
                generate_with_gemini("prompt", self.settings, "test-key")
        self.assertEqual(captured["calls"], 3)
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual(raised.exception.attempt_count, 3)
        self.assertEqual(len(raised.exception.error_details), 3)
        self.assertEqual(raised.exception.final_api_status, "503 UNAVAILABLE")

    def test_network_error_retries_but_invalid_request_does_not(self):
        with fake_genai_responses([ConnectionError("connection reset"), SimpleNamespace(text="ok")]) as (captured, sleep, _):
            answer = generate_with_gemini("prompt", self.settings, "test-key")
        self.assertEqual(answer.attempt_count, 2)
        self.assertEqual(captured["calls"], 2)
        sleep.assert_called_once()

        with fake_genai_responses([FakeHttpError(400, "400 INVALID_ARGUMENT: bad request")]) as (captured, sleep, _):
            with self.assertRaises(ApiRequestError):
                generate_with_gemini("prompt", self.settings, "test-key")
        self.assertEqual(captured["calls"], 1)
        sleep.assert_not_called()

    def test_retry_telemetry_is_one_run_record(self):
        response = GeminiResponse("answer", 2, [{"attempt": 1, "status_code": 503}])
        result = self.run_one(FakeGenerator(response))
        records = self.read_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(result["attempt_count"], 2)
        self.assertEqual(result["final_status"], "succeeded")
        self.assertEqual(result["error_details"][0]["status_code"], 503)

    def test_exhausted_retry_telemetry_is_logged_as_one_failed_run(self):
        error = TransientApiError("Gemini transient service error: 503 UNAVAILABLE")
        error.attempt_count = 3
        error.error_details = [
            {"attempt": attempt, "status_code": 503, "message": "503 UNAVAILABLE"}
            for attempt in range(1, 4)
        ]
        error.final_status = "failed"
        error.final_api_status = "503 UNAVAILABLE"
        with self.assertRaises(TransientApiError):
            self.run_one(FakeGenerator(error=error))
        records = self.read_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["attempt_count"], 3)
        self.assertEqual(records[0]["final_status"], "failed")
        self.assertEqual(records[0]["final_api_status"], "503 UNAVAILABLE")
        self.assertEqual(len(records[0]["error_details"]), 3)


if __name__ == "__main__":
    unittest.main()
