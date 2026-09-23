#!/usr/bin/env python3
"""Test script to reproduce the utility model initialization error."""

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

# Import models
print("Importing models module...")
try:
    import models
    print("Successfully imported models module")
except Exception as e:
    print(f"Error importing models: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test utility model initialization
print("Testing utility model initialization...")
try:
    from models import ModelType, ModelProvider
    print(f"Available ModelType enum: {list(ModelType)}")
    print(f"Available ModelProvider enum: {list(ModelProvider)}")
    
    # This should trigger the error we're looking for
    print("Attempting to get utility model with (ModelType.CHAT, ModelProvider.OPENAI, 'gpt-4.1-mini')")
    model = models.get_model(ModelType.CHAT, ModelProvider.OPENAI, "gpt-4.1-mini")
    print(f"Successfully initialized model: {model}")
    
except Exception as e:
    print(f"Error initializing utility model: {e}")
    import traceback
    traceback.print_exc()

# Test initialization through agent
print("\nTesting agent initialization...")
try:
    from initialize import initialize_agent
    print("Calling initialize_agent()...")
    config = initialize_agent()
    print(f"Agent configuration created: {config}")
    
    # Try to create an agent context
    from agent import AgentContext
    print("Creating AgentContext...")
    context = AgentContext(config)
    print(f"AgentContext created: {context}")
    
    # Try to get the utility model from the agent
    print("Getting utility model from agent...")
    utility_model = context.agent0.get_utility_model()
    print(f"Utility model obtained: {utility_model}")
    
except Exception as e:
    print(f"Error in agent initialization: {e}")
    import traceback
    traceback.print_exc()

print("\nTest completed.")
