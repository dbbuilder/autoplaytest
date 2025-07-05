"""
Gemini AI Provider Implementation
Uses Google's Gemini API for test generation
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import google.generativeai as genai

from .base_provider import (
    BaseAIProvider, PageAnalysis, TestGenerationRequest,
    GeneratedTest, TestType, PageElement
)
from utils.logger import setup_logger


class GeminiProvider(BaseAIProvider):
    """Gemini AI provider for test generation"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Gemini provider"""
        super().__init__(config_path)
        self.logger = setup_logger(self.__class__.__name__)
        
        # Get API key from environment
        api_key = os.getenv(self.config.get('provider', {}).get('api_key_env', 'GOOGLE_API_KEY'))
        if not api_key:
            raise ValueError("Gemini API key not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize the model
        model_name = self.config.get('models', {}).get('default', 'gemini-1.5-pro')
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=self._get_generation_config(),
            safety_settings=self.config.get('safety_settings', [])
        )
        
    def _get_generation_config(self) -> Dict[str, Any]:
        """Get generation configuration"""
        params = self.config.get('request_params', {})
        return {
            'temperature': params.get('temperature', 0.2),
            'top_p': params.get('top_p', 0.95),
            'top_k': params.get('top_k', 40),
            'max_output_tokens': params.get('max_output_tokens', 8192),
        }
    
    async def analyze_page(self, page_content: str, url: str) -> PageAnalysis:
        """Use Gemini to analyze a web page"""
        self.logger.info(f"Analyzing page: {url}")
        
        # Prepare the prompt
        system_prompt = self.prompts.get('system_prompt', '')
        analysis_prompt = self.prompts.get('page_analysis', '')
        
        # Combine prompts
        full_prompt = f"{system_prompt}\n\n{analysis_prompt}\n\nURL: {url}\n\nPage Content:\n{page_content[:8000]}"
        
        try:
            # Generate response
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt
            )
            
            # Parse the response
            response_text = response.text
            
            # Extract JSON from the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                analysis_data = json.loads(response_text[json_start:json_end])
            else:
                raise ValueError("No JSON found in response")
            
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
            self.logger.error(f"Failed to analyze page with Gemini: {str(e)}")
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
    
    async def validate_test(self, test_code: str) -> Tuple[bool, List[str]]:
        """Validate generated test code using Gemini"""
        self.logger.info("Validating generated test code")
        
        validation_prompt = """
        Please validate this Playwright test code and identify any issues:
        
        ```python
        {code}
        ```
        
        Check for:
        1. Syntax errors
        2. Missing imports
        3. Incorrect Playwright API usage
        4. Missing async/await
        5. Test structure issues
        
        Return a JSON response with:
        {{
            "is_valid": boolean,
            "issues": ["list of issues found"],
            "suggestions": ["list of improvement suggestions"]
        }}
        """
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                validation_prompt.format(code=test_code)
            )
            
            response_text = response.text
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                validation_result = json.loads(response_text[json_start:json_end])
                return validation_result.get('is_valid', False), validation_result.get('issues', [])
            else:
                return False, ["Could not parse validation response"]
                
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