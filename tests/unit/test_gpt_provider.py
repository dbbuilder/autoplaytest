"""
Unit tests for GPT AI Provider
Following TDD principles
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch

from ai.providers.gpt_provider import GPTProvider
from ai.providers.base_provider import TestType, PageAnalysis, TestGenerationRequest


class TestGPTProvider:
    """Test GPT AI Provider implementation"""
    
    @pytest.mark.asyncio
    @patch('ai.providers.gpt_provider.AsyncOpenAI')
    async def test_provider_initialization(self, mock_openai_class, mock_env_vars):
        """Test GPT provider initialization"""
        # Initialize provider
        provider = GPTProvider()
        
        # Verify OpenAI client was created with API key
        mock_openai_class.assert_called_once_with(api_key='test-gpt-key')
        assert provider.model == 'gpt-4-turbo-preview'
    
    @pytest.mark.asyncio
    @patch('ai.providers.gpt_provider.AsyncOpenAI')
    async def test_analyze_page_with_json_mode(self, mock_openai_class, mock_env_vars):
        """Test page analysis with JSON response format"""
        # Setup mock
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content=json.dumps({
                            "page_info": {
                                "title": "Dashboard",
                                "type": "dashboard"
                            },
                            "elements": [],
                            "forms": [],
                            "navigation": ["/home", "/profile"],
                            "api_endpoints": ["/api/data"],
                            "has_authentication": True
                        })
                    )
                )
            ]
        )
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        provider = GPTProvider()
        
        # Analyze page
        analysis = await provider.analyze_page("<html>Dashboard</html>", "https://example.com/dashboard")
        
        # Verify API call
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['model'] == 'gpt-4-turbo-preview'
        assert call_args[1]['response_format'] == {"type": "json_object"}
        
        # Verify analysis
        assert analysis.title == "Dashboard"
        assert analysis.page_type == "dashboard"
        assert analysis.has_authentication is True
    
    @pytest.mark.asyncio
    @patch('ai.providers.gpt_provider.AsyncOpenAI')
    async def test_generate_test_with_code_extraction(self, mock_openai_class, mock_env_vars, mock_openai_response):
        """Test test generation with code extraction"""
        # Setup mock
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)
        
        provider = GPTProvider()
        
        # Create request
        analysis = PageAnalysis(
            url="https://example.com/login",
            title="Login",
            page_type="login",
            elements=[],
            forms=[],
            navigation_links=[],
            api_endpoints=[],
            has_authentication=True,
            user_flows=[],
            test_scenarios=[]
        )
        
        request = TestGenerationRequest(
            page_analysis=analysis,
            test_type=TestType.LOGIN,
            context={"timeout": 30000}
        )
        
        # Generate test
        generated_test = await provider.generate_test(request)
        
        # Verify results
        assert generated_test.test_type == TestType.LOGIN
        assert "test_login_flow" in generated_test.code
        assert "await page.goto" in generated_test.code
        assert generated_test.file_name.endswith(".py")
    
    @pytest.mark.asyncio
    @patch('ai.providers.gpt_provider.AsyncOpenAI')
    async def test_validate_test_with_json_response(self, mock_openai_class, mock_env_vars):
        """Test validation with structured JSON response"""
        # Setup mock
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content=json.dumps({
                            "is_valid": True,
                            "issues": [],
                            "suggestions": ["Add timeout handling", "Include error scenarios"]
                        })
                    )
                )
            ]
        )
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        provider = GPTProvider()
        
        # Validate test
        is_valid, issues = await provider.validate_test("async def test(): pass")
        
        # Verify validation call
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs['temperature'] == 0.1
        assert call_args.kwargs['response_format'] == {"type": "json_object"}
        
        # Verify results
        assert is_valid is True
        assert len(issues) == 0
    
    def test_extract_code_blocks(self, mock_env_vars):
        """Test code block extraction from GPT responses"""
        with patch('ai.providers.gpt_provider.AsyncOpenAI'):
            provider = GPTProvider()
        
        # Test with labeled code blocks
        text = '''
        Here's the test code:
        ```python # test
        async def test_example():
            pass
        ```
        
        And here's the page object:
        ```python # page_object
        class LoginPage:
            pass
        ```
        '''
        
        blocks = provider._extract_code_blocks(text)
        
        assert 'test' in blocks
        assert 'page_object' in blocks
        assert 'async def test_example()' in blocks['test']
        assert 'class LoginPage:' in blocks['page_object']
    
    @pytest.mark.asyncio
    @patch('ai.providers.gpt_provider.AsyncOpenAI')
    async def test_error_handling(self, mock_openai_class, mock_env_vars):
        """Test error handling in GPT provider"""
        # Setup mock to raise exception
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        
        provider = GPTProvider()
        
        # Should handle error gracefully
        analysis = await provider.analyze_page("content", "https://example.com")
        
        assert analysis.page_type == "unknown"
        assert len(analysis.elements) == 0