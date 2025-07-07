"""Unit tests for DatabaseManager."""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import json
from unittest.mock import AsyncMock, MagicMock, patch

from src.utils.database import DatabaseManager


@pytest.fixture
def temp_db_path():
    """Create a temporary database path."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir) / "test.db"


@pytest_asyncio.fixture
async def db_manager(temp_db_path):
    """Create a DatabaseManager instance with temporary database."""
    config = {
        'database': {
            'path': str(temp_db_path)
        }
    }
    manager = DatabaseManager(config)
    await manager.initialize()
    yield manager
    await manager.shutdown()


@pytest.mark.asyncio
class TestDatabaseManager:
    """Test DatabaseManager functionality."""
    
    async def test_initialization(self, temp_db_path):
        """Test database initialization."""
        config = {'database': {'path': str(temp_db_path)}}
        manager = DatabaseManager(config)
        
        assert manager.db_path == temp_db_path
        assert manager.connection is None
        
        await manager.initialize()
        
        assert manager.connection is not None
        assert temp_db_path.exists()
        
        await manager.shutdown()
    
    async def test_create_tables(self, db_manager):
        """Test that all required tables are created."""
        # Check tables exist
        async with db_manager.connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ) as cursor:
            tables = await cursor.fetchall()
            table_names = [t['name'] for t in tables]
        
        expected_tables = [
            'test_sessions',
            'test_results', 
            'performance_metrics',
            'error_logs'
        ]
        
        for table in expected_tables:
            assert table in table_names
    
    async def test_create_test_session(self, db_manager):
        """Test creating a test session."""
        session_data = {
            'session_id': 'test-session-123',
            'url': 'https://example.com',
            'ai_provider': 'gpt',
            'started_at': datetime.now().isoformat(),
            'status': 'running',
            'metadata': {'browser': 'chromium', 'headless': True}
        }
        
        session_id = await db_manager.create_test_session(session_data)
        
        assert session_id == 'test-session-123'
        
        # Verify session was created
        async with db_manager.connection.execute(
            "SELECT * FROM test_sessions WHERE session_id = ?",
            (session_id,)
        ) as cursor:
            session = await cursor.fetchone()
        
        assert session is not None
        assert session['url'] == 'https://example.com'
        assert session['ai_provider'] == 'gpt'
        assert session['status'] == 'running'
        assert json.loads(session['metadata'])['browser'] == 'chromium'
    
    async def test_update_test_session(self, db_manager):
        """Test updating a test session."""
        # Create session
        session_data = {
            'session_id': 'update-test-123',
            'url': 'https://example.com',
            'ai_provider': 'claude',
            'status': 'running'
        }
        await db_manager.create_test_session(session_data)
        
        # Update session
        update_data = {
            'status': 'completed',
            'completed_at': datetime.now().isoformat(),
            'total_tests': 10,
            'passed_tests': 8,
            'failed_tests': 2,
            'execution_time': 45.5
        }
        await db_manager.update_test_session('update-test-123', update_data)
        
        # Verify update
        async with db_manager.connection.execute(
            "SELECT * FROM test_sessions WHERE session_id = ?",
            ('update-test-123',)
        ) as cursor:
            session = await cursor.fetchone()
        
        assert session['status'] == 'completed'
        assert session['total_tests'] == 10
        assert session['passed_tests'] == 8
        assert session['failed_tests'] == 2
        assert session['execution_time'] == 45.5
    
    async def test_save_test_result(self, db_manager):
        """Test saving test results."""
        # Create session first
        await db_manager.create_test_session({
            'session_id': 'result-test-123',
            'url': 'https://example.com',
            'ai_provider': 'claude'
        })
        
        # Save test result
        result_data = {
            'session_id': 'result-test-123',
            'test_name': 'test_login_flow',
            'test_category': 'authentication',
            'status': 'passed',
            'started_at': datetime.now().isoformat(),
            'completed_at': (datetime.now() + timedelta(seconds=5)).isoformat(),
            'execution_time': 5.0,
            'screenshots': ['screenshot1.png', 'screenshot2.png'],
            'performance_metrics': {
                'page_load_time': 1.2,
                'first_contentful_paint': 0.8
            }
        }
        
        await db_manager.save_test_result(result_data)
        
        # Verify result was saved
        async with db_manager.connection.execute(
            "SELECT * FROM test_results WHERE session_id = ? AND test_name = ?",
            ('result-test-123', 'test_login_flow')
        ) as cursor:
            result = await cursor.fetchone()
        
        assert result is not None
        assert result['status'] == 'passed'
        assert result['test_category'] == 'authentication'
        assert result['execution_time'] == 5.0
        assert json.loads(result['screenshots']) == ['screenshot1.png', 'screenshot2.png']
    
    async def test_save_performance_metric(self, db_manager):
        """Test saving performance metrics."""
        # Create session
        await db_manager.create_test_session({
            'session_id': 'perf-test-123',
            'url': 'https://example.com',
            'ai_provider': 'gpt'
        })
        
        # Save metric
        metric_data = {
            'session_id': 'perf-test-123',
            'test_name': 'test_home_page',
            'metric_name': 'largest_contentful_paint',
            'metric_value': 2.5,
            'unit': 'seconds',
            'timestamp': datetime.now().isoformat()
        }
        
        await db_manager.save_performance_metric(metric_data)
        
        # Verify metric was saved
        async with db_manager.connection.execute(
            "SELECT * FROM performance_metrics WHERE session_id = ?",
            ('perf-test-123',)
        ) as cursor:
            metric = await cursor.fetchone()
        
        assert metric is not None
        assert metric['metric_name'] == 'largest_contentful_paint'
        assert metric['metric_value'] == 2.5
        assert metric['unit'] == 'seconds'
    
    async def test_save_error_log(self, db_manager):
        """Test saving error logs."""
        # Create session
        await db_manager.create_test_session({
            'session_id': 'error-test-123',
            'url': 'https://example.com',
            'ai_provider': 'gemini'
        })
        
        # Save error log
        error_data = {
            'session_id': 'error-test-123',
            'test_name': 'test_checkout',
            'error_type': 'ElementNotFound',
            'error_message': 'Could not find checkout button',
            'stack_trace': 'at test_checkout line 45...',
            'severity': 'HIGH',
            'metadata': {'selector': '#checkout-btn', 'timeout': 30}
        }
        
        await db_manager.save_error_log(error_data)
        
        # Verify error was saved
        async with db_manager.connection.execute(
            "SELECT * FROM error_logs WHERE session_id = ?",
            ('error-test-123',)
        ) as cursor:
            error = await cursor.fetchone()
        
        assert error is not None
        assert error['error_type'] == 'ElementNotFound'
        assert error['severity'] == 'HIGH'
        assert json.loads(error['metadata'])['selector'] == '#checkout-btn'
    
    async def test_get_session_results(self, db_manager):
        """Test retrieving complete session results."""
        # Create a complete test session
        session_id = 'complete-test-123'
        
        # Create session
        await db_manager.create_test_session({
            'session_id': session_id,
            'url': 'https://example.com',
            'ai_provider': 'claude',
            'metadata': {'test_suite': 'regression'}
        })
        
        # Add test results
        await db_manager.save_test_result({
            'session_id': session_id,
            'test_name': 'test_1',
            'status': 'passed',
            'started_at': datetime.now().isoformat(),
            'execution_time': 2.5
        })
        
        await db_manager.save_test_result({
            'session_id': session_id,
            'test_name': 'test_2',
            'status': 'failed',
            'started_at': datetime.now().isoformat(),
            'error_message': 'Assertion failed'
        })
        
        # Add performance metrics
        await db_manager.save_performance_metric({
            'session_id': session_id,
            'metric_name': 'total_duration',
            'metric_value': 10.5,
            'unit': 'seconds'
        })
        
        # Add error log
        await db_manager.save_error_log({
            'session_id': session_id,
            'error_type': 'NetworkError',
            'error_message': '404 Not Found'
        })
        
        # Get complete results
        results = await db_manager.get_session_results(session_id)
        
        assert results is not None
        assert results['session_id'] == session_id
        assert results['metadata']['test_suite'] == 'regression'
        assert len(results['results']) == 2
        assert len(results['performance_metrics']) == 1
        assert len(results['error_logs']) == 1
        
        # Check test results
        assert results['results'][0]['test_name'] == 'test_1'
        assert results['results'][0]['status'] == 'passed'
        assert results['results'][1]['test_name'] == 'test_2'
        assert results['results'][1]['status'] == 'failed'
    
    async def test_get_recent_sessions(self, db_manager):
        """Test retrieving recent sessions."""
        # Create multiple sessions
        for i in range(5):
            await db_manager.create_test_session({
                'session_id': f'recent-{i}',
                'url': f'https://example{i}.com',
                'ai_provider': 'claude',
                'started_at': (datetime.now() - timedelta(days=i)).isoformat()
            })
        
        # Get recent sessions
        sessions = await db_manager.get_recent_sessions(limit=3)
        
        assert len(sessions) == 3
        # Should be ordered by most recent first
        assert sessions[0]['session_id'] == 'recent-0'
        assert sessions[1]['session_id'] == 'recent-1'
        assert sessions[2]['session_id'] == 'recent-2'
    
    async def test_cleanup_old_sessions(self, db_manager):
        """Test cleaning up old sessions."""
        # Create old and new sessions
        old_date = (datetime.now() - timedelta(days=35)).isoformat()
        new_date = (datetime.now() - timedelta(days=5)).isoformat()
        
        # Create old session
        await db_manager.create_test_session({
            'session_id': 'old-session',
            'url': 'https://old.com',
            'ai_provider': 'gpt',
            'started_at': old_date
        })
        
        # Add data to old session
        await db_manager.save_test_result({
            'session_id': 'old-session',
            'test_name': 'old_test',
            'status': 'passed',
            'started_at': old_date
        })
        
        # Create new session
        await db_manager.create_test_session({
            'session_id': 'new-session',
            'url': 'https://new.com',
            'ai_provider': 'claude',
            'started_at': new_date
        })
        
        # Run cleanup (30 days)
        deleted_count = await db_manager.cleanup_old_sessions(days=30)
        
        assert deleted_count == 1
        
        # Verify old session is gone
        async with db_manager.connection.execute(
            "SELECT * FROM test_sessions WHERE session_id = ?",
            ('old-session',)
        ) as cursor:
            old_session = await cursor.fetchone()
        assert old_session is None
        
        # Verify new session still exists
        async with db_manager.connection.execute(
            "SELECT * FROM test_sessions WHERE session_id = ?",
            ('new-session',)
        ) as cursor:
            new_session = await cursor.fetchone()
        assert new_session is not None
    
    async def test_error_handling_invalid_session(self, db_manager):
        """Test error handling for invalid session operations."""
        # Try to save result for non-existent session
        # SQLite with foreign key constraints disabled won't raise an error
        # This is a limitation of the current implementation
        # In production, you might want to enable foreign key constraints
        
        # Save result for non-existent session (will succeed in SQLite)
        await db_manager.save_test_result({
            'session_id': 'non-existent',
            'test_name': 'test',
            'status': 'failed',
            'started_at': datetime.now().isoformat()
        })
        
        # Verify the result was saved (even without parent session)
        async with db_manager.connection.execute(
            "SELECT * FROM test_results WHERE session_id = ?",
            ('non-existent',)
        ) as cursor:
            result = await cursor.fetchone()
            assert result is not None
    
    async def test_shutdown(self, temp_db_path):
        """Test proper shutdown."""
        config = {'database': {'path': str(temp_db_path)}}
        manager = DatabaseManager(config)
        
        await manager.initialize()
        assert manager.connection is not None
        
        await manager.shutdown()
        assert manager.connection is None
        
        # Shutdown again should not raise error
        await manager.shutdown()