"""
AI Provider Factory
Manages the creation and selection of AI providers
"""

from typing import Dict, Optional, Type
from enum import Enum

from .base_provider import BaseAIProvider
from utils.logger import setup_logger


class AIProviderType(Enum):
    """Available AI provider types"""
    CLAUDE = "claude"
    GEMINI = "gemini"
    GPT = "gpt"


class AIProviderFactory:
    """Factory for creating AI providers"""
    
    # Registry of available providers (lazy loaded)
    _providers: Dict[AIProviderType, Type[BaseAIProvider]] = None
    
    def __init__(self):
        """Initialize the factory"""
        self.logger = setup_logger(self.__class__.__name__)
        
    @classmethod
    def _load_providers(cls):
        """Lazy load provider classes"""
        if cls._providers is None:
            cls._providers = {}
            
            # Try to load each provider
            try:
                from .claude_provider import ClaudeProvider
                cls._providers[AIProviderType.CLAUDE] = ClaudeProvider
            except ImportError:
                pass
                
            try:
                from .gemini_provider import GeminiProvider
                cls._providers[AIProviderType.GEMINI] = GeminiProvider
            except ImportError:
                pass
                
            try:
                from .gpt_provider import GPTProvider
                cls._providers[AIProviderType.GPT] = GPTProvider
            except ImportError:
                pass
    
    @classmethod
    def create_provider(
        cls, 
        provider_type: AIProviderType,
        config_path: Optional[str] = None
    ) -> BaseAIProvider:
        """
        Create an AI provider instance
        
        Args:
            provider_type: Type of AI provider to create
            config_path: Optional path to configuration file
            
        Returns:
            Configured AI provider instance
        """
        cls._load_providers()
        
        if provider_type not in cls._providers:
            # Try to give helpful error message
            provider_name = provider_type.value
            if provider_name == 'claude':
                raise ValueError(f"Claude provider not available. Install with: pip install anthropic")
            elif provider_name == 'gemini':
                raise ValueError(f"Gemini provider not available. Install with: pip install google-generativeai")
            elif provider_name == 'gpt':
                raise ValueError(f"GPT provider not available. Install with: pip install openai")
            else:
                raise ValueError(f"Unknown provider type: {provider_type}")
        
        provider_class = cls._providers[provider_type]
        return provider_class(config_path)
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, bool]:
        """
        Check which providers are available (have API keys configured)
        
        Returns:
            Dictionary of provider names and their availability
        """
        import os
        
        availability = {}
        
        # Check Claude
        availability['claude'] = bool(os.getenv('ANTHROPIC_API_KEY'))
        
        # Check Gemini
        availability['gemini'] = bool(os.getenv('GOOGLE_API_KEY'))
        
        # Check GPT
        availability['gpt'] = bool(os.getenv('OPENAI_API_KEY'))
        
        return availability
    
    @classmethod
    def get_default_provider(cls) -> Optional[AIProviderType]:
        """
        Get the default provider based on availability
        
        Returns:
            Default provider type or None if none available
        """
        # Load providers first
        cls._load_providers()
        
        availability = cls.get_available_providers()
        
        # Priority order: Claude > GPT > Gemini
        # But also check if the provider is actually loaded
        if availability.get('claude') and AIProviderType.CLAUDE in cls._providers:
            return AIProviderType.CLAUDE
        elif availability.get('gpt') and AIProviderType.GPT in cls._providers:
            return AIProviderType.GPT
        elif availability.get('gemini') and AIProviderType.GEMINI in cls._providers:
            return AIProviderType.GEMINI
        else:
            return None