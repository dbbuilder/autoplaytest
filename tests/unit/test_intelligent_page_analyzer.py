"""
Unit tests for Intelligent Page Analyzer
Following TDD principles
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from ai.intelligent_page_analyzer import IntelligentPageAnalyzer


class TestIntelligentPageAnalyzer:
    """Test Intelligent Page Analyzer"""
    
    @pytest.fixture
    def mock_page(self):
        """Create a mock Playwright page"""
        page = AsyncMock()
        page.url = "https://example.com/test"
        page.title = AsyncMock(return_value="Test Page")
        page.content = AsyncMock(return_value="<html><body>Test</body></html>")
        page.viewport_size = {"width": 1920, "height": 1080}
        
        # Mock locator for different elements
        def create_locator_mock(count=0, elements=[]):
            locator = AsyncMock()
            locator.count = AsyncMock(return_value=count)
            
            def nth(index):
                if index < len(elements):
                    return elements[index]
                return AsyncMock()
            
            locator.nth = nth
            locator.all = AsyncMock(return_value=elements)
            return locator
        
        page.locator = Mock(side_effect=lambda selector: create_locator_mock())
        page.evaluate = AsyncMock(return_value={})
        
        return page
    
    @pytest.mark.asyncio
    async def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        analyzer = IntelligentPageAnalyzer()
        assert analyzer.logger is not None
    
    @pytest.mark.asyncio
    async def test_analyze_page_basic(self, mock_page):
        """Test basic page analysis"""
        analyzer = IntelligentPageAnalyzer()
        
        analysis = await analyzer.analyze_page(mock_page)
        
        assert analysis['url'] == "https://example.com/test"
        assert analysis['title'] == "Test Page"
        assert 'viewport' in analysis
        assert 'elements' in analysis
        assert 'forms' in analysis
        assert 'navigation' in analysis
    
    @pytest.mark.asyncio
    async def test_extract_elements(self, mock_page):
        """Test element extraction"""
        # Create mock elements
        button_element = AsyncMock()
        button_element.text_content = AsyncMock(return_value="Click Me")
        button_element.is_visible = AsyncMock(return_value=True)
        button_element.is_enabled = AsyncMock(return_value=True)
        button_element.evaluate = AsyncMock(return_value="button")
        button_element.get_attribute = AsyncMock(side_effect=lambda attr: {
            'id': 'submit-btn',
            'class': 'btn btn-primary',
            'data-testid': 'submit-button'
        }.get(attr))
        
        # Setup locator mock
        button_locator = AsyncMock()
        button_locator.count = AsyncMock(return_value=1)
        button_locator.nth = Mock(return_value=button_element)
        
        mock_page.locator = Mock(side_effect=lambda sel: button_locator if sel == 'button' else AsyncMock(count=AsyncMock(return_value=0)))
        
        analyzer = IntelligentPageAnalyzer()
        elements = await analyzer._extract_elements(mock_page)
        
        assert len(elements) > 0
        button_data = elements[0]
        assert button_data['text'] == "Click Me"
        assert button_data['visible'] is True
        assert button_data['enabled'] is True
        assert button_data['attributes']['id'] == 'submit-btn'
    
    @pytest.mark.asyncio
    async def test_analyze_forms(self, mock_page):
        """Test form analysis"""
        # Create mock form
        form_element = AsyncMock()
        form_element.get_attribute = AsyncMock(side_effect=lambda attr: {
            'action': '/submit',
            'method': 'post'
        }.get(attr))
        
        # Create mock input field
        input_element = AsyncMock()
        input_element.get_attribute = AsyncMock(side_effect=lambda attr: {
            'type': 'text',
            'name': 'username',
            'id': 'username-input',
            'required': 'required',
            'placeholder': 'Enter username'
        }.get(attr))
        
        # Setup form locator
        form_locator = AsyncMock()
        form_locator.count = AsyncMock(return_value=1)
        form_locator.nth = Mock(return_value=form_element)
        
        # Setup input locator within form
        input_locator = AsyncMock()
        input_locator.count = AsyncMock(return_value=1)
        input_locator.nth = Mock(return_value=input_element)
        
        form_element.locator = Mock(return_value=input_locator)
        
        mock_page.locator = Mock(side_effect=lambda sel: form_locator if sel == 'form' else AsyncMock(count=AsyncMock(return_value=0)))
        
        analyzer = IntelligentPageAnalyzer()
        forms = await analyzer._analyze_forms(mock_page)
        
        assert len(forms) == 1
        assert forms[0]['action'] == '/submit'
        assert forms[0]['method'] == 'post'
    
    @pytest.mark.asyncio
    async def test_detect_authentication(self, mock_page):
        """Test authentication detection"""
        # Mock password input (indicates login form)
        password_locator = AsyncMock()
        password_locator.count = AsyncMock(return_value=1)
        
        # Mock logout button (indicates authenticated state)
        logout_locator = AsyncMock()
        logout_locator.count = AsyncMock(return_value=0)
        
        mock_page.locator = Mock(side_effect=lambda sel: {
            'input[type="password"]': password_locator,
            'button:has-text("Logout")': logout_locator,
            'button:has-text("Sign out")': logout_locator,
            'a:has-text("Logout")': logout_locator,
            'a:has-text("Sign out")': logout_locator
        }.get(sel, AsyncMock(count=AsyncMock(return_value=0))))
        
        analyzer = IntelligentPageAnalyzer()
        auth_info = await analyzer._detect_authentication(mock_page)
        
        assert auth_info['has_login_form'] is True
        assert auth_info['has_logout_button'] is False
        assert auth_info['is_authenticated'] is False
    
    @pytest.mark.asyncio
    async def test_determine_page_type(self, mock_page):
        """Test page type determination"""
        analyzer = IntelligentPageAnalyzer()
        
        # Test login page detection by URL
        mock_page.url = "https://example.com/login"
        page_type = await analyzer._determine_page_type(mock_page)
        assert page_type == "login"
        
        # Test dashboard detection
        mock_page.url = "https://example.com/dashboard"
        page_type = await analyzer._determine_page_type(mock_page)
        assert page_type == "dashboard"
        
        # Test form page detection
        mock_page.url = "https://example.com/create-user"
        page_type = await analyzer._determine_page_type(mock_page)
        assert page_type == "form"
    
    @pytest.mark.asyncio
    async def test_detect_interactions(self, mock_page):
        """Test interaction detection"""
        # Create mock elements
        button = AsyncMock()
        button.get_attribute = AsyncMock(return_value="test-button")
        button.text_content = AsyncMock(return_value="Click Me")
        
        input_field = AsyncMock()
        input_field.get_attribute = AsyncMock(side_effect=lambda attr: "username" if attr == "name" else None)
        
        # Setup locators
        mock_page.locator = Mock(side_effect=lambda sel: {
            'button, a, [onclick], [role="button"]': AsyncMock(all=AsyncMock(return_value=[button])),
            'input[type="text"], input[type="email"], textarea': AsyncMock(all=AsyncMock(return_value=[input_field])),
            'select, input[type="checkbox"], input[type="radio"]': AsyncMock(all=AsyncMock(return_value=[]))
        }.get(sel, AsyncMock(all=AsyncMock(return_value=[]))))
        
        analyzer = IntelligentPageAnalyzer()
        interactions = await analyzer._detect_interactions(mock_page)
        
        assert len(interactions['clickable']) > 0
        assert len(interactions['fillable']) > 0
        assert interactions['clickable'][0] in ["test-button", "Click Me"]
        assert interactions['fillable'][0] == "username"
    
    @pytest.mark.asyncio
    async def test_analyze_accessibility(self, mock_page):
        """Test accessibility analysis"""
        # Mock elements for accessibility checks
        mock_page.locator = Mock(side_effect=lambda sel: {
            'h1, h2, h3, h4, h5, h6': AsyncMock(count=AsyncMock(return_value=3)),
            '[aria-label], [aria-describedby], [role]': AsyncMock(count=AsyncMock(return_value=5)),
            'img': AsyncMock(count=AsyncMock(return_value=2)),
            'img[alt]': AsyncMock(count=AsyncMock(return_value=2)),
            '[tabindex]': AsyncMock(count=AsyncMock(return_value=4))
        }.get(sel, AsyncMock(count=AsyncMock(return_value=0))))
        
        analyzer = IntelligentPageAnalyzer()
        accessibility = await analyzer._analyze_accessibility(mock_page)
        
        assert accessibility['has_proper_headings'] is True
        assert accessibility['has_aria_labels'] is True
        assert accessibility['has_alt_text'] is True
        assert accessibility['keyboard_navigable'] is True
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics(self, mock_page):
        """Test performance metrics collection"""
        # Mock performance data
        mock_page.evaluate = AsyncMock(return_value={
            'domContentLoaded': 150,
            'loadComplete': 500,
            'firstPaint': 100,
            'firstContentfulPaint': 200
        })
        
        analyzer = IntelligentPageAnalyzer()
        metrics = await analyzer._get_performance_metrics(mock_page)
        
        assert metrics['domContentLoaded'] == 150
        assert metrics['loadComplete'] == 500
        assert metrics['firstPaint'] == 100
        assert metrics['firstContentfulPaint'] == 200