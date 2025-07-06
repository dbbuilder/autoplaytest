"""
AI Script Generator
Integrates with Claude, Gemini, and GPT for intelligent test generation
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from playwright.async_api import Page, Browser, async_playwright

from ai.providers import (
    AIProviderFactory, AIProviderType, BaseAIProvider,
    TestType, PageAnalysis, GeneratedTest
)
from ai.intelligent_page_analyzer import IntelligentPageAnalyzer
from utils.logger import setup_logger


class AIScriptGenerator:
    """Generates intelligent Playwright test scripts using AI providers"""
    
    def __init__(self, provider_type: Optional[str] = None):
        """
        Initialize the AI Script Generator
        
        Args:
            provider_type: Optional provider type (claude, gemini, gpt)
                         If not specified, uses the first available provider
        """
        self.logger = setup_logger(__name__)
        
        # Initialize AI provider
        if provider_type:
            self.provider_type = AIProviderType(provider_type.lower())
        else:
            self.provider_type = AIProviderFactory.get_default_provider()
            
        if not self.provider_type:
            raise ValueError("No AI providers available. Please set API keys.")
            
        self.provider = AIProviderFactory.create_provider(self.provider_type)
        self.page_analyzer = IntelligentPageAnalyzer()
        
        self.logger.info(f"Using AI provider: {self.provider_type.value}")
        
    async def initialize(self):
        """Initialize the script generator"""
        self.logger.info("AI Script Generator initialized")
    
    def set_provider(self, provider_type: str):
        """
        Change the AI provider type
        
        Args:
            provider_type: Provider type (claude, gemini, gpt)
        """
        self.provider_type = AIProviderType(provider_type.lower())
        self.provider = AIProviderFactory.create_provider(self.provider_type)
        self.logger.info(f"Changed AI provider to: {self.provider_type.value}")
        
    async def analyze_and_generate(
        self,
        url: str,
        username: str,
        password: str,
        test_types: Optional[List[str]] = None,
        browser_type: str = 'chromium'
    ) -> Dict[str, Any]:
        """
        Analyze a web page and generate comprehensive tests
        
        Args:
            url: Target URL to analyze
            username: Username for authentication (if needed)
            password: Password for authentication (if needed)
            test_types: List of test types to generate
            browser_type: Browser to use for analysis
            
        Returns:
            Dictionary containing generated tests and metadata
        """
        self.logger.info(f"Analyzing and generating tests for: {url}")
        
        # Default test types if not specified
        if not test_types:
            test_types = ['login', 'navigation', 'form_interaction', 'accessibility']
        
        # Convert string test types to enums
        test_type_enums = []
        for test_type in test_types:
            try:
                test_type_enums.append(TestType(test_type))
            except ValueError:
                self.logger.warning(f"Unknown test type: {test_type}")
        
        # Analyze the page using Playwright
        page_analysis = await self._analyze_page_with_playwright(url, browser_type)
        
        # Convert to PageAnalysis object for AI provider
        ai_page_analysis = PageAnalysis(
            url=url,
            title=page_analysis['title'],
            page_type=page_analysis['page_type'],
            elements=[],  # Simplified for now
            forms=page_analysis['forms'],
            navigation_links=[nav['href'] for nav in page_analysis['navigation']],
            api_endpoints=page_analysis['api_endpoints'],
            has_authentication=page_analysis['authentication']['has_login_form'],
            user_flows=[],
            test_scenarios=[]
        )
        
        # Generate tests using AI provider
        async with self.provider as provider:
            generated_tests = await provider.generate_test_suite(
                ai_page_analysis,
                test_type_enums
            )
        
        # Prepare results
        results = {
            'url': url,
            'provider': self.provider_type.value,
            'timestamp': datetime.now().isoformat(),
            'page_analysis': page_analysis,
            'generated_tests': [
                {
                    'type': test.test_type.value,
                    'file_name': test.file_name,
                    'code': test.code,
                    'description': test.description,
                    'dependencies': test.dependencies,
                    'page_objects': test.page_objects
                }
                for test in generated_tests
            ]
        }
        
        return results
    
    async def _analyze_page_with_playwright(self, url: str, browser_type: str = 'chromium') -> Dict[str, Any]:
        """
        Analyze a page using Playwright browser automation
        
        Args:
            url: URL to analyze
            browser_type: Type of browser to use
            
        Returns:
            Page analysis data
        """
        async with async_playwright() as p:
            # Launch browser
            browser_args = {
                'headless': True,
                'args': ['--no-sandbox', '--disable-setuid-sandbox']
            }
            
            if browser_type == 'chromium':
                browser = await p.chromium.launch(**browser_args)
            elif browser_type == 'firefox':
                browser = await p.firefox.launch(**browser_args)
            else:
                browser = await p.webkit.launch(**browser_args)
            
            try:
                # Create context and page
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                
                page = await context.new_page()
                
                # Navigate to the page with increased timeout
                await page.goto(url, wait_until='networkidle', timeout=60000)
                
                # Analyze the page
                analysis = await self.page_analyzer.analyze_page(page)
                
                # Take screenshot for reference
                screenshot_path = Path('screenshots') / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                screenshot_path.parent.mkdir(exist_ok=True)
                await page.screenshot(path=str(screenshot_path))
                
                analysis['screenshot'] = str(screenshot_path)
                
                return analysis
                
            finally:
                await browser.close()
    
    async def generate_test_suite(
        self,
        analysis_results: Dict[str, Any],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate comprehensive test suite based on analysis
        
        Args:
            analysis_results: Results from page analysis
            config: Test generation configuration
            
        Returns:
            List of generated test files
        """
        url = config.get('url', '')
        username = config.get('username', '')
        password = config.get('password', '')
        test_types = config.get('test_types', ['login', 'navigation'])
        
        # Use the new analyze_and_generate method
        results = await self.analyze_and_generate(
            url=url,
            username=username,
            password=password,
            test_types=test_types
        )
        
        # Convert to expected format
        test_scripts = []
        for test in results['generated_tests']:
            test_scripts.append({
                'file_name': test['file_name'],
                'content': test['code'],
                'test_type': test['type'],
                'description': test['description']
            })
            
            # Add page objects if any
            if test.get('page_objects'):
                for po_file, po_code in test['page_objects'].items():
                    test_scripts.append({
                        'file_name': f"page_objects/{po_file}",
                        'content': po_code,
                        'test_type': 'page_object',
                        'description': f"Page object for {test['type']}"
                    })
        
        return test_scripts
    
    def _get_pytest_template(self) -> str:
        """Get pytest template"""
        return '''"""
{description}
Generated by AI Playwright Test Generator
"""

import pytest
from playwright.async_api import Page, expect
{imports}

@pytest.mark.asyncio
class Test{class_name}:
    """Test suite for {feature}"""
    
{test_methods}
'''

    def _get_playwright_test_template(self) -> str:
        """Get Playwright test template"""
        return '''import {{ test, expect }} from '@playwright/test';

test.describe('{feature}', () => {{
{test_cases}
}});
'''

    def _get_jest_template(self) -> str:
        """Get Jest template"""
        return '''const {{ chromium }} = require('playwright');

describe('{feature}', () => {{
    let browser;
    let page;
    
    beforeAll(async () => {{
        browser = await chromium.launch();
    }});
    
    afterAll(async () => {{
        await browser.close();
    }});
    
    beforeEach(async () => {{
        page = await browser.newPage();
    }});
    
    afterEach(async () => {{
        await page.close();
    }});
    
{test_cases}
}});
'''