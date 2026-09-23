#!/usr/bin/env python3
"""
Unit tests for models.py API key retrieval and model name translation enhancements.

Tests the fixes implemented in Step 5 for patching the failure point:
- Enhanced API key retrieval with Railway support
- Model name translation layer
- Clear error messages
"""

import os
import unittest
from unittest.mock import patch, MagicMock

import models


class TestApiKeyRetrieval(unittest.TestCase):
    """Test enhanced API key retrieval functionality."""

    def setUp(self):
        """Set up test environment."""
        self.original_env = dict(os.environ)

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch('models.dotenv.get_dotenv_value')
    def test_standard_api_key_patterns(self, mock_dotenv):
        """Test that standard API key patterns are checked correctly."""
        # Test API_KEY_OPENAI pattern
        mock_dotenv.side_effect = lambda key: "sk-test-key" if key == "API_KEY_OPENAI" else None
        
        result = models.get_api_key("openai")
        
        mock_dotenv.assert_called_with("API_KEY_OPENAI")
        self.assertEqual(result, "sk-test-key")

    @patch('models.dotenv.get_dotenv_value')
    def test_railway_api_key_patterns(self, mock_dotenv):
        """Test that Railway API key patterns are checked."""
        def mock_dotenv_side_effect(key):
            if key == "RAILWAY_OPENAI_API_KEY":
                return "sk-railway-key"
            return None
        
        mock_dotenv.side_effect = mock_dotenv_side_effect
        
        result = models.get_api_key("openai")
        
        # Should eventually call RAILWAY_OPENAI_API_KEY pattern
        self.assertEqual(result, "sk-railway-key")

    @patch('models.dotenv.get_dotenv_value')
    def test_api_key_priority_order(self, mock_dotenv):
        """Test that API key patterns are checked in the right priority order."""
        def mock_dotenv_side_effect(key):
            if key == "API_KEY_OPENAI":
                return "sk-standard-key"
            elif key == "RAILWAY_OPENAI_API_KEY":
                return "sk-railway-key"
            return None
        
        mock_dotenv.side_effect = mock_dotenv_side_effect
        
        result = models.get_api_key("openai")
        
        # Should return the standard pattern first
        self.assertEqual(result, "sk-standard-key")

    @patch('models.dotenv.get_dotenv_value')
    def test_empty_key_handling(self, mock_dotenv):
        """Test that empty or 'None' keys are ignored."""
        def mock_dotenv_side_effect(key):
            if key == "API_KEY_OPENAI":
                return ""  # Empty string
            elif key == "OPENAI_API_KEY":
                return "None"  # String "None"
            elif key == "RAILWAY_OPENAI_API_KEY":
                return "sk-valid-key"
            return None
        
        mock_dotenv.side_effect = mock_dotenv_side_effect
        
        result = models.get_api_key("openai")
        
        # Should return the valid key, skipping empty and "None" values
        self.assertEqual(result, "sk-valid-key")

    @patch('models.dotenv.get_dotenv_value')
    def test_no_api_key_found(self, mock_dotenv):
        """Test behavior when no API key is found."""
        mock_dotenv.return_value = None
        
        result = models.get_api_key("openai")
        
        self.assertIsNone(result)


class TestModelNameTranslation(unittest.TestCase):
    """Test model name translation functionality."""

    def test_gpt_4_1_mini_translation(self):
        """Test that gpt-4.1-mini is correctly translated to gpt-4o-mini."""
        translated_name, was_translated = models.translate_model_name("gpt-4.1-mini")
        
        self.assertEqual(translated_name, "gpt-4o-mini")
        self.assertTrue(was_translated)

    def test_gpt_4_1_translation(self):
        """Test that gpt-4.1 is correctly translated to gpt-4o."""
        translated_name, was_translated = models.translate_model_name("gpt-4.1")
        
        self.assertEqual(translated_name, "gpt-4o")
        self.assertTrue(was_translated)

    def test_gpt_4_1_nano_translation(self):
        """Test that gpt-4.1-nano is correctly translated to gpt-4o-mini."""
        translated_name, was_translated = models.translate_model_name("gpt-4.1-nano")
        
        self.assertEqual(translated_name, "gpt-4o-mini")
        self.assertTrue(was_translated)

    def test_valid_model_no_translation(self):
        """Test that valid model names are not translated."""
        translated_name, was_translated = models.translate_model_name("gpt-4o-mini")
        
        self.assertEqual(translated_name, "gpt-4o-mini")
        self.assertFalse(was_translated)

    def test_o3_future_proofing(self):
        """Test that o3 models are mapped to o1 for future compatibility."""
        translated_name, was_translated = models.translate_model_name("o3-mini")
        
        self.assertEqual(translated_name, "o1-mini")
        self.assertTrue(was_translated)


class TestOpenAIChatIntegration(unittest.TestCase):
    """Test the integrated OpenAI chat functionality."""

    @patch('models.ChatOpenAI')
    @patch('models.get_api_key')
    def test_model_name_translation_in_chatopenai(self, mock_get_api_key, mock_chat_openai):
        """Test that model name translation works in the ChatOpenAI constructor."""
        mock_get_api_key.return_value = "sk-test-key"
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance
        
        result = models.get_openai_chat("gpt-4.1-mini")
        
        # Verify ChatOpenAI was called with the translated model name
        mock_chat_openai.assert_called_once_with(
            api_key="sk-test-key",
            model="gpt-4o-mini",  # Should be translated
            base_url=None
        )
        self.assertEqual(result, mock_instance)

    @patch('models.ChatOpenAI')
    @patch('models.get_api_key')
    def test_api_key_retrieval_in_chatopenai(self, mock_get_api_key, mock_chat_openai):
        """Test that API key retrieval works in the ChatOpenAI constructor."""
        mock_get_api_key.return_value = "sk-test-key"
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance
        
        result = models.get_openai_chat("gpt-4o-mini")
        
        # Verify the API key was retrieved and used
        mock_get_api_key.assert_called_once_with("openai")
        mock_chat_openai.assert_called_once_with(
            api_key="sk-test-key",
            model="gpt-4o-mini",
            base_url=None
        )

    @patch('models.ChatOpenAI')
    @patch('models.get_api_key')
    def test_no_api_key_warning(self, mock_get_api_key, mock_chat_openai):
        """Test that a warning is printed when no API key is found."""
        mock_get_api_key.return_value = None
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance
        
        with patch('builtins.print') as mock_print:
            result = models.get_openai_chat("gpt-4o-mini")
            
            # Check that a warning was printed
            mock_print.assert_called()
            printed_args = [call[0][0] for call in mock_print.call_args_list]
            warning_printed = any("WARNING" in arg for arg in printed_args)
            self.assertTrue(warning_printed, "Expected warning message not found in print calls")

    @patch('models.ChatOpenAI')
    @patch('models.get_api_key')
    def test_chatopenai_exception_handling(self, mock_get_api_key, mock_chat_openai):
        """Test that ChatOpenAI exceptions are handled with error messages."""
        mock_get_api_key.return_value = "sk-test-key"
        mock_chat_openai.side_effect = Exception("API connection failed")
        
        with patch('builtins.print') as mock_print:
            with self.assertRaises(Exception):
                models.get_openai_chat("gpt-4o-mini")
            
            # Check that an error message was printed
            printed_args = [call[0][0] for call in mock_print.call_args_list]
            error_printed = any("ERROR" in arg for arg in printed_args)
            self.assertTrue(error_printed, "Expected error message not found in print calls")


class TestDebugOutput(unittest.TestCase):
    """Test debug output functionality."""

    @patch.dict(os.environ, {'DEBUG_MODELS': '1'})
    @patch('models.dotenv.get_dotenv_value')
    def test_debug_output_on_api_key_retrieval(self, mock_dotenv):
        """Test that debug output is printed when DEBUG_MODELS is set."""
        mock_dotenv.return_value = "sk-test-key"
        
        with patch('builtins.print') as mock_print:
            models.get_api_key("openai")
            
            # Check that debug output was printed
            mock_print.assert_called()
            printed_args = [call[0][0] for call in mock_print.call_args_list]
            debug_printed = any("DEBUG" in arg for arg in printed_args)
            self.assertTrue(debug_printed, "Expected debug output not found in print calls")

    @patch.dict(os.environ, {'DEBUG_MODELS': '1'})
    def test_debug_output_on_model_translation(self):
        """Test that debug output is printed for model name translation."""
        with patch('builtins.print') as mock_print:
            models.translate_model_name("gpt-4.1-mini")
            
            # Check that debug translation output was printed
            printed_args = [call[0][0] for call in mock_print.call_args_list]
            translation_debug_printed = any(
                "Model name translation" in arg for arg in printed_args
            )
            self.assertTrue(
                translation_debug_printed, 
                "Expected model translation debug output not found in print calls"
            )


if __name__ == '__main__':
    unittest.main()
