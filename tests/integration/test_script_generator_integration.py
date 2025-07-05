"""
Integration tests for AI Script Generator
Tests the complete flow of script generation
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from core.script_generator.ai_script_generator import AIScriptGenerator
from ai.providers.base_provider import TestType, GeneratedTest


class TestAIScriptGeneratorIntegration:
    """Integration tests for AI Script Generator"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @patch('core.script_generator.ai_script_generator.async_playwright')
    @patch('ai.providers.claude_provider.AsyncAnthropic')
    async def test_analyze_and_generate_complete_flow(
        self,
        mock_anthropic,
        mock_playwright,
        mock_env_vars,
        mock_claude_response
    ):
        """Test complete analyze and generate flow"""
        # Setup Playwright mock
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_context = AsyncMock()
        
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        
        # Setup page mock responses
        mock_page.url = "https://example.com/login"
        mock_page.title = AsyncMock(return_value="Login Page")
        mock_page.content = AsyncMock(return_value="<html>Login form</html>")
        mock_page.viewport_size = {"width": 1920, "height": 1080}
        mock_page.locator = Mock(return_value=AsyncMock(count=AsyncMock(return_value=2)))
        mock_page.evaluate = AsyncMock(return_value={})
        
        # Setup Claude mock
        mock_client = AsyncMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create = AsyncMock(return_value=mock_claude_response)
        
        # Create generator
        generator = AIScriptGenerator("claude")
        
        # Run analysis and generation
        results = await generator.analyze_and_generate(
            url="https://example.com/login",
            username="testuser",
            password="testpass",
            test_types=["login", "navigation"]
        )
        
        # Verify results
        assert results['url'] == "https://example.com/login"
        assert results['provider'] == "claude"
        assert 'page_analysis' in results
        assert 'generated_tests' in results
        assert len(results['generated_tests']) > 0
        
        # Verify browser was properly closed
        mock_browser.close.assert_called_once()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_provider_fallback(self):
        """Test fallback to available provider"""
        # Only set GPT API key
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}, clear=True):
            with patch('ai.providers.gpt_provider.AsyncOpenAI'):
                generator = AIScriptGenerator()  # No provider specified
                assert generator.provider_type.value == "gpt"
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_no_providers_available(self):
        """Test error when no providers are available"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="No AI providers available"):
                AIScriptGenerator()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @patch('core.script_generator.ai_script_generator.async_playwright')
    async def test_screenshot_capture(self, mock_playwright, mock_env_vars):
        """Test screenshot capture during analysis"""
        # Setup mocks
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock()
        mock_browser.new_context.return_value.new_page = AsyncMock(return_value=mock_page)
        
        # Mock page methods
        mock_page.goto = AsyncMock()
        mock_page.screenshot = AsyncMock()
        mock_page.title = AsyncMock(return_value="Test Page")
        
        with patch('ai.providers.claude_provider.AsyncAnthropic'):
            generator = AIScriptGenerator("claude")
            
            # Analyze page
            analysis = await generator._analyze_page_with_playwright(
                "https://example.com",
                "chromium"
            )
            
            # Verify screenshot was taken
            mock_page.screenshot.assert_called_once()
            screenshot_path = mock_page.screenshot.call_args[1]['path']
            assert 'screenshots' in screenshot_path
            assert screenshot_path.endswith('.png')