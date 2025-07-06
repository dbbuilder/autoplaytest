"""
GPT AI Provider Implementation
Uses OpenAI's GPT API for test generation
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    raise ImportError(
        "openai package is not installed. "
        "Please install it with: pip install openai"
    )

from .base_provider import (
    BaseAIProvider, PageAnalysis, TestGenerationRequest,
    GeneratedTest, TestType, PageElement
)
from utils.logger import setup_logger


class GPTProvider(BaseAIProvider):
    """GPT AI provider for test generation"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize GPT provider"""
        super().__init__(config_path)
        self.logger = setup_logger(self.__class__.__name__)
        
        # Get API key from environment
        api_key = os.getenv(self.config.get('provider', {}).get('api_key_env', 'OPENAI_API_KEY'))
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = self.config.get('models', {}).get('default', 'gpt-4-turbo-preview')
        
    async def analyze_page(self, page_content: str, url: str) -> PageAnalysis:
        """Use GPT to analyze a web page"""
        self.logger.info(f"Analyzing page: {url}")
        
        # Prepare the prompt
        system_prompt = self.prompts.get('system_prompt', '')
        analysis_prompt = self.prompts.get('page_analysis', '')
        
        try:
            # Create the chat completion
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{analysis_prompt}\n\nURL: {url}\n\nPage Content:\n{page_content[:8000]}"}
                ],
                temperature=self.config.get('request_params', {}).get('temperature', 0.2),
                max_tokens=self.config.get('request_params', {}).get('max_tokens', 4096),
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            response_text = response.choices[0].message.content
            analysis_data = json.loads(response_text)
            
            # Convert to PageAnalysis object
            elements = [
                PageElement(**elem) for elem in analysis_data.get('elements', [])
            ]
            
            return PageAnalysis(
                url=url,
                title=analysis_data.get('page_info', {}).get('title', ''),
                page_type=analysis_data.get('page_info', {}).get('type', 'unknown'),
                elements=elements,
                forms=analysis_data.get('forms', []),
                navigation_links=analysis_data.get('navigation', []),
                api_endpoints=analysis_data.get('api_endpoints', []),
                has_authentication=analysis_data.get('has_authentication', False),
                user_flows=analysis_data.get('user_flows', []),
                test_scenarios=analysis_data.get('test_scenarios', [])
            )
            
        except Exception as e:
            self.logger.error(f"Failed to analyze page with GPT: {str(e)}")
            return PageAnalysis(
                url=url,
                title="Unknown",
                page_type="unknown",
                elements=[],
                forms=[],
                navigation_links=[],
                api_endpoints=[],
                has_authentication=False,
                user_flows=[],
                test_scenarios=[]
            )
    
    async def generate_test(self, request: TestGenerationRequest) -> GeneratedTest:
        """Generate a test using GPT"""
        self.logger.info(f"Generating {request.test_type.value} test")
        
        # Prepare the prompt
        system_prompt = self.prompts.get('system_prompt', '')
        generation_prompt = self.prompts.get('test_generation', '')
        
        # Format the prompt
        formatted_prompt = self._format_prompt(
            generation_prompt,
            page_analysis=json.dumps(request.page_analysis.to_dict(), indent=2),
            test_type=request.test_type.value,
            url=request.page_analysis.url,
            context=json.dumps(request.context or {})
        )
        
        try:
            # Generate the test
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": formatted_prompt}
                ],
                temperature=self.config.get('request_params', {}).get('temperature', 0.2),
                max_tokens=self.config.get('request_params', {}).get('max_tokens', 4096)
            )
            
            response_text = response.choices[0].message.content
            
            # Extract code blocks
            code_blocks = self._extract_code_blocks(response_text)
            test_code = code_blocks.get('test', '') or code_blocks.get('python', '')
            page_object_code = code_blocks.get('page_object', '')
            
            # Generate file name
            file_name = f"test_{request.test_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            
            return GeneratedTest(
                test_type=request.test_type,
                file_name=file_name,
                code=test_code,
                description=f"TDD test for {request.test_type.value}",
                dependencies=['pytest', 'playwright', 'pytest-asyncio'],
                page_objects={f"{request.test_type.value}_page.py": page_object_code} if page_object_code else None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate test with GPT: {str(e)}")
            raise
    
    async def validate_test(self, test_code: str) -> Tuple[bool, List[str]]:
        """Validate generated test code using GPT"""
        self.logger.info("Validating generated test code")
        
        validation_prompt = """Please validate this Playwright test code and identify any issues.
        
Check for:
1. Syntax errors
2. Missing imports
3. Incorrect Playwright API usage
4. Missing async/await
5. Test structure issues

Return a JSON response with the following structure:
{"is_valid": boolean, "issues": ["list of issues found"], "suggestions": ["list of improvement suggestions"]}

Test code:
```python
{code}
```"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Python and Playwright expert. Validate the test code and return JSON."},
                    {"role": "user", "content": validation_prompt.format(code=test_code)}
                ],
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            validation_result = json.loads(content)
            return validation_result.get('is_valid', False), validation_result.get('issues', [])
            
        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            return False, [str(e)]
    
    def _extract_code_blocks(self, text: str) -> Dict[str, str]:
        """Extract code blocks from the response"""
        code_blocks = {}
        
        # Look for code blocks with labels
        import re
        
        # Pattern for labeled code blocks
        pattern = r'```(?:python|py)?\s*(?:#\s*)?(\w+)?\n(.*?)```'
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            label = match.group(1) or 'python'
            code = match.group(2).strip()
            code_blocks[label.lower()] = code
        
        # If no labeled blocks, get all Python blocks
        if not code_blocks:
            pattern = r'```(?:python|py)\n(.*?)```'
            matches = re.finditer(pattern, text, re.DOTALL)
            for i, match in enumerate(matches):
                code_blocks[f'block_{i}'] = match.group(1).strip()
        
        return code_blocks