"""
Unit tests for Base AI Provider
Following TDD principles - tests written first
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from ai.providers.base_provider import (
    BaseAIProvider, TestType, PageElement, PageAnalysis,
    TestGenerationRequest, GeneratedTest
)


class TestPageElement:
    """Test PageElement dataclass"""
    
    def test_page_element_creation(self):
        """Test creating a PageElement"""
        element = PageElement(
            selector="#test",
            element_type="button",
            text="Click me",
            attributes={"id": "test", "class": "btn"},
            is_interactive=True
        )
        
        assert element.selector == "#test"
        assert element.element_type == "button"
        assert element.text == "Click me"
        assert element.attributes["id"] == "test"
        assert element.is_interactive is True
    
    def test_page_element_to_dict(self):
        """Test converting PageElement to dictionary"""
        element = PageElement(
            selector="#test",
            element_type="input"
        )
        
        element_dict = element.to_dict()
        assert isinstance(element_dict, dict)
        assert element_dict["selector"] == "#test"
        assert element_dict["element_type"] == "input"
        assert element_dict["text"] is None
        assert element_dict["is_interactive"] is False


class TestPageAnalysis:
    """Test PageAnalysis dataclass"""
    
    def test_page_analysis_creation(self):
        """Test creating PageAnalysis object"""
        elements = [
            PageElement(selector="#btn1", element_type="button"),
            PageElement(selector="#input1", element_type="input")
        ]
        
        analysis = PageAnalysis(
            url="https://example.com",
            title="Test Page",
            page_type="form",
            elements=elements,
            forms=[{"action": "/submit", "method": "post"}],
            navigation_links=["/home", "/about"],
            api_endpoints=["/api/data"],
            has_authentication=True,
            user_flows=[],
            test_scenarios=[]
        )
        
        assert analysis.url == "https://example.com"
        assert analysis.title == "Test Page"
        assert analysis.page_type == "form"
        assert len(analysis.elements) == 2
        assert analysis.has_authentication is True
    
    def test_page_analysis_to_dict(self):
        """Test converting PageAnalysis to dictionary"""
        analysis = PageAnalysis(
            url="https://example.com",
            title="Test",
            page_type="login",
            elements=[PageElement(selector="#test", element_type="div")],
            forms=[],
            navigation_links=[],
            api_endpoints=[],
            has_authentication=False,
            user_flows=[],
            test_scenarios=[]
        )
        
        analysis_dict = analysis.to_dict()
        assert isinstance(analysis_dict, dict)
        assert analysis_dict["url"] == "https://example.com"
        assert len(analysis_dict["elements"]) == 1
        assert isinstance(analysis_dict["elements"][0], dict)


class TestGeneratedTest:
    """Test GeneratedTest dataclass"""
    
    def test_generated_test_creation(self):
        """Test creating GeneratedTest object"""
        test = GeneratedTest(
            test_type=TestType.LOGIN,
            file_name="test_login.py",
            code="# Test code here",
            description="Login test",
            dependencies=["pytest", "playwright"],
            page_objects={"login_page.py": "# Page object code"}
        )
        
        assert test.test_type == TestType.LOGIN
        assert test.file_name == "test_login.py"
        assert test.code == "# Test code here"
        assert "pytest" in test.dependencies
        assert test.page_objects is not None


class ConcreteProvider(BaseAIProvider):
    """Concrete implementation for testing abstract base class"""
    
    async def analyze_page(self, page_content: str, url: str) -> PageAnalysis:
        return PageAnalysis(
            url=url,
            title="Test Page",
            page_type="test",
            elements=[],
            forms=[],
            navigation_links=[],
            api_endpoints=[],
            has_authentication=False,
            user_flows=[],
            test_scenarios=[]
        )
    
    async def generate_test(self, request: TestGenerationRequest) -> GeneratedTest:
        return GeneratedTest(
            test_type=request.test_type,
            file_name="test.py",
            code="# Test code",
            description="Test",
            dependencies=[]
        )
    
    async def validate_test(self, test_code: str):
        return True, []


class TestBaseAIProvider:
    """Test BaseAIProvider abstract class"""
    
    def test_provider_initialization(self, temp_config_dir):
        """Test provider initialization with config"""
        with patch('ai.providers.base_provider.Path') as mock_path:
            mock_path.return_value.parent.parent.parent.parent = temp_config_dir.parent
            provider = ConcreteProvider()
            
            assert provider.config == {}  # No specific config for test provider
            assert isinstance(provider.prompts, dict)
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality"""
        provider = ConcreteProvider()
        
        async with provider as p:
            assert p.session is not None
            assert hasattr(p.session, 'close')
        
        # Session should be closed after context
        assert provider.session is None or provider.session.closed
    
    @pytest.mark.asyncio
    async def test_determine_applicable_tests(self):
        """Test determining which tests are applicable"""
        provider = ConcreteProvider()
        
        # Test with login page
        login_analysis = PageAnalysis(
            url="https://example.com/login",
            title="Login",
            page_type="login",
            elements=[],
            forms=[{"fields": []}],
            navigation_links=[],
            api_endpoints=["/api/login"],
            has_authentication=True,
            user_flows=[],
            test_scenarios=[]
        )
        
        applicable_tests = provider._determine_applicable_tests(login_analysis)
        
        assert TestType.LOGIN in applicable_tests
        assert TestType.NAVIGATION in applicable_tests
        assert TestType.FORM_INTERACTION in applicable_tests
        assert TestType.API_INTEGRATION in applicable_tests
        assert TestType.ACCESSIBILITY in applicable_tests
        assert TestType.PERFORMANCE in applicable_tests
    
    @pytest.mark.asyncio
    async def test_generate_test_suite(self):
        """Test generating a complete test suite"""
        provider = ConcreteProvider()
        
        analysis = PageAnalysis(
            url="https://example.com",
            title="Test Page",
            page_type="generic",
            elements=[],
            forms=[],
            navigation_links=[],
            api_endpoints=[],
            has_authentication=False,
            user_flows=[],
            test_scenarios=[]
        )
        
        # Generate test suite with specific test types
        test_types = [TestType.NAVIGATION, TestType.ACCESSIBILITY]
        tests = await provider.generate_test_suite(analysis, test_types)
        
        assert len(tests) == 2
        assert all(isinstance(test, GeneratedTest) for test in tests)
        assert tests[0].test_type == TestType.NAVIGATION
        assert tests[1].test_type == TestType.ACCESSIBILITY
    
    def test_format_prompt(self):
        """Test prompt formatting"""
        provider = ConcreteProvider()
        
        template = "Hello {name}, you are {age} years old"
        formatted = provider._format_prompt(template, name="Test", age=25)
        
        assert formatted == "Hello Test, you are 25 years old"
        
        # Test with missing parameter
        formatted_missing = provider._format_prompt(template, name="Test")
        assert formatted_missing == template  # Should return original on error