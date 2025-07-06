#!/usr/bin/env python3
"""
Example: Simple Login Test Generation
Shows the minimal code needed to generate a login test for any website.
"""

import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from simple_runner import SimpleRunner


async def generate_login_test():
    """Generate a simple login test for a website."""
    runner = SimpleRunner()
    
    # Minimal configuration - just URL and credentials
    config = {
        'url': 'https://example.com/login',
        'username': 'your_username',
        'password': 'your_password',
        'test_types': ['login'],  # Only generate login test
        'ai_provider': 'gpt'      # Uses OpenAI GPT
    }
    
    # Generate and execute in one line
    print("Generating and executing login test...")
    results = await runner.one_line_execution(**config)
    
    print(f"Test {'passed' if results['success'] else 'failed'}!")
    await runner.shutdown()


if __name__ == "__main__":
    asyncio.run(generate_login_test())