"""
Mock test result generator for demonstrations
Used when API keys are not available
"""

import random
from typing import Dict, List, Any
from datetime import datetime
import asyncio


class MockTestGenerator:
    """Generates realistic mock test results"""
    
    def __init__(self):
        self.test_patterns = {
            "login": [
                "test_successful_login_with_valid_credentials",
                "test_failed_login_with_invalid_password",
                "test_failed_login_with_invalid_username",
                "test_login_form_validation_empty_fields",
                "test_remember_me_functionality",
                "test_password_visibility_toggle",
                "test_login_redirect_after_success",
                "test_session_persistence_after_login"
            ],
            "navigation": [
                "test_main_navigation_menu_links",
                "test_breadcrumb_navigation",
                "test_footer_links_accessibility",
                "test_mobile_menu_hamburger_toggle",
                "test_page_not_found_404_handling",
                "test_back_button_functionality",
                "test_deep_linking_support"
            ],
            "forms": [
                "test_form_field_validation",
                "test_required_fields_enforcement",
                "test_email_format_validation",
                "test_phone_number_format_validation",
                "test_form_submission_success",
                "test_form_error_message_display",
                "test_form_data_persistence",
                "test_file_upload_functionality"
            ],
            "search": [
                "test_search_box_functionality",
                "test_search_results_relevance",
                "test_search_with_special_characters",
                "test_search_autocomplete_suggestions",
                "test_search_filters_application",
                "test_search_pagination",
                "test_no_results_found_message"
            ],
            "cart": [
                "test_add_item_to_cart",
                "test_remove_item_from_cart",
                "test_update_cart_quantity",
                "test_cart_total_calculation",
                "test_apply_discount_code",
                "test_cart_persistence_across_sessions",
                "test_empty_cart_message"
            ],
            "e2e": [
                "test_complete_user_journey_registration_to_purchase",
                "test_guest_checkout_workflow",
                "test_user_account_creation_and_profile_update",
                "test_password_reset_workflow",
                "test_order_tracking_functionality"
            ],
            "accessibility": [
                "test_keyboard_navigation_support",
                "test_screen_reader_compatibility",
                "test_color_contrast_compliance",
                "test_alt_text_for_images",
                "test_aria_labels_presence",
                "test_focus_indicators_visibility"
            ],
            "performance": [
                "test_page_load_time_under_3_seconds",
                "test_time_to_interactive_metric",
                "test_largest_contentful_paint",
                "test_cumulative_layout_shift",
                "test_api_response_time"
            ]
        }
        
        self.error_messages = [
            "Element not found: {selector}",
            "Timeout waiting for element: {selector}",
            "Expected text '{expected}' but found '{actual}'",
            "Network request failed: {url}",
            "JavaScript error on page: {error}",
            "Assertion failed: {assertion}",
            "Page did not load within timeout",
            "Unexpected redirect to: {url}"
        ]
    
    async def generate_mock_results(self, test_types: List[str], 
                                   url: str) -> Dict[str, Any]:
        """Generate mock test results"""
        tests = []
        total_duration = 0
        
        # Generate tests for each type
        for test_type in test_types:
            type_tests = self.test_patterns.get(test_type, [])
            num_tests = min(len(type_tests), random.randint(3, 6))
            selected_tests = random.sample(type_tests, num_tests)
            
            for test_name in selected_tests:
                # Simulate test execution
                duration = round(random.uniform(0.5, 5.0), 2)
                total_duration += duration
                
                # 85% pass rate
                status = "passed" if random.random() < 0.85 else "failed"
                
                test_result = {
                    "name": test_name,
                    "status": status,
                    "duration": duration,
                    "test_type": test_type
                }
                
                # Add error for failed tests
                if status == "failed":
                    error_template = random.choice(self.error_messages)
                    test_result["error"] = error_template.format(
                        selector="#" + test_name.split("_")[1],
                        expected="Expected Value",
                        actual="Actual Value",
                        url=url + "/error",
                        error="Undefined variable",
                        assertion=f"{test_name} assertion"
                    )
                
                tests.append(test_result)
                
                # Small delay to simulate execution
                await asyncio.sleep(0.1)
        
        # Calculate summary
        passed = sum(1 for t in tests if t["status"] == "passed")
        failed = sum(1 for t in tests if t["status"] == "failed")
        
        return {
            "url": url,
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "skipped": 0,
            "duration": round(total_duration, 2),
            "tests": tests,
            "timestamp": datetime.now().isoformat(),
            "ai_provider": "mock",
            "test_types": test_types,
            "report_path": f"./reports/mock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        }
    
    def generate_mock_scripts(self, test_types: List[str]) -> List[Dict[str, str]]:
        """Generate mock test scripts"""
        scripts = []
        
        for test_type in test_types:
            script_content = f'''"""
Mock test script for {test_type} testing
Generated by AutoPlayTest Demo
"""

import pytest
from playwright.async_api import Page, expect

@pytest.mark.asyncio
class Test{test_type.title()}:
    """Test suite for {test_type} functionality"""
    
'''
            
            # Add test methods
            type_tests = self.test_patterns.get(test_type, [])[:3]
            for test_name in type_tests:
                script_content += f'''    async def {test_name}(self, page: Page):
        """Test: {test_name.replace('_', ' ').title()}"""
        # Test implementation would go here
        await page.goto("https://example.com")
        # Add test assertions
        pass
    
'''
            
            scripts.append({
                "filename": f"test_{test_type}.py",
                "content": script_content,
                "test_type": test_type
            })
        
        return scripts