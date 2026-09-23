#!/usr/bin/env python3
"""Test script to debug OpenAI model initialization in detail."""

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

# Import models
print("Importing models module...")
try:
    import models
    from models import ModelType, ModelProvider
    print("Successfully imported models module")
except Exception as e:
    print(f"Error importing models: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test the get_openai_chat function directly
print("\nTesting get_openai_chat function directly...")
try:
    from models import get_openai_chat
    print("Testing with non-existent model 'gpt-4o-mini'...")
    model = get_openai_chat("gpt-4o-mini")
    print(f"Result: {model}")
    print(f"Model type: {type(model)}")
    if model:
        print(f"Model model_name: {getattr(model, 'model_name', 'N/A')}")
        print(f"Model api_key is set: {'Yes' if getattr(model, 'openai_api_key', None) else 'No'}")
    
except Exception as e:
    print(f"Exception in get_openai_chat: {e}")
    import traceback
    traceback.print_exc()

# Test the get_openai_chat function with a real model name
print("\nTesting get_openai_chat function with real model name...")
try:
    print("Testing with real model 'gpt-4o-mini' (but this doesn't actually exist)...")
    model = get_openai_chat("gpt-4o-mini")
    print(f"Result: {model}")
    print(f"Model type: {type(model)}")
    if model:
        print(f"Model model_name: {getattr(model, 'model_name', 'N/A')}")
        print(f"Model api_key is set: {'Yes' if getattr(model, 'openai_api_key', None) else 'No'}")
    
except Exception as e:
    print(f"Exception in get_openai_chat with real model: {e}")
    import traceback
    traceback.print_exc()

# Test the get_openai_chat function with a truly real model name
print("\nTesting get_openai_chat function with truly real model name...")
try:
    print("Testing with truly real model 'gpt-4o'...")
    model = get_openai_chat("gpt-4o")
    print(f"Result: {model}")
    print(f"Model type: {type(model)}")
    if model:
        print(f"Model model_name: {getattr(model, 'model_name', 'N/A')}")
        print(f"Model api_key is set: {'Yes' if getattr(model, 'openai_api_key', None) else 'No'}")
    
except Exception as e:
    print(f"Exception in get_openai_chat with truly real model: {e}")
    import traceback
    traceback.print_exc()

# Test the get_model function with various model names
print("\nTesting get_model function with various model names...")
test_models = ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo", "gpt-4.1-mini"]

for model_name in test_models:
    try:
        print(f"\nTesting with model: {model_name}")
        model = models.get_model(ModelType.CHAT, ModelProvider.OPENAI, model_name)
        print(f"Result: {model}")
        print(f"Model type: {type(model)}")
        if model:
            print(f"Model model_name: {getattr(model, 'model_name', 'N/A')}")
            print(f"SUCCESS: Model {model_name} initialized successfully")
        else:
            print(f"ERROR: Model {model_name} returned None")

    except Exception as e:
        print(f"Exception with model {model_name}: {e}")

print("\nTest completed.")
