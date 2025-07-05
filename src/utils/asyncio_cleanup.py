"""
Asyncio cleanup helper for Windows
Properly closes all asyncio resources to prevent warnings
"""

import asyncio
import gc
import warnings
from typing import Any

# Suppress all ResourceWarnings globally
warnings.filterwarnings("ignore", category=ResourceWarning)

class AsyncioCleanup:
    """Helper class to ensure proper asyncio cleanup on Windows."""
    
    @staticmethod
    def cleanup_event_loop():
        """Properly close and cleanup the asyncio event loop."""
        try:
            # Get the current event loop
            loop = asyncio.get_event_loop()
            
            # Cancel all tasks
            pending = asyncio.all_tasks(loop) if hasattr(asyncio, 'all_tasks') else asyncio.Task.all_tasks(loop)
            for task in pending:
                task.cancel()
            
            # Run until all tasks are cancelled
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            
            # Close the loop
            loop.call_soon_threadsafe(loop.stop)
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
            
        except Exception:
            pass
        
        # Force garbage collection
        gc.collect()
    
    @staticmethod
    def suppress_warnings():
        """Suppress various warnings that occur on Windows."""
        import warnings
        import sys
        
        # Suppress ResourceWarning
        warnings.filterwarnings("ignore", category=ResourceWarning)
        
        # Suppress specific asyncio warnings
        warnings.filterwarnings("ignore", message="unclosed.*<socket.socket.*>")
        warnings.filterwarnings("ignore", message="unclosed transport")
        warnings.filterwarnings("ignore", message="I/O operation on closed pipe")
        
        # For Python 3.12+ on Windows
        if sys.platform == 'win32' and sys.version_info >= (3, 12):
            import asyncio
            # Set the event loop policy to suppress warnings
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
