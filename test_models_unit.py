#!/usr/bin/env python3
"""
Unit Tests for Gary-Zero Model Name Translation and API Key Retrieval Fixes

This test suite validates:
1. Model name alias translation functionality
2. Enhanced API key retrieval with Railway support
3. OpenAI chat model integration with translation
4. Clear error messaging for missing credentials
"""

import os
import pytest
import unittest
from unittest.mock import patch, MagicMock

# Import our models module
import models


class TestAPIKeyRetrieval(unittest.TestCase):
    """Test enhanced API key retrieval functionality."""
    
    @patch.dict(os.environ, {
        'API_KEY_OPENAI': 'sk-test-standard-key',
        'OPENAI_API_KEY': 'sk-test-openai-key',
        'RAILWAY_OPENAI_API_KEY': 'sk-test-railway-key'
    }, clear=True)
    def test_api_key_patterns(self):
        """Test various API key patterns are recognized."""
        # Clear environment first, then set test values
        with patch('framework.helpers.dotenv.get_dotenv_value') as mock_dotenv:
            # Test standard pattern
            mock_dotenv.return_value = 'sk-test-standard-key'
            key = models.get_api_key('openai')
            self.assertEqual(key, 'sk-test-standard-key')
            
            # Test Railway pattern
            mock_dotenv.return_value = 'sk-test-railway-key'
            key = models.get_api_key('openai')
            self.assertEqual(key, 'sk-test-railway-key')
    
    @patch('framework.helpers.dotenv.get_dotenv_value')
    def test_api_key_priority_order(self, mock_dotenv):
        """Test API key priority order."""
        # Mock that the first pattern returns a key
        mock_dotenv.side_effect = lambda pattern: {
            'API_KEY_OPENAI': 'sk-priority-key',
            'OPENAI_API_KEY': 'sk-secondary-key',
            'RAILWAY_OPENAI_API_KEY': 'sk-railway-key'
        }.get(pattern, None)
        
        key = models.get_api_key('openai')
        self.assertEqual(key, 'sk-priority-key')
    
    @patch('framework.helpers.dotenv.get_dotenv_value')
    def test_empty_key_handling(self, mock_dotenv):
        """Test that empty/None keys are skipped."""
        mock_dotenv.side_effect = lambda pattern: {
            'API_KEY_OPENAI': '',  # Empty key
            'OPENAI_API_KEY': 'None',  # String "None"
            'RAILWAY_OPENAI_API_KEY': 'sk-valid-key'
        }.get(pattern, None)
        
        key = models.get_api_key('openai')
        self.assertEqual(key, 'sk-valid-key')
    
    @patch('framework.helpers.dotenv.get_dotenv_value')
    def test_no_key_found(self, mock_dotenv):
        """Test behavior when no API key is found."""
        mock_dotenv.return_value = None
        
        key = models.get_api_key('openai')
        self.assertIsNone(key)


class TestModelNameTranslation(unittest.TestCase):
    """Test model name translation functionality."""
    
    def test_gpt_4_1_mini_translation(self):
        """Test gpt-4.1-mini translates to gpt-4o-mini."""
        translated, was_translated = models.translate_model_name('gpt-4.1-mini')
        self.assertEqual(translated, 'gpt-4o-mini')
        self.assertTrue(was_translated)
    
    def test_gpt_4_1_translation(self):
        """Test gpt-4.1 translates to gpt-4o."""
        translated, was_translated = models.translate_model_name('gpt-4.1')
        self.assertEqual(translated, 'gpt-4o')
        self.assertTrue(was_translated)
    
    def test_gpt_4_1_nano_translation(self):
        """Test gpt-4.1-nano translates to gpt-4o-mini."""
        translated, was_translated = models.translate_model_name('gpt-4.1-nano')
        self.assertEqual(translated, 'gpt-4o-mini')
        self.assertTrue(was_translated)
    
    def test_o3_series_translation(self):
        """Test o3 series models translate to o1 equivalents."""
        translated, was_translated = models.translate_model_name('o3')
        self.assertEqual(translated, 'o1')
        self.assertTrue(was_translated)
        
        translated, was_translated = models.translate_model_name('o3-mini')
        self.assertEqual(translated, 'o1-mini')
        self.assertTrue(was_translated)
    
    def test_no_translation_needed(self):
        """Test models that don't need translation."""
        translated, was_translated = models.translate_model_name('gpt-4o-mini')
        self.assertEqual(translated, 'gpt-4o-mini')
        self.assertFalse(was_translated)
        
        translated, was_translated = models.translate_model_name('claude-3-5-sonnet')
        self.assertEqual(translated, 'claude-3-5-sonnet')
        self.assertFalse(was_translated)
    
    def test_model_name_aliases_dict(self):
        """Test that MODEL_NAME_ALIASES dict contains expected mappings."""
        self.assertIn('gpt-4.1-mini', models.MODEL_NAME_ALIASES)
        self.assertEqual(models.MODEL_NAME_ALIASES['gpt-4.1-mini'], 'gpt-4o-mini')
        
        self.assertIn('gpt-4.1', models.MODEL_NAME_ALIASES)
        self.assertEqual(models.MODEL_NAME_ALIASES['gpt-4.1'], 'gpt-4o')
        
        self.assertIn('o3', models.MODEL_NAME_ALIASES)
        self.assertEqual(models.MODEL_NAME_ALIASES['o3'], 'o1')


class TestOpenAIChatIntegration(unittest.TestCase):
    """Test OpenAI chat model integration with translation."""
    
    @patch('models.get_api_key')
    @patch('langchain_openai.ChatOpenAI')
    def test_openai_chat_with_translation(self, mock_chat_openai, mock_get_api_key):
        """Test OpenAI chat model creation with model name translation."""
        mock_get_api_key.return_value = 'sk-test-key'
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance
        
        result = models.get_openai_chat('gpt-4.1-mini')
        
        # Verify ChatOpenAI was called with translated model name
        mock_chat_openai.assert_called_once()
        call_args = mock_chat_openai.call_args
        self.assertEqual(call_args[1]['model'], 'gpt-4o-mini')  # Translated name
        self.assertEqual(call_args[1]['api_key'], 'sk-test-key')
        
        self.assertEqual(result, mock_instance)
    
    @patch('models.get_api_key')
    @patch('langchain_openai.ChatOpenAI')  
    def test_openai_chat_no_translation(self, mock_chat_openai, mock_get_api_key):
        """Test OpenAI chat model creation without translation needed."""
        mock_get_api_key.return_value = 'sk-test-key'
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance
        
        result = models.get_openai_chat('gpt-4o-mini')
        
        # Verify ChatOpenAI was called with original model name
        mock_chat_openai.assert_called_once()
        call_args = mock_chat_openai.call_args
        self.assertEqual(call_args[1]['model'], 'gpt-4o-mini')  # No translation
        
        self.assertEqual(result, mock_instance)
    
    @patch('models.get_api_key')
    @patch('builtins.print')  # Capture print statements
    def test_openai_chat_no_api_key_warning(self, mock_print, mock_get_api_key):
        """Test warning message when no API key is found."""
        mock_get_api_key.return_value = None
        
        try:
            models.get_openai_chat('gpt-4o-mini')
        except Exception:
            pass  # Expected to fail without API key
        
        # Check if warning was printed
        warning_printed = any(
            call for call in mock_print.call_args_list 
            if len(call[0]) > 0 and '⚠️ WARNING:' in str(call[0][0])
        )
        self.assertTrue(warning_printed, "Expected warning message was not printed")


class TestIntegrationWithModelSystem(unittest.TestCase):
    """Test integration with the broader model system."""
    
    @patch('models.get_openai_chat')
    def test_get_model_integration(self, mock_get_openai_chat):
        """Test that get_model() works with translated model names."""
        mock_instance = MagicMock()
        mock_get_openai_chat.return_value = mock_instance
        
        result = models.get_model(
            models.ModelType.CHAT,
            models.ModelProvider.OPENAI,
            'gpt-4.1-mini'
        )
        
        # Verify get_openai_chat was called with the original model name
        # (translation happens inside get_openai_chat)
        mock_get_openai_chat.assert_called_once_with('gpt-4.1-mini')
        self.assertEqual(result, mock_instance)


if __name__ == '__main__':
    # Run tests with debug output
    os.environ['DEBUG_MODELS'] = '1'
    unittest.main(verbosity=2)
