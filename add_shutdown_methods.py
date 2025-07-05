"""
Add missing shutdown methods to components
"""

import os
from pathlib import Path

# Add shutdown method to PerformanceMonitor
perf_monitor_path = Path("D:/Dev2/autoplaytest/src/monitoring/performance/performance_monitor.py")
if perf_monitor_path.exists():
    with open(perf_monitor_path, 'a', encoding='utf-8') as f:
        f.write('''
    
    async def shutdown(self) -> None:
        """Shutdown the Performance Monitor."""
        pass  # Placeholder for cleanup if needed
''')
    print("Added shutdown to PerformanceMonitor")

# Add shutdown method to ErrorDetector
error_detector_path = Path("D:/Dev2/autoplaytest/src/monitoring/errors/error_detector.py")
if error_detector_path.exists():
    with open(error_detector_path, 'a', encoding='utf-8') as f:
        f.write('''
    
    async def shutdown(self) -> None:
        """Shutdown the Error Detector."""
        pass  # Placeholder for cleanup if needed
''')
    print("Added shutdown to ErrorDetector")

# Add shutdown method to DatabaseManager
db_manager_path = Path("D:/Dev2/autoplaytest/src/utils/database.py")
if db_manager_path.exists():
    with open(db_manager_path, 'a', encoding='utf-8') as f:
        f.write('''
    
    async def shutdown(self) -> None:
        """Shutdown the Database Manager."""
        if hasattr(self, 'connection') and self.connection:
            await self.connection.close()
''')
    print("Added shutdown to DatabaseManager")

print("\nShutdown methods added to all components!")
