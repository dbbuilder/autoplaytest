"""Pattern Analyzer - Analyzes web page structure and identifies interaction patterns."""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup, Tag
import re
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


@dataclass
class FormField:
    """Represents a form field."""
    name: str
    field_type: str
    label: str
    required: bool
    placeholder: Optional[str] = None
    value: Optional[str] = None
    options: Optional[List[str]] = None
    validation_pattern: Optional[str] = None
    autocomplete: Optional[str] = None


@dataclass
class Form:
    """Represents a form on the page."""
    form_id: Optional[str]
    name: Optional[str]
    action: str
    method: str
    fields: List[FormField]
    submit_button_text: Optional[str] = None


@dataclass
class NavigationElement:
    """Represents a navigation element."""
    text: str
    href: str
    element_type: str  # 'link', 'button', 'menu_item'
    is_external: bool
    has_submenu: bool = False
    aria_label: Optional[str] = None


@dataclass
class InteractiveElement:
    """Represents an interactive element."""
    element_type: str
    selector: str
    text: Optional[str]
    aria_label: Optional[str]
    role: Optional[str]
    attributes: Dict[str, str]


@dataclass
class PageStructure:
    """Represents the analyzed page structure."""
    title: str
    url: str
    forms: List[Form]
    navigation: List[NavigationElement]
    interactive_elements: List[InteractiveElement]
    main_content_area: Optional[str]
    has_login_form: bool
    has_search: bool
    has_pagination: bool
    detected_patterns: List[str]


class PatternAnalyzer:
    """Analyzes web page structure and identifies common patterns."""
    
    def __init__(self):
        self.logger = logger
        self._init_patterns()
    
    def _init_patterns(self):
        """Initialize pattern detection rules."""
        self.form_patterns = {
            'login': [
                re.compile(r'(login|signin|sign[\s-]?in)', re.I),
                re.compile(r'(username|email|user[\s-]?name)', re.I),
                re.compile(r'password', re.I)
            ],
            'registration': [
                re.compile(r'(register|signup|sign[\s-]?up|create[\s-]?account)', re.I),
                re.compile(r'(confirm|repeat)[\s-]?password', re.I)
            ],
            'search': [
                re.compile(r'search', re.I),
                re.compile(r'query|q\b', re.I)
            ],
            'contact': [
                re.compile(r'contact', re.I),
                re.compile(r'message|comment', re.I),
                re.compile(r'(your[\s-]?name|full[\s-]?name)', re.I)
            ],
            'checkout': [
                re.compile(r'(checkout|payment|billing)', re.I),
                re.compile(r'(card[\s-]?number|credit[\s-]?card)', re.I)
            ]
        }
        
        self.navigation_patterns = {
            'header': ['header', 'nav', 'navigation', 'menu', 'navbar'],
            'footer': ['footer', 'site-footer', 'page-footer'],
            'sidebar': ['sidebar', 'aside', 'side-nav']
        }
        
        self.interactive_patterns = {
            'modal_triggers': [
                re.compile(r'(open|show|toggle)[\s-]?(modal|dialog|popup)', re.I),
                re.compile(r'data-toggle="modal"', re.I)
            ],
            'tab_controls': [
                re.compile(r'tab|nav-tab', re.I),
                re.compile(r'role="tab"', re.I)
            ],
            'accordion': [
                re.compile(r'accordion|collapse', re.I),
                re.compile(r'data-toggle="collapse"', re.I)
            ]
        }
    
    async def initialize(self):
        """Initialize the pattern analyzer."""
        self.logger.info("Pattern analyzer initialized")
    
    async def analyze_application(self, url: str, username: str, password: str):
        """Analyze application structure and patterns."""
        # This is a placeholder that returns basic structure
        # In a real implementation, this would use Playwright to navigate and analyze
        return {
            'pages': [],
            'forms': [],
            'navigation': [],
            'patterns': []
        }
    
    async def analyze_page(self, page_content: str, url: str) -> PageStructure:
        """Analyze page structure and identify patterns."""
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # Extract basic info
        title = self._extract_title(soup)
        
        # Analyze forms
        forms = self._analyze_forms(soup)
        
        # Analyze navigation
        navigation = self._analyze_navigation(soup, url)
        
        # Find interactive elements
        interactive_elements = self._find_interactive_elements(soup)
        
        # Identify main content area
        main_content = self._find_main_content_area(soup)
        
        # Detect patterns
        detected_patterns = self._detect_patterns(soup, forms, navigation)
        
        # Check for specific features
        has_login = any(self._is_login_form(form) for form in forms)
        has_search = any(self._is_search_form(form) for form in forms)
        has_pagination = self._has_pagination(soup)
        
        return PageStructure(
            title=title,
            url=url,
            forms=forms,
            navigation=navigation,
            interactive_elements=interactive_elements,
            main_content_area=main_content,
            has_login_form=has_login,
            has_search=has_search,
            has_pagination=has_pagination,
            detected_patterns=detected_patterns
        )
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        # Fallback to h1
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text(strip=True)
        
        return "Untitled Page"
    
    def _analyze_forms(self, soup: BeautifulSoup) -> List[Form]:
        """Analyze all forms on the page."""
        forms = []
        
        for form_tag in soup.find_all('form'):
            form_id = form_tag.get('id')
            form_name = form_tag.get('name')
            action = form_tag.get('action', '')
            method = form_tag.get('method', 'get').lower()
            
            # Analyze form fields
            fields = self._analyze_form_fields(form_tag)
            
            # Find submit button
            submit_button = form_tag.find(['button', 'input'], {'type': ['submit', 'button']})
            submit_text = None
            if submit_button:
                if submit_button.name == 'button':
                    submit_text = submit_button.get_text(strip=True)
                else:
                    submit_text = submit_button.get('value', 'Submit')
            
            forms.append(Form(
                form_id=form_id,
                name=form_name,
                action=action,
                method=method,
                fields=fields,
                submit_button_text=submit_text
            ))
        
        return forms
    
    def _analyze_form_fields(self, form_tag: Tag) -> List[FormField]:
        """Analyze fields within a form."""
        fields = []
        
        # Find all input fields
        for input_tag in form_tag.find_all(['input', 'textarea', 'select']):
            field_type = input_tag.get('type', 'text')
            
            # Skip submit/button types
            if field_type in ['submit', 'button', 'reset']:
                continue
            
            name = input_tag.get('name', '')
            field_id = input_tag.get('id', '')
            
            # Find associated label
            label = self._find_field_label(form_tag, input_tag, field_id)
            
            # Extract field properties
            required = input_tag.has_attr('required')
            placeholder = input_tag.get('placeholder')
            value = input_tag.get('value')
            pattern = input_tag.get('pattern')
            autocomplete = input_tag.get('autocomplete')
            
            # For select elements, get options
            options = None
            if input_tag.name == 'select':
                options = []
                for option in input_tag.find_all('option'):
                    opt_value = option.get('value', option.get_text(strip=True))
                    if opt_value:
                        options.append(opt_value)
            
            fields.append(FormField(
                name=name or field_id,
                field_type=field_type if input_tag.name != 'select' else 'select',
                label=label,
                required=required,
                placeholder=placeholder,
                value=value,
                options=options,
                validation_pattern=pattern,
                autocomplete=autocomplete
            ))
        
        return fields
    
    def _find_field_label(self, form_tag: Tag, field_tag: Tag, field_id: str) -> str:
        """Find label for a form field."""
        # Method 1: Label with 'for' attribute
        if field_id:
            label = form_tag.find('label', {'for': field_id})
            if label:
                return label.get_text(strip=True)
        
        # Method 2: Field wrapped in label
        parent = field_tag.parent
        if parent and parent.name == 'label':
            return parent.get_text(strip=True).replace(field_tag.get_text(strip=True), '').strip()
        
        # Method 3: Look for text before the field
        prev = field_tag.previous_sibling
        if prev and isinstance(prev, str):
            text = prev.strip()
            if text and len(text) < 50:  # Reasonable label length
                return text
        
        # Method 4: Use placeholder as fallback
        placeholder = field_tag.get('placeholder')
        if placeholder:
            return placeholder
        
        # Method 5: Use field name
        name = field_tag.get('name', '')
        if name:
            # Convert snake_case or camelCase to readable
            return re.sub(r'[_-]', ' ', name).title()
        
        return field_tag.get('type', 'Field')
    
    def _analyze_navigation(self, soup: BeautifulSoup, base_url: str) -> List[NavigationElement]:
        """Analyze navigation elements."""
        navigation = []
        seen_hrefs = set()
        
        # Find navigation containers
        nav_containers = soup.find_all(['nav', 'header', 'footer'])
        nav_containers.extend(soup.find_all(class_=re.compile(r'nav|menu', re.I)))
        
        for container in nav_containers:
            # Find links within navigation
            for link in container.find_all('a', href=True):
                href = link['href']
                
                # Skip if already processed
                if href in seen_hrefs:
                    continue
                seen_hrefs.add(href)
                
                # Resolve relative URLs
                absolute_url = urljoin(base_url, href)
                is_external = self._is_external_link(absolute_url, base_url)
                
                # Check for submenu
                has_submenu = bool(link.find_next_sibling(['ul', 'div'], class_=re.compile(r'submenu|dropdown', re.I)))
                
                navigation.append(NavigationElement(
                    text=link.get_text(strip=True) or link.get('aria-label', 'Link'),
                    href=href,
                    element_type='link',
                    is_external=is_external,
                    has_submenu=has_submenu,
                    aria_label=link.get('aria-label')
                ))
        
        # Find navigation buttons
        for button in soup.find_all('button', class_=re.compile(r'nav|menu', re.I)):
            if not button.get_text(strip=True):
                continue
            
            navigation.append(NavigationElement(
                text=button.get_text(strip=True),
                href='#',
                element_type='button',
                is_external=False,
                aria_label=button.get('aria-label')
            ))
        
        return navigation
    
    def _is_external_link(self, url: str, base_url: str) -> bool:
        """Check if a URL is external."""
        try:
            url_domain = urlparse(url).netloc
            base_domain = urlparse(base_url).netloc
            return url_domain != '' and url_domain != base_domain
        except:
            return False
    
    def _find_interactive_elements(self, soup: BeautifulSoup) -> List[InteractiveElement]:
        """Find interactive elements on the page."""
        elements = []
        seen_selectors = set()
        
        # Buttons
        for button in soup.find_all(['button', 'input'], type=['button', 'submit']):
            selector = self._generate_selector(button)
            if selector in seen_selectors:
                continue
            seen_selectors.add(selector)
            
            elements.append(InteractiveElement(
                element_type='button',
                selector=selector,
                text=button.get_text(strip=True) if button.name == 'button' else button.get('value'),
                aria_label=button.get('aria-label'),
                role=button.get('role'),
                attributes={k: v for k, v in button.attrs.items() if k.startswith('data-')}
            ))
        
        # Links with onclick or data attributes
        for link in soup.find_all('a', attrs={'onclick': True}):
            selector = self._generate_selector(link)
            if selector in seen_selectors:
                continue
            seen_selectors.add(selector)
            
            elements.append(InteractiveElement(
                element_type='clickable_link',
                selector=selector,
                text=link.get_text(strip=True),
                aria_label=link.get('aria-label'),
                role=link.get('role'),
                attributes={k: v for k, v in link.attrs.items() if k.startswith('data-')}
            ))
        
        # Elements with interactive roles
        for elem in soup.find_all(attrs={'role': ['button', 'tab', 'menuitem', 'switch']}):
            if elem.name in ['button', 'a', 'input']:  # Already processed
                continue
            
            selector = self._generate_selector(elem)
            if selector in seen_selectors:
                continue
            seen_selectors.add(selector)
            
            elements.append(InteractiveElement(
                element_type=f"role_{elem.get('role')}",
                selector=selector,
                text=elem.get_text(strip=True),
                aria_label=elem.get('aria-label'),
                role=elem.get('role'),
                attributes={k: v for k, v in elem.attrs.items() if k.startswith('data-')}
            ))
        
        return elements
    
    def _generate_selector(self, element: Tag) -> str:
        """Generate a CSS selector for an element."""
        # Prefer ID
        if element.get('id'):
            return f"#{element['id']}"
        
        # Use unique class combination
        classes = element.get('class', [])
        if classes:
            class_selector = '.' + '.'.join(classes)
            # Check if unique
            if len(element.parent.select(class_selector)) == 1:
                return class_selector
        
        # Use data attributes
        for attr, value in element.attrs.items():
            if attr.startswith('data-') and value:
                selector = f"{element.name}[{attr}='{value}']"
                if len(element.parent.select(selector)) == 1:
                    return selector
        
        # Use text content for buttons/links
        if element.name in ['button', 'a']:
            text = element.get_text(strip=True)
            if text:
                return f"{element.name}:contains('{text[:20]}')"
        
        # Fallback to tag name with index
        siblings = element.parent.find_all(element.name)
        index = siblings.index(element)
        return f"{element.name}:nth-of-type({index + 1})"
    
    def _find_main_content_area(self, soup: BeautifulSoup) -> Optional[str]:
        """Identify the main content area of the page."""
        # Check for semantic HTML5 tags
        main_tag = soup.find('main')
        if main_tag:
            return self._generate_selector(main_tag)
        
        # Check for common content identifiers
        content_selectors = [
            '#content', '#main', '#main-content',
            '.content', '.main', '.main-content',
            '[role="main"]'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                return selector
        
        # Look for largest content area
        # (simplified heuristic - could be improved)
        article = soup.find('article')
        if article:
            return self._generate_selector(article)
        
        return None
    
    def _detect_patterns(self, soup: BeautifulSoup, forms: List[Form], 
                        navigation: List[NavigationElement]) -> List[str]:
        """Detect common UI patterns."""
        patterns = []
        
        # Check form patterns
        for form in forms:
            if self._is_login_form(form):
                patterns.append('login_form')
            elif self._is_registration_form(form):
                patterns.append('registration_form')
            elif self._is_search_form(form):
                patterns.append('search_form')
            elif self._is_contact_form(form):
                patterns.append('contact_form')
        
        # Check for modals
        if soup.find_all(class_=re.compile(r'modal|dialog|popup', re.I)):
            patterns.append('modal_dialogs')
        
        # Check for tabs
        if soup.find_all(role='tab') or soup.find_all(class_=re.compile(r'tab', re.I)):
            patterns.append('tabbed_interface')
        
        # Check for accordions
        if soup.find_all(class_=re.compile(r'accordion|collapse', re.I)):
            patterns.append('accordion')
        
        # Check for carousel/slider
        if soup.find_all(class_=re.compile(r'carousel|slider|swiper', re.I)):
            patterns.append('carousel')
        
        # Check for data tables
        tables = soup.find_all('table')
        if any(table.find('thead') for table in tables):
            patterns.append('data_table')
        
        # Check for infinite scroll indicators
        if soup.find_all(attrs={'data-infinite-scroll': True}) or \
           soup.find_all(class_=re.compile(r'infinite-scroll', re.I)):
            patterns.append('infinite_scroll')
        
        # Check for AJAX indicators
        if soup.find_all(attrs=lambda x: x and 'ajax' in str(x).lower()):
            patterns.append('ajax_interactions')
        
        return patterns
    
    def _is_login_form(self, form: Form) -> bool:
        """Check if a form is a login form."""
        login_indicators = 0
        
        # Check form attributes
        form_text = f"{form.action} {form.name or ''} {form.form_id or ''}"
        for pattern in self.form_patterns['login']:
            if pattern.search(form_text):
                login_indicators += 1
        
        # Check fields
        has_username = False
        has_password = False
        
        for field in form.fields:
            field_text = f"{field.name} {field.label}"
            
            if field.field_type == 'password':
                has_password = True
            elif field.field_type in ['text', 'email']:
                if any(p.search(field_text) for p in self.form_patterns['login'][1:2]):
                    has_username = True
        
        return has_username and has_password
    
    def _is_registration_form(self, form: Form) -> bool:
        """Check if a form is a registration form."""
        # Check for registration keywords
        form_text = f"{form.action} {form.name or ''} {form.form_id or ''} {form.submit_button_text or ''}"
        has_registration_keyword = any(p.search(form_text) for p in self.form_patterns['registration'][:1])
        
        # Check for password confirmation field
        password_fields = [f for f in form.fields if f.field_type == 'password']
        has_password_confirm = len(password_fields) >= 2
        
        # Check for email field
        has_email = any(f.field_type == 'email' or 'email' in f.name.lower() for f in form.fields)
        
        return has_registration_keyword or (has_password_confirm and has_email)
    
    def _is_search_form(self, form: Form) -> bool:
        """Check if a form is a search form."""
        # Check form attributes
        form_text = f"{form.action} {form.name or ''} {form.form_id or ''}"
        for pattern in self.form_patterns['search']:
            if pattern.search(form_text):
                return True
        
        # Check if has single text field
        text_fields = [f for f in form.fields if f.field_type in ['text', 'search']]
        if len(text_fields) == 1:
            field = text_fields[0]
            field_text = f"{field.name} {field.label} {field.placeholder or ''}"
            if any(p.search(field_text) for p in self.form_patterns['search']):
                return True
        
        return False
    
    def _is_contact_form(self, form: Form) -> bool:
        """Check if a form is a contact form."""
        indicators = 0
        
        # Check form text
        form_text = f"{form.action} {form.name or ''} {form.form_id or ''} {form.submit_button_text or ''}"
        for pattern in self.form_patterns['contact']:
            if pattern.search(form_text):
                indicators += 1
        
        # Check for typical contact form fields
        has_name = any('name' in f.name.lower() or 'name' in f.label.lower() for f in form.fields)
        has_email = any(f.field_type == 'email' or 'email' in f.name.lower() for f in form.fields)
        has_message = any(f.field_type == 'textarea' or 'message' in f.name.lower() for f in form.fields)
        
        return indicators >= 2 or (has_name and has_email and has_message)
    
    def _has_pagination(self, soup: BeautifulSoup) -> bool:
        """Check if page has pagination."""
        # Check for pagination containers
        pagination_selectors = [
            '.pagination', '.pager', '[role="navigation"]',
            'nav[aria-label*="pagination"]'
        ]
        
        for selector in pagination_selectors:
            if soup.select(selector):
                return True
        
        # Check for page number links
        page_links = soup.find_all('a', text=re.compile(r'^\d+$'))
        if len(page_links) >= 3:  # Multiple page numbers
            return True
        
        # Check for next/previous links
        nav_keywords = ['next', 'previous', 'prev', '»', '«', '›', '‹']
        for keyword in nav_keywords:
            if soup.find('a', text=re.compile(keyword, re.I)):
                return True
        
        return False
    
    def get_test_scenarios(self, page_structure: PageStructure) -> List[Dict[str, Any]]:
        """Generate test scenarios based on page analysis."""
        scenarios = []
        
        # Form-based scenarios
        for form in page_structure.forms:
            if self._is_login_form(form):
                scenarios.append({
                    'name': 'Login Flow',
                    'category': 'authentication',
                    'priority': 'high',
                    'steps': [
                        'Navigate to login form',
                        'Enter valid credentials',
                        'Submit form',
                        'Verify successful login'
                    ]
                })
                scenarios.append({
                    'name': 'Login with Invalid Credentials',
                    'category': 'authentication',
                    'priority': 'high',
                    'steps': [
                        'Navigate to login form',
                        'Enter invalid credentials',
                        'Submit form',
                        'Verify error message'
                    ]
                })
            
            elif self._is_registration_form(form):
                scenarios.append({
                    'name': 'User Registration',
                    'category': 'authentication',
                    'priority': 'high',
                    'steps': [
                        'Navigate to registration form',
                        'Fill in all required fields',
                        'Submit form',
                        'Verify account creation'
                    ]
                })
            
            elif self._is_search_form(form):
                scenarios.append({
                    'name': 'Search Functionality',
                    'category': 'search',
                    'priority': 'medium',
                    'steps': [
                        'Enter search query',
                        'Submit search',
                        'Verify search results displayed'
                    ]
                })
        
        # Navigation scenarios
        if len(page_structure.navigation) > 3:
            scenarios.append({
                'name': 'Main Navigation',
                'category': 'navigation',
                'priority': 'medium',
                'steps': [
                    'Click each main navigation link',
                    'Verify page loads correctly',
                    'Verify active state updates'
                ]
            })
        
        # Interactive element scenarios
        if any('modal' in p for p in page_structure.detected_patterns):
            scenarios.append({
                'name': 'Modal Interactions',
                'category': 'ui_interaction',
                'priority': 'low',
                'steps': [
                    'Trigger modal opening',
                    'Verify modal displays',
                    'Interact with modal content',
                    'Close modal'
                ]
            })
        
        if any('tab' in p for p in page_structure.detected_patterns):
            scenarios.append({
                'name': 'Tab Navigation',
                'category': 'ui_interaction',
                'priority': 'low',
                'steps': [
                    'Click through all tabs',
                    'Verify content changes',
                    'Verify tab state updates'
                ]
            })
        
        return scenarios