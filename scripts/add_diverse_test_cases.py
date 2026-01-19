"""
Script to add diverse test case examples to the knowledge base
This will help the RAG system retrieve examples of different test case types
"""
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import generate_id


# Diverse test case examples covering all types
diverse_test_cases = [
    # NEGATIVE TEST CASE EXAMPLE 1
    {
        "id": generate_id("Empty Username Field Validation"),
        "title": "Login with Empty Username Field - Negative",
        "description": "Verify system prevents login when username field is left empty",
        "business_rule": "All required authentication fields must be populated before login submission",
        "preconditions": ["User is on the login page", "Username and password fields are visible"],
        "test_steps": [
            {
                "step_number": 1,
                "action": "Navigate to login page",
                "expected_result": "Login page displays with username and password fields"
            },
            {
                "step_number": 2,
                "action": "Leave username field empty",
                "expected_result": "Username field remains empty"
            },
            {
                "step_number": 3,
                "action": "Enter valid password in password field",
                "expected_result": "Password is masked and entered successfully"
            },
            {
                "step_number": 4,
                "action": "Click Login button",
                "expected_result": "Error message 'Username field cannot be empty' is displayed. Login is blocked"
            }
        ],
        "expected_outcome": "User remains on login page with appropriate validation error",
        "postconditions": ["User is not authenticated", "Error message is visible"],
        "tags": ["Authentication", "Negative", "Validation"],
        "priority": "High",
        "test_type": "Negative",
        "is_regression": True,
        "boundary_conditions": ["Empty string input", "Field validation"],
        "side_effects": ["Login attempt is logged"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "version": 1,
        "source_document": "diverse_examples"
    },
    # NEGATIVE TEST CASE EXAMPLE 2
    {
        "id": generate_id("Invalid Credentials Error"),
        "title": "Login with Invalid Credentials - Negative",
        "description": "Verify system displays generic error for wrong username/password combination",
        "business_rule": "System must not reveal whether username or password is incorrect to prevent account enumeration",
        "preconditions": ["User has registered account", "User is on login page"],
        "test_steps": [
            {
                "step_number": 1,
                "action": "Enter valid username",
                "expected_result": "Username is accepted"
            },
            {
                "step_number": 2,
                "action": "Enter incorrect password",
                "expected_result": "Password is masked and entered"
            },
            {
                "step_number": 3,
                "action": "Click Login button",
                "expected_result": "Generic error 'Invalid credentials' is displayed without specifying which field is wrong"
            }
        ],
        "expected_outcome": "Login fails with secure generic error message",
        "postconditions": ["User remains unauthenticated", "Failed attempt is logged"],
        "tags": ["Authentication", "Negative", "Security"],
        "priority": "Critical",
        "test_type": "Negative",
        "is_regression": True,
        "boundary_conditions": ["Wrong password", "Account enumeration prevention"],
        "side_effects": ["Failed login attempt counter increments"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "version": 1,
        "source_document": "diverse_examples"
    },
    # NEGATIVE TEST CASE EXAMPLE 3
    {
        "id": generate_id("Special Characters in Username"),
        "title": "Login with Special Characters in Username - Negative",
        "description": "Verify system handles special characters in username field appropriately",
        "business_rule": "System must validate and sanitize input to prevent injection attacks",
        "preconditions": ["User is on login page"],
        "test_steps": [
            {
                "step_number": 1,
                "action": "Enter special characters in username field (e.g., <script>alert('xss')</script>)",
                "expected_result": "Input is accepted or sanitized"
            },
            {
                "step_number": 2,
                "action": "Enter valid password",
                "expected_result": "Password is entered"
            },
            {
                "step_number": 3,
                "action": "Click Login button",
                "expected_result": "Either validation error or safe handling occurs. No script execution"
            }
        ],
        "expected_outcome": "System safely handles special characters without security vulnerabilities",
        "postconditions": ["No XSS attack executed", "User not authenticated"],
        "tags": ["Authentication", "Negative", "Security", "XSS"],
        "priority": "Critical",
        "test_type": "Negative",
        "is_regression": True,
        "boundary_conditions": ["XSS injection attempt", "Input sanitization"],
        "side_effects": ["Security event may be logged"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "version": 1,
        "source_document": "diverse_examples"
    },
    # UI TEST CASE EXAMPLE 1
    {
        "id": generate_id("OTP Field Dynamic Visibility"),
        "title": "OTP Field Appears When Password Entered - UI",
        "description": "Verify OTP field becomes visible with animation when user enters password",
        "business_rule": "OTP field should only appear when password field is populated to streamline UX",
        "preconditions": ["User is on login page", "OTP field is hidden by default"],
        "test_steps": [
            {
                "step_number": 1,
                "action": "Open login page and verify initial state",
                "expected_result": "Username and password fields visible. OTP field is hidden"
            },
            {
                "step_number": 2,
                "action": "Enter at least one character in password field",
                "expected_result": "OTP field appears with smooth fade-in or slide-down animation"
            },
            {
                "step_number": 3,
                "action": "Observe Resend OTP button state",
                "expected_result": "Resend OTP button is visible but disabled for 30-60 seconds"
            }
        ],
        "expected_outcome": "OTP field visibility is dynamically controlled with proper animation",
        "postconditions": ["OTP field is visible", "Resend button is disabled initially"],
        "tags": ["Authentication", "UI", "Animation", "UX"],
        "priority": "High",
        "test_type": "UI",
        "is_regression": False,
        "boundary_conditions": ["Single character triggers visibility"],
        "side_effects": ["DOM element visibility changes"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "version": 1,
        "source_document": "diverse_examples"
    },
    # UI TEST CASE EXAMPLE 2
    {
        "id": generate_id("Password Masking Toggle"),
        "title": "Password Show/Hide Toggle Functionality - UI",
        "description": "Verify password can be toggled between masked and visible states",
        "business_rule": "Users should be able to verify their password entry while maintaining security by default",
        "preconditions": ["User is on login page"],
        "test_steps": [
            {
                "step_number": 1,
                "action": "Enter password in password field",
                "expected_result": "Password appears as masked dots or asterisks. Eye icon is visible"
            },
            {
                "step_number": 2,
                "action": "Click eye icon to show password",
                "expected_result": "Password becomes visible in plain text. Icon changes to 'hide' state"
            },
            {
                "step_number": 3,
                "action": "Click eye icon again to hide password",
                "expected_result": "Password is masked again. Icon returns to 'show' state"
            }
        ],
        "expected_outcome": "Password visibility can be toggled smoothly",
        "postconditions": ["Password field state is preserved"],
        "tags": ["Authentication", "UI", "Password", "UX"],
        "priority": "Medium",
        "test_type": "UI",
        "is_regression": False,
        "boundary_conditions": ["Toggle state persistence"],
        "side_effects": ["Field type changes between password and text"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "version": 1,
        "source_document": "diverse_examples"
    },
    # UI TEST CASE EXAMPLE 3
    {
        "id": generate_id("Login Button State"),
        "title": "Login Button Disabled Until All Fields Complete - UI",
        "description": "Verify login button state changes based on form field completion",
        "business_rule": "Submit button should only be enabled when all required fields are populated",
        "preconditions": ["User is on login page"],
        "test_steps": [
            {
                "step_number": 1,
                "action": "Observe initial login button state",
                "expected_result": "Login button is disabled or shows visual indication it cannot be clicked"
            },
            {
                "step_number": 2,
                "action": "Enter username and password (OTP field appears)",
                "expected_result": "Login button remains disabled"
            },
            {
                "step_number": 3,
                "action": "Enter OTP code",
                "expected_result": "Login button becomes enabled with active styling"
            }
        ],
        "expected_outcome": "Button state correctly reflects form completion status",
        "postconditions": ["Login button is in appropriate state"],
        "tags": ["Authentication", "UI", "Button", "UX"],
        "priority": "High",
        "test_type": "UI",
        "is_regression": False,
        "boundary_conditions": ["All required fields populated"],
        "side_effects": ["Button CSS classes change"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "version": 1,
        "source_document": "diverse_examples"
    },
    # SECURITY TEST CASE EXAMPLE 1
    {
        "id": generate_id("Account Lockout After Failed Attempts"),
        "title": "Account Locked After 5 Failed Login Attempts - Security",
        "description": "Verify account is temporarily locked after multiple consecutive failed login attempts",
        "business_rule": "System must protect against brute force attacks by locking accounts after threshold failures",
        "preconditions": ["User has valid registered account"],
        "test_steps": [
            {
                "step_number": 1,
                "action": "Attempt login with valid username and wrong password",
                "expected_result": "Generic error 'Invalid credentials' displayed"
            },
            {
                "step_number": 2,
                "action": "Repeat failed login 4 more times (total 5 attempts)",
                "expected_result": "After 5th attempt, error changes to 'Account temporarily locked for security'"
            },
            {
                "step_number": 3,
                "action": "Attempt login with correct credentials",
                "expected_result": "Login blocked with 'Account locked' message"
            }
        ],
        "expected_outcome": "Account is locked and cannot be accessed until cooldown expires",
        "postconditions": ["Account is locked", "Unlock timer is started", "Security event logged"],
        "tags": ["Authentication", "Security", "Brute Force", "Account Protection"],
        "priority": "Critical",
        "test_type": "Security",
        "is_regression": True,
        "boundary_conditions": ["5 failed attempt threshold", "Lockout duration"],
        "side_effects": ["Account status changes to locked", "Admin notification may trigger"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "version": 1,
        "source_document": "diverse_examples"
    },
    # SECURITY TEST CASE EXAMPLE 2
    {
        "id": generate_id("Session Management After Login"),
        "title": "Secure Session Created Upon Successful Login - Security",
        "description": "Verify system creates secure session with proper tokens upon successful authentication",
        "business_rule": "Authenticated sessions must be secured with HTTPOnly, Secure, and SameSite cookies",
        "preconditions": ["User has valid credentials"],
        "test_steps": [
            {
                "step_number": 1,
                "action": "Complete successful login with valid credentials",
                "expected_result": "User is authenticated and redirected to dashboard"
            },
            {
                "step_number": 2,
                "action": "Inspect browser cookies and session storage",
                "expected_result": "Session cookie exists with HTTPOnly, Secure, and SameSite flags set"
            },
            {
                "step_number": 3,
                "action": "Verify session token is not accessible via JavaScript",
                "expected_result": "Console shows session token is HTTPOnly and cannot be accessed"
            }
        ],
        "expected_outcome": "Secure session is established with proper security flags",
        "postconditions": ["Active session exists", "Session token is secure"],
        "tags": ["Authentication", "Security", "Session", "Cookies"],
        "priority": "Critical",
        "test_type": "Security",
        "is_regression": True,
        "boundary_conditions": ["Cookie security flags", "XSS protection"],
        "side_effects": ["Session created in database", "Session cookie set"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "version": 1,
        "source_document": "diverse_examples"
    },
    # EDGE CASE EXAMPLE 1
    {
        "id": generate_id("OTP Expiry Validation"),
        "title": "Expired OTP Rejected and New OTP Required - Edge Case",
        "description": "Verify system rejects expired OTP and prompts user to request new one",
        "business_rule": "OTP must be validated within its validity window (typically 5-10 minutes)",
        "preconditions": ["User has received OTP", "OTP validity is 5-10 minutes"],
        "test_steps": [
            {
                "step_number": 1,
                "action": "Enter valid username and password to trigger OTP",
                "expected_result": "OTP field appears and OTP is sent"
            },
            {
                "step_number": 2,
                "action": "Wait for OTP validity period to expire (>10 minutes)",
                "expected_result": "Time passes"
            },
            {
                "step_number": 3,
                "action": "Enter the expired OTP and click Login",
                "expected_result": "Error 'OTP has expired. Please request a new OTP' is displayed"
            },
            {
                "step_number": 4,
                "action": "Click Resend OTP button",
                "expected_result": "New OTP is generated and sent. Success message appears"
            }
        ],
        "expected_outcome": "Expired OTP is rejected and user can request fresh OTP",
        "postconditions": ["Old OTP is invalidated", "New OTP is active"],
        "tags": ["Authentication", "Edge Case", "OTP", "Timeout"],
        "priority": "High",
        "test_type": "Edge_Case",
        "is_regression": True,
        "boundary_conditions": ["OTP expiry timeout", "Token refresh"],
        "side_effects": ["Old OTP invalidated", "New OTP created"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "version": 1,
        "source_document": "diverse_examples"
    },
    # EDGE CASE EXAMPLE 2
    {
        "id": generate_id("Browser Back Button After Login"),
        "title": "Browser Back Button After Successful Login - Edge Case",
        "description": "Verify system handles browser back button correctly after authentication",
        "business_rule": "Authenticated users should not be able to return to login page via back button",
        "preconditions": ["User successfully logs in"],
        "test_steps": [
            {
                "step_number": 1,
                "action": "Complete successful login",
                "expected_result": "User is redirected to dashboard"
            },
            {
                "step_number": 2,
                "action": "Click browser back button",
                "expected_result": "User either stays on dashboard or is redirected to it (not login page)"
            },
            {
                "step_number": 3,
                "action": "Verify session is still active",
                "expected_result": "User remains authenticated"
            }
        ],
        "expected_outcome": "Browser navigation is handled securely without exposing login page",
        "postconditions": ["User remains authenticated", "Session is active"],
        "tags": ["Authentication", "Edge Case", "Navigation", "UX"],
        "priority": "Medium",
        "test_type": "Edge_Case",
        "is_regression": False,
        "boundary_conditions": ["Browser history manipulation", "Session persistence"],
        "side_effects": ["History state may be modified"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "version": 1,
        "source_document": "diverse_examples"
    },
    # POSITIVE TEST CASE EXAMPLE
    {
        "id": generate_id("Successful Login with All Fields"),
        "title": "Successful Login with Valid Credentials and OTP - Positive",
        "description": "Verify user can successfully log in when all required fields are correctly populated",
        "business_rule": "Users with valid credentials and OTP should gain access to their account",
        "preconditions": ["User has registered account with valid credentials"],
        "test_steps": [
            {
                "step_number": 1,
                "action": "Navigate to login page",
                "expected_result": "Login page displays with username and password fields"
            },
            {
                "step_number": 2,
                "action": "Enter valid username",
                "expected_result": "Username is accepted"
            },
            {
                "step_number": 3,
                "action": "Enter valid password",
                "expected_result": "Password is masked. OTP field appears"
            },
            {
                "step_number": 4,
                "action": "Enter valid OTP received",
                "expected_result": "OTP is accepted. Login button becomes enabled"
            },
            {
                "step_number": 5,
                "action": "Click Login button",
                "expected_result": "User is authenticated and redirected to personalized dashboard"
            }
        ],
        "expected_outcome": "User successfully logs in and accesses their account",
        "postconditions": ["User is authenticated", "Session is active", "User is on dashboard"],
        "tags": ["Authentication", "Positive", "Happy Path"],
        "priority": "Critical",
        "test_type": "Positive",
        "is_regression": True,
        "boundary_conditions": ["All required fields populated correctly"],
        "side_effects": ["Session created", "Login timestamp recorded", "User status set to active"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "version": 1,
        "source_document": "diverse_examples"
    }
]


def add_diverse_test_cases():
    """Add diverse test case examples to the knowledge base"""
    kb_path = Path("knowledge_base/default.json")
    
    print("=" * 70)
    print("ADD DIVERSE TEST CASE EXAMPLES TO KNOWLEDGE BASE")
    print("=" * 70)
    
    if not kb_path.exists():
        print(f" Knowledge base file not found: {kb_path}")
        return
    
    # Load existing knowledge base
    print(f"\n Loading existing knowledge base...")
    with open(kb_path, 'r', encoding='utf-8') as f:
        kb_data = json.load(f)
    
    # Check structure
    if isinstance(kb_data, dict) and "test_cases" in kb_data:
        test_cases = kb_data["test_cases"]
    elif isinstance(kb_data, list):
        test_cases = kb_data
        kb_data = {"test_cases": test_cases}
    else:
        print(f" Unexpected knowledge base format")
        return
    
    existing_count = len(test_cases)
    print(f" Found {existing_count} existing test cases")
    
    # Add new diverse test cases
    print(f"\n Adding {len(diverse_test_cases)} diverse test case examples...")
    test_cases.extend(diverse_test_cases)
    kb_data["test_cases"] = test_cases
    
    # Save updated knowledge base
    print(f"\n Saving updated knowledge base...")
    with open(kb_path, 'w', encoding='utf-8') as f:
        json.dump(kb_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully saved knowledge base")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f" Previous test cases: {existing_count}")
    print(f" New test cases added: {len(diverse_test_cases)}")
    print(f" Total test cases: {len(kb_data['test_cases'])}")
    print("\n Added test case types:")
    print(f"   ✓ {sum(1 for tc in diverse_test_cases if tc['test_type'] == 'Negative')} Negative test cases")
    print(f"   ✓ {sum(1 for tc in diverse_test_cases if tc['test_type'] == 'UI')} UI test cases")
    print(f"   ✓ {sum(1 for tc in diverse_test_cases if tc['test_type'] == 'Security')} Security test cases")
    print(f"   ✓ {sum(1 for tc in diverse_test_cases if tc['test_type'] == 'Edge_Case')} Edge Case test cases")
    print(f"   ✓ {sum(1 for tc in diverse_test_cases if tc['test_type'] == 'Positive')} Positive test cases")
    print("\n Knowledge base updated successfully!")
    print("=" * 70)


if __name__ == "__main__":
    add_diverse_test_cases()
