# AI Provider Package
"""AI providers for test generation - Claude, Gemini, and GPT"""

from .base_provider import BaseAIProvider, TestType, PageAnalysis, GeneratedTest

# Import providers with error handling
_available_providers = {}

try:
    from .claude_provider import ClaudeProvider
    _available_providers['claude'] = ClaudeProvider
except ImportError as e:
    ClaudeProvider = None
    if "anthropic" in str(e):
        print("⚠️  Claude provider not available: anthropic package not installed")

try:
    from .gemini_provider import GeminiProvider
    _available_providers['gemini'] = GeminiProvider
except ImportError as e:
    GeminiProvider = None
    if "google-generativeai" in str(e):
        print("⚠️  Gemini provider not available: google-generativeai package not installed")

try:
    from .gpt_provider import GPTProvider
    _available_providers['gpt'] = GPTProvider
except ImportError as e:
    GPTProvider = None
    if "openai" in str(e):
        print("⚠️  GPT provider not available: openai package not installed")

from .provider_factory import AIProviderFactory, AIProviderType

__all__ = [
    'BaseAIProvider',
    'ClaudeProvider',
    'GeminiProvider',
    'GPTProvider',
    'AIProviderFactory',
    'AIProviderType',
    'TestType',
    'PageAnalysis',
    'GeneratedTest',
    '_available_providers'
]