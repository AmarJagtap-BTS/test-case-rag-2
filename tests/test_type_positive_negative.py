"""
Test: Test types must be Positive or Negative only
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import validate_test_type, parse_test_case_json
import pandas as pd
import tempfile
from core.utils import import_from_excel


def test_validate_function():
    """Test the validate_test_type function"""
    print("\n" + "=" * 70)
    print("TEST 1: validate_test_type() Function")
    print("=" * 70)
    
    tests = [
        # Input, Expected Output
        ("Positive", "Positive"),
        ("positive", "Positive"),
        ("POSITIVE", "Positive"),
        ("  Positive  ", "Positive"),
        ("Negative", "Negative"),
        ("negative", "Negative"),
        ("NEGATIVE", "Negative"),
        ("  negative  ", "Negative"),
        # Invalid inputs - should default to Positive
        ("Functional", "Positive"),
        ("Integration", "Positive"),
        ("Security", "Positive"),
        ("Performance", "Positive"),
        ("", "Positive"),
        ("   ", "Positive"),
        ("Random", "Positive"),
        ("API", "Positive"),
        ("Unit", "Positive"),
    ]
    
    all_passed = True
    for input_val, expected in tests:
        result = validate_test_type(input_val)
        status = "✅" if result == expected else "❌"
        if result != expected:
            all_passed = False
        print(f"{status} {repr(input_val):25s} -> {result:10s} (expected: {expected})")
    
    return all_passed


def test_parse_json():
    """Test parse_test_case_json with various test types"""
    print("\n" + "=" * 70)
    print("TEST 2: parse_test_case_json() Function")
    print("=" * 70)
    
    test_types = [
        ("Positive", "Positive"),
        ("Negative", "Negative"),
        ("positive", "Positive"),
        ("NEGATIVE", "Negative"),
        ("Functional", "Positive"),
        ("", "Positive"),
    ]
    
    all_passed = True
    for input_type, expected_type in test_types:
        tc_data = {
            'title': 'Test',
            'description': 'Test description',
            'business_rule': 'Test',
            'test_steps': ['Step 1'],
            'expected_outcome': 'Success',
            'priority': 'Medium',
            'test_type': input_type
        }
        
        tc = parse_test_case_json(tc_data)
        status = "✅" if tc.test_type == expected_type else "❌"
        if tc.test_type != expected_type:
            all_passed = False
        print(f"{status} Input: {repr(input_type):20s} -> Result: {tc.test_type:10s} (expected: {expected_type})")
    
    return all_passed


def test_excel_import():
    """Test Excel import with various test types"""
    print("\n" + "=" * 70)
    print("TEST 3: Excel Import with Test Type Validation")
    print("=" * 70)
    
    # Create test data
    data = {
        'Title': ['Test 1', 'Test 2', 'Test 3', 'Test 4', 'Test 5'],
        'Description': ['Desc 1', 'Desc 2', 'Desc 3', 'Desc 4', 'Desc 5'],
        'Test Steps': ['Step 1', 'Step 2', 'Step 3', 'Step 4', 'Step 5'],
        'Expected Outcome': ['Pass', 'Pass', 'Pass', 'Pass', 'Pass'],
        'Priority': ['High', 'Medium', 'Low', 'High', 'Medium'],
        'Test Type': ['Positive', 'Negative', 'Functional', '', 'negative']
    }
    
    expected_types = ['Positive', 'Negative', 'Positive', 'Positive', 'Negative']
    
    df = pd.DataFrame(data)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        df.to_excel(tmp_path, index=False, engine='openpyxl')
        test_cases = import_from_excel(tmp_path)
        
        all_passed = True
        for i, (tc, expected) in enumerate(zip(test_cases, expected_types), 1):
            input_type = data['Test Type'][i-1]
            status = "✅" if tc.test_type == expected else "❌"
            if tc.test_type != expected:
                all_passed = False
            print(f"{status} Row {i}: Input='{input_type}', Result='{tc.test_type}', Expected='{expected}'")
        
        return all_passed
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("COMPREHENSIVE TEST: Test Type = Positive or Negative ONLY")
    print("=" * 70)
    print("\n📋 Rule: All test types must be either 'Positive' or 'Negative'")
    print("📋 Default: Invalid types default to 'Positive'")
    
    result1 = test_validate_function()
    result2 = test_parse_json()
    result3 = test_excel_import()
    
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"validate_test_type():  {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"parse_test_case_json(): {'✅ PASS' if result2 else '❌ FAIL'}")
    print(f"Excel Import:           {'✅ PASS' if result3 else '❌ FAIL'}")
    print("=" * 70)
    
    if all([result1, result2, result3]):
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Test types are strictly limited to: Positive or Negative")
        print("✅ All invalid types default to: Positive")
    else:
        print("\n❌ SOME TESTS FAILED")
