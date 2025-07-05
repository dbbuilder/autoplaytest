"""
Base AI Provider Implementation
Defines the interface and common functionality for all AI providers
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import aiohttp
import json
import yaml
from pathlib import Path
import logging
from datetime import datetime


class TestType(Enum):
    """Types of tests that can be generated"""
    LOGIN = "login"
    NAVIGATION = "navigation"
    FORM_INTERACTION = "form_interaction"
    SEARCH = "search"
    CRUD_OPERATIONS = "crud"
    API_INTEGRATION = "api"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    VISUAL_REGRESSION = "visual"
    E2E_WORKFLOW = "e2e"


@dataclass
class PageElement:
    """Represents a UI element on the page"""
    selector: str
    element_type: str
    text: Optional[str] = None
    attributes: Dict[str, str] = None
    is_interactive: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PageAnalysis:
    """Results of analyzing a web page"""
    url: str
    title: str
    page_type: str  # login, dashboard, form, etc.
    elements: List[PageElement]
    forms: List[Dict[str, Any]]
    navigation_links: List[str]
    api_endpoints: List[str]
    has_authentication: bool
    user_flows: List[Dict[str, Any]]
    test_scenarios: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['elements'] = [e.to_dict() for e in self.elements]
        return data

@dataclass
class TestGenerationRequest:
    """Request for test generation"""
    page_analysis: PageAnalysis
    test_type: TestType
    context: Dict[str, Any] = None
    options: Dict[str, Any] = None


@dataclass
class GeneratedTest:
    """Represents a generated test"""
    test_type: TestType
    file_name: str
    code: str
    description: str
    dependencies: List[str]
    page_objects: Optional[Dict[str, str]] = None


class BaseAIProvider(ABC):
    """Base class for all AI providers"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the AI provider with configuration"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = self._load_config(config_path)
        self.prompts = self._load_prompts()
        self.session: Optional[aiohttp.ClientSession] = None
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load provider-specific configuration"""
        if config_path:
            config_file = Path(config_path)
        else:
            # Load from default location
            provider_name = self.__class__.__name__.lower().replace('provider', '')
            config_file = Path(__file__).parent.parent.parent.parent / 'config' / 'ai_providers' / f'{provider_name}.yaml'
            
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            self.logger.warning(f"Config file not found: {config_file}")
            return {}
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load provider-specific prompts"""
        provider_name = self.__class__.__name__.lower().replace('provider', '')
        prompts_dir = Path(__file__).parent.parent.parent.parent / 'config' / 'prompts' / provider_name
        
        prompts = {}
        if prompts_dir.exists():
            for prompt_file in prompts_dir.glob('*.md'):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompts[prompt_file.stem] = f.read()
        
        return prompts
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def analyze_page(self, page_content: str, url: str) -> PageAnalysis:
        """Analyze a web page and extract information for test generation"""
        pass
    
    @abstractmethod
    async def generate_test(self, request: TestGenerationRequest) -> GeneratedTest:
        """Generate a test based on page analysis and test type"""
        pass
    
    @abstractmethod
    async def validate_test(self, test_code: str) -> Tuple[bool, List[str]]:
        """Validate generated test code"""
        pass
    
    async def generate_test_suite(
        self, 
        page_analysis: PageAnalysis,
        test_types: Optional[List[TestType]] = None
    ) -> List[GeneratedTest]:
        """Generate a complete test suite for the analyzed page"""
        if test_types is None:
            test_types = self._determine_applicable_tests(page_analysis)
        
        tests = []
        for test_type in test_types:
            try:
                request = TestGenerationRequest(
                    page_analysis=page_analysis,
                    test_type=test_type
                )
                test = await self.generate_test(request)
                tests.append(test)
            except Exception as e:
                self.logger.error(f"Failed to generate {test_type.value} test: {str(e)}")
        
        return tests
    
    def _determine_applicable_tests(self, analysis: PageAnalysis) -> List[TestType]:
        """Determine which test types are applicable based on page analysis"""
        applicable = []
        
        # Always include navigation tests
        applicable.append(TestType.NAVIGATION)
        
        # Check for specific features
        if analysis.has_authentication or analysis.page_type == "login":
            applicable.append(TestType.LOGIN)
        
        if analysis.forms:
            applicable.append(TestType.FORM_INTERACTION)
        
        if any('search' in element.attributes.get('name', '').lower() 
               for element in analysis.elements if element.attributes):
            applicable.append(TestType.SEARCH)
        
        if analysis.api_endpoints:
            applicable.append(TestType.API_INTEGRATION)
        
        # Always include accessibility and performance
        applicable.extend([TestType.ACCESSIBILITY, TestType.PERFORMANCE])
        
        return applicable
    
    def _format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with provided values"""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            self.logger.error(f"Missing prompt parameter: {e}")
            return template