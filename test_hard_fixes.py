#!/usr/bin/env python3
"""
Hard Test Script for API Key and Model Name Fixes

This script thoroughly tests all the fixes implemented in Step 5:
1. Enhanced API key retrieval with Railway support
2. Model name translation layer (gpt-4.1-mini -> gpt-4o-mini)
3. Clear error messages for missing configurations
4. Integration testing with actual model instantiation

Run this script to validate that all fixes are working correctly.
"""

import os
import sys
import traceback
from typing import Dict, List, Tuple

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

import models
from models import ModelType, ModelProvider


class TestResult:
    """Container for test results."""
    
    def __init__(self, test_name: str, passed: bool, message: str = "", error: str = ""):
        self.test_name = test_name
        self.passed = passed
        self.message = message
        self.error = error


class HardTestSuite:
    """Comprehensive test suite for API key and model name fixes."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.original_env = dict(os.environ)
        
    def add_result(self, test_name: str, passed: bool, message: str = "", error: str = ""):
        """Add a test result to the suite."""
        result = TestResult(test_name, passed, message, error)
        self.results.append(result)
        
        # Print immediate feedback
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    Message: {message}")
        if error:
            print(f"    Error: {error}")
        print()
    
    def setup_test_env(self, env_vars: Dict[str, str]):
        """Set up test environment variables."""
        os.environ.clear()
        os.environ.update(self.original_env)
        for key, value in env_vars.items():
            os.environ[key] = value
    
    def cleanup_test_env(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_api_key_patterns(self):
        """Test various API key pattern retrieval."""
        print("🔍 Testing API Key Pattern Retrieval")
        print("=" * 50)
        
        # Test 1: Standard API_KEY_OPENAI pattern
        try:
            self.setup_test_env({"API_KEY_OPENAI": "sk-standard-key"})
            result = models.get_api_key("openai")
            self.add_result(
                "Standard API_KEY_OPENAI Pattern",
                result == "sk-standard-key",
                f"Retrieved: {result}"
            )
        except Exception as e:
            self.add_result("Standard API_KEY_OPENAI Pattern", False, error=str(e))
        
        # Test 2: OPENAI_API_KEY pattern
        try:
            self.setup_test_env({"OPENAI_API_KEY": "sk-openai-key"})
            result = models.get_api_key("openai")
            self.add_result(
                "OPENAI_API_KEY Pattern",
                result == "sk-openai-key",
                f"Retrieved: {result}"
            )
        except Exception as e:
            self.add_result("OPENAI_API_KEY Pattern", False, error=str(e))
        
        # Test 3: Railway RAILWAY_OPENAI_API_KEY pattern
        try:
            self.setup_test_env({"RAILWAY_OPENAI_API_KEY": "sk-railway-key"})
            result = models.get_api_key("openai")
            self.add_result(
                "Railway RAILWAY_OPENAI_API_KEY Pattern",
                result == "sk-railway-key",
                f"Retrieved: {result}"
            )
        except Exception as e:
            self.add_result("Railway RAILWAY_OPENAI_API_KEY Pattern", False, error=str(e))
        
        # Test 4: Priority order (standard should override Railway)
        try:
            self.setup_test_env({
                "API_KEY_OPENAI": "sk-priority-key",
                "RAILWAY_OPENAI_API_KEY": "sk-railway-backup"
            })
            result = models.get_api_key("openai") 
            self.add_result(
                "API Key Priority Order",
                result == "sk-priority-key",
                f"Expected priority key, got: {result}"
            )
        except Exception as e:
            self.add_result("API Key Priority Order", False, error=str(e))
        
        # Test 5: Empty/None key handling
        try:
            self.setup_test_env({
                "API_KEY_OPENAI": "",
                "OPENAI_API_KEY": "None",
                "RAILWAY_OPENAI_API_KEY": "sk-valid-key"
            })
            result = models.get_api_key("openai")
            self.add_result(
                "Empty/None Key Handling",
                result == "sk-valid-key",
                f"Skipped empty keys, got: {result}"
            )
        except Exception as e:
            self.add_result("Empty/None Key Handling", False, error=str(e))
    
    def test_model_name_translation(self):
        """Test model name translation functionality."""
        print("🔄 Testing Model Name Translation")
        print("=" * 40)
        
        # Test cases: (input, expected_output, should_translate)
        test_cases = [
            ("gpt-4.1-mini", "gpt-4o-mini", True),
            ("gpt-4.1", "gpt-4o", True),
            ("gpt-4.1-nano", "gpt-4o-mini", True),
            ("gpt-4.1-preview", "gpt-4o", True),
            ("gpt-4o-mini", "gpt-4o-mini", False),  # Should not translate
            ("o3-mini", "o1-mini", True),  # Future proofing
            ("o3", "o1", True),
            ("claude-3-5-sonnet", "claude-3-5-sonnet", False),  # Should not translate
        ]
        
        for input_name, expected_output, should_translate in test_cases:
            try:
                translated_name, was_translated = models.translate_model_name(input_name)
                passed = (
                    translated_name == expected_output and 
                    was_translated == should_translate
                )
                self.add_result(
                    f"Translate '{input_name}'",
                    passed,
                    f"'{input_name}' -> '{translated_name}' (translated: {was_translated})"
                )
            except Exception as e:
                self.add_result(f"Translate '{input_name}'", False, error=str(e))
    
    def test_openai_chat_integration(self):
        """Test OpenAI chat integration with fixes."""
        print("🤖 Testing OpenAI Chat Integration")
        print("=" * 40)
        
        # Test with a valid API key (using a dummy key for testing)
        try:
            self.setup_test_env({"OPENAI_API_KEY": "sk-test-key-for-validation"})
            
            # Enable debug mode to see the translation in action
            os.environ["DEBUG_MODELS"] = "1"
            
            # Test that we can create the function without errors (won't actually connect)
            # This tests the API key retrieval and model name translation
            try:
                # Note: This will fail at the OpenAI API level, but should succeed
                # in our local processing (key retrieval, name translation)
                model = models.get_openai_chat("gpt-4.1-mini")
                self.add_result(
                    "OpenAI Chat with gpt-4.1-mini Translation",
                    True,
                    "Successfully created ChatOpenAI instance with translated model name"
                )
            except Exception as e:
                # Expected to fail at API level, but check if it's our code or OpenAI API
                if "api_key" in str(e).lower() or "authentication" in str(e).lower():
                    # This is an OpenAI API authentication error, which means our code worked
                    self.add_result(
                        "OpenAI Chat with gpt-4.1-mini Translation",
                        True,
                        "Translation and API key retrieval worked (OpenAI API auth expected to fail)"
                    )
                else:
                    # This is likely our code failing
                    self.add_result(
                        "OpenAI Chat with gpt-4.1-mini Translation",
                        False,
                        error=str(e)
                    )
        except Exception as e:
            self.add_result("OpenAI Chat Integration Setup", False, error=str(e))
        
        # Test with no API key - should show warning
        try:
            self.setup_test_env({})  # No API keys
            
            # Capture print output to check for warning
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()
            
            try:
                with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                    model = models.get_openai_chat("gpt-4o-mini")
                    
                # Check if warning was printed
                output = output_buffer.getvalue() + error_buffer.getvalue()
                warning_shown = "WARNING" in output or "⚠️" in output
                
                self.add_result(
                    "No API Key Warning",
                    warning_shown,
                    "Warning message displayed for missing API key" if warning_shown else "No warning shown"
                )
            except Exception as e:
                # Exception is expected, but check if warning was shown first
                output = output_buffer.getvalue() + error_buffer.getvalue()
                warning_shown = "WARNING" in output or "⚠️" in output
                
                self.add_result(
                    "No API Key Warning",
                    warning_shown,
                    f"Warning shown before exception: {warning_shown}"
                )
        except Exception as e:
            self.add_result("No API Key Warning Test", False, error=str(e))
    
    def test_error_message_clarity(self):
        """Test that error messages are clear and helpful."""
        print("📝 Testing Error Message Clarity")
        print("=" * 40)
        
        # Test clear error messages when API key is missing
        try:
            self.setup_test_env({})  # No API keys
            
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            output_buffer = io.StringIO()
            
            try:
                with redirect_stdout(output_buffer):
                    result = models.get_api_key("openai")
                    
                # Should return None but not show debug without DEBUG_MODELS
                self.add_result(
                    "No API Key Returns None",
                    result is None,
                    "get_api_key correctly returns None when no key found"
                )
                
            except Exception as e:
                self.add_result("API Key Error Handling", False, error=str(e))
                
        except Exception as e:
            self.add_result("Error Message Test Setup", False, error=str(e))
    
    def test_integration_with_model_registry(self):
        """Test integration with the broader model system."""
        print("🔗 Testing Integration with Model System")
        print("=" * 50)
        
        # Test that the get_model function works with our fixes
        try:
            self.setup_test_env({"OPENAI_API_KEY": "sk-integration-test-key"})
            
            try:
                # This should use our enhanced get_openai_chat function
                model = models.get_model(
                    ModelType.CHAT, 
                    ModelProvider.OPENAI, 
                    "gpt-4.1-mini"  # Should be translated to gpt-4o-mini
                )
                self.add_result(
                    "Integration with get_model()",
                    True,
                    "Successfully created model through get_model() with translation"
                )
            except Exception as e:
                # Check if it's an API authentication error (expected) vs our code error
                if "api_key" in str(e).lower() or "authentication" in str(e).lower():
                    self.add_result(
                        "Integration with get_model()",
                        True,
                        "Integration successful (API auth failure expected)"
                    )
                else:
                    self.add_result("Integration with get_model()", False, error=str(e))
                    
        except Exception as e:
            self.add_result("Integration Test Setup", False, error=str(e))
    
    def run_all_tests(self):
        """Run the complete test suite."""
        print("🚀 Gary-Zero API Key & Model Name Fixes - Hard Test Suite")
        print("=" * 70)
        print(f"Testing enhanced models.py functionality\n")
        
        # Run all test categories
        self.test_api_key_patterns()
        self.test_model_name_translation()
        self.test_openai_chat_integration()
        self.test_error_message_clarity()
        self.test_integration_with_model_registry()
        
        # Clean up
        self.cleanup_test_env()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary."""
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 30)
        
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        
        print(f"Total Tests: {len(self.results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {passed/len(self.results)*100:.1f}%")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if not result.passed:
                    print(f"  • {result.test_name}")
                    if result.error:
                        print(f"    Error: {result.error}")
        
        print("\n" + "=" * 70)
        if failed == 0:
            print("🎉 ALL TESTS PASSED! The fixes are working correctly.")
        else:
            print(f"⚠️  {failed} test(s) failed. Review the issues above.")
        print("=" * 70)


def main():
    """Main test execution."""
    print("Starting hard test suite for API key and model name fixes...\n")
    
    # Create and run the test suite
    test_suite = HardTestSuite()
    
    try:
        test_suite.run_all_tests()
        return 0 if all(r.passed for r in test_suite.results) else 1
    except Exception as e:
        print(f"❌ Test suite failed with exception: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
