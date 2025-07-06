"""
Unit tests for SessionManager
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from playwright.async_api import BrowserContext, Page
from core.session.session_manager import SessionManager, SessionData


@pytest.fixture
async def session_manager():
    """Create a SessionManager instance for testing."""
    manager = SessionManager(session_timeout_minutes=30)
    await manager.initialize()
    yield manager
    # Cleanup
    if manager.sessions_dir.exists():
        import shutil
        shutil.rmtree(manager.sessions_dir, ignore_errors=True)


@pytest.fixture
def mock_browser_context():
    """Create a mock browser context."""
    context = AsyncMock(spec=BrowserContext)
    context.cookies = AsyncMock(return_value=[
        {'name': 'session_id', 'value': 'test123', 'domain': 'example.com'},
        {'name': 'auth_token', 'value': 'abc456', 'domain': 'example.com'}
    ])
    context.add_cookies = AsyncMock()
    context.new_page = AsyncMock()
    return context


@pytest.fixture
def mock_page():
    """Create a mock page."""
    page = AsyncMock(spec=Page)
    page.goto = AsyncMock()
    page.url = 'https://example.com/dashboard'
    page.locator = MagicMock()
    page.evaluate = AsyncMock(return_value={
        'user_id': '12345',
        'auth_token': 'stored_token'
    })
    page.wait_for_load_state = AsyncMock()
    page.close = AsyncMock()
    return page


@pytest.fixture
def sample_session_data():
    """Create sample session data."""
    return SessionData(
        session_id='test_session_123',
        url='https://example.com',
        username='testuser',
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(minutes=30),
        cookies=[
            {'name': 'session_id', 'value': 'test123'},
            {'name': 'auth_token', 'value': 'abc456'}
        ],
        local_storage={'user_id': '12345'},
        session_storage={'temp_data': 'value'},
        auth_tokens={'cookie_session_id': 'test123'},
        is_valid=True
    )


class TestSessionData:
    """Test SessionData class functionality."""
    
    def test_is_expired(self, sample_session_data):
        """Test session expiration check."""
        # Not expired
        assert not sample_session_data.is_expired()
        
        # Expired
        sample_session_data.expires_at = datetime.now() - timedelta(minutes=1)
        assert sample_session_data.is_expired()
    
    def test_to_dict(self, sample_session_data):
        """Test conversion to dictionary."""
        data_dict = sample_session_data.to_dict()
        
        assert data_dict['session_id'] == 'test_session_123'
        assert data_dict['url'] == 'https://example.com'
        assert data_dict['username'] == 'testuser'
        assert len(data_dict['cookies']) == 2
        assert data_dict['is_valid'] is True
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data_dict = {
            'session_id': 'test_123',
            'url': 'https://example.com',
            'username': 'testuser',
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(minutes=30)).isoformat(),
            'cookies': [{'name': 'test', 'value': 'value'}],
            'local_storage': {},
            'session_storage': {},
            'auth_tokens': {},
            'is_valid': True
        }
        
        session_data = SessionData.from_dict(data_dict)
        assert session_data.session_id == 'test_123'
        assert session_data.username == 'testuser'
        assert len(session_data.cookies) == 1


class TestSessionManager:
    """Test SessionManager functionality."""
    
    @pytest.mark.asyncio
    async def test_initialize(self, session_manager):
        """Test session manager initialization."""
        assert session_manager.sessions_dir.exists()
        assert session_manager.session_timeout == timedelta(minutes=30)
        assert session_manager.persist_sessions is True
    
    @pytest.mark.asyncio
    async def test_generate_session_key(self, session_manager):
        """Test session key generation."""
        key = session_manager._generate_session_key(
            'https://example.com/app',
            'testuser'
        )
        assert key == 'example_com_testuser'
        
        # Test with port
        key = session_manager._generate_session_key(
            'https://example.com:8080/app',
            'user@email.com'
        )
        assert key == 'example_com_8080_user@email.com'
    
    @pytest.mark.asyncio
    async def test_get_or_create_session_new(
        self,
        session_manager,
        mock_browser_context,
        mock_page
    ):
        """Test creating a new session."""
        mock_browser_context.new_page.return_value = mock_page
        
        session, is_new = await session_manager.get_or_create_session(
            'https://example.com',
            'testuser',
            'password',
            mock_browser_context,
            force_new=True
        )
        
        assert is_new is True
        assert session.username == 'testuser'
        assert session.url == 'https://example.com'
        assert len(session.cookies) > 0
        
        # Verify browser interactions
        mock_browser_context.new_page.assert_called()
        mock_page.goto.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_or_create_session_existing(
        self,
        session_manager,
        mock_browser_context,
        sample_session_data
    ):
        """Test reusing an existing session."""
        # Pre-populate session
        session_key = session_manager._generate_session_key(
            sample_session_data.url,
            sample_session_data.username
        )
        session_manager.active_sessions[session_key] = sample_session_data
        
        session, is_new = await session_manager.get_or_create_session(
            sample_session_data.url,
            sample_session_data.username,
            'password',
            mock_browser_context,
            force_new=False
        )
        
        assert is_new is False
        assert session.session_id == sample_session_data.session_id
        mock_browser_context.add_cookies.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_inject_auth_steps(self, session_manager, sample_session_data):
        """Test injecting authentication steps into test code."""
        original_code = """
import asyncio
from playwright.async_api import async_playwright

async def test_navigation():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto('https://example.com/dashboard')
        await page.click('nav >> text=Products')
        
        await browser.close()
"""
        
        modified_code = await session_manager.inject_auth_steps(
            original_code,
            sample_session_data,
            'navigation'
        )
        
        # Check that session restoration was injected
        assert 'add_cookies' in modified_code
        assert 'Restore authentication session' in modified_code
        assert json.dumps(sample_session_data.cookies) in modified_code
    
    @pytest.mark.asyncio
    async def test_inject_auth_steps_login_test(
        self,
        session_manager,
        sample_session_data
    ):
        """Test that login tests are not modified."""
        login_code = """
async def test_login():
    # Login test code
    pass
"""
        
        modified_code = await session_manager.inject_auth_steps(
            login_code,
            sample_session_data,
            'login'
        )
        
        # Login tests should not be modified
        assert modified_code == login_code
    
    @pytest.mark.asyncio
    async def test_session_persistence(self, session_manager, sample_session_data):
        """Test saving and loading sessions from disk."""
        # Save session
        await session_manager._persist_session(sample_session_data)
        
        # Load session
        session_key = session_manager._generate_session_key(
            sample_session_data.url,
            sample_session_data.username
        )
        loaded_session = await session_manager._load_session_from_disk(session_key)
        
        assert loaded_session is not None
        assert loaded_session.session_id == sample_session_data.session_id
        assert loaded_session.username == sample_session_data.username
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, session_manager):
        """Test cleanup of expired sessions."""
        # Create expired session
        expired_session = SessionData(
            session_id='expired_123',
            url='https://example.com',
            username='expireduser',
            created_at=datetime.now() - timedelta(hours=2),
            expires_at=datetime.now() - timedelta(hours=1),
            cookies=[],
            local_storage={},
            session_storage={},
            auth_tokens={},
            is_valid=True
        )
        
        # Create valid session
        valid_session = SessionData(
            session_id='valid_123',
            url='https://example.com',
            username='validuser',
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            cookies=[],
            local_storage={},
            session_storage={},
            auth_tokens={},
            is_valid=True
        )
        
        # Add to cache
        session_manager.active_sessions['expired_key'] = expired_session
        session_manager.active_sessions['valid_key'] = valid_session
        
        # Persist both
        await session_manager._persist_session(expired_session)
        await session_manager._persist_session(valid_session)
        
        # Run cleanup
        await session_manager._cleanup_expired_sessions()
        
        # Check results
        assert 'expired_key' not in session_manager.active_sessions
        assert 'valid_key' in session_manager.active_sessions
    
    @pytest.mark.asyncio
    async def test_invalidate_session(self, session_manager, sample_session_data):
        """Test session invalidation."""
        # Add session
        session_key = session_manager._generate_session_key(
            sample_session_data.url,
            sample_session_data.username
        )
        session_manager.active_sessions[session_key] = sample_session_data
        
        # Persist it
        await session_manager._persist_session(sample_session_data)
        
        # Invalidate
        await session_manager.invalidate_session(
            sample_session_data.url,
            sample_session_data.username
        )
        
        # Check it's removed
        assert session_key not in session_manager.active_sessions
        session_file = session_manager.sessions_dir / f"{session_key}.json"
        assert not session_file.exists()
    
    @pytest.mark.asyncio
    async def test_extract_auth_tokens(self, session_manager):
        """Test extraction of auth tokens from cookies and storage."""
        cookies = [
            {'name': 'session_id', 'value': 'abc123'},
            {'name': 'auth_token', 'value': 'xyz789'},
            {'name': 'regular_cookie', 'value': 'value'}
        ]
        
        local_storage = {
            'access_token': 'token123',
            'user_pref': 'dark_mode'
        }
        
        tokens = session_manager._extract_auth_tokens(cookies, local_storage)
        
        assert 'cookie_session_id' in tokens
        assert tokens['cookie_session_id'] == 'abc123'
        assert 'cookie_auth_token' in tokens
        assert tokens['cookie_auth_token'] == 'xyz789'
        assert 'storage_access_token' in tokens
        assert tokens['storage_access_token'] == 'token123'
        assert 'cookie_regular_cookie' not in tokens


@pytest.mark.asyncio
async def test_standard_login_detection(session_manager, mock_page):
    """Test standard login form detection and execution."""
    # Setup mock locators
    username_locator = MagicMock()
    username_locator.count = AsyncMock(return_value=1)
    username_locator.first = MagicMock()
    username_locator.first.fill = AsyncMock()
    username_locator.first.is_visible = AsyncMock(return_value=False)
    
    password_locator = MagicMock()
    password_locator.count = AsyncMock(return_value=1)
    password_locator.first = MagicMock()
    password_locator.first.fill = AsyncMock()
    
    submit_locator = MagicMock()
    submit_locator.count = AsyncMock(return_value=1)
    submit_locator.first = MagicMock()
    submit_locator.first.click = AsyncMock()
    
    # Configure page.locator to return appropriate mocks
    def locator_side_effect(selector):
        if 'email' in selector or 'text' in selector:
            return username_locator
        elif 'password' in selector:
            return password_locator
        elif 'submit' in selector or 'button' in selector:
            return submit_locator
        return MagicMock(count=AsyncMock(return_value=0))
    
    mock_page.locator.side_effect = locator_side_effect
    mock_page.url = 'https://example.com/dashboard'  # Changed after login
    
    result = await session_manager._perform_standard_login(
        mock_page,
        'testuser',
        'testpass'
    )
    
    assert result is True
    username_locator.first.fill.assert_called_with('testuser')
    password_locator.first.fill.assert_called_with('testpass')
    submit_locator.first.click.assert_called_once()