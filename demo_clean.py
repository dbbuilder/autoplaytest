#!/usr/bin/env python3
"""
Clean Demo Runner - Suppresses Windows asyncio warnings
"""

import os
import sys
import warnings

# Suppress all asyncio warnings on Windows BEFORE importing anything else
if sys.platform == 'win32':
    # Set UTF-8 encoding
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # Suppress warnings
    warnings.filterwarnings("ignore", category=ResourceWarning)
    warnings.filterwarnings("ignore", message="unclosed")
    warnings.filterwarnings("ignore", message="Exception ignored")
    
    # Disable asyncio debug mode
    os.environ['PYTHONASYNCIODEBUG'] = '0'

# Now import and run the demo
from demo import main
import asyncio

if __name__ == "__main__":
    if sys.platform == 'win32':
        # Use Windows-specific event loop settings
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(False)
        
        try:
            loop.run_until_complete(main())
        finally:
            # Force cleanup
            try:
                _cancel_all_tasks(loop)
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.run_until_complete(loop.shutdown_default_executor())
            finally:
                loop.close()
    else:
        # Non-Windows systems
        asyncio.run(main())

def _cancel_all_tasks(loop):
    """Cancel all pending tasks"""
    tasks = asyncio.all_tasks(loop)
    if not tasks:
        return
    
    for task in tasks:
        task.cancel()
    
    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    
    for task in tasks:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler({
                'message': 'unhandled exception during shutdown',
                'exception': task.exception(),
                'task': task,
            })