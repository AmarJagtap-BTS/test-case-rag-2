"""
Script to create a sample Excel template for importing test cases
"""
import pandas as pd
from pathlib import Path

# Create example data
data = [
    {
        "ID": "TC001",
        "Title": "Valid User Login",
        "Description": "Verify that users can successfully log in with valid credentials",
        "Business Rule": "User authentication and session management",
        "Preconditions": "User account exists, User has valid credentials",
        "Test Steps": """1. Navigate to login page -> Login form is displayed
2. Enter valid email address -> Email is accepted
3. Enter valid password -> Password is masked
4. Click 'Login' button -> User is authenticated and redirected""",
        "Expected Outcome": "User successfully logs in and is redirected to the dashboard",
        "Postconditions": "User session is created, User is logged in",
        "Tags": "login, authentication, positive",
        "Priority": "High",
        "Test Type": "Functional",
        "Boundary Conditions": "",
        "Side Effects": ""
    },
    {
        "ID": "TC002",
        "Title": "Invalid Password Login Attempt",
        "Description": "Verify that login fails with incorrect password",
        "Business Rule": "User authentication and session management",
        "Preconditions": "User account exists in the system",
        "Test Steps": """1. Navigate to login page -> Login form is displayed
2. Enter valid email address -> Email is accepted
3. Enter incorrect password -> Password is masked
4. Click 'Login' button -> Error message displayed: 'Invalid credentials'""",
        "Expected Outcome": "Login fails and appropriate error message is shown",
        "Postconditions": "User remains on login page, No session is created",
        "Tags": "login, authentication, negative",
        "Priority": "High",
        "Test Type": "Functional",
        "Boundary Conditions": "",
        "Side Effects": ""
    },
    {
        "ID": "TC003",
        "Title": "Account Lockout After Multiple Failed Attempts",
        "Description": "Verify that account is locked after 3 failed login attempts",
        "Business Rule": "Security - Account lockout policy",
        "Preconditions": "User account exists and is active, Lockout policy is enabled (3 attempts)",
        "Test Steps": """1. Attempt login with wrong password (attempt 1) -> Error shown, not locked
2. Attempt login with wrong password (attempt 2) -> Error shown, not locked
3. Attempt login with wrong password (attempt 3) -> Account locked, message shown
4. Attempt login with correct password -> Login denied, account locked""",
        "Expected Outcome": "Account is locked after 3 failed attempts and cannot log in",
        "Postconditions": "Account status is 'locked', User cannot log in",
        "Tags": "login, security, lockout, negative",
        "Priority": "High",
        "Test Type": "Security",
        "Boundary Conditions": "Exactly 3 attempts trigger lockout, 2 attempts do not",
        "Side Effects": "Account must be unlocked by administrator"
    },
    {
        "ID": "TC004",
        "Title": "Password Reset Request",
        "Description": "Verify that users can request a password reset via email",
        "Business Rule": "User account recovery",
        "Preconditions": "User account exists with valid email",
        "Test Steps": """1. Click 'Forgot Password' link -> Password reset form displayed
2. Enter registered email address -> Email is accepted
3. Click 'Send Reset Link' -> Confirmation message shown
4. Check email inbox -> Password reset email received""",
        "Expected Outcome": "User receives password reset email with reset link",
        "Postconditions": "Password reset token generated, Email sent",
        "Tags": "password, reset, email",
        "Priority": "Medium",
        "Test Type": "Functional",
        "Boundary Conditions": "Reset link expires after 24 hours",
        "Side Effects": "Previous reset links are invalidated"
    },
    {
        "ID": "TC005",
        "Title": "Session Timeout After Inactivity",
        "Description": "Verify that user session expires after 30 minutes of inactivity",
        "Business Rule": "Session management - Timeout policy",
        "Preconditions": "User is logged in",
        "Test Steps": """1. User is logged in and active -> Session is valid
2. Leave application idle for 30 minutes -> No activity
3. Attempt to perform an action -> Session timeout message shown
4. Redirect to login page -> User must log in again""",
        "Expected Outcome": "Session expires after 30 minutes and user is logged out",
        "Postconditions": "Session is destroyed, User must re-authenticate",
        "Tags": "session, timeout, security",
        "Priority": "Medium",
        "Test Type": "Functional",
        "Boundary Conditions": "Exactly 30 minutes of inactivity triggers timeout",
        "Side Effects": "Any unsaved work is lost"
    }
]

# Create DataFrame
df = pd.DataFrame(data)

# Ensure examples directory exists
Path("examples").mkdir(exist_ok=True)

# Save to Excel
output_path = "examples/existing_test_cases.xlsx"
df.to_excel(output_path, index=False, engine='openpyxl')

print(f"✓ Created Excel template: {output_path}")
print(f"  - {len(df)} sample test cases")
print(f"  - Columns: {', '.join(df.columns)}")
