"""
Test script to verify the JSON parsing fixes and business rule handling
"""
from test_case_generator import TestCaseGenerator
from comparison_engine import ComparisonEngine
from models import TestCase, TestStep
from utils import parse_test_case_json

def test_generate_without_business_rules():
    """Test generating test cases without explicit business rules"""
    print("=" * 80)
    print("TEST 1: Generating test cases WITHOUT explicit business rules")
    print("=" * 80)
    
    generator = TestCaseGenerator()
    
    requirement = """
    User can view their profile page.
    The profile page should display user's name and email.
    """
    
    try:
        test_cases = generator.generate_from_text(requirement)
        print(f"\n✓ Successfully generated {len(test_cases)} test cases")
        
        for i, tc in enumerate(test_cases, 1):
            print(f"\n  Test Case {i}:")
            print(f"  - Title: {tc.title}")
            print(f"  - Business Rule: {tc.business_rule}")
            print(f"  - Description: {tc.description}")
        
        return True
    except Exception as e:
        print(f"\n✗ Failed: {e}")
        return False

def test_generate_with_business_rules():
    """Test generating test cases WITH explicit business rules"""
    print("\n" + "=" * 80)
    print("TEST 2: Generating test cases WITH explicit business rules")
    print("=" * 80)
    
    generator = TestCaseGenerator()
    
    requirement = """
    User can login with valid credentials.
    
    Business Rules:
    - Only authenticated users can access the system
    - Password must be at least 8 characters
    - Account locks after 3 failed attempts
    
    Acceptance Criteria:
    - User enters valid username and password
    - System validates credentials
    - User is redirected to dashboard
    """
    
    try:
        test_cases = generator.generate_from_text(requirement)
        print(f"\n✓ Successfully generated {len(test_cases)} test cases")
        
        for i, tc in enumerate(test_cases, 1):
            print(f"\n  Test Case {i}:")
            print(f"  - Title: {tc.title}")
            print(f"  - Business Rule: {tc.business_rule}")
            print(f"  - Priority: {tc.priority}")
        
        return True
    except Exception as e:
        print(f"\n✗ Failed: {e}")
        return False

def test_comparison_json_parsing():
    """Test comparison engine JSON parsing"""
    print("\n" + "=" * 80)
    print("TEST 3: Testing comparison engine JSON parsing")
    print("=" * 80)
    
    # Create two simple test cases
    tc1 = TestCase(
        id="tc1",
        title="Test user login",
        description="Verify user can login with valid credentials",
        business_rule="Only authenticated users can access the system",
        test_steps=[
            TestStep(step_number=1, action="Enter username", expected_result="Username accepted"),
            TestStep(step_number=2, action="Enter password", expected_result="Password accepted"),
            TestStep(step_number=3, action="Click login", expected_result="User logged in")
        ],
        expected_outcome="User successfully logged in"
    )
    
    tc2 = TestCase(
        id="tc2",
        title="Test user login with remember me",
        description="Verify user can login and stay logged in",
        business_rule="Only authenticated users can access the system",
        test_steps=[
            TestStep(step_number=1, action="Enter username", expected_result="Username accepted"),
            TestStep(step_number=2, action="Enter password", expected_result="Password accepted"),
            TestStep(step_number=3, action="Check remember me", expected_result="Remember me selected"),
            TestStep(step_number=4, action="Click login", expected_result="User logged in")
        ],
        expected_outcome="User successfully logged in and session persists"
    )
    
    try:
        engine = ComparisonEngine()
        result = engine.compare_test_cases(tc1, tc2)
        
        print(f"\n✓ Successfully compared test cases")
        print(f"  - Decision: {result.decision.value}")
        print(f"  - Similarity: {result.similarity_score:.2%}")
        print(f"  - Business Rule Match: {result.business_rule_match}")
        print(f"  - Behavior Match: {result.behavior_match}")
        print(f"  - Reasoning: {result.reasoning}")
        
        return True
    except Exception as e:
        print(f"\n✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parse_json_without_business_rule():
    """Test parsing JSON without business_rule field"""
    print("\n" + "=" * 80)
    print("TEST 4: Parsing JSON without business_rule field")
    print("=" * 80)
    
    json_data = {
        "title": "Test case without business rule",
        "description": "This test case has no business rule field",
        "test_steps": [
            {
                "step_number": 1,
                "action": "Do something",
                "expected_result": "Something happens"
            }
        ],
        "expected_outcome": "Test completes successfully"
    }
    
    try:
        tc = parse_test_case_json(json_data)
        print(f"\n✓ Successfully parsed JSON")
        print(f"  - Title: {tc.title}")
        print(f"  - Business Rule: {tc.business_rule}")
        print(f"  - Description: {tc.description}")
        
        return True
    except Exception as e:
        print(f"\n✗ Failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("TESTING JSON PARSING AND BUSINESS RULE HANDLING FIXES")
    print("=" * 80)
    
    results = {
        "Test 1 (Generate without business rules)": test_generate_without_business_rules(),
        "Test 2 (Generate with business rules)": test_generate_with_business_rules(),
        "Test 3 (Comparison JSON parsing)": test_comparison_json_parsing(),
        "Test 4 (Parse JSON without business rule)": test_parse_json_without_business_rule()
    }
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print("\n" + "=" * 80)
    if all_passed:
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
    else:
        print("✗✗✗ SOME TESTS FAILED ✗✗✗")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
