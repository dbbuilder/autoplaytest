"""
Unit tests for AI Provider Factory
Following TDD principles
"""

import pytest
import os
from unittest.mock import patch, Mock

from ai.providers.provider_factory import AIProviderFactory, AIProviderType
from ai.providers.claude_provider import ClaudeProvider
from ai.providers.gemini_provider import GeminiProvider
from ai.providers.gpt_provider import GPTProvider


class TestAIProviderFactory:
    """Test AI Provider Factory"""
    
    def test_create_claude_provider(self, mock_env_vars):
        """Test creating Claude provider"""
        with patch('ai.providers.claude_provider.AsyncAnthropic'):
            provider = AIProviderFactory.create_provider(AIProviderType.CLAUDE)
            assert isinstance(provider, ClaudeProvider)
    
    def test_create_gemini_provider(self, mock_env_vars):
        """Test creating Gemini provider"""
        with patch('ai.providers.gemini_provider.genai'):
            provider = AIProviderFactory.create_provider(AIProviderType.GEMINI)
            assert isinstance(provider, GeminiProvider)
    
    def test_create_gpt_provider(self, mock_env_vars):
        """Test creating GPT provider"""
        with patch('ai.providers.gpt_provider.AsyncOpenAI'):
            provider = AIProviderFactory.create_provider(AIProviderType.GPT)
            assert isinstance(provider, GPTProvider)
    
    def test_create_invalid_provider(self):
        """Test creating provider with invalid type"""
        with pytest.raises(ValueError):
            AIProviderFactory.create_provider("invalid_provider")
    
    def test_get_available_providers_all_configured(self, mock_env_vars):
        """Test checking available providers when all are configured"""
        availability = AIProviderFactory.get_available_providers()
        
        assert availability['claude'] is True
        assert availability['gemini'] is True
        assert availability['gpt'] is True
    
    def test_get_available_providers_none_configured(self):
        """Test checking available providers when none are configured"""
        with patch.dict(os.environ, {}, clear=True):
            availability = AIProviderFactory.get_available_providers()
            
            assert availability['claude'] is False
            assert availability['gemini'] is False
            assert availability['gpt'] is False
    
    def test_get_available_providers_partial_configured(self):
        """Test checking available providers with partial configuration"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}, clear=True):
            availability = AIProviderFactory.get_available_providers()
            
            assert availability['claude'] is False
            assert availability['gemini'] is False
            assert availability['gpt'] is True
    
    def test_get_default_provider_claude_priority(self, mock_env_vars):
        """Test default provider selection with Claude priority"""
        default = AIProviderFactory.get_default_provider()
        assert default == AIProviderType.CLAUDE
    
    def test_get_default_provider_gpt_fallback(self):
        """Test default provider falls back to GPT when Claude unavailable"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}, clear=True):
            default = AIProviderFactory.get_default_provider()
            assert default == AIProviderType.GPT
    
    def test_get_default_provider_gemini_last_resort(self):
        """Test default provider falls back to Gemini as last option"""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test-key'}, clear=True):
            default = AIProviderFactory.get_default_provider()
            assert default == AIProviderType.GEMINI
    
    def test_get_default_provider_none_available(self):
        """Test default provider returns None when none available"""
        with patch.dict(os.environ, {}, clear=True):
            default = AIProviderFactory.get_default_provider()
            assert default is None
    
    def test_create_provider_with_custom_config(self, mock_env_vars, tmp_path):
        """Test creating provider with custom configuration"""
        # Create custom config file
        config_file = tmp_path / "custom_config.yaml"
        config_file.write_text("test: config")
        
        with patch('ai.providers.claude_provider.AsyncAnthropic'):
            provider = AIProviderFactory.create_provider(
                AIProviderType.CLAUDE,
                str(config_file)
            )
            assert isinstance(provider, ClaudeProvider)