#!/usr/bin/env python3
"""Debug script to trace get_model → provider factory chain."""

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, '.')

# Set DEBUG environment variable
os.environ['DEBUG'] = '1'

# Load environment variables first
from framework.helpers.dotenv import load_dotenv
print("Loading environment variables...")
load_dotenv()

# Print some relevant environment variables
print(f"OPENAI_API_KEY set: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
if os.getenv('OPENAI_API_KEY'):
    print(f"OPENAI_API_KEY length: {len(os.getenv('OPENAI_API_KEY', ''))}")

# Import directly from models.py (bypass the models package)
print("Importing models module...")
try:
    # Import the actual models.py file directly 
    import importlib.util
    spec = importlib.util.spec_from_file_location("models_main", "./models.py")
    models_main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models_main)
    
    # Import the classes and functions we need
    ModelType = models_main.ModelType
    ModelProvider = models_main.ModelProvider
    get_model = models_main.get_model
    get_openai_chat = models_main.get_openai_chat
    get_api_key = models_main.get_api_key
    
    print(f"Successfully imported models module directly from: ./models.py")
except Exception as e:
    print(f"Error importing models: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test API key retrieval first
print("\n=== Testing API Key Retrieval ===")
try:
    api_key = get_api_key("openai")
    print(f"get_api_key('openai') returned: {type(api_key)} - {'<key present>' if api_key else 'None'}")
    if api_key:
        print(f"API key length: {len(str(api_key))}")
        print(f"API key first 10 chars: {str(api_key)[:10]}...")
except Exception as e:
    print(f"Exception in get_api_key: {e}")
    import traceback
    traceback.print_exc()

# Test the get_openai_chat function directly
print("\n=== Testing get_openai_chat Function Directly ===")
try:
    print("Testing with model 'gpt-4o'...")
    model = get_openai_chat("gpt-4o")
    print(f"Result: {model}")
    print(f"Model type: {type(model)}")
    if model:
        print(f"Model model_name: {getattr(model, 'model_name', 'N/A')}")
        print(f"Model openai_api_key present: {'Yes' if getattr(model, 'openai_api_key', None) else 'No'}")
        # Try to inspect the ChatOpenAI instance
        if hasattr(model, 'client'):
            print(f"Model has client: {type(model.client)}")
        if hasattr(model, 'api_key'):
            print(f"Model api_key set: {'Yes' if model.api_key else 'No'}")
    
except Exception as e:
    print(f"Exception in get_openai_chat: {e}")
    import traceback
    traceback.print_exc()

# Test the get_model function to trace the full chain
print("\n=== Testing get_model Function (Full Chain) ===")
test_models = ["gpt-4o", "gpt-4.1-mini", "gpt-4o-mini"]

for model_name in test_models:
    print(f"\n--- Testing with model: {model_name} ---")
    try:
        model = get_model(ModelType.CHAT, ModelProvider.OPENAI, model_name)
        print(f"SUCCESS: get_model returned: {type(model)}")
        if model:
            print(f"Model attributes:")
            print(f"  - model_name: {getattr(model, 'model_name', 'N/A')}")
            if hasattr(model, 'api_key'):
                print(f"  - api_key set: {'Yes' if model.api_key else 'No'}")
            if hasattr(model, 'client'):
                print(f"  - client type: {type(model.client)}")
                # Try to check if the client has the OpenAI SDK
                if hasattr(model.client, '_client'):
                    print(f"  - underlying client: {type(model.client._client)}")
        else:
            print(f"ERROR: get_model returned None")

    except Exception as e:
        print(f"Exception with model {model_name}: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

# Test importing the OpenAI SDK directly
print("\n=== Testing OpenAI SDK Import ===")
try:
    import openai
    print(f"OpenAI SDK version: {openai.__version__}")
    print(f"OpenAI SDK location: {openai.__file__}")
    
    # Test creating a client directly
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    print(f"OpenAI client created successfully: {type(client)}")
    
except Exception as e:
    print(f"Exception importing/using OpenAI SDK: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Debug trace completed ===")
