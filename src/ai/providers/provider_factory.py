"""
AI Provider Factory
Manages the creation and selection of AI providers
"""

from typing import Dict, Optional, Type
from enum import Enum

from .base_provider import BaseAIProvider
from .claude_provider import ClaudeProvider
from .gemini_provider import GeminiProvider
from .gpt_provider import GPTProvider
from utils.logger import setup_logger


class AIProviderType(Enum):
    """Available AI provider types"""
    CLAUDE = "claude"
    GEMINI = "gemini"
    GPT = "gpt"


class AIProviderFactory:
    """Factory for creating AI providers"""
    
    # Registry of available providers
    _providers: Dict[AIProviderType, Type[BaseAIProvider]] = {
        AIProviderType.CLAUDE: ClaudeProvider,
        AIProviderType.GEMINI: GeminiProvider,
        AIProviderType.GPT: GPTProvider
    }
    
    def __init__(self):
        """Initialize the factory"""
        self.logger = setup_logger(self.__class__.__name__)
        
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
        if provider_type not in cls._providers:
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
        availability = cls.get_available_providers()
        
        # Priority order: Claude > GPT > Gemini
        if availability.get('claude'):
            return AIProviderType.CLAUDE
        elif availability.get('gpt'):
            return AIProviderType.GPT
        elif availability.get('gemini'):
            return AIProviderType.GEMINI
        else:
            return None