"""
AI-Powered Test Generator
Orchestrates test generation using Claude, Gemini, or GPT
Implements TDD principles and autonomous test discovery
"""

import os
import asyncio
import json
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser
import hashlib

from ai.providers.base_provider import (
    BaseAIProvider, TestType, TestScenario, PageAnalysis
)
from utils.logger import setup_logger


class AITestGenerator:
    """
    Autonomous AI-powered test generator with TDD principles
    """
    
    def __init__(self, provider_name: str = None):
        self.logger = setup_logger(__name__)
        self.provider_name = provider_name or os.getenv("DEFAULT_AI_PROVIDER", "claude")
        self.provider = self._initialize_provider()
        self.discovered_pages: Set[str] = set()
        self.generated_tests: Dict[str, List[TestScenario]] = {}
        self.test_results: Dict[str, Any] = {}
        
    def _initialize_provider(self) -> BaseAIProvider:
        """Initialize the selected AI provider"""
        provider_map = {
            "claude": "claude_provider.ClaudeProvider",
            "gemini": "gemini_provider.GeminiProvider", 
            "gpt": "gpt_provider.GPTProvider"
        }
        
        if self.provider_name not in provider_map:
            raise ValueError(f"Unknown provider: {self.provider_name}")
            
        # Dynamic import
        module_name, class_name = provider_map[self.provider_name].rsplit(".", 1)
        module = __import__(f"ai.providers.{module_name}", fromlist=[class_name])
        provider_class = getattr(module, class_name)
        
        return provider_class()
        
    async def discover_and_analyze(self, start_url: str, max_depth: int = 3) -> Dict[str, PageAnalysis]:
        """
        Autonomously discover pages and analyze them
        Implements crawling with depth limit
        """
        self.logger.info(f"Starting autonomous discovery from {start_url}")
        analyzed_pages = {}
        to_visit = [(start_url, 0)]
        visited = set()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            while to_visit:
                url, depth = to_visit.pop(0)
                
                if url in visited or depth > max_depth:
                    continue
                    
                visited.add(url)
                self.logger.info(f"Analyzing {url} (depth: {depth})")
                
                try:
                    page = await context.new_page()
                    await page.goto(url, wait_until="networkidle")
                    
                    # Get page content
                    content = await page.content()
                    
                    # Take screenshot
                    screenshot_path = f"screenshots/page_{hashlib.md5(url.encode()).hexdigest()}.png"
                    await page.screenshot(path=screenshot_path)
                    
                    # Analyze with AI
                    analysis = await self.provider.analyze_page(content, url)
                    analysis.screenshots = [screenshot_path]
                    analyzed_pages[url] = analysis
                    
                    # Discover more pages
                    if depth < max_depth:
                        # Extract links
                        links = await page.evaluate("""
                            () => Array.from(document.querySelectorAll('a[href]'))
                                    .map(a => a.href)
                                    .filter(href => href.startsWith('http'))
                        """)
                        
                        # Add new links to visit
                        base_domain = url.split('/')[2]
                        for link in links:
                            if base_domain in link and link not in visited:
                                to_visit.append((link, depth + 1))
                                
                    await page.close()
                    
                except Exception as e:
                    self.logger.error(f"Error analyzing {url}: {e}")
                    
            await browser.close()
            
        return analyzed_pages
        
    async def generate_tdd_tests(self, 
                               analyzed_pages: Dict[str, PageAnalysis],
                               test_types: Optional[List[TestType]] = None) -> Dict[str, List[TestScenario]]:
        """
        Generate TDD-minded tests for all analyzed pages
        Follows Red-Green-Refactor cycle
        """
        if not test_types:
            test_types = [
                TestType.LOGIN,
                TestType.NAVIGATION,
                TestType.FORM_INTERACTION,
                TestType.SEARCH,
                TestType.ACCESSIBILITY,
                TestType.PERFORMANCE
            ]
            
        all_scenarios = {}
        
        for url, analysis in analyzed_pages.items():
            self.logger.info(f"Generating TDD tests for {url}")
            
            # Determine applicable test types based on page analysis
            applicable_types = self._determine_test_types(analysis)
            
            # Generate scenarios
            scenarios = await self.provider.generate_test_scenarios(
                analysis,
                [t for t in test_types if t in applicable_types]
            )
            
            # Apply TDD principles
            tdd_scenarios = self._apply_tdd_principles(scenarios)
            all_scenarios[url] = tdd_scenarios
            
        return all_scenarios
        
    def _determine_test_types(self, analysis: PageAnalysis) -> List[TestType]:
        """Determine which test types are applicable for a page"""
        applicable = []
        
        if analysis.has_authentication or analysis.page_type == "login":
            applicable.append(TestType.LOGIN)
            
        if analysis.navigation_links:
            applicable.append(TestType.NAVIGATION)
            
        if analysis.forms:
            applicable.append(TestType.FORM_INTERACTION)
            
        # Search functionality detection
        search_selectors = ['input[type="search"]', 'input[placeholder*="search"]', '#search']
        if any(elem.selector in search_selectors for elem in analysis.elements if elem.is_interactive):
            applicable.append(TestType.SEARCH)
            
        # Always include accessibility and performance
        applicable.extend([TestType.ACCESSIBILITY, TestType.PERFORMANCE])
        
        return applicable
        
    def _apply_tdd_principles(self, scenarios: List[TestScenario]) -> List[TestScenario]:
        """
        Apply TDD principles to test scenarios
        - Write failing test first
        - Make it pass with minimal code
        - Refactor for better structure
        """
        tdd_scenarios = []
        
        for scenario in scenarios:
            # Add TDD metadata
            scenario.test_data = scenario.test_data or {}
            scenario.test_data.update({
                "tdd_phase": "red",  # Start with failing test
                "assertions_first": True,  # Write assertions before implementation
                "minimal_implementation": True,  # Use minimal code to pass
                "refactor_needed": True  # Plan for refactoring
            })
            
            # Prioritize based on business value
            if scenario.test_type in [TestType.LOGIN, TestType.E2E_WORKFLOW]:
                scenario.priority = 1
            elif scenario.test_type in [TestType.FORM_INTERACTION, TestType.SEARCH]:
                scenario.priority = 2
            else:
                scenario.priority = 3
                
            tdd_scenarios.append(scenario)
            
        # Sort by priority
        return sorted(tdd_scenarios, key=lambda s: s.priority)
        
    async def generate_playwright_tests(self,
                                      scenarios: Dict[str, List[TestScenario]],
                                      output_dir: str) -> Dict[str, str]:
        """
        Generate actual Playwright test files
        Returns mapping of test files to their paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        for url, page_scenarios in scenarios.items():
            # Group scenarios by test type
            by_type = {}
            for scenario in page_scenarios:
                test_type = scenario.test_type.value
                if test_type not in by_type:
                    by_type[test_type] = []
                by_type[test_type].append(scenario)
                
            # Generate test file for each type
            for test_type, type_scenarios in by_type.items():
                file_name = f"test_{test_type}_{hashlib.md5(url.encode()).hexdigest()[:8]}.py"
                file_path = output_path / file_name
                
                # Generate test code
                test_code = await self._generate_test_file(url, type_scenarios)
                
                # Write to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(test_code)
                    
                generated_files[file_name] = str(file_path)
                self.logger.info(f"Generated {file_name}")
                
        # Generate test runner
        runner_path = output_path / "run_all_tests.py"
        runner_code = self._generate_test_runner(generated_files.keys())
        with open(runner_path, 'w', encoding='utf-8') as f:
            f.write(runner_code)
            
        return generated_files