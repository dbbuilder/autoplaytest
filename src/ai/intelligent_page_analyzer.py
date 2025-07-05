"""
Intelligent Page Analyzer
Analyzes web pages using Playwright to extract structure and content for test generation
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from playwright.async_api import Page, Browser, async_playwright
from bs4 import BeautifulSoup
import re

from utils.logger import setup_logger


class IntelligentPageAnalyzer:
    """
    Analyzes web pages to extract information needed for test generation
    Works in conjunction with AI providers
    """
    
    def __init__(self):
        """Initialize the page analyzer"""
        self.logger = setup_logger(self.__class__.__name__)
        
    async def analyze_page(self, page: Page) -> Dict[str, Any]:
        """
        Analyze a page using Playwright
        
        Args:
            page: Playwright page object
            
        Returns:
            Dictionary containing page analysis data
        """
        self.logger.info(f"Analyzing page: {page.url}")
        
        # Get page content and metadata
        url = page.url
        title = await page.title()
        
        # Get page HTML
        html_content = await page.content()
        
        # Extract viewport information
        viewport = page.viewport_size
        
        # Analyze the page structure
        analysis = {
            'url': url,
            'title': title,
            'viewport': viewport,
            'elements': await self._extract_elements(page),
            'forms': await self._analyze_forms(page),
            'navigation': await self._extract_navigation(page),
            'api_endpoints': await self._detect_api_endpoints(page),
            'authentication': await self._detect_authentication(page),
            'page_type': await self._determine_page_type(page),
            'interactions': await self._detect_interactions(page),
            'accessibility': await self._analyze_accessibility(page),
            'performance_metrics': await self._get_performance_metrics(page)
        }
        
        return analysis
    
    async def _extract_elements(self, page: Page) -> List[Dict[str, Any]]:
        """Extract all interactive elements from the page"""
        elements = []
        
        # Define selectors for interactive elements
        interactive_selectors = [
            'button',
            'a[href]',
            'input',
            'select',
            'textarea',
            '[role="button"]',
            '[onclick]',
            '[data-testid]'
        ]
        
        for selector in interactive_selectors:
            try:
                locators = page.locator(selector)
                count = await locators.count()
                
                for i in range(count):
                    element = locators.nth(i)
                    
                    # Get element properties
                    element_data = {
                        'selector': selector,
                        'index': i,
                        'text': await element.text_content() or '',
                        'type': await element.evaluate('el => el.tagName.toLowerCase()'),
                        'visible': await element.is_visible(),
                        'enabled': await element.is_enabled(),
                        'attributes': {}
                    }
                    
                    # Get specific attributes
                    for attr in ['id', 'class', 'name', 'data-testid', 'aria-label', 'placeholder', 'href', 'type']:
                        value = await element.get_attribute(attr)
                        if value:
                            element_data['attributes'][attr] = value
                    
                    elements.append(element_data)
                    
            except Exception as e:
                self.logger.debug(f"Error extracting {selector}: {str(e)}")
        
        return elements
    
    async def _analyze_forms(self, page: Page) -> List[Dict[str, Any]]:
        """Analyze all forms on the page"""
        forms = []
        
        form_elements = page.locator('form')
        count = await form_elements.count()
        
        for i in range(count):
            form = form_elements.nth(i)
            
            form_data = {
                'index': i,
                'action': await form.get_attribute('action') or '',
                'method': await form.get_attribute('method') or 'get',
                'fields': []
            }
            
            # Get all form fields
            field_selectors = ['input', 'select', 'textarea']
            for selector in field_selectors:
                fields = form.locator(selector)
                field_count = await fields.count()
                
                for j in range(field_count):
                    field = fields.nth(j)
                    field_info = {
                        'type': await field.get_attribute('type') or 'text',
                        'name': await field.get_attribute('name') or '',
                        'id': await field.get_attribute('id') or '',
                        'required': await field.get_attribute('required') is not None,
                        'placeholder': await field.get_attribute('placeholder') or ''
                    }
                    form_data['fields'].append(field_info)
            
            forms.append(form_data)
        
        return forms
    
    async def _extract_navigation(self, page: Page) -> List[Dict[str, Any]]:
        """Extract navigation elements"""
        navigation = []
        
        # Look for common navigation patterns
        nav_selectors = [
            'nav a',
            'header a',
            '[role="navigation"] a',
            '.nav a',
            '.navbar a',
            '.menu a'
        ]
        
        for selector in nav_selectors:
            try:
                links = page.locator(selector)
                count = await links.count()
                
                for i in range(count):
                    link = links.nth(i)
                    nav_item = {
                        'text': await link.text_content() or '',
                        'href': await link.get_attribute('href') or '',
                        'visible': await link.is_visible()
                    }
                    if nav_item['href'] and nav_item not in navigation:
                        navigation.append(nav_item)
                        
            except Exception:
                pass
        
        return navigation
    
    async def _detect_api_endpoints(self, page: Page) -> List[str]:
        """Detect API endpoints from network traffic"""
        api_endpoints = []
        
        # This would need to be set up with page.on('request') before navigation
        # For now, we'll look for common patterns in the page
        
        # Look for fetch/ajax calls in scripts
        scripts = await page.evaluate('''
            () => {
                const scripts = Array.from(document.scripts);
                const content = scripts.map(s => s.textContent).join('\\n');
                const apiPattern = /(?:fetch|axios|\\$\\.ajax)\\s*\\([\'"`]([^\'"`]+)[\'"`]/g;
                const matches = [...content.matchAll(apiPattern)];
                return matches.map(m => m[1]);
            }
        ''')
        
        api_endpoints.extend(scripts)
        
        return list(set(api_endpoints))
    
    async def _detect_authentication(self, page: Page) -> Dict[str, Any]:
        """Detect authentication elements"""
        auth_info = {
            'has_login_form': False,
            'has_logout_button': False,
            'login_fields': [],
            'is_authenticated': False
        }
        
        # Check for login forms
        login_indicators = [
            'input[type="password"]',
            'input[name*="password"]',
            'input[name*="username"]',
            'input[name*="email"]',
            'button:has-text("Login")',
            'button:has-text("Sign in")'
        ]
        
        for indicator in login_indicators:
            count = await page.locator(indicator).count()
            if count > 0:
                auth_info['has_login_form'] = True
                break
        
        # Check for logout elements
        logout_indicators = [
            'button:has-text("Logout")',
            'button:has-text("Sign out")',
            'a:has-text("Logout")',
            'a:has-text("Sign out")'
        ]
        
        for indicator in logout_indicators:
            count = await page.locator(indicator).count()
            if count > 0:
                auth_info['has_logout_button'] = True
                auth_info['is_authenticated'] = True
                break
        
        return auth_info
    
    async def _determine_page_type(self, page: Page) -> str:
        """Determine the type of page"""
        url = page.url.lower()
        title = (await page.title()).lower()
        
        # Check URL patterns
        if any(pattern in url for pattern in ['login', 'signin', 'auth']):
            return 'login'
        elif any(pattern in url for pattern in ['dashboard', 'home', 'index']):
            return 'dashboard'
        elif any(pattern in url for pattern in ['form', 'create', 'new', 'add']):
            return 'form'
        elif any(pattern in url for pattern in ['list', 'table', 'grid']):
            return 'listing'
        elif any(pattern in url for pattern in ['profile', 'account', 'settings']):
            return 'profile'
        
        # Check page content
        if await page.locator('input[type="password"]').count() > 0:
            return 'login'
        elif await page.locator('form').count() > 2:
            return 'form'
        elif await page.locator('table').count() > 0:
            return 'listing'
        
        return 'generic'
    
    async def _detect_interactions(self, page: Page) -> Dict[str, List[str]]:
        """Detect possible user interactions"""
        interactions = {
            'clickable': [],
            'fillable': [],
            'selectable': [],
            'draggable': []
        }
        
        # Clickable elements
        clickable = await page.locator('button, a, [onclick], [role="button"]').all()
        interactions['clickable'] = [await el.get_attribute('data-testid') or await el.text_content() or 'unnamed' for el in clickable[:10]]
        
        # Fillable elements
        fillable = await page.locator('input[type="text"], input[type="email"], textarea').all()
        interactions['fillable'] = [await el.get_attribute('name') or await el.get_attribute('id') or 'unnamed' for el in fillable[:10]]
        
        # Selectable elements
        selectable = await page.locator('select, input[type="checkbox"], input[type="radio"]').all()
        interactions['selectable'] = [await el.get_attribute('name') or await el.get_attribute('id') or 'unnamed' for el in selectable[:10]]
        
        return interactions
    
    async def _analyze_accessibility(self, page: Page) -> Dict[str, Any]:
        """Analyze accessibility features"""
        accessibility = {
            'has_proper_headings': False,
            'has_aria_labels': False,
            'has_alt_text': False,
            'keyboard_navigable': False,
            'color_contrast_ok': None  # Would need more complex analysis
        }
        
        # Check headings hierarchy
        headings = await page.locator('h1, h2, h3, h4, h5, h6').count()
        accessibility['has_proper_headings'] = headings > 0
        
        # Check ARIA labels
        aria_elements = await page.locator('[aria-label], [aria-describedby], [role]').count()
        accessibility['has_aria_labels'] = aria_elements > 0
        
        # Check alt text on images
        images = await page.locator('img').count()
        images_with_alt = await page.locator('img[alt]').count()
        accessibility['has_alt_text'] = images == 0 or images_with_alt > 0
        
        # Check for keyboard navigation indicators
        tabindex_elements = await page.locator('[tabindex]').count()
        accessibility['keyboard_navigable'] = tabindex_elements > 0
        
        return accessibility
    
    async def _get_performance_metrics(self, page: Page) -> Dict[str, Any]:
        """Get basic performance metrics"""
        metrics = await page.evaluate('''
            () => {
                const navigation = performance.getEntriesByType('navigation')[0];
                return {
                    domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                    loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                    firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
                    firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
                };
            }
        ''')
        
        return metrics