# ai-test-automation/aiqatester/knowledge/test_patterns.py
"""
Test Patterns module for AIQATester.

This module defines common testing patterns and heuristics.
"""

from typing import Dict, List, Any, Callable

# Dictionary of common test patterns for different element types
ELEMENT_TEST_PATTERNS = {
    "input": [
        {"name": "valid_input", "description": "Test with valid input"},
        {"name": "empty_input", "description": "Test with empty input"},
        {"name": "special_chars", "description": "Test with special characters"},
        {"name": "maximum_length", "description": "Test with maximum allowed length"},
        {"name": "over_maximum_length", "description": "Test with length exceeding maximum"}
    ],
    "button": [
        {"name": "click", "description": "Test button click"},
        {"name": "double_click", "description": "Test double click"},
        {"name": "disabled_state", "description": "Test when button is disabled"}
    ],
    "link": [
        {"name": "navigate", "description": "Test navigation to link target"},
        {"name": "new_tab", "description": "Test opening link in new tab"}
    ],
    "select": [
        {"name": "select_option", "description": "Test selecting different options"},
        {"name": "default_option", "description": "Test default selected option"}
    ],
    "checkbox": [
        {"name": "check", "description": "Test checking the checkbox"},
        {"name": "uncheck", "description": "Test unchecking the checkbox"}
    ],
    "radio": [
        {"name": "select", "description": "Test selecting the radio button"},
        {"name": "group_behavior", "description": "Test behavior of radio button group"}
    ],
    "form": [
        {"name": "valid_submission", "description": "Test submission with valid data"},
        {"name": "validation_errors", "description": "Test validation error messages"},
        {"name": "required_fields", "description": "Test submission with missing required fields"}
    ]
}

# Dictionary of common business flow test patterns
FLOW_TEST_PATTERNS = {
    "login": [
        {"name": "valid_credentials", "description": "Test with valid credentials"},
        {"name": "invalid_credentials", "description": "Test with invalid credentials"},
        {"name": "empty_credentials", "description": "Test with empty credentials"},
        {"name": "account_locked", "description": "Test with locked account"},
        {"name": "password_reset", "description": "Test password reset flow"}
    ],
    "registration": [
        {"name": "valid_registration", "description": "Test with valid registration data"},
        {"name": "existing_user", "description": "Test with existing username/email"},
        {"name": "password_requirements", "description": "Test password requirements validation"},
        {"name": "email_verification", "description": "Test email verification process"}
    ],
    "search": [
        {"name": "valid_search", "description": "Test with valid search query"},
        {"name": "empty_search", "description": "Test with empty search query"},
        {"name": "no_results", "description": "Test search with no matching results"},
        {"name": "special_characters", "description": "Test search with special characters"}
    ],
    "checkout": [
        {"name": "valid_purchase", "description": "Test valid purchase flow"},
        {"name": "empty_cart", "description": "Test checkout with empty cart"},
        {"name": "invalid_payment", "description": "Test with invalid payment information"},
        {"name": "shipping_options", "description": "Test different shipping options"}
    ],
    "profile_management": [
        {"name": "update_profile", "description": "Test updating profile information"},
        {"name": "change_password", "description": "Test changing password"},
        {"name": "privacy_settings", "description": "Test changing privacy settings"}
    ]
}

# Test data generators
TEST_DATA_GENERATORS = {
    "email": lambda: "test.user@example.com",
    "password": lambda: "Password123!",
    "name": lambda: "Test User",
    "address": lambda: "123 Test Street, Test City, 12345",
    "phone": lambda: "123-456-7890",
    "credit_card": lambda: "4111 1111 1111 1111",
    "expiry_date": lambda: "12/25",
    "cvv": lambda: "123"
}

# Common assertions
COMMON_ASSERTIONS = {
    "element_visible": "Verify element is visible",
    "element_not_visible": "Verify element is not visible",
    "element_enabled": "Verify element is enabled",
    "element_disabled": "Verify element is disabled",
    "element_text": "Verify element text matches expected value",
    "element_attribute": "Verify element attribute matches expected value",
    "page_url": "Verify page URL matches expected value",
    "page_title": "Verify page title matches expected value",
    "alert_present": "Verify alert is present",
    "alert_text": "Verify alert text matches expected value"
}

def get_test_patterns_for_element(element_type: str) -> List[Dict[str, str]]:
    """Get test patterns for a specific element type."""
    return ELEMENT_TEST_PATTERNS.get(element_type, [])

def get_test_patterns_for_flow(flow_type: str) -> List[Dict[str, str]]:
    """Get test patterns for a specific business flow type."""
    return FLOW_TEST_PATTERNS.get(flow_type, [])

def get_test_data_generator(data_type: str) -> Callable:
    """Get a test data generator for a specific data type."""
    return TEST_DATA_GENERATORS.get(data_type, lambda: "")

def get_assertion(assertion_type: str) -> str:
    """Get an assertion description for a specific assertion type."""
    return COMMON_ASSERTIONS.get(assertion_type, "")