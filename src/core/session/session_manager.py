"""
Session Manager for AI Playwright Engine
Handles authentication state, cookies, and session persistence across test executions.
"""

import asyncio
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import aiofiles

from playwright.async_api import BrowserContext, Page, Cookie
from utils.logger import setup_logger


@dataclass
class SessionData:
    """Container for session authentication data."""
    session_id: str
    url: str
    username: str
    created_at: datetime
    expires_at: datetime
    cookies: List[Dict[str, Any]]
    local_storage: Dict[str, str]
    session_storage: Dict[str, str]
    auth_tokens: Dict[str, str]
    is_valid: bool = True
    
    def is_expired(self) -> bool:
        """Check if the session has expired."""
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session data to dictionary for serialization."""
        return {
            'session_id': self.session_id,
            'url': self.url,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'cookies': self.cookies,
            'local_storage': self.local_storage,
            'session_storage': self.session_storage,
            'auth_tokens': self.auth_tokens,
            'is_valid': self.is_valid
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionData':
        """Create SessionData from dictionary."""
        return cls(
            session_id=data['session_id'],
            url=data['url'],
            username=data['username'],
            created_at=datetime.fromisoformat(data['created_at']),
            expires_at=datetime.fromisoformat(data['expires_at']),
            cookies=data['cookies'],
            local_storage=data['local_storage'],
            session_storage=data['session_storage'],
            auth_tokens=data['auth_tokens'],
            is_valid=data['is_valid']
        )


class SessionManager:
    """
    Manages authentication sessions and state persistence for Playwright tests.
    Handles login once and reuses the session for subsequent tests.
    """
    
    def __init__(self, session_timeout_minutes: int = 30):
        """
        Initialize the Session Manager.
        
        Args:
            session_timeout_minutes: Session validity duration in minutes
        """
        self.logger = setup_logger(__name__)
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.sessions_dir = Path("sessions")
        self.sessions_dir.mkdir(exist_ok=True)
        
        # In-memory session cache
        self.active_sessions: Dict[str, SessionData] = {}
        
        # Session persistence settings
        self.persist_sessions = True
        self.encryption_enabled = False  # Can be enhanced with encryption later
        
    async def initialize(self) -> None:
        """Initialize the session manager and load persisted sessions."""
        self.logger.info("Initializing Session Manager...")
        
        # Load persisted sessions
        await self._load_persisted_sessions()
        
        # Clean up expired sessions
        await self._cleanup_expired_sessions()
        
        self.logger.info("Session Manager initialized successfully")
    
    async def get_or_create_session(
        self,
        url: str,
        username: str,
        password: str,
        browser_context: BrowserContext,
        force_new: bool = False
    ) -> Tuple[SessionData, bool]:
        """
        Get existing session or create a new one.
        
        Args:
            url: Target application URL
            username: Login username
            password: Login password
            browser_context: Playwright browser context
            force_new: Force creation of new session
            
        Returns:
            Tuple of (SessionData, is_new_session)
        """
        session_key = self._generate_session_key(url, username)
        
        # Check for existing valid session
        if not force_new:
            existing_session = await self._get_valid_session(session_key)
            if existing_session:
                self.logger.info(f"Reusing existing session for {username}@{url}")
                await self._restore_session_to_context(existing_session, browser_context)
                return existing_session, False
        
        # Create new session
        self.logger.info(f"Creating new session for {username}@{url}")
        new_session = await self._create_new_session(
            url, username, password, browser_context
        )
        
        # Cache and persist the session
        self.active_sessions[session_key] = new_session
        if self.persist_sessions:
            await self._persist_session(new_session)
        
        return new_session, True
    
    async def execute_with_session(
        self,
        url: str,
        username: str,
        password: str,
        browser_context: BrowserContext,
        login_function: Optional[Any] = None
    ) -> SessionData:
        """
        Execute login if needed and return authenticated session.
        
        Args:
            url: Target application URL
            username: Login username
            password: Login password
            browser_context: Playwright browser context
            login_function: Custom login function (optional)
            
        Returns:
            Authenticated SessionData
        """
        session, is_new = await self.get_or_create_session(
            url, username, password, browser_context
        )
        
        if is_new and login_function:
            # Execute custom login function
            page = await browser_context.new_page()
            try:
                await login_function(page, url, username, password)
                # Capture session data after login
                session = await self._capture_session_data(
                    browser_context, url, username
                )
                # Update cache and persist
                session_key = self._generate_session_key(url, username)
                self.active_sessions[session_key] = session
                if self.persist_sessions:
                    await self._persist_session(session)
            finally:
                await page.close()
        
        return session
    
    async def inject_auth_steps(
        self,
        test_code: str,
        session_data: SessionData,
        test_type: str
    ) -> str:
        """
        Inject authentication steps into test code if needed.
        
        Args:
            test_code: Original test code
            session_data: Session data with auth information
            test_type: Type of test being modified
            
        Returns:
            Modified test code with auth steps
        """
        if test_type == 'login':
            # Login tests don't need session injection
            return test_code
        
        # Find the appropriate injection point
        lines = test_code.split('\n')
        modified_lines = []
        
        # Look for page navigation or test start
        for i, line in enumerate(lines):
            modified_lines.append(line)
            
            # Inject after page creation
            if 'page = await' in line and 'new_page()' in line:
                # Add session restoration code
                modified_lines.extend([
                    '',
                    '    # Restore authentication session',
                    f'    await context.add_cookies({json.dumps(session_data.cookies)})',
                    ''
                ])
                
                # Add local storage restoration if needed
                if session_data.local_storage:
                    modified_lines.extend([
                        '    # Restore local storage',
                        f'    await page.goto("{session_data.url}")',
                        '    await page.evaluate("""(storage) => {',
                        '        for (const [key, value] of Object.entries(storage)) {',
                        '            localStorage.setItem(key, value);',
                        '        }',
                        f'    }}""", {json.dumps(session_data.local_storage)})',
                        ''
                    ])
        
        return '\n'.join(modified_lines)
    
    async def _create_new_session(
        self,
        url: str,
        username: str,
        password: str,
        browser_context: BrowserContext
    ) -> SessionData:
        """
        Create a new session by performing login.
        
        Args:
            url: Target application URL
            username: Login username
            password: Login password
            browser_context: Playwright browser context
            
        Returns:
            New SessionData object
        """
        page = await browser_context.new_page()
        
        try:
            # Navigate to the URL
            await page.goto(url, wait_until='networkidle')
            
            # Attempt standard login detection and execution
            login_successful = await self._perform_standard_login(
                page, username, password
            )
            
            if not login_successful:
                self.logger.warning("Standard login failed, session may not be authenticated")
            
            # Capture session data
            session_data = await self._capture_session_data(
                browser_context, url, username
            )
            
            return session_data
            
        finally:
            await page.close()
    
    async def _perform_standard_login(
        self,
        page: Page,
        username: str,
        password: str
    ) -> bool:
        """
        Perform standard login flow detection and execution.
        
        Args:
            page: Playwright page object
            username: Login username
            password: Login password
            
        Returns:
            True if login was successful
        """
        try:
            # Common login selectors
            username_selectors = [
                'input[type="email"]',
                'input[type="text"][name*="user"]',
                'input[type="text"][name*="email"]',
                'input[type="text"][name*="login"]',
                'input[id*="user"]',
                'input[id*="email"]',
                'input[id*="login"]',
                '#username',
                '#email'
            ]
            
            password_selectors = [
                'input[type="password"]',
                'input[name*="pass"]',
                'input[id*="pass"]',
                '#password'
            ]
            
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Sign in")',
                'button:has-text("Log in")',
                'button:has-text("Login")',
                '*[type="submit"]'
            ]
            
            # Find and fill username field
            username_field = None
            for selector in username_selectors:
                if await page.locator(selector).count() > 0:
                    username_field = page.locator(selector).first
                    break
            
            if not username_field:
                self.logger.warning("Could not find username field")
                return False
            
            await username_field.fill(username)
            
            # Find and fill password field
            password_field = None
            for selector in password_selectors:
                if await page.locator(selector).count() > 0:
                    password_field = page.locator(selector).first
                    break
            
            if not password_field:
                self.logger.warning("Could not find password field")
                return False
            
            await password_field.fill(password)
            
            # Find and click submit button
            submit_button = None
            for selector in submit_selectors:
                if await page.locator(selector).count() > 0:
                    submit_button = page.locator(selector).first
                    break
            
            if submit_button:
                await submit_button.click()
            else:
                # Try pressing Enter
                await password_field.press('Enter')
            
            # Wait for navigation or URL change
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Simple success detection - URL changed or login form disappeared
            current_url = page.url
            login_form_visible = await username_field.is_visible() if username_field else False
            
            return current_url != page.url or not login_form_visible
            
        except Exception as e:
            self.logger.error(f"Error during standard login: {str(e)}")
            return False
    
    async def _capture_session_data(
        self,
        browser_context: BrowserContext,
        url: str,
        username: str
    ) -> SessionData:
        """
        Capture current session data from browser context.
        
        Args:
            browser_context: Playwright browser context
            url: Application URL
            username: Username for the session
            
        Returns:
            SessionData object
        """
        # Get cookies
        cookies = await browser_context.cookies()
        
        # Get storage data (requires a page)
        page = await browser_context.new_page()
        await page.goto(url, wait_until='domcontentloaded')
        
        # Capture local storage
        local_storage = await page.evaluate("""
            () => {
                const storage = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    storage[key] = localStorage.getItem(key);
                }
                return storage;
            }
        """)
        
        # Capture session storage
        session_storage = await page.evaluate("""
            () => {
                const storage = {};
                for (let i = 0; i < sessionStorage.length; i++) {
                    const key = sessionStorage.key(i);
                    storage[key] = sessionStorage.getItem(key);
                }
                return storage;
            }
        """)
        
        await page.close()
        
        # Extract auth tokens from cookies/storage
        auth_tokens = self._extract_auth_tokens(cookies, local_storage)
        
        # Create session data
        session_data = SessionData(
            session_id=f"{username}_{int(datetime.now().timestamp())}",
            url=url,
            username=username,
            created_at=datetime.now(),
            expires_at=datetime.now() + self.session_timeout,
            cookies=cookies,
            local_storage=local_storage,
            session_storage=session_storage,
            auth_tokens=auth_tokens
        )
        
        return session_data
    
    async def _restore_session_to_context(
        self,
        session_data: SessionData,
        browser_context: BrowserContext
    ) -> None:
        """
        Restore session data to a browser context.
        
        Args:
            session_data: Session data to restore
            browser_context: Target browser context
        """
        # Restore cookies
        if session_data.cookies:
            await browser_context.add_cookies(session_data.cookies)
        
        # Note: Local storage and session storage need to be restored
        # after navigating to the page in the actual test
    
    async def _get_valid_session(self, session_key: str) -> Optional[SessionData]:
        """
        Get a valid session by key.
        
        Args:
            session_key: Session identifier key
            
        Returns:
            Valid SessionData or None
        """
        # Check in-memory cache first
        if session_key in self.active_sessions:
            session = self.active_sessions[session_key]
            if not session.is_expired() and session.is_valid:
                return session
            else:
                # Remove expired session
                del self.active_sessions[session_key]
        
        # Check persisted sessions
        if self.persist_sessions:
            session = await self._load_session_from_disk(session_key)
            if session and not session.is_expired() and session.is_valid:
                # Cache in memory
                self.active_sessions[session_key] = session
                return session
        
        return None
    
    async def _persist_session(self, session_data: SessionData) -> None:
        """
        Persist session data to disk.
        
        Args:
            session_data: Session data to persist
        """
        session_key = self._generate_session_key(session_data.url, session_data.username)
        session_file = self.sessions_dir / f"{session_key}.json"
        
        try:
            async with aiofiles.open(session_file, 'w') as f:
                await f.write(json.dumps(session_data.to_dict(), indent=2))
            
            self.logger.debug(f"Persisted session to {session_file}")
        except Exception as e:
            self.logger.error(f"Failed to persist session: {str(e)}")
    
    async def _load_session_from_disk(self, session_key: str) -> Optional[SessionData]:
        """
        Load session data from disk.
        
        Args:
            session_key: Session identifier key
            
        Returns:
            SessionData or None
        """
        session_file = self.sessions_dir / f"{session_key}.json"
        
        if not session_file.exists():
            return None
        
        try:
            async with aiofiles.open(session_file, 'r') as f:
                data = json.loads(await f.read())
            
            return SessionData.from_dict(data)
        except Exception as e:
            self.logger.error(f"Failed to load session from disk: {str(e)}")
            return None
    
    async def _load_persisted_sessions(self) -> None:
        """Load all persisted sessions from disk."""
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                async with aiofiles.open(session_file, 'r') as f:
                    data = json.loads(await f.read())
                
                session = SessionData.from_dict(data)
                if not session.is_expired() and session.is_valid:
                    session_key = session_file.stem
                    self.active_sessions[session_key] = session
            except Exception as e:
                self.logger.error(f"Failed to load session {session_file}: {str(e)}")
    
    async def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions from memory and disk."""
        # Clean up in-memory sessions
        expired_keys = [
            key for key, session in self.active_sessions.items()
            if session.is_expired()
        ]
        
        for key in expired_keys:
            del self.active_sessions[key]
            # Remove from disk
            session_file = self.sessions_dir / f"{key}.json"
            if session_file.exists():
                session_file.unlink()
        
        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired sessions")
    
    def _generate_session_key(self, url: str, username: str) -> str:
        """
        Generate a unique session key.
        
        Args:
            url: Application URL
            username: Username
            
        Returns:
            Session key string
        """
        # Extract domain from URL
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        # Create session key
        return f"{domain}_{username}".replace('.', '_').replace(':', '_')
    
    def _extract_auth_tokens(
        self,
        cookies: List[Dict[str, Any]],
        local_storage: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Extract authentication tokens from cookies and storage.
        
        Args:
            cookies: Browser cookies
            local_storage: Local storage data
            
        Returns:
            Dictionary of auth tokens
        """
        auth_tokens = {}
        
        # Common auth cookie names
        auth_cookie_names = [
            'session', 'sessionid', 'auth', 'token',
            'access_token', 'refresh_token', 'jwt',
            'authorization', 'auth_token'
        ]
        
        # Extract from cookies
        for cookie in cookies:
            name = cookie.get('name', '').lower()
            if any(auth_name in name for auth_name in auth_cookie_names):
                auth_tokens[f"cookie_{cookie['name']}"] = cookie['value']
        
        # Extract from local storage
        for key, value in local_storage.items():
            key_lower = key.lower()
            if any(auth_name in key_lower for auth_name in auth_cookie_names):
                auth_tokens[f"storage_{key}"] = value
        
        return auth_tokens
    
    async def invalidate_session(self, url: str, username: str) -> None:
        """
        Invalidate a session.
        
        Args:
            url: Application URL
            username: Username
        """
        session_key = self._generate_session_key(url, username)
        
        # Remove from memory
        if session_key in self.active_sessions:
            del self.active_sessions[session_key]
        
        # Remove from disk
        session_file = self.sessions_dir / f"{session_key}.json"
        if session_file.exists():
            session_file.unlink()
        
        self.logger.info(f"Invalidated session for {username}@{url}")
    
    async def shutdown(self) -> None:
        """Shutdown the session manager and cleanup resources."""
        self.logger.info("Shutting down Session Manager...")
        
        # Persist all active sessions
        if self.persist_sessions:
            for session in self.active_sessions.values():
                await self._persist_session(session)
        
        self.active_sessions.clear()
        self.logger.info("Session Manager shutdown completed")