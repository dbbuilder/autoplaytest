"""Database Manager - Manages database connections and operations."""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
from pathlib import Path
import aiosqlite
import json

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations for test results."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_path = Path(config.get('database', {}).get('path', 'test_results.db'))
        self.connection: Optional[aiosqlite.Connection] = None
        self.logger = logger
    
    async def initialize(self) -> None:
        """Initialize the database connection and create tables."""
        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.connection = await aiosqlite.connect(str(self.db_path))
            self.connection.row_factory = aiosqlite.Row
            
            # Create tables
            await self._create_tables()
            
            self.logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        async with self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS test_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                ai_provider TEXT NOT NULL,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                status TEXT NOT NULL,
                total_tests INTEGER DEFAULT 0,
                passed_tests INTEGER DEFAULT 0,
                failed_tests INTEGER DEFAULT 0,
                skipped_tests INTEGER DEFAULT 0,
                execution_time REAL,
                metadata TEXT
            )
            """
        ):
            pass
        
        async with self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                test_name TEXT NOT NULL,
                test_category TEXT,
                status TEXT NOT NULL,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                execution_time REAL,
                error_message TEXT,
                stack_trace TEXT,
                screenshots TEXT,
                performance_metrics TEXT,
                FOREIGN KEY (session_id) REFERENCES test_sessions(session_id)
            )
            """
        ):
            pass
        
        async with self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                test_name TEXT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                unit TEXT,
                timestamp TIMESTAMP NOT NULL,
                FOREIGN KEY (session_id) REFERENCES test_sessions(session_id)
            )
            """
        ):
            pass
        
        async with self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                test_name TEXT,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                stack_trace TEXT,
                timestamp TIMESTAMP NOT NULL,
                severity TEXT DEFAULT 'ERROR',
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES test_sessions(session_id)
            )
            """
        ):
            pass
        
        # Create indices for better performance
        await self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_test_sessions_session_id ON test_sessions(session_id)"
        )
        await self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_test_results_session_id ON test_results(session_id)"
        )
        await self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_performance_metrics_session_id ON performance_metrics(session_id)"
        )
        await self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_error_logs_session_id ON error_logs(session_id)"
        )
        
        await self.connection.commit()
    
    async def create_test_session(self, session_data: Dict[str, Any]) -> str:
        """Create a new test session record."""
        try:
            async with self.connection.execute(
                """
                INSERT INTO test_sessions 
                (session_id, url, ai_provider, started_at, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session_data['session_id'],
                    session_data['url'],
                    session_data['ai_provider'],
                    session_data.get('started_at', datetime.now().isoformat()),
                    session_data.get('status', 'running'),
                    json.dumps(session_data.get('metadata', {}))
                )
            ):
                await self.connection.commit()
            return session_data['session_id']
        except Exception as e:
            self.logger.error(f"Failed to create test session: {e}")
            raise
    
    async def update_test_session(self, session_id: str, update_data: Dict[str, Any]) -> None:
        """Update test session record."""
        try:
            # Build dynamic update query
            update_fields = []
            values = []
            
            for field, value in update_data.items():
                if field in ['completed_at', 'status', 'total_tests', 'passed_tests', 
                           'failed_tests', 'skipped_tests', 'execution_time']:
                    update_fields.append(f"{field} = ?")
                    values.append(value)
            
            if not update_fields:
                return
            
            values.append(session_id)
            query = f"UPDATE test_sessions SET {', '.join(update_fields)} WHERE session_id = ?"
            
            async with self.connection.execute(query, values):
                await self.connection.commit()
        except Exception as e:
            self.logger.error(f"Failed to update test session: {e}")
            raise
    
    async def save_test_result(self, result_data: Dict[str, Any]) -> None:
        """Save individual test result."""
        try:
            async with self.connection.execute(
                """
                INSERT INTO test_results 
                (session_id, test_name, test_category, status, started_at, 
                 completed_at, execution_time, error_message, stack_trace, 
                 screenshots, performance_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result_data['session_id'],
                    result_data['test_name'],
                    result_data.get('test_category'),
                    result_data['status'],
                    result_data['started_at'],
                    result_data.get('completed_at'),
                    result_data.get('execution_time'),
                    result_data.get('error_message'),
                    result_data.get('stack_trace'),
                    json.dumps(result_data.get('screenshots', [])),
                    json.dumps(result_data.get('performance_metrics', {}))
                )
            ):
                await self.connection.commit()
        except Exception as e:
            self.logger.error(f"Failed to save test result: {e}")
            raise
    
    async def save_performance_metric(self, metric_data: Dict[str, Any]) -> None:
        """Save performance metric."""
        try:
            async with self.connection.execute(
                """
                INSERT INTO performance_metrics 
                (session_id, test_name, metric_name, metric_value, unit, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    metric_data['session_id'],
                    metric_data.get('test_name'),
                    metric_data['metric_name'],
                    metric_data['metric_value'],
                    metric_data.get('unit'),
                    metric_data.get('timestamp', datetime.now().isoformat())
                )
            ):
                await self.connection.commit()
        except Exception as e:
            self.logger.error(f"Failed to save performance metric: {e}")
            raise
    
    async def save_error_log(self, error_data: Dict[str, Any]) -> None:
        """Save error log entry."""
        try:
            async with self.connection.execute(
                """
                INSERT INTO error_logs 
                (session_id, test_name, error_type, error_message, 
                 stack_trace, timestamp, severity, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    error_data['session_id'],
                    error_data.get('test_name'),
                    error_data['error_type'],
                    error_data['error_message'],
                    error_data.get('stack_trace'),
                    error_data.get('timestamp', datetime.now().isoformat()),
                    error_data.get('severity', 'ERROR'),
                    json.dumps(error_data.get('metadata', {}))
                )
            ):
                await self.connection.commit()
        except Exception as e:
            self.logger.error(f"Failed to save error log: {e}")
            raise
    
    async def get_session_results(self, session_id: str) -> Dict[str, Any]:
        """Get all results for a test session."""
        try:
            # Get session info
            async with self.connection.execute(
                "SELECT * FROM test_sessions WHERE session_id = ?",
                (session_id,)
            ) as cursor:
                session = await cursor.fetchone()
                if not session:
                    return None
                
                session_data = dict(session)
                session_data['metadata'] = json.loads(session_data.get('metadata', '{}'))
            
            # Get test results
            async with self.connection.execute(
                "SELECT * FROM test_results WHERE session_id = ? ORDER BY started_at",
                (session_id,)
            ) as cursor:
                results = await cursor.fetchall()
                session_data['results'] = [
                    {
                        **dict(r),
                        'screenshots': json.loads(r['screenshots'] or '[]'),
                        'performance_metrics': json.loads(r['performance_metrics'] or '{}')
                    }
                    for r in results
                ]
            
            # Get performance metrics
            async with self.connection.execute(
                "SELECT * FROM performance_metrics WHERE session_id = ? ORDER BY timestamp",
                (session_id,)
            ) as cursor:
                metrics = await cursor.fetchall()
                session_data['performance_metrics'] = [dict(m) for m in metrics]
            
            # Get error logs
            async with self.connection.execute(
                "SELECT * FROM error_logs WHERE session_id = ? ORDER BY timestamp",
                (session_id,)
            ) as cursor:
                errors = await cursor.fetchall()
                session_data['error_logs'] = [
                    {
                        **dict(e),
                        'metadata': json.loads(e['metadata'] or '{}')
                    }
                    for e in errors
                ]
            
            return session_data
        except Exception as e:
            self.logger.error(f"Failed to get session results: {e}")
            raise
    
    async def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent test sessions."""
        try:
            async with self.connection.execute(
                """
                SELECT * FROM test_sessions 
                ORDER BY started_at DESC 
                LIMIT ?
                """,
                (limit,)
            ) as cursor:
                sessions = await cursor.fetchall()
                return [
                    {
                        **dict(s),
                        'metadata': json.loads(s['metadata'] or '{}')
                    }
                    for s in sessions
                ]
        except Exception as e:
            self.logger.error(f"Failed to get recent sessions: {e}")
            raise
    
    async def cleanup_old_sessions(self, days: int = 30) -> int:
        """Clean up old test sessions and related data."""
        try:
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            # Get sessions to delete
            async with self.connection.execute(
                "SELECT session_id FROM test_sessions WHERE started_at < datetime(?, 'unixepoch')",
                (cutoff_date,)
            ) as cursor:
                sessions = await cursor.fetchall()
                session_ids = [s['session_id'] for s in sessions]
            
            if not session_ids:
                return 0
            
            # Delete related data
            placeholders = ','.join('?' * len(session_ids))
            
            await self.connection.execute(
                f"DELETE FROM test_results WHERE session_id IN ({placeholders})",
                session_ids
            )
            await self.connection.execute(
                f"DELETE FROM performance_metrics WHERE session_id IN ({placeholders})",
                session_ids
            )
            await self.connection.execute(
                f"DELETE FROM error_logs WHERE session_id IN ({placeholders})",
                session_ids
            )
            await self.connection.execute(
                f"DELETE FROM test_sessions WHERE session_id IN ({placeholders})",
                session_ids
            )
            
            await self.connection.commit()
            
            self.logger.info(f"Cleaned up {len(session_ids)} old sessions")
            return len(session_ids)
        except Exception as e:
            self.logger.error(f"Failed to cleanup old sessions: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the database connection."""
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.logger.info("Database connection closed")