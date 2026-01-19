"""
Test to verify that double numbering is prevented
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import (
    has_existing_numbering,
    remove_existing_numbering,
    format_step_with_number,
    parse_test_case_json
)
from core.models import TestCase


def test_has_existing_numbering():
    """Test detection of existing numbering"""
    print("\n=== Testing has_existing_numbering() ===")
    
    test_cases = [
        ("1. Navigate to page", True),
        ("1) Navigate to page", True),
        ("Step 1: Navigate to page", True),
        ("1 - Navigate to page", True),
        ("  2. Click button", True),
        ("Navigate to page", False),
        ("Click the button", False),
        ("  Enter credentials", False),
    ]
    
    for text, expected in test_cases:
        result = has_existing_numbering(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> {result} (expected: {expected})")
    
    print()


def test_remove_existing_numbering():
    """Test removal of existing numbering"""
    print("\n=== Testing remove_existing_numbering() ===")
    
    test_cases = [
        ("1. Navigate to page", "Navigate to page"),
        ("1) Navigate to page", "Navigate to page"),
        ("Step 1: Navigate to page", "Navigate to page"),
        ("1 - Navigate to page", "Navigate to page"),
        ("  2. Click button", "Click button"),
        ("Navigate to page", "Navigate to page"),
        ("Step 10: Complex action", "Complex action"),
    ]
    
    for text, expected in test_cases:
        result = remove_existing_numbering(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text}' -> '{result}' (expected: '{expected}')")
    
    print()


def test_format_step_with_number():
    """Test step formatting with smart numbering"""
    print("\n=== Testing format_step_with_number() ===")
    
    print("\nWith preserve_existing=True (default):")
    test_cases = [
        (1, "1. Navigate to page", "1. Navigate to page"),
        (1, "Navigate to page", "1. Navigate to page"),
        (2, "Step 2: Click button", "Step 2: Click button"),
        (2, "Click button", "2. Click button"),
    ]
    
    for number, text, expected in test_cases:
        result = format_step_with_number(number, text, preserve_existing=True)
        status = "✅" if result == expected else "❌"
        print(f"{status} ({number}) '{text}' -> '{result}' (expected: '{expected}')")
    
    print("\nWith preserve_existing=False (normalize):")
    test_cases = [
        (1, "1. Navigate to page", "1. Navigate to page"),
        (1, "Navigate to page", "1. Navigate to page"),
        (2, "Step 2: Click button", "2. Click button"),
        (2, "Click button", "2. Click button"),
    ]
    
    for number, text, expected in test_cases:
        result = format_step_with_number(number, text, preserve_existing=False)
        status = "✅" if result == expected else "❌"
        print(f"{status} ({number}) '{text}' -> '{result}' (expected: '{expected}')")
    
    print()


def test_parse_test_case_with_numbered_steps():
    """Test parsing of test case with numbered steps"""
    print("\n=== Testing parse_test_case_json() with numbered steps ===")
    
    # Test case with numbered string steps
    json_data = {
        "title": "User Login Test",
        "description": "Test user login functionality",
        "business_rule": "User authentication",
        "test_steps": [
            "1. Navigate to login page",
            "2. Enter valid email address",
            "3. Enter valid password",
            "4. Click submit button"
        ],
        "expected_outcome": "User successfully logged in",
        "priority": "High",
        "test_type": "Functional"
    }
    
    test_case = parse_test_case_json(json_data)
    
    print(f"Test Case: {test_case.title}")
    print(f"Number of steps: {len(test_case.test_steps)}")
    print("\nParsed Steps:")
    
    for step in test_case.test_steps:
        print(f"  Step {step.step_number}: {step.action}")
        # Verify no double numbering in action
        if step.action.startswith("1. ") or step.action.startswith("2. "):
            print(f"     ERROR: Double numbering detected in action!")
        else:
            print(f"     No double numbering")
    
    # Test to_text() method
    print("\n=== Testing to_text() output ===")
    text_output = test_case.to_text()
    print(text_output)
    
    # Check for double numbering in output
    if "Step 1: 1." in text_output or "Step 2: 2." in text_output:
        print("\n ERROR: Double numbering found in to_text() output!")
    else:
        print("\n SUCCESS: No double numbering in to_text() output!")
    
    print()


def test_parse_test_case_with_dict_steps():
    """Test parsing of test case with dict format steps"""
    print("\n=== Testing parse_test_case_json() with dict steps ===")
    
    # Test case with dict steps that have numbered actions
    json_data = {
        "title": "User Registration Test",
        "description": "Test user registration process",
        "business_rule": "User account creation",
        "test_steps": [
            {
                "step_number": 1,
                "action": "1. Navigate to registration page",
                "expected_result": "Registration form displayed"
            },
            {
                "step_number": 2,
                "action": "Enter user details",
                "expected_result": "Form accepts input"
            },
            {
                "step_number": 3,
                "action": "Step 3: Click register button",
                "expected_result": "Account created"
            }
        ],
        "expected_outcome": "User successfully registered",
        "priority": "High",
        "test_type": "Functional"
    }
    
    test_case = parse_test_case_json(json_data)
    
    print(f"Test Case: {test_case.title}")
    print("\nParsed Steps:")
    
    for step in test_case.test_steps:
        print(f"  Step {step.step_number}: {step.action} -> {step.expected_result}")
        # Verify no double numbering
        action_clean = step.action.strip()
        if has_existing_numbering(action_clean):
            print(f"     ERROR: Numbering not removed from action!")
        else:
            print(f"     Numbering properly handled")
    
    print()


def test_mixed_numbering():
    """Test mixed numbered and unnumbered steps"""
    print("\n=== Testing mixed numbered/unnumbered steps ===")
    
    json_data = {
        "title": "Mixed Numbering Test",
        "description": "Test with mixed step formats",
        "business_rule": "Test various formats",
        "test_steps": [
            "1. Navigate to page",
            "Enter credentials",  # No number
            "3) Click submit",
            "Verify success",  # No number
            "Step 5: Log out"
        ],
        "expected_outcome": "All steps executed",
        "priority": "Medium",
        "test_type": "Functional"
    }
    
    test_case = parse_test_case_json(json_data)
    
    print(f"Test Case: {test_case.title}")
    print("\nParsed Steps (should have clean actions):")
    
    expected_actions = [
        "Navigate to page",
        "Enter credentials",
        "Click submit",
        "Verify success",
        "Log out"
    ]
    
    for i, step in enumerate(test_case.test_steps):
        expected = expected_actions[i]
        status = "✅" if step.action == expected else "❌"
        print(f"{status} Step {step.step_number}: '{step.action}' (expected: '{expected}')")
    
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING SMART NUMBERING FIX")
    print("=" * 60)
    
    test_has_existing_numbering()
    test_remove_existing_numbering()
    test_format_step_with_number()
    test_parse_test_case_with_numbered_steps()
    test_parse_test_case_with_dict_steps()
    test_mixed_numbering()
    
    print("=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
