#!/usr/bin/env python3
"""
Comprehensive Model Validation Script for Gary-Zero

This script validates all model configurations across the entire system hierarchy
to ensure they use valid, existing models and proper API configurations.
"""

import os
import sys
from typing import Any

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

try:
    import models
    from framework.helpers.settings import get_settings
    from framework.helpers.settings.types import DEFAULT_SETTINGS

    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def validate_model_name(provider: str, model_name: str) -> bool:
    """Validate if a model name exists for the given provider."""

    # Common valid models for each provider (verified against official docs)
    valid_models = {
        "ANTHROPIC": [
            # Current Claude 4 models
            "claude-opus-4-20250514",
            "claude-sonnet-4-20250514",
            # Claude 3.7 models  
            "claude-3-7-sonnet-20250219",
            # Claude 3.5 models
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-20240620",
            "claude-3-5-haiku-20241022",
            # Claude 3 legacy models
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307",
            # Aliases (production should use specific versions)
            "claude-opus-4-0",
            "claude-sonnet-4-0", 
            "claude-3-7-sonnet-latest",
            "claude-3-5-sonnet-latest",
            "claude-3-5-haiku-latest",
        ],
        "OPENAI": [
            # Current chat models
            "gpt-4o",
            "gpt-4o-mini",
            # O-series reasoning models
            "o1",
            "o1-preview", 
            "o1-mini",
            "o3-mini",
            # Legacy models still supported
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            # Embedding models
            "text-embedding-3-large",
            "text-embedding-3-small",
            "text-embedding-ada-002",
            # Audio/image models
            "dall-e-3",
            "whisper-1",
            "tts-1",
            "tts-1-hd",
            # Moderation
            "omni-moderation-latest",
        ],
        "GOOGLE": [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-pro",
            "gemini-pro-vision",
        ],
        "GROQ": ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"],
    }

    return model_name in valid_models.get(provider, [])


def validate_model_config(
    config_name: str, provider: str, model_name: str
) -> dict[str, Any]:
    """Validate a single model configuration."""
    result = {
        "config_name": config_name,
        "provider": provider,
        "model_name": model_name,
        "valid": False,
        "issues": [],
    }

    # Check if provider exists
    if not hasattr(models.ModelProvider, provider):
        result["issues"].append(f"Invalid provider: {provider}")
        return result

    # Check if model name is valid
    if not validate_model_name(provider, model_name):
        result["issues"].append(f"Invalid/non-existent model: {model_name}")
        return result

    # Try to create the model
    try:
        provider_enum = getattr(models.ModelProvider, provider)

        # Determine model type
        if "embedding" in model_name.lower():
            model_type = models.ModelType.EMBEDDING
        else:
            model_type = models.ModelType.CHAT

        model = models.get_model(model_type, provider_enum, model_name)
        if model is None:
            result["issues"].append("Model initialization returned None")
            return result

        result["valid"] = True

    except Exception as e:
        result["issues"].append(f"Model initialization failed: {str(e)}")

    return result


def validate_default_settings():
    """Validate all model configurations in DEFAULT_SETTINGS."""
    print("\n🔍 Validating DEFAULT_SETTINGS configurations...")

    model_configs = [
        (
            "Chat Model",
            DEFAULT_SETTINGS["chat_model_provider"],
            DEFAULT_SETTINGS["chat_model_name"],
        ),
        (
            "Utility Model",
            DEFAULT_SETTINGS["util_model_provider"],
            DEFAULT_SETTINGS["util_model_name"],
        ),
        (
            "Embedding Model",
            DEFAULT_SETTINGS["embed_model_provider"],
            DEFAULT_SETTINGS["embed_model_name"],
        ),
        (
            "Browser Model",
            DEFAULT_SETTINGS["browser_model_provider"],
            DEFAULT_SETTINGS["browser_model_name"],
        ),
        (
            "Voice Model",
            DEFAULT_SETTINGS["voice_model_provider"],
            DEFAULT_SETTINGS["voice_model_name"],
        ),
        (
            "Code Model",
            DEFAULT_SETTINGS["code_model_provider"],
            DEFAULT_SETTINGS["code_model_name"],
        ),
    ]

    results = []
    for config_name, provider, model_name in model_configs:
        result = validate_model_config(config_name, provider, model_name)
        results.append(result)

        if result["valid"]:
            print(f"  ✅ {config_name}: {provider}/{model_name}")
        else:
            print(f"  ❌ {config_name}: {provider}/{model_name}")
            for issue in result["issues"]:
                print(f"     - {issue}")

    return results


def validate_current_settings():
    """Validate current user settings."""
    print("\n🔍 Validating current user settings...")

    try:
        current_settings = get_settings()

        model_configs = [
            (
                "Chat Model",
                current_settings["chat_model_provider"],
                current_settings["chat_model_name"],
            ),
            (
                "Utility Model",
                current_settings["util_model_provider"],
                current_settings["util_model_name"],
            ),
            (
                "Embedding Model",
                current_settings["embed_model_provider"],
                current_settings["embed_model_name"],
            ),
            (
                "Browser Model",
                current_settings["browser_model_provider"],
                current_settings["browser_model_name"],
            ),
        ]

        results = []
        for config_name, provider, model_name in model_configs:
            result = validate_model_config(config_name, provider, model_name)
            results.append(result)

            if result["valid"]:
                print(f"  ✅ {config_name}: {provider}/{model_name}")
            else:
                print(f"  ❌ {config_name}: {provider}/{model_name}")
                for issue in result["issues"]:
                    print(f"     - {issue}")

        return results

    except Exception as e:
        print(f"  ❌ Failed to load current settings: {e}")
        return []


def validate_agent_initialization():
    """Validate agent initialization with current settings."""
    print(
        "\n🔍 Skipping agent initialization validation (requires complex dependencies)..."
    )
    return []


def check_api_keys():
    """Check if necessary API keys are configured."""
    print("\n🔍 Checking API key configurations...")

    required_keys = {
        "ANTHROPIC": ["ANTHROPIC_API_KEY", "API_KEY_ANTHROPIC"],
        "OPENAI": ["OPENAI_API_KEY", "API_KEY_OPENAI"],
        "GOOGLE": ["GOOGLE_API_KEY", "API_KEY_GOOGLE", "GEMINI_API_KEY"],
        "GROQ": ["GROQ_API_KEY", "API_KEY_GROQ"],
    }

    for provider, key_names in required_keys.items():
        key_found = False
        for key_name in key_names:
            if os.environ.get(key_name):
                print(f"  ✅ {provider}: {key_name} found")
                key_found = True
                break

        if not key_found:
            print(
                f"  ⚠️  {provider}: No API key found (checked: {', '.join(key_names)})"
            )


def main():
    """Main validation function."""
    print("🚀 Gary-Zero Model Configuration Validator")
    print("=" * 50)

    # Check basic imports and setup
    print(f"✅ Models module loaded: {models}")
    print(f"✅ Available providers: {[p.name for p in models.ModelProvider]}")
    print(f"✅ Available model types: {[t.name for t in models.ModelType]}")

    # Validate configurations
    default_results = validate_default_settings()
    current_results = validate_current_settings()
    agent_results = validate_agent_initialization()

    # Check API keys
    check_api_keys()

    # Summary
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 30)

    all_results = default_results + current_results + agent_results
    valid_count = sum(1 for r in all_results if r["valid"])
    total_count = len(all_results)

    print(f"Total configurations checked: {total_count}")
    print(f"Valid configurations: {valid_count}")
    print(f"Invalid configurations: {total_count - valid_count}")

    if total_count == valid_count:
        print("🎉 ALL MODEL CONFIGURATIONS ARE VALID!")
        return 0
    else:
        print("❌ SOME MODEL CONFIGURATIONS NEED ATTENTION!")
        print("\nInvalid configurations:")
        for result in all_results:
            if not result["valid"]:
                print(
                    f"  - {result['config_name']}: {result['provider']}/{result['model_name']}"
                )
                for issue in result["issues"]:
                    print(f"    └─ {issue}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
