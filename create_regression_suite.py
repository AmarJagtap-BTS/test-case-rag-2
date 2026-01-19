#!/usr/bin/env python3
"""
Simple script to create a regression test suite
Run this after starting the API server
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def wait_for_api():
    """Wait for API to be ready"""
    print("⏳ Waiting for API to start...")
    for i in range(30):
        try:
            response = requests.get(f"{API_BASE}/health", timeout=2)
            if response.status_code == 200:
                print("✅ API is ready!")
                return True
        except:
            time.sleep(1)
    print("❌ API not responding")
    return False

def create_regression_suite():
    """Create and export regression test suite"""
    
    print("\n" + "="*60)
    print("🚀 CREATING REGRESSION TEST SUITE")
    print("="*60 + "\n")
    
    # Check if API is running
    if not wait_for_api():
        print("\n❌ Please start the API first:")
        print("   python ui/api.py")
        return
    
    print("\n" + "-"*60)
    print("📋 STEP 1: Check existing test cases")
    print("-"*60)
    
    try:
        response = requests.get(f"{API_BASE}/test-cases?suite_name=default")
        if response.status_code == 200:
            all_tests = response.json()
            print(f"✅ Total test cases in suite: {len(all_tests)}")
            
            # Count regression tests
            regression_count = sum(1 for tc in all_tests if tc.get('is_regression', False))
            print(f"✅ Test cases marked as regression: {regression_count}")
            
            if regression_count == 0:
                print("\n⚠️  No tests marked as regression yet.")
                print("   Tip: Generate new test cases - AI will automatically mark critical ones as regression")
        else:
            print(f"❌ Could not fetch test cases: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("\n" + "-"*60)
    print("📊 STEP 2: Export High-Priority Regression Tests")
    print("-"*60)
    
    try:
        export_request = {
            "suite_name": "default",
            "format": "excel",
            "priorities": ["High", "Critical"],
            "is_regression": True
        }
        
        print(f"\nExport configuration:")
        print(f"  - Suite: {export_request['suite_name']}")
        print(f"  - Format: {export_request['format']}")
        print(f"  - Priorities: {export_request['priorities']}")
        print(f"  - Regression only: {export_request['is_regression']}")
        
        response = requests.post(
            f"{API_BASE}/export/filtered-test-suite",
            json=export_request,
            timeout=30
        )
        
        if response.status_code == 200:
            filename = "regression_suite_high_critical.xlsx"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"\n✅ Exported to: {filename}")
        else:
            print(f"\n⚠️  Export returned status {response.status_code}")
            print(f"   This might mean no tests match the filter criteria")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error exporting: {e}")
    
    print("\n" + "-"*60)
    print("📊 STEP 3: Export ALL Regression Tests (any priority)")
    print("-"*60)
    
    try:
        export_request = {
            "suite_name": "default",
            "format": "excel",
            "is_regression": True
        }
        
        print(f"\nExport configuration:")
        print(f"  - Suite: {export_request['suite_name']}")
        print(f"  - Format: {export_request['format']}")
        print(f"  - Regression only: {export_request['is_regression']}")
        
        response = requests.post(
            f"{API_BASE}/export/filtered-test-suite",
            json=export_request,
            timeout=30
        )
        
        if response.status_code == 200:
            filename = "regression_suite_all.xlsx"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"\n✅ Exported to: {filename}")
        else:
            print(f"\n⚠️  Export returned status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error exporting: {e}")
    
    print("\n" + "-"*60)
    print("📈 SUMMARY")
    print("-"*60)
    
    try:
        # Get filtered test cases
        response = requests.get(
            f"{API_BASE}/test-cases/filtered",
            params={"is_regression": True}
        )
        
        if response.status_code == 200:
            regression_tests = response.json()
            print(f"\n✅ Total regression test cases: {len(regression_tests)}")
            
            if len(regression_tests) > 0:
                # Count by priority
                priority_counts = {}
                for tc in regression_tests:
                    priority = tc.get('priority', 'Unknown')
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                print(f"\n📊 By Priority:")
                for priority in ['Critical', 'High', 'Medium', 'Low']:
                    count = priority_counts.get(priority, 0)
                    if count > 0:
                        print(f"   {priority}: {count} tests")
                
                # Count by test type
                type_counts = {}
                for tc in regression_tests:
                    test_type = tc.get('test_type', 'Unknown')
                    type_counts[test_type] = type_counts.get(test_type, 0) + 1
                
                print(f"\n📊 By Test Type:")
                for test_type, count in sorted(type_counts.items()):
                    print(f"   {test_type}: {count} tests")
            else:
                print("\n⚠️  No regression tests found.")
                print("\n💡 To create regression tests:")
                print("   1. Generate test cases from requirements")
                print("   2. AI will automatically mark critical/high priority tests as regression")
                print("   3. Or manually mark existing tests as regression via API")
                
        else:
            print(f"❌ Could not fetch filtered tests: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✅ REGRESSION SUITE CREATION COMPLETE!")
    print("="*60)
    
    print("\n📚 Next Steps:")
    print("   - Review exported Excel files")
    print("   - Import into your test management tool")
    print("   - Integrate with CI/CD pipeline")
    print("\n📖 For more details, see: HOW_TO_CREATE_REGRESSION_SUITE.md")

if __name__ == "__main__":
    create_regression_suite()
