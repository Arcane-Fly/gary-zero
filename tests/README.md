# Model Initialization Tests

This directory contains regression tests for the model initialization functionality in Gary-Zero.

## Core Test Requirements

The main test verifies that:
```python
from models import get_model, ModelType, ModelProvider  
model = get_model(ModelType.CHAT, ModelProvider.OPENAI, "gpt-4.1-mini")  
assert model is not None
```

## Running Tests

### Local Development

Run the core regression test directly:
```bash
python tests/test_model_initialization.py
```

This will test the exact requirement from Step 6 without requiring pytest or complex setup.

### With pytest

If you have pytest installed, you can run more comprehensive tests:
```bash
# Install pytest if needed
pip install pytest pytest-mock

# Run with pytest
python -m pytest tests/test_model_initialization.py -v
```

### CI Environment

The tests are designed to work in CI environments with minimal setup. The GitHub Actions workflow will:

1. Create necessary directories (webui/public, webui/css, webui/js)
2. Install basic dependencies
3. Run the regression test with mocked API keys
4. Verify that no actual network calls are made

## Test Features

- **Network Isolation**: All external API calls are mocked to ensure reliable testing
- **Model Name Translation**: Verifies that `gpt-4.1-mini` correctly translates to `gpt-4o-mini`
- **Error Handling**: Tests proper error messages when models fail to initialize
- **Environment Compatibility**: Works in both local development and CI environments

## Dependencies

The test uses only Python standard library modules:
- `unittest.mock` for mocking external dependencies
- `os` and `sys` for environment and path management

Optional dependencies:
- `pytest` for enhanced test runner (falls back to simple runner if not available)

## Test Structure

- `TestModelInitialization`: Core test suite with mocked dependencies
- `TestModelInitializationCI`: Additional tests for CI environments
- `run_basic_test()`: Simple test runner that doesn't require pytest

## Expected Output

When successful, you should see:
```
🧪 Running model initialization regression test...
📋 Testing the core requirement from Step 6:
   get_model(ModelType.CHAT, ModelProvider.OPENAI, 'gpt-4.1-mini') should return non-None
✅ CORE TEST PASSED: get_model returned a valid model instance
   Model type: ChatOpenAI
   Model has expected attributes: True
   Translated model name: gpt-4o-mini

🎉 All tests passed! Model initialization is working correctly.
```

## Troubleshooting

If tests fail:

1. **Import Errors**: Ensure you're running from the project root directory
2. **Missing Directories**: Create `webui/public`, `webui/css`, `webui/js` directories
3. **API Key Issues**: Tests should work without real API keys (they're mocked)
4. **Dependency Issues**: The core test only needs Python standard library

For more detailed debugging, set the `DEBUG_MODELS` environment variable:
```bash
DEBUG_MODELS=1 python tests/test_model_initialization.py
```
