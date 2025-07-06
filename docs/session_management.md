# Session Management in AI Playwright Engine

## Overview

The AI Playwright Engine now includes comprehensive session management capabilities that handle authentication efficiently across multiple test executions. This feature ensures that login is performed only once, and the authenticated session is reused for all subsequent tests.

## Key Features

### 1. Automatic Session Handling
- **Login Once**: The engine automatically executes login tests first
- **Session Reuse**: Authenticated sessions are reused for all non-login tests
- **Cookie Management**: Browser cookies are captured and restored
- **Storage Persistence**: Local storage and session storage are preserved

### 2. Session Persistence
- **Disk Storage**: Sessions are saved to disk for reuse across test runs
- **Timeout Management**: Sessions expire after a configurable timeout (default: 30 minutes)
- **Automatic Cleanup**: Expired sessions are automatically removed

### 3. Intelligent Test Ordering
- **Priority Execution**: Login tests are automatically executed first
- **Dependency Management**: Tests that require authentication run after login
- **Session Injection**: Authentication state is injected into test scripts

## Architecture

### Components

1. **SessionManager** (`src/core/session/session_manager.py`)
   - Handles session creation, storage, and restoration
   - Manages session lifecycle and expiration
   - Provides session injection capabilities

2. **SessionAwareTestExecutor** (`src/core/executor/session_aware_executor.py`)
   - Extends the base TestExecutor with session capabilities
   - Orchestrates test execution with session management
   - Handles session capture after successful login

3. **SessionData**
   - Contains cookies, storage data, and authentication tokens
   - Tracks session validity and expiration
   - Serializable for persistence

## Usage

### Basic Usage

```python
from simple_runner import SimpleRunner

runner = SimpleRunner()

# Configuration with authentication
config = {
    'url': 'https://example.com',
    'username': 'testuser',
    'password': 'testpass',
    'test_types': ['login', 'navigation', 'forms', 'search']
}

# Generate and execute tests
results = await runner.run_one_line(**config)
```

### Two-Phase Execution

```python
# Phase 1: Generate scripts
scripts_dir = await runner.generate_scripts(**config)

# Phase 2: Execute with session management
results = await runner.execute_scripts(scripts_dir)
```

### Custom Login Functions

For applications with non-standard login flows:

```python
async def custom_login(page, url, username, password):
    await page.goto(url)
    # Custom login logic
    await page.fill('#custom-username', username)
    await page.fill('#custom-password', password)
    await page.click('#custom-submit')
    await page.wait_for_load_state('networkidle')

# Use with session manager
session = await session_manager.execute_with_session(
    url, username, password, browser_context, custom_login
)
```

## How It Works

### 1. Test Execution Flow

```
1. Test Suite Starts
   ↓
2. Tests Sorted (Login First)
   ↓
3. Login Test Executes
   ↓
4. Session Captured & Stored
   ↓
5. Non-Login Tests Execute
   ↓
6. Session Restored for Each Test
   ↓
7. Results Aggregated
```

### 2. Session Injection

For non-login tests, the session manager automatically injects:

```python
# Cookie restoration
await context.add_cookies(session_cookies)

# Local storage restoration
await page.evaluate("""(storage) => {
    for (const [key, value] of Object.entries(storage)) {
        localStorage.setItem(key, value);
    }
}""", local_storage_data)
```

### 3. Session Storage Format

Sessions are stored as JSON files:

```json
{
  "session_id": "example_com_testuser",
  "url": "https://example.com",
  "username": "testuser",
  "created_at": "2024-01-15T10:30:00",
  "expires_at": "2024-01-15T11:00:00",
  "cookies": [...],
  "local_storage": {...},
  "session_storage": {...},
  "auth_tokens": {...},
  "is_valid": true
}
```

## Configuration

### Session Timeout

Configure session timeout in the SessionManager:

```python
session_manager = SessionManager(session_timeout_minutes=60)  # 1 hour
```

### Session Persistence

Enable/disable session persistence:

```python
session_manager.persist_sessions = True  # Default
session_manager.sessions_dir = Path("custom_sessions_dir")
```

### Force New Session

Force creation of a new session:

```python
session, is_new = await session_manager.get_or_create_session(
    url, username, password, browser_context, force_new=True
)
```

## Benefits

1. **Performance**: Reduces test execution time by avoiding repeated logins
2. **Reliability**: Maintains consistent authentication state across tests
3. **Scalability**: Supports concurrent test execution with shared sessions
4. **Flexibility**: Works with standard and custom login flows
5. **Persistence**: Sessions survive across test runs within timeout period

## Troubleshooting

### Session Not Created

If sessions are not being created:
1. Verify login test is marked with type 'login'
2. Check login test passes successfully
3. Ensure credentials are correct

### Session Not Reused

If sessions are not being reused:
1. Check session hasn't expired (default 30 minutes)
2. Verify URL and username match exactly
3. Check session files exist in sessions directory

### Authentication Failures

If tests fail due to authentication:
1. Invalidate existing session: `await session_manager.invalidate_session(url, username)`
2. Force new session creation with `force_new=True`
3. Implement custom login function for non-standard flows

## Examples

See `examples/session_management_demo.py` for complete examples demonstrating:
- Basic session management
- Custom login functions
- Session persistence
- Multi-test execution with session reuse