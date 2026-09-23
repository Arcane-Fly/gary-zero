#!/usr/bin/env python3
"""Unit tests for model configuration, validation, and migration functionality."""

import unittest

from framework.helpers.model_catalog import (
    MODEL_CATALOG,
    get_model_release_date,
    get_models_for_provider,
    get_modern_models_for_provider,
    is_model_modern,
    is_valid_model_for_provider,
    validate_model_selection,
)
from framework.helpers.settings.types import DEFAULT_SETTINGS


class TestModelConfiguration(unittest.TestCase):
    """Test suite for model configuration and validation."""

    def test_model_catalog_structure(self):
        """Test that the model catalog has correct structure."""
        # Test that all providers have valid structure
        for provider, models in MODEL_CATALOG.items():
            self.assertIsInstance(provider, str)
            self.assertIsInstance(models, list)

            for model in models:
                self.assertIsInstance(model, dict)
                self.assertIn("value", model)
                self.assertIn("label", model)
                self.assertIsInstance(model["value"], str)
                self.assertIsInstance(model["label"], str)

    def test_anthropic_models_valid(self):
        """Test that Anthropic models are properly configured."""
        anthropic_models = MODEL_CATALOG["ANTHROPIC"]

        # Should have the updated model names
        model_names = [model["value"] for model in anthropic_models]
        self.assertIn("claude-opus-4-0", model_names)
        self.assertIn("claude-sonnet-4-0", model_names)
        self.assertIn("claude-3-5-sonnet-latest", model_names)

        # All models should be marked as modern
        for model in anthropic_models:
            self.assertTrue(model.get("modern", False))

    def test_openai_models_valid(self):
        """Test that OpenAI models are properly configured."""
        openai_models = MODEL_CATALOG["OPENAI"]

        # Should have the correct model names
        model_names = [model["value"] for model in openai_models]
        self.assertIn("gpt-4o", model_names)
        self.assertIn("gpt-4o-mini", model_names)
        self.assertIn("o1", model_names)
        self.assertIn("o3-mini", model_names)
        self.assertIn("dall-e-3", model_names)
        self.assertIn("whisper-1", model_names)
        self.assertIn("tts-1", model_names)
        self.assertIn("text-embedding-3-large", model_names)

        # All models should be marked as modern
        for model in openai_models:
            self.assertTrue(model.get("modern", False))

    def test_google_models_valid(self):
        """Test that Google models are properly configured."""
        google_models = MODEL_CATALOG["GOOGLE"]

        # Should have the correct model names
        model_names = [model["value"] for model in google_models]
        self.assertIn("gemini-2.5-pro", model_names)
        self.assertIn("gemini-2.5-flash", model_names)
        self.assertIn("gemini-2.0-flash", model_names)
        self.assertIn("imagen-4", model_names)
        self.assertIn("veo-2", model_names)

        # All models should be marked as modern
        for model in google_models:
            self.assertTrue(model.get("modern", False))


    def test_model_validation(self):
        """Test model validation functionality."""
        # Test valid models
        self.assertTrue(
            validate_model_selection("ANTHROPIC", "claude-sonnet-4-0")
        )
        self.assertTrue(validate_model_selection("OPENAI", "gpt-4o"))
        self.assertTrue(validate_model_selection("GOOGLE", "gemini-2.5-pro"))

        # Test embedding exemptions
        self.assertTrue(validate_model_selection("OPENAI", "text-embedding-3-large"))
        self.assertTrue(validate_model_selection("OPENAI", "text-embedding-3-small"))

        # Test invalid models
        self.assertFalse(validate_model_selection("ANTHROPIC", "non-existent-model"))
        self.assertFalse(validate_model_selection("OPENAI", "fake-model"))

        # Test migration during validation
        self.assertTrue(
            validate_model_selection("ANTHROPIC", "claude-sonnet-4-0")
        )  # Should migrate

    def test_default_settings_valid_models(self):
        """Test that all models in DEFAULT_SETTINGS are valid."""
        model_configs = [
            ("chat_model_provider", "chat_model_name"),
            ("util_model_provider", "util_model_name"),
            ("embed_model_provider", "embed_model_name"),
            ("browser_model_provider", "browser_model_name"),
            ("voice_model_provider", "voice_model_name"),
            ("code_model_provider", "code_model_name"),
        ]

        for provider_key, model_key in model_configs:
            provider = DEFAULT_SETTINGS[provider_key]
            model = DEFAULT_SETTINGS[model_key]

            # Check that the model is valid
            is_valid = validate_model_selection(provider, model)
            self.assertTrue(
                is_valid, f"Invalid model in DEFAULT_SETTINGS: {provider}/{model}"
            )

    def test_get_models_for_provider(self):
        """Test getting models for specific providers."""
        # Test existing providers
        anthropic_models = get_models_for_provider("ANTHROPIC")
        self.assertIsInstance(anthropic_models, list)
        self.assertGreater(len(anthropic_models), 0)

        openai_models = get_models_for_provider("OPENAI")
        self.assertIsInstance(openai_models, list)
        self.assertGreater(len(openai_models), 0)

        # Test non-existent provider
        fake_models = get_models_for_provider("FAKE_PROVIDER")
        self.assertEqual(fake_models, [])

    def test_get_modern_models_for_provider(self):
        """Test getting modern models for providers."""
        # All models in our catalog should be modern
        for provider in ["ANTHROPIC", "OPENAI", "GOOGLE"]:
            all_models = get_models_for_provider(provider)
            modern_models = get_modern_models_for_provider(provider)

            # All models should be modern in our updated catalog
            self.assertEqual(len(all_models), len(modern_models))

    def test_is_valid_model_for_provider(self):
        """Test model validity checking."""
        # Test valid combinations
        self.assertTrue(
            is_valid_model_for_provider("ANTHROPIC", "claude-sonnet-4-0")
        )
        self.assertTrue(is_valid_model_for_provider("OPENAI", "gpt-4o"))

        # Test invalid combinations
        self.assertFalse(
            is_valid_model_for_provider("ANTHROPIC", "gpt-4o")
        )  # Wrong provider
        self.assertFalse(
            is_valid_model_for_provider("OPENAI", "claude-sonnet-4-0")
        )  # Wrong provider
        self.assertFalse(
            is_valid_model_for_provider("ANTHROPIC", "fake-model")
        )  # Non-existent model

    def test_is_model_modern(self):
        """Test modern model checking."""
        # All models in our catalog should be modern except OTHER and deprecated providers
        skip_providers = ["OTHER", "MISTRALAI", "OPENAI_AZURE", "HUGGINGFACE", "CHUTES"]

        for provider, models in MODEL_CATALOG.items():
            if provider in skip_providers:
                continue

            for model in models:
                model_name = model["value"]
                self.assertTrue(
                    is_model_modern(provider, model_name),
                    f"Model {provider}/{model_name} should be modern",
                )

    def test_get_model_release_date(self):
        """Test getting model release dates."""
        # Test some known release dates
        date = get_model_release_date("ANTHROPIC", "claude-sonnet-4-0")
        self.assertEqual(date, "2025-05-14")

        date = get_model_release_date("OPENAI", "gpt-4o")
        self.assertEqual(date, "2024-05-13")

        # Test non-existent model
        date = get_model_release_date("ANTHROPIC", "fake-model")
        self.assertIsNone(date)

    def test_token_limits_reasonable(self):
        """Test that token limits are reasonable for special models."""
        # This test would check CSV data if we were to implement token limit validation
        # For now, just check that the structure allows for token limits
        pass

    def test_embedding_model_exemption(self):
        """Test that embedding models are exempt from modern-only requirements."""
        # Test embedding models pass validation
        self.assertTrue(validate_model_selection("OPENAI", "text-embedding-3-large"))
        self.assertTrue(validate_model_selection("OPENAI", "text-embedding-3-small"))
        self.assertTrue(validate_model_selection("OPENAI", "text-embedding-ada-002"))

    def test_deprecated_providers_empty(self):
        """Test that deprecated providers have no models."""
        deprecated_providers = ["MISTRALAI", "OPENAI_AZURE", "HUGGINGFACE", "CHUTES"]

        for provider in deprecated_providers:
            models = get_models_for_provider(provider)
            self.assertEqual(
                len(models), 0, f"Deprecated provider {provider} should have no models"
            )

    def test_modern_providers_have_models(self):
        """Test that modern providers have models."""
        modern_providers = ["ANTHROPIC", "OPENAI", "GOOGLE", "XAI", "DEEPSEEK"]

        for provider in modern_providers:
            models = get_models_for_provider(provider)
            self.assertGreater(
                len(models), 0, f"Modern provider {provider} should have models"
            )




class TestModelConfigEdgeCases(unittest.TestCase):
    """Test suite for edge cases in model configuration."""

    def test_empty_provider_name(self):
        """Test handling of empty provider names."""
        models = get_models_for_provider("")
        self.assertEqual(models, [])

    def test_none_provider_name(self):
        """Test handling of None provider names."""
        models = get_models_for_provider(None)
        self.assertEqual(models, [])

    def test_case_sensitive_provider_names(self):
        """Test that provider names are case sensitive."""
        # Should work
        models = get_models_for_provider("ANTHROPIC")
        self.assertGreater(len(models), 0)

        # Should not work (case sensitive)
        models = get_models_for_provider("anthropic")
        self.assertEqual(len(models), 0)

    def test_special_model_names(self):
        """Test handling of special model names with unusual characters."""
        # Test models with forward slashes (like OpenRouter models)
        self.assertTrue(
            is_valid_model_for_provider("OPENROUTER", "anthropic/claude-3.5-sonnet")
        )
        self.assertTrue(
            is_valid_model_for_provider("GROQ", "moonshotai/kimi-k2-instruct")
        )


if __name__ == "__main__":
    unittest.main()
