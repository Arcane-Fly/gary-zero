"""AI Model Registry for Gary-Zero."""

# Import necessary classes from the main models.py file
import os
import sys
import importlib.util

# Load the models.py file directly from the parent directory
models_py_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models.py')

try:
    # Import from the models.py file in the parent directory using importlib
    spec = importlib.util.spec_from_file_location("models_main", models_py_path)
    models_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models_module)

    ModelProvider = models_module.ModelProvider
    ModelType = models_module.ModelType
    get_api_key = models_module.get_api_key
    get_model = models_module.get_model
    get_rate_limiter = models_module.get_rate_limiter
    parse_chunk = models_module.parse_chunk
    
    # Import new functions added for Step 5 fixes
    translate_model_name = models_module.translate_model_name
    get_openai_chat = models_module.get_openai_chat
    MODEL_NAME_ALIASES = models_module.MODEL_NAME_ALIASES
except (ImportError, AttributeError) as e:
    print(f"[DEBUG] Failed to import from models.py: {e}")
    # Fallback definitions if main models.py is not available
    from enum import Enum

    class ModelProvider(Enum):
        ANTHROPIC = "Anthropic"
        OPENAI = "OpenAI"
        GOOGLE = "Google"
        GROQ = "Groq"
        MISTRALAI = "Mistral AI"
        OTHER = "Other"

    class ModelType(Enum):
        CHAT = "Chat"
        EMBEDDING = "Embedding"

    def get_api_key(service):
        return None

    def get_model(model_type, provider, name, **kwargs):
        return None
    
    def get_rate_limiter(provider, name, requests, input_tokens, output_tokens):
        from framework.helpers.rate_limiter import RateLimiter
        return RateLimiter(
            requests=requests or 1000,
            input_tokens=input_tokens or 1000000,
            output_tokens=output_tokens or 1000000
        )
    
    def parse_chunk(chunk):
        if isinstance(chunk, str):
            return chunk
        elif hasattr(chunk, "content"):
            return str(chunk.content)
        else:
            return str(chunk)
    
    # Fallback implementations for the new functions
    def translate_model_name(model_name):
        return model_name, False
    
    def get_openai_chat(model_name, **kwargs):
        return None
    
    MODEL_NAME_ALIASES = {}
