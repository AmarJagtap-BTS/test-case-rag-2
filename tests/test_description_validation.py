"""
Test to verify descriptions are never blank in generated test cases
"""
import sys
import os
import pandas as pd
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import parse_test_case_json, import_from_excel, import_from_json


def test_parse_test_case_with_blank_description():
    """Test parsing test cases with blank descriptions"""
    print("\n" + "=" * 70)
    print("TEST: parse_test_case_json with blank descriptions")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "Blank description with title",
            "data": {
                'title': 'User Login Test',
                'description': '',
                'business_rule': 'Auth',
                'test_steps': ['Login'],
                'expected_outcome': 'Success',
                'priority': 'High',
                'test_type': 'Functional'
            },
            "expected_pattern": "User Login Test"
        },
        {
            "name": "Missing description key",
            "data": {
                'title': 'Password Reset',
                'business_rule': 'Auth',
                'test_steps': ['Reset'],
                'expected_outcome': 'Success',
                'priority': 'Medium',
                'test_type': 'Functional'
            },
            "expected_pattern": "Password Reset"
        },
        {
            "name": "Whitespace description",
            "data": {
                'title': 'Data Export',
                'description': '   \n  \t  ',
                'business_rule': 'Data',
                'test_steps': ['Export'],
                'expected_outcome': 'Success',
                'priority': 'Low',
                'test_type': 'Functional'
            },
            "expected_pattern": "Data Export"
        },
        {
            "name": "Both title and description blank",
            "data": {
                'title': '',
                'description': '',
                'business_rule': 'Test',
                'test_steps': ['Test'],
                'expected_outcome': 'Success',
                'priority': 'Low',
                'test_type': 'Functional'
            },
            "expected_pattern": "functional requirement"
        },
        {
            "name": "Valid description (should not change)",
            "data": {
                'title': 'Valid Test',
                'description': 'This is a valid description',
                'business_rule': 'Test',
                'test_steps': ['Test'],
                'expected_outcome': 'Success',
                'priority': 'Low',
                'test_type': 'Functional'
            },
            "expected_pattern": "This is a valid description"
        }
    ]
    
    all_passed = True
    for test in test_cases:
        tc = parse_test_case_json(test["data"])
        
        # Validate
        is_valid = (
            tc.description and 
            tc.description.strip() and 
            tc.description != 'nan' and
            test["expected_pattern"].lower() in tc.description.lower()
        )
        
        status = "✅" if is_valid else "❌"
        print(f"\n{status} {test['name']}")
        print(f"   Title: {tc.title}")
        print(f"   Description: {tc.description}")
        
        if not is_valid:
            all_passed = False
            print(f"   ❌ FAILED: Expected pattern '{test['expected_pattern']}' in description")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ All parse_test_case_json tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return all_passed


def test_excel_import_with_blank_descriptions():
    """Test Excel import with blank descriptions"""
    print("\n" + "=" * 70)
    print("TEST: Excel import with blank descriptions")
    print("=" * 70)
    
    # Create test Excel file
    data = {
        'Title': ['Login Test', 'Logout Test', '', 'Export Test'],
        'Description': ['', '   ', '', 'Valid description here'],
        'Test Steps': ['Step 1', 'Step 2', 'Step 3', 'Step 4'],
        'Expected Outcome': ['Pass', 'Pass', 'Pass', 'Pass'],
        'Priority': ['High', 'Medium', 'Low', 'Medium'],
        'Test Type': ['Functional', 'Functional', 'Functional', 'Functional']
    }
    
    df = pd.DataFrame(data)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        df.to_excel(tmp_path, index=False, engine='openpyxl')
        test_cases = import_from_excel(tmp_path)
        
        print(f"\nImported {len(test_cases)} test cases")
        
        all_valid = True
        for i, tc in enumerate(test_cases, 1):
            is_valid = (
                tc.description and 
                tc.description.strip() and 
                tc.description != 'nan'
            )
            
            status = "✅" if is_valid else "❌"
            print(f"\n{status} Test Case {i}")
            print(f"   Title: {tc.title}")
            print(f"   Description: {tc.description}")
            
            if not is_valid:
                all_valid = False
        
        print("\n" + "=" * 70)
        if all_valid:
            print("✅ All Excel import tests passed!")
        else:
            print("❌ Some tests failed!")
        
        return all_valid
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_json_import_with_blank_descriptions():
    """Test JSON import with blank descriptions"""
    print("\n" + "=" * 70)
    print("TEST: JSON import with blank descriptions")
    print("=" * 70)
    
    # Create test JSON data
    json_data = [
        {
            'title': 'JSON Test 1',
            'description': '',
            'business_rule': 'Test',
            'test_steps': ['Step 1'],
            'expected_outcome': 'Success',
            'priority': 'High',
            'test_type': 'Functional'
        },
        {
            'title': 'JSON Test 2',
            'business_rule': 'Test',
            'test_steps': ['Step 2'],
            'expected_outcome': 'Success',
            'priority': 'Medium',
            'test_type': 'Functional'
        },
        {
            'title': '',
            'description': '  ',
            'business_rule': 'Test',
            'test_steps': ['Step 3'],
            'expected_outcome': 'Success',
            'priority': 'Low',
            'test_type': 'Functional'
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        tmp_path = tmp.name
        import json
        json.dump(json_data, tmp.file)
    
    try:
        test_cases = import_from_json(tmp_path)
        
        print(f"\nImported {len(test_cases)} test cases")
        
        all_valid = True
        for i, tc in enumerate(test_cases, 1):
            is_valid = (
                tc.description and 
                tc.description.strip() and 
                tc.description != 'nan'
            )
            
            status = "✅" if is_valid else "❌"
            print(f"\n{status} Test Case {i}")
            print(f"   Title: {tc.title}")
            print(f"   Description: {tc.description}")
            
            if not is_valid:
                all_valid = False
        
        print("\n" + "=" * 70)
        if all_valid:
            print("✅ All JSON import tests passed!")
        else:
            print("❌ Some tests failed!")
        
        return all_valid
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("COMPREHENSIVE TEST: Descriptions Never Blank")
    print("=" * 70)
    
    result1 = test_parse_test_case_with_blank_description()
    result2 = test_excel_import_with_blank_descriptions()
    result3 = test_json_import_with_blank_descriptions()
    
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"parse_test_case_json: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"Excel Import:         {'✅ PASS' if result2 else '❌ FAIL'}")
    print(f"JSON Import:          {'✅ PASS' if result3 else '❌ FAIL'}")
    print("=" * 70)
    
    if all([result1, result2, result3]):
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Descriptions are NEVER blank in generated test cases")
    else:
        print("\n❌ SOME TESTS FAILED")
