"""
Unit tests for Claude AI Provider
Following TDD principles
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch

from ai.providers.claude_provider import ClaudeProvider
from ai.providers.base_provider import TestType, PageAnalysis, TestGenerationRequest


class TestClaudeProvider:
    """Test Claude AI Provider implementation"""
    
    @pytest.mark.asyncio
    @patch('ai.providers.claude_provider.AsyncAnthropic')
    async def test_provider_initialization(self, mock_anthropic_class, mock_env_vars):
        """Test Claude provider initialization"""
        # Initialize provider
        provider = ClaudeProvider()
        
        # Verify Anthropic client was created with API key
        mock_anthropic_class.assert_called_once_with(api_key='test-claude-key')
        assert provider.model == 'claude-3-opus-20240229'
    
    @pytest.mark.asyncio
    @patch('ai.providers.claude_provider.AsyncAnthropic')
    async def test_analyze_page_success(self, mock_anthropic_class, mock_env_vars, mock_claude_response):
        """Test successful page analysis with Claude"""
        # Setup mock
        mock_client = AsyncMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create = AsyncMock(return_value=mock_claude_response)
        
        provider = ClaudeProvider()
        
        # Analyze page
        page_content = "<html><body>Test page</body></html>"
        url = "https://example.com/login"
        
        analysis = await provider.analyze_page(page_content, url)
        
        # Verify API was called correctly
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args
        assert call_args[1]['model'] == 'claude-3-opus-20240229'
        assert call_args[1]['max_tokens'] == 4096
        assert call_args[1]['temperature'] == 0.2
        
        # Verify analysis results
        assert isinstance(analysis, PageAnalysis)
        assert analysis.url == url
        assert analysis.title == "Login Page"
        assert analysis.page_type == "login"
        assert analysis.has_authentication is True
    
    @pytest.mark.asyncio
    @patch('ai.providers.claude_provider.AsyncAnthropic')
    async def test_analyze_page_error_handling(self, mock_anthropic_class, mock_env_vars):
        """Test page analysis error handling"""
        # Setup mock to raise error
        mock_client = AsyncMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create = AsyncMock(side_effect=Exception("API Error"))
        
        provider = ClaudeProvider()
        
        # Should return basic analysis on error
        analysis = await provider.analyze_page("content", "https://example.com")
        
        assert analysis.url == "https://example.com"
        assert analysis.title == "Unknown"
        assert analysis.page_type == "unknown"
        assert len(analysis.elements) == 0
    
    @pytest.mark.asyncio
    @patch('ai.providers.claude_provider.AsyncAnthropic')
    async def test_generate_test_success(self, mock_anthropic_class, mock_env_vars, mock_claude_response):
        """Test successful test generation"""
        # Setup mock
        mock_client = AsyncMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create = AsyncMock(return_value=mock_claude_response)
        
        provider = ClaudeProvider()
        
        # Create test request
        analysis = PageAnalysis(
            url="https://example.com/login",
            title="Login Page",
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
            test_type=TestType.LOGIN
        )
        
        # Generate test
        generated_test = await provider.generate_test(request)
        
        # Verify results
        assert generated_test.test_type == TestType.LOGIN
        assert generated_test.file_name.startswith("test_login_")
        assert "test_login_with_valid_credentials" in generated_test.code
        assert "playwright" in generated_test.dependencies
    
    @pytest.mark.asyncio
    @patch('ai.providers.claude_provider.AsyncAnthropic')
    async def test_validate_test_success(self, mock_anthropic_class, mock_env_vars):
        """Test successful test validation"""
        # Setup mock
        mock_client = AsyncMock()
        mock_anthropic_class.return_value = mock_client
        
        validation_response = Mock(content=[Mock(text='''
        {
            "is_valid": true,
            "issues": [],
            "suggestions": ["Consider adding more assertions"]
        }
        ''')])
        
        mock_client.messages.create = AsyncMock(return_value=validation_response)
        
        provider = ClaudeProvider()
        
        # Validate test code
        test_code = "async def test_example(): pass"
        is_valid, issues = await provider.validate_test(test_code)
        
        assert is_valid is True
        assert len(issues) == 0
    
    @pytest.mark.asyncio
    @patch('ai.providers.claude_provider.AsyncAnthropic')
    async def test_validate_test_with_issues(self, mock_anthropic_class, mock_env_vars):
        """Test validation with issues found"""
        # Setup mock
        mock_client = AsyncMock()
        mock_anthropic_class.return_value = mock_client
        
        validation_response = Mock(content=[Mock(text='''
        {
            "is_valid": false,
            "issues": ["Missing await keyword", "Invalid selector"],
            "suggestions": []
        }
        ''')])
        
        mock_client.messages.create = AsyncMock(return_value=validation_response)
        
        provider = ClaudeProvider()
        
        # Validate test code
        is_valid, issues = await provider.validate_test("def test(): pass")
        
        assert is_valid is False
        assert len(issues) == 2
        assert "Missing await keyword" in issues