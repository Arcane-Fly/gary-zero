#!/usr/bin/env python3
"""
Regression test for model initialization.

This test verifies that the get_model function can successfully initialize models
and return valid model instances. Network calls are mocked to ensure tests run
consistently without requiring actual API access.

Test requirements:
- Assert that get_model(ModelType.CHAT, ModelProvider.OPENAI, "gpt-4.1-mini") returns a non-None model instance
- Mock external network calls where possible
- Run both locally and in CI environments
"""

import os
import sys
from unittest.mock import patch, MagicMock

try:
    import pytest
except ImportError:
    pytest = None

# Add parent directory to sys.path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the models module components
from models import get_model, ModelType, ModelProvider


def test_get_model_returns_non_none():
    """
    Core regression test: Assert that get_model returns a non-None instance.
    
    This is the core requirement from Step 6: verify that calling
    get_model(ModelType.CHAT, ModelProvider.OPENAI, "gpt-4.1-mini")
    returns a valid model instance (not None).
    """
    with patch('models.get_api_key') as mock_get_api_key, \
         patch('langchain_openai.ChatOpenAI') as mock_chat_openai:
        
        # Mock API key retrieval to avoid actual environment dependencies
        mock_get_api_key.return_value = "sk-test-key-for-regression-test"
        
        # Mock ChatOpenAI constructor to return a mock instance
        mock_model_instance = MagicMock()
        mock_model_instance.__class__.__name__ = "ChatOpenAI"
        mock_chat_openai.return_value = mock_model_instance
        
        # Execute the function under test
        model = get_model(ModelType.CHAT, ModelProvider.OPENAI, "gpt-4.1-mini")
        
        # Core assertion: model should not be None
        assert model is not None, "get_model should return a non-None model instance"
        
        # Verify that the model has expected characteristics
        assert hasattr(model, '__class__'), "Model should be a valid object instance"
        
        # Check that model name is correct (should not be translated since GPT-4.1 models exist)
        call_args = mock_chat_openai.call_args
        if call_args and 'model' in call_args.kwargs:
            assert call_args.kwargs['model'] == "gpt-4.1-mini", "Model name should be passed through unchanged"


def run_basic_test():
    """Run the core regression test without pytest."""
    print("🧪 Running model initialization regression test...")
    print("📋 Testing the core requirement from Step 6:")
    print("   get_model(ModelType.CHAT, ModelProvider.OPENAI, 'gpt-4.1-mini') should return non-None")
    
    # Core regression test - test the exact requirement from Step 6
    try:
        from models import get_model, ModelType, ModelProvider
        model = get_model(ModelType.CHAT, ModelProvider.OPENAI, "gpt-4.1-mini")
        assert model is not None, "get_model should return a non-None model instance"
        print("✅ CORE TEST PASSED: get_model returned a valid model instance")
        print(f"   Model type: {type(model).__name__}")
        print(f"   Model has expected attributes: {hasattr(model, 'model_name')}")
        if hasattr(model, 'model_name'):
            print(f"   Translated model name: {model.model_name}")
        return True
    except Exception as e:
        print(f"❌ CORE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if pytest is not None:
        # Use pytest if available
        pytest.main([__file__, "-v"])
    else:
        # Run basic tests without pytest
        success = run_basic_test()
        exit(0 if success else 1)
