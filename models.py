"""
Models module for managing AI language model integrations and configurations.

This module provides a centralized interface for various AI language models
including OpenAI, Anthropic, Google, Mistral, and others. It handles model
initialization, configuration, and rate limiting.
"""

import os
from enum import Enum
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models.azure_openai import AzureChatOpenAI
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.embeddings.azure_openai import AzureOpenAIEmbeddings
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)
from langchain_google_genai import (
    embeddings as google_embeddings,
)
from langchain_groq import ChatGroq
from langchain_huggingface import (
    ChatHuggingFace,
    HuggingFaceEmbeddings,
    HuggingFaceEndpoint,
)
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic.v1.types import SecretStr

from framework.helpers import dotenv, runtime
from framework.helpers.dotenv import load_dotenv
from framework.helpers.rate_limiter import RateLimiter

# environment variables
load_dotenv()


class ModelType(Enum):
    CHAT = "Chat"
    EMBEDDING = "Embedding"


class ModelProvider(Enum):
    ANTHROPIC = "Anthropic"
    CHUTES = "Chutes"
    DEEPSEEK = "DeepSeek"
    GOOGLE = "Google"
    GROQ = "Groq"
    HUGGINGFACE = "HuggingFace"
    LMSTUDIO = "LM Studio"
    META = "Meta"
    MISTRALAI = "Mistral AI"
    OLLAMA = "Ollama"
    OPENAI = "OpenAI"
    OPENAI_AZURE = "OpenAI Azure"
    OPENROUTER = "OpenRouter"
    PERPLEXITY = "Perplexity"
    QWEN = "Qwen"
    SAMBANOVA = "Sambanova"
    XAI = "xAI"
    OTHER = "Other"


rate_limiters: dict[str, RateLimiter] = {}


# Utility function to get API keys from environment variables
def get_api_key(service) -> str | None:
    """Enhanced API key retrieval with Railway deployment support.
    
    Args:
        service: Service name (e.g., 'openai', 'anthropic')
        
    Returns:
        API key string or None if not found
        
    Note:
        Supports Railway environment variables like RAILWAY_OPENAI_API_KEY
        and standard patterns like API_KEY_OPENAI, OPENAI_API_KEY, etc.
    """
    service_upper = service.upper()
    
    # Standard patterns
    key_patterns = [
        f"API_KEY_{service_upper}",
        f"{service_upper}_API_KEY",
        f"{service_upper}_API_TOKEN",
    ]
    
    # Railway deployment patterns
    railway_patterns = [
        f"RAILWAY_{service_upper}_API_KEY",
        f"RAILWAY_API_KEY_{service_upper}",
    ]
    
    # Check all patterns in order of preference
    all_patterns = key_patterns + railway_patterns
    
    for pattern in all_patterns:
        key_value = dotenv.get_dotenv_value(pattern)
        if key_value and key_value != "None" and key_value.strip():
            if os.getenv('DEBUG_MODELS'):
                print(f"[DEBUG] Found API key for {service} using pattern: {pattern}")
            return str(key_value).strip()
    
    if os.getenv('DEBUG_MODELS'):
        print(f"[DEBUG] No API key found for {service}. Checked patterns: {all_patterns}")
    
    return None


def get_model(model_type: ModelType, provider: ModelProvider, name: str, **kwargs):
    """Get a model instance for the specified provider and type.

    Args:
        model_type: Type of model (CHAT or EMBEDDING)
        provider: Model provider enum
        name: Model name
        **kwargs: Additional model configuration

    Returns:
        Model instance

    Raises:
        ValueError: If provider/model combination is not supported
        Exception: If model initialization fails
    """
    # DEBUG TRACE: Entry point (conditional)
    if os.getenv('DEBUG_MODELS'):
        print(f"[DEBUG] get_model() called with: model_type={model_type}, provider={provider}, name='{name}', kwargs={kwargs}")
    
    # Construct the function name for the model getter
    fnc_name = f"get_{provider.name.lower()}_{model_type.name.lower()}"
    if os.getenv('DEBUG_MODELS'):
        print(f"[DEBUG] Constructed function name: '{fnc_name}'")

    try:
        # Check if the function exists
        if fnc_name not in globals():
            available_functions = [
                k
                for k in globals()
                if k.startswith("get_") and ("_chat" in k or "_embedding" in k)
            ]
            if os.getenv('DEBUG_MODELS'):
                print(f"[DEBUG] Function '{fnc_name}' not found in globals. Available functions: {available_functions[:10]}")
            raise ValueError(
                f"Provider {provider.name} does not support "
                f"{model_type.name} models. Function '{fnc_name}' not found. "
                f"Available functions: {available_functions[:5]}..."
            )

        # Call the function
        model_func = globals()[fnc_name]
        if os.getenv('DEBUG_MODELS'):
            print(f"[DEBUG] Found function '{fnc_name}', calling with args: name='{name}', kwargs={kwargs}")
        
        # Add a breakpoint here if needed
        # breakpoint()  # Uncomment this line to set a breakpoint
        
        model = model_func(name, **kwargs)
        if os.getenv('DEBUG_MODELS'):
            print(f"[DEBUG] Function '{fnc_name}' returned: {type(model)} - {model}")

        if model is None:
            if os.getenv('DEBUG_MODELS'):
                print(f"[DEBUG] Model function '{fnc_name}' returned None - this indicates an initialization issue")
            raise ValueError(
                f"DEBUG: Model function '{fnc_name}' returned None - " \
                f"input args: model_type={model_type}, provider={provider}, " \
                f"name={name}, kwargs={kwargs} - "
                f"check API key and configuration"
            )

        if os.getenv('DEBUG_MODELS'):
            print(f"[DEBUG] Successfully created model: {type(model)}")
        return model

    except KeyError as e:
        if os.getenv('DEBUG_MODELS'):
            print(f"[DEBUG] KeyError in get_model: {e}")
        raise ValueError(f"Provider function '{fnc_name}' not found: {e}") from e
    except Exception as e:
        if os.getenv('DEBUG_MODELS'):
            print(f"[DEBUG] Exception in get_model: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(
            f"Failed to initialize {provider.name} {model_type.name} "
            f"model '{name}': {e}"
        ) from e


def get_rate_limiter(
    provider: ModelProvider,
    name: str,
    requests: int,
    input_tokens: int,
    output_tokens: int,
) -> RateLimiter:
    """Get or create a rate limiter for the specified model.

    Args:
        provider: The model provider
        name: The model name
        requests: Maximum number of requests per minute
        input_tokens: Maximum input tokens per minute
        output_tokens: Maximum output tokens per minute

    Returns:
        RateLimiter: Configured rate limiter instance
    """
    key = f"{provider.name}\\{name}"
    if key not in rate_limiters:
        rate_limiters[key] = RateLimiter(
            requests=requests, input_tokens=input_tokens, output_tokens=output_tokens
        )
    limiter = rate_limiters[key]
    limiter.limits["requests"] = requests or 0
    limiter.limits["input"] = input_tokens or 0
    limiter.limits["output"] = output_tokens or 0
    return limiter


def parse_chunk(chunk: Any):
    if isinstance(chunk, str):
        content = chunk
    elif hasattr(chunk, "content"):
        content = str(chunk.content)
    else:
        content = str(chunk)
    return content


# Ollama models
def get_ollama_base_url():
    return (
        dotenv.get_dotenv_value("OLLAMA_BASE_URL")
        or f"http://{runtime.get_local_url()}:11434"
    )


def get_ollama_chat(
    model_name: str,
    base_url=None,
    num_ctx=8192,
    **kwargs,
):
    if not base_url:
        base_url = get_ollama_base_url()
    return ChatOllama(
        model=model_name,
        base_url=base_url,
        num_ctx=num_ctx,
        **kwargs,
    )


def get_ollama_embedding(
    model_name: str,
    base_url=None,
    num_ctx=8192,
    **kwargs,
):
    if not base_url:
        base_url = get_ollama_base_url()
    return OllamaEmbeddings(
        model=model_name, base_url=base_url, num_ctx=num_ctx, **kwargs
    )


# HuggingFace models
def get_huggingface_chat(
    model_name: str,
    api_key=None,
    **kwargs,
):
    # different naming convention here
    if not api_key:
        api_key = get_api_key("huggingface") or os.environ["HUGGINGFACEHUB_API_TOKEN"]

    # Initialize the HuggingFaceEndpoint with the specified model and parameters
    llm = HuggingFaceEndpoint(
        repo_id=model_name,
        task="text-generation",
        do_sample=True,
        huggingfacehub_api_token=api_key,
        **kwargs,
    )

    # Initialize the ChatHuggingFace with the configured llm
    return ChatHuggingFace(llm=llm)


def get_huggingface_embedding(model_name: str, **kwargs):
    return HuggingFaceEmbeddings(model_name=model_name, **kwargs)


# LM Studio and other OpenAI compatible interfaces
def get_lmstudio_base_url():
    return (
        dotenv.get_dotenv_value("LM_STUDIO_BASE_URL")
        or f"http://{runtime.get_local_url()}:1234/v1"
    )


def get_lmstudio_chat(
    model_name: str,
    base_url=None,
    **kwargs,
):
    if not base_url:
        base_url = get_lmstudio_base_url()
    return ChatOpenAI(
        model=model_name, base_url=base_url, api_key=SecretStr("none"), **kwargs
    )


def get_lmstudio_embedding(
    model_name: str,
    base_url=None,
    **kwargs,
):
    if not base_url:
        base_url = get_lmstudio_base_url()
    return OpenAIEmbeddings(
        model=model_name,
        api_key=SecretStr("none"),
        base_url=base_url,
        check_embedding_ctx_length=False,
        **kwargs,
    )


# Anthropic models
def get_anthropic_chat(
    model_name: str,
    api_key=None,
    base_url=None,
    **kwargs,
):
    if not api_key:
        api_key = get_api_key("anthropic")
    if not base_url:
        base_url = (
            dotenv.get_dotenv_value("ANTHROPIC_BASE_URL") or "https://api.anthropic.com"
        )

    # Production hotfix for LangChain Anthropic streaming metadata bug (Issue #26348)
    # Disable stream_usage when LANGCHAIN_ANTHROPIC_STREAM_USAGE is set to false
    stream_usage_disabled = (
        dotenv.get_dotenv_value("LANGCHAIN_ANTHROPIC_STREAM_USAGE", "true").lower()
        == "false"
    )
    if stream_usage_disabled and "stream_usage" not in kwargs:
        kwargs["stream_usage"] = False

    return ChatAnthropic(model=model_name, api_key=api_key, base_url=base_url, **kwargs)


# right now anthropic does not have embedding models, but that might change
def get_anthropic_embedding(
    model_name: str,
    api_key=None,
    **kwargs,
):
    if not api_key:
        api_key = get_api_key("anthropic")
    return OpenAIEmbeddings(model=model_name, api_key=api_key, **kwargs)


# Model name translation layer - maps non-standard names to OpenAI API compatible names
MODEL_NAME_ALIASES = {
    # GPT-4.1 models exist in OpenAI API, so no translation needed
    # "gpt-4.1", "gpt-4.1-mini" should be used as-is
    
    # Only translate nano variant since it doesn't exist
    "gpt-4.1-nano": "gpt-4.1-mini",  # No nano variant exists, use mini
    
    # o3 models (future-proofing)
    "o3": "o1",  # Fallback until o3 is available
    "o3-mini": "o1-mini",
    "o4-mini": "o1-mini",  # Future model fallback
    
    # Legacy aliases
    "gpt-4-turbo-preview": "gpt-4-turbo",
    "gpt-3.5-turbo-instruct": "gpt-3.5-turbo",
}

def translate_model_name(model_name: str) -> tuple[str, bool]:
    """Translate model names to OpenAI API compatible names.
    
    Args:
        model_name: Original model name
        
    Returns:
        Tuple of (translated_name, was_translated)
    """
    original_name = model_name
    translated_name = MODEL_NAME_ALIASES.get(model_name, model_name)
    was_translated = translated_name != original_name
    
    if was_translated and os.getenv('DEBUG_MODELS'):
        print(f"[DEBUG] Model name translation: '{original_name}' -> '{translated_name}'")
    
    return translated_name, was_translated

# OpenAI models
def get_openai_chat(
    model_name: str, api_key: str | None = None, base_url: str | None = None, **kwargs
) -> ChatOpenAI:
    """Get an OpenAI chat model with automatic model name translation."""
    # Translate model name if needed
    translated_name, was_translated = translate_model_name(model_name)
    
    if os.getenv('DEBUG_MODELS'):
        print(f"[DEBUG] get_openai_chat() called with: model_name='{model_name}' (translated: {translated_name}), api_key={'<provided>' if api_key else 'None'}, base_url='{base_url}', kwargs={kwargs}")
    
    final_api_key_for_constructor: str | None = None
    if api_key:  # User provided a string for the function's api_key parameter
        if os.getenv('DEBUG_MODELS'):
            print(f"[DEBUG] Using provided api_key parameter (type: {type(api_key)})")
        # Handle case where api_key might already be a SecretStr
        if isinstance(api_key, SecretStr) or hasattr(api_key, "get_secret_value"):
            final_api_key_for_constructor = api_key.get_secret_value()
            if os.getenv('DEBUG_MODELS'):
                print(f"[DEBUG] Extracted secret value from SecretStr")
        else:
            final_api_key_for_constructor = api_key
            if os.getenv('DEBUG_MODELS'):
                print(f"[DEBUG] Using api_key as-is")
    else:
        if os.getenv('DEBUG_MODELS'):
            print(f"[DEBUG] No api_key provided, retrieving from environment")
        # get_api_key returns str | None, but might return SecretStr from Railway
        v1_secret_key = get_api_key("openai")
        if os.getenv('DEBUG_MODELS'):
            print(f"[DEBUG] get_api_key('openai') returned: {type(v1_secret_key)} - {'<key present>' if v1_secret_key else 'None'}")
        if v1_secret_key:
            # Handle case where Railway provides SecretStr objects
            if isinstance(v1_secret_key, SecretStr) or hasattr(
                v1_secret_key, "get_secret_value"
            ):
                final_api_key_for_constructor = v1_secret_key.get_secret_value()
                if os.getenv('DEBUG_MODELS'):
                    print(f"[DEBUG] Extracted secret value from environment SecretStr")
            else:
                final_api_key_for_constructor = str(v1_secret_key)
                if os.getenv('DEBUG_MODELS'):
                    print(f"[DEBUG] Using environment key as string (length: {len(str(v1_secret_key))})")
        else:
            warning_message = ("No API key found for OpenAI. Please set the appropriate environment variable "
                                "or secret store entry for your deployment (e.g., OPENAI_API_KEY or "
                                "RAILWAY_OPENAI_API_KEY). Check your configuration and try again.")
            print(f"⚠️ WARNING: {warning_message}")
    
    if os.getenv('DEBUG_MODELS'):
        print(f"[DEBUG] Final API key for ChatOpenAI constructor: {'<key present>' if final_api_key_for_constructor else 'None'} (length: {len(final_api_key_for_constructor) if final_api_key_for_constructor else 0})")
    
    try:
        if os.getenv('DEBUG_MODELS'):
            print(f"[DEBUG] Creating ChatOpenAI instance with model='{model_name}', base_url='{base_url}'")
            # Check if we're importing the OpenAI SDK correctly
            from langchain_openai import ChatOpenAI as ChatOpenAIImport
            print(f"[DEBUG] Successfully imported ChatOpenAI: {ChatOpenAIImport}")
        
        model_instance = ChatOpenAI(
            api_key=final_api_key_for_constructor,
            model=translated_name,  # Use translated name for OpenAI API
            base_url=base_url,
            **kwargs,
        )
        if os.getenv('DEBUG_MODELS'):
            print(f"[DEBUG] Successfully created ChatOpenAI instance: {type(model_instance)}")
            print(f"[DEBUG] Model instance has client: {hasattr(model_instance, 'client')}")
            if hasattr(model_instance, 'client'):
                print(f"[DEBUG] Client type: {type(model_instance.client)}")
                if hasattr(model_instance.client, 'base_url'):
                    print(f"[DEBUG] Client base_url: {model_instance.client.base_url}")
        
        return model_instance
        
    except Exception as e:
        if os.getenv('DEBUG_MODELS'):
            print(f"[DEBUG] Exception creating ChatOpenAI: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        error_message = ("Error creating ChatOpenAI instance. Check the model name and API key configuration, "
                          "and ensure that the OpenAI service is accessible and correctly configured.")
        print(f"❌ ERROR: {error_message}")
        raise


def get_openai_embedding(
    model_name: str, api_key: str | None = None, **kwargs
) -> OpenAIEmbeddings:
    """Get an OpenAI embedding model."""
    final_api_key_for_constructor: str | None = None
    if api_key:  # User provided a string for the function's api_key parameter
        # Handle case where api_key might already be a SecretStr
        if isinstance(api_key, SecretStr) or hasattr(api_key, "get_secret_value"):
            final_api_key_for_constructor = api_key.get_secret_value()
        else:
            final_api_key_for_constructor = api_key
    else:
        # get_api_key returns str | None, but might return SecretStr from Railway
        v1_secret_key = get_api_key("openai")
        if v1_secret_key:
            # Handle case where Railway provides SecretStr objects
            if isinstance(v1_secret_key, SecretStr) or hasattr(
                v1_secret_key, "get_secret_value"
            ):
                final_api_key_for_constructor = v1_secret_key.get_secret_value()
            else:
                final_api_key_for_constructor = str(v1_secret_key)
    return OpenAIEmbeddings(
        model=model_name, api_key=final_api_key_for_constructor, **kwargs
    )


def get_openai_azure_chat(
    deployment_name: str,
    api_key: str | None = None,
    azure_endpoint: str | None = None,
    **kwargs,
) -> AzureChatOpenAI:
    """Get an Azure OpenAI chat model."""
    final_api_key_str: str | None = None
    if api_key:  # User provided a string for the function's api_key parameter
        final_api_key_str = api_key
    else:
        # get_api_key returns str | None
        v1_secret_key = get_api_key("openai_azure")
        if v1_secret_key:
            final_api_key_str = v1_secret_key

    if not azure_endpoint:
        azure_endpoint = dotenv.get_dotenv_value("OPENAI_AZURE_ENDPOINT")
    return AzureChatOpenAI(
        azure_deployment=deployment_name,
        api_key=final_api_key_str,
        azure_endpoint=azure_endpoint,
        **kwargs,
    )


def get_openai_azure_embedding(
    deployment_name: str,
    api_key: str | None = None,
    azure_endpoint: str | None = None,
    **kwargs,
) -> AzureOpenAIEmbeddings:
    """Get an Azure OpenAI embedding model."""
    final_api_key_str: str | None = None
    if api_key:  # User provided a string for the function's api_key parameter
        final_api_key_str = api_key
    else:
        # get_api_key returns str | None
        v1_secret_key = get_api_key("openai_azure")
        if v1_secret_key:
            final_api_key_str = v1_secret_key

    if not azure_endpoint:
        azure_endpoint = dotenv.get_dotenv_value("OPENAI_AZURE_ENDPOINT")
    return AzureOpenAIEmbeddings(
        azure_deployment=deployment_name,
        api_key=final_api_key_str,
        azure_endpoint=azure_endpoint,
        **kwargs,
    )


# Google models
def get_google_chat(
    model_name: str,
    api_key=None,
    **kwargs,
):
    final_api_key_for_constructor: SecretStr | None = None
    if api_key:  # User provided a string for the function's api_key parameter
        final_api_key_for_constructor = SecretStr(api_key)
    else:
        v1_secret_key = get_api_key("google")
        if v1_secret_key:
            final_api_key_for_constructor = SecretStr(v1_secret_key)
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=final_api_key_for_constructor,
        safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
        },
        **kwargs,
    )


def get_google_embedding(
    model_name: str,
    api_key=None,
    **kwargs,
):
    final_api_key_for_constructor: SecretStr | None = None
    if api_key:  # User provided a string for the function's api_key parameter
        final_api_key_for_constructor = SecretStr(api_key)
    else:
        v1_secret_key = get_api_key("google")
        if v1_secret_key:
            final_api_key_for_constructor = SecretStr(v1_secret_key)
    return google_embeddings.GoogleGenerativeAIEmbeddings(
        model=model_name,
        google_api_key=final_api_key_for_constructor,
        **kwargs,
    )


# Mistral models
def get_mistralai_chat(
    model_name: str, api_key: str | None = None, **kwargs
) -> ChatMistralAI:
    """Get a MistralAI chat model."""
    final_api_key_for_constructor: SecretStr | None = None
    if api_key:  # User provided a string for the function's api_key parameter
        final_api_key_for_constructor = SecretStr(api_key)
    else:
        v1_secret_key = get_api_key("mistral")
        if v1_secret_key:
            final_api_key_for_constructor = SecretStr(v1_secret_key)
    return ChatMistralAI(
        model_name=model_name, api_key=final_api_key_for_constructor, **kwargs
    )


# Groq models
def get_groq_chat(model_name: str, api_key: str | None = None, **kwargs) -> ChatGroq:
    """Get a Groq chat model."""
    final_api_key_for_constructor: SecretStr | None = None
    if api_key:  # User provided a string for the function's api_key parameter
        final_api_key_for_constructor = SecretStr(api_key)
    else:
        # get_api_key returns str | None
        v1_secret_key = get_api_key("groq")
        if v1_secret_key:
            final_api_key_for_constructor = SecretStr(v1_secret_key)

    # Extract string value from SecretStr for ChatGroq constructor
    if final_api_key_for_constructor is not None:
        if hasattr(final_api_key_for_constructor, 'get_secret_value'):
            api_key_string = final_api_key_for_constructor.get_secret_value()
        else:
            api_key_string = str(final_api_key_for_constructor)
    else:
        api_key_string = None
    model = ChatGroq(model=model_name, api_key=api_key_string, **kwargs)
    return model


# DeepSeek models
def get_deepseek_chat(
    model_name: str, api_key: str | None = None, base_url: str | None = None, **kwargs
) -> ChatOpenAI:
    """Get a DeepSeek chat model."""
    final_api_key_for_constructor: str | None = None
    if isinstance(
        api_key, str
    ):  # User provided a string for the function's api_key parameter
        final_api_key_for_constructor = api_key
    elif isinstance(api_key, SecretStr):  # User provided SecretStr
        final_api_key_for_constructor = api_key.get_secret_value()
    elif hasattr(api_key, "get_secret_value"):  # User provided object with get_secret_value
        final_api_key_for_constructor = api_key.get_secret_value()  # type: ignore
    elif (
        api_key is None
    ):  # api_key was not provided to the function, try to get from env
        v1_secret_key = get_api_key("deepseek")
        if v1_secret_key:
            # Handle case where Railway provides SecretStr objects
            if isinstance(v1_secret_key, SecretStr) or hasattr(
                v1_secret_key, "get_secret_value"
            ):
                final_api_key_for_constructor = v1_secret_key.get_secret_value()
            else:
                final_api_key_for_constructor = str(v1_secret_key)

    if not base_url:
        base_url = (
            dotenv.get_dotenv_value("DEEPSEEK_BASE_URL") or "https://api.deepseek.com"
        )
    return ChatOpenAI(
        api_key=final_api_key_for_constructor,
        model=model_name,
        base_url=base_url,
        **kwargs,
    )


# OpenRouter models
def get_openrouter_chat(
    model_name: str, api_key: str | None = None, base_url: str | None = None, **kwargs
) -> ChatOpenAI:
    """Get an OpenRouter chat model."""
    final_api_key_for_constructor: SecretStr | None = None
    if isinstance(
        api_key, str
    ):  # User provided a string for the function's api_key parameter
        final_api_key_for_constructor = SecretStr(api_key)
    elif (
        api_key is None
    ):  # api_key was not provided to the function, try to get from env
        v1_secret_key = get_api_key("openrouter")
        if v1_secret_key:
            final_api_key_for_constructor = SecretStr(v1_secret_key)
    elif hasattr(api_key, "get_secret_value"):
        final_api_key_for_constructor = SecretStr(api_key.get_secret_value())

    if not base_url:
        base_url = (
            dotenv.get_dotenv_value("OPEN_ROUTER_BASE_URL")
            or "https://openrouter.ai/api/v1"
        )
    return ChatOpenAI(
        api_key=final_api_key_for_constructor,
        model=model_name,
        base_url=base_url,
        **kwargs,
    )


def get_openrouter_embedding(
    model_name: str,
    api_key=None,
    base_url=None,
    **kwargs,
):
    final_api_key_for_constructor: SecretStr | None = None
    if isinstance(
        api_key, str
    ):  # User provided a string for the function's api_key parameter
        final_api_key_for_constructor = SecretStr(api_key)
    elif (
        api_key is None
    ):  # api_key was not provided to the function, try to get from env
        v1_secret_key = get_api_key("openrouter")
        if v1_secret_key:
            final_api_key_for_constructor = SecretStr(v1_secret_key)
    elif hasattr(api_key, "get_secret_value"):
        final_api_key_for_constructor = SecretStr(api_key.get_secret_value())

    if not base_url:
        base_url = (
            dotenv.get_dotenv_value("OPEN_ROUTER_BASE_URL")
            or "https://openrouter.ai/api/v1"
        )
    return OpenAIEmbeddings(
        model=model_name,
        api_key=final_api_key_for_constructor,
        base_url=base_url,
        **kwargs,
    )


# Sambanova models
def get_sambanova_chat(
    model_name: str, api_key: str | None = None, base_url: str | None = None, **kwargs
) -> ChatOpenAI:
    """Get a Sambanova chat model."""
    final_api_key_for_constructor: SecretStr | None = None
    if isinstance(api_key, str):
        final_api_key_for_constructor = SecretStr(api_key)
    elif api_key is None:
        v1_secret_key = get_api_key("sambanova")
        if v1_secret_key:
            final_api_key_for_constructor = SecretStr(v1_secret_key)
    elif hasattr(api_key, "get_secret_value") and callable(api_key.get_secret_value):
        final_api_key_for_constructor = SecretStr(api_key.get_secret_value())  # type: ignore

    if not base_url:
        base_url = (
            dotenv.get_dotenv_value("SAMBANOVA_BASE_URL")
            or "https://fast-api.snova.ai/v1"
        )
    return ChatOpenAI(
        api_key=final_api_key_for_constructor,
        model=model_name,
        base_url=base_url,
        **kwargs,
    )


# right now sambanova does not have embedding models, but that might change
def get_sambanova_embedding(
    model_name: str,
    api_key: str | None = None,
    base_url: str | None = None,
    **kwargs,
) -> OpenAIEmbeddings:
    final_api_key_for_constructor: SecretStr | None = None
    if isinstance(api_key, str):
        final_api_key_for_constructor = SecretStr(api_key)
    elif api_key is None:
        v1_secret_key = get_api_key("sambanova")
        if v1_secret_key:
            final_api_key_for_constructor = SecretStr(v1_secret_key)
    elif hasattr(api_key, "get_secret_value") and callable(api_key.get_secret_value):
        final_api_key_for_constructor = SecretStr(api_key.get_secret_value())  # type: ignore

    if not base_url:
        base_url = (
            dotenv.get_dotenv_value("SAMBANOVA_BASE_URL")
            or "https://fast-api.snova.ai/v1"
        )
    return OpenAIEmbeddings(
        model=model_name,
        api_key=final_api_key_for_constructor,
        base_url=base_url,
        **kwargs,
    )


# Qwen models
def get_qwen_chat(
    model_name: str, api_key: str | None = None, base_url: str | None = None, **kwargs
) -> ChatOpenAI:
    """Get a Qwen chat model."""
    final_api_key_for_constructor: SecretStr | None = None
    if isinstance(api_key, str):
        final_api_key_for_constructor = SecretStr(api_key)
    elif api_key is None:
        v1_secret_key = get_api_key("qwen")
        if v1_secret_key:
            final_api_key_for_constructor = SecretStr(v1_secret_key)
    elif hasattr(api_key, "get_secret_value") and callable(api_key.get_secret_value):
        final_api_key_for_constructor = SecretStr(api_key.get_secret_value())

    if not base_url:
        base_url = (
            dotenv.get_dotenv_value("QWEN_BASE_URL")
            or "https://dashscope.aliyuncs.com/api/v1"
        )
    return ChatOpenAI(
        api_key=final_api_key_for_constructor,
        model=model_name,
        base_url=base_url,
        **kwargs,
    )


def get_qwen_embedding(
    model_name: str, api_key: str | None = None, base_url: str | None = None, **kwargs
) -> OpenAIEmbeddings:
    """Get a Qwen embedding model."""
    final_api_key_for_constructor: SecretStr | None = None
    if isinstance(api_key, str):
        final_api_key_for_constructor = SecretStr(api_key)
    elif api_key is None:
        v1_secret_key = get_api_key("qwen")
        if v1_secret_key:
            final_api_key_for_constructor = SecretStr(v1_secret_key)
    elif hasattr(api_key, "get_secret_value") and callable(api_key.get_secret_value):
        final_api_key_for_constructor = SecretStr(api_key.get_secret_value())

    if not base_url:
        base_url = (
            dotenv.get_dotenv_value("QWEN_BASE_URL")
            or "https://dashscope.aliyuncs.com/api/v1"
        )
    return OpenAIEmbeddings(
        model=model_name,
        api_key=final_api_key_for_constructor,
        base_url=base_url,
        **kwargs,
    )


# xAI models (Grok)
def get_xai_chat(
    model_name: str, api_key: str | None = None, base_url: str | None = None, **kwargs
) -> ChatOpenAI:
    """Get an xAI (Grok) chat model."""
    final_api_key_for_constructor: SecretStr | None = None
    if isinstance(api_key, str):
        final_api_key_for_constructor = SecretStr(api_key)
    elif api_key is None:
        v1_secret_key = get_api_key("xai") or get_api_key("grok")
        if v1_secret_key:
            final_api_key_for_constructor = SecretStr(v1_secret_key)
    elif hasattr(api_key, "get_secret_value") and callable(api_key.get_secret_value):
        final_api_key_for_constructor = SecretStr(api_key.get_secret_value())  # type: ignore

    if not base_url:
        base_url = dotenv.get_dotenv_value("XAI_BASE_URL") or "https://api.x.ai/v1"
    return ChatOpenAI(
        api_key=final_api_key_for_constructor,
        model=model_name,
        base_url=base_url,
        **kwargs,
    )


def get_xai_embedding(
    model_name: str, api_key: str | None = None, base_url: str | None = None, **kwargs
) -> OpenAIEmbeddings:
    """Get an xAI embedding model."""
    final_api_key_for_constructor: SecretStr | None = None
    if isinstance(api_key, str):
        final_api_key_for_constructor = SecretStr(api_key)
    elif api_key is None:
        v1_secret_key = get_api_key("xai") or get_api_key("grok")
        if v1_secret_key:
            final_api_key_for_constructor = SecretStr(v1_secret_key)
    elif hasattr(api_key, "get_secret_value") and callable(api_key.get_secret_value):
        final_api_key_for_constructor = SecretStr(api_key.get_secret_value())  # type: ignore

    if not base_url:
        base_url = dotenv.get_dotenv_value("XAI_BASE_URL") or "https://api.x.ai/v1"
    return OpenAIEmbeddings(
        model=model_name,
        api_key=final_api_key_for_constructor,
        base_url=base_url,
        **kwargs,
    )


# Meta models (handled through existing providers like Groq, but we add for consistency)
def get_meta_chat(
    model_name: str, api_key: str | None = None, base_url: str | None = None, **kwargs
) -> ChatOpenAI:
    """Get a Meta chat model."""
    final_api_key_for_constructor: SecretStr | None = None
    if isinstance(api_key, str):
        final_api_key_for_constructor = SecretStr(api_key)
    elif api_key is None:
        v1_secret_key = get_api_key("meta")
        if v1_secret_key:
            final_api_key_for_constructor = SecretStr(v1_secret_key)
    elif hasattr(api_key, "get_secret_value") and callable(api_key.get_secret_value):
        final_api_key_for_constructor = SecretStr(api_key.get_secret_value())  # type: ignore

    if not base_url:
        base_url = dotenv.get_dotenv_value("META_BASE_URL") or "https://api.meta.ai/v1"
    return ChatOpenAI(
        api_key=final_api_key_for_constructor,
        model=model_name,
        base_url=base_url,
        **kwargs,
    )


def get_meta_embedding(
    model_name: str, api_key: str | None = None, base_url: str | None = None, **kwargs
) -> OpenAIEmbeddings:
    """Get a Meta embedding model."""
    final_api_key_for_constructor: SecretStr | None = None
    if isinstance(api_key, str):
        final_api_key_for_constructor = SecretStr(api_key)
    elif api_key is None:
        v1_secret_key = get_api_key("meta")
        if v1_secret_key:
            final_api_key_for_constructor = SecretStr(v1_secret_key)
    elif hasattr(api_key, "get_secret_value") and callable(api_key.get_secret_value):
        final_api_key_for_constructor = SecretStr(api_key.get_secret_value())  # type: ignore

    if not base_url:
        base_url = dotenv.get_dotenv_value("META_BASE_URL") or "https://api.meta.ai/v1"
    return OpenAIEmbeddings(
        model=model_name,
        api_key=final_api_key_for_constructor,
        base_url=base_url,
        **kwargs,
    )
