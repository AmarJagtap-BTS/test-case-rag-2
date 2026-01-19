"""
Example: Import existing test cases into the Knowledge Base
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engines.test_case_manager import TestCaseManager
from pathlib import Path

def import_from_excel_example():
    """Example: Import test cases from Excel file"""
    
    print("="*80)
    print("IMPORTING TEST CASES FROM EXCEL")
    print("="*80)
    
    # Initialize manager
    manager = TestCaseManager()
    
    # Path to your existing test cases Excel file
    excel_file = "./examples/existing_test_cases.xlsx"
    
    # Check if file exists
    if not Path(excel_file).exists():
        print(f"\n⚠ File not found: {excel_file}")
        print("Please create an Excel file with your existing test cases.")
        print("\nRequired columns:")
        print("- Title, Description, Test Steps, Expected Outcome")
        print("\nOptional columns:")
        print("- Business Rule, Preconditions, Postconditions, Tags,")
        print("  Priority, Test Type, Boundary Conditions, Side Effects, ID")
        return
    
    # Import test cases
    print(f"\nImporting from: {excel_file}")
    result = manager.import_existing_test_cases(
        file_path=excel_file,
        suite_name="existing_tests",
        file_format="auto"  # Auto-detect format
    )
    
    # Display results
    print("\n" + "="*80)
    print("IMPORT RESULTS")
    print("="*80)
    
    if result['success']:
        print(f"\n✓ Successfully imported {result['imported_count']} test cases")
        
        if result['failed_count'] > 0:
            print(f"\n⚠ Failed to import {result['failed_count']} test cases:")
            for error in result['errors']:
                print(f"  - {error}")
        
        # Show statistics
        stats = manager.get_statistics()
        print("\n" + "-"*80)
        print("KNOWLEDGE BASE STATISTICS")
        print("-"*80)
        print(f"Total test cases in KB: {stats['knowledge_base']['total_test_cases']}")
        print(f"Test suites: {', '.join(stats['knowledge_base']['test_suites'])}")
        
        # Display some imported test cases
        test_cases = manager.get_test_suite("existing_tests")
        print(f"\n" + "-"*80)
        print(f"IMPORTED TEST CASES (showing first 3)")
        print("-"*80)
        
        for i, tc in enumerate(test_cases[:3], 1):
            print(f"\n{i}. {tc.title}")
            print(f"   ID: {tc.id}")
            print(f"   Business Rule: {tc.business_rule}")
            print(f"   Priority: {tc.priority}")
            print(f"   Description: {tc.description[:100]}...")
    else:
        print(f"\n✗ Import failed:")
        for error in result['errors']:
            print(f"  - {error}")


def import_from_json_example():
    """Example: Import test cases from JSON file"""
    
    print("\n" + "="*80)
    print("IMPORTING TEST CASES FROM JSON")
    print("="*80)
    
    # Initialize manager
    manager = TestCaseManager()
    
    # Path to your JSON file
    json_file = "./examples/existing_test_cases.json"
    
    # Check if file exists
    if not Path(json_file).exists():
        print(f"\n⚠ File not found: {json_file}")
        print("Please create a JSON file with your existing test cases.")
        return
    
    # Import test cases
    print(f"\nImporting from: {json_file}")
    result = manager.import_existing_test_cases(
        file_path=json_file,
        suite_name="json_imported_tests",
        file_format="json"
    )
    
    # Display results
    if result['success']:
        print(f"\n✓ Successfully imported {result['imported_count']} test cases")
        
        # Show what was imported
        for tc in result['test_cases'][:3]:
            print(f"\n  - {tc.title}")
    else:
        print(f"\n✗ Import failed:")
        for error in result['errors']:
            print(f"  - {error}")


def test_with_imported_cases():
    """Example: Process new user story with imported test cases"""
    from models import UserStory
    from utils import generate_id
    
    print("\n" + "="*80)
    print("TESTING WITH IMPORTED TEST CASES")
    print("="*80)
    
    manager = TestCaseManager()
    
    # First, import some existing test cases
    print("\nStep 1: Import existing test cases...")
    result = manager.import_existing_test_cases(
        file_path="./examples/existing_test_cases.xlsx",
        suite_name="authentication"
    )
    
    if not result['success']:
        print("⚠ No existing test cases to import. Skipping this example.")
        return
    
    print(f"✓ Imported {result['imported_count']} existing test cases")
    
    # Now process a new user story
    print("\nStep 2: Process a new user story...")
    user_story = UserStory(
        id=generate_id("login_feature"),
        title="User Login Feature",
        description="As a user, I want to log in using email and password",
        acceptance_criteria=[
            "User can enter email and password",
            "System validates credentials",
            "User is redirected on success"
        ],
        business_rules=[
            "Password must be at least 8 characters",
            "Email must be valid format"
        ]
    )
    
    # Process and compare with existing cases
    results = manager.process_user_story(
        user_story,
        suite_name="authentication",
        auto_apply=False
    )
    
    # Show comparison results
    print("\n" + "-"*80)
    print("COMPARISON RESULTS")
    print("-"*80)
    
    summary = results['summary']
    print(f"\nGenerated {summary['total_test_cases']} test cases:")
    print(f"  - SAME: {summary['same_count']} ({summary['same_percentage']:.1f}%)")
    print(f"  - ADD-ON: {summary['addon_count']} ({summary['addon_percentage']:.1f}%)")
    print(f"  - NEW: {summary['new_count']} ({summary['new_percentage']:.1f}%)")
    
    print("\nDetailed decisions:")
    for i, result in enumerate(results['results'][:3], 1):
        comparison = result['comparison']
        print(f"\n{i}. {result['test_case'].title}")
        print(f"   Decision: {comparison.decision.value.upper()}")
        print(f"   Hybrid Similarity: {comparison.similarity_score:.2%}")
        print(f"   Confidence: {comparison.confidence_score:.2%}")


if __name__ == "__main__":
    print("="*80)
    print("RAG TEST CASE MANAGEMENT - IMPORT EXAMPLES")
    print("="*80)
    
    print("\nSelect example:")
    print("1. Import from Excel")
    print("2. Import from JSON")
    print("3. Test with imported cases")
    print("4. Run all examples")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        import_from_excel_example()
    elif choice == "2":
        import_from_json_example()
    elif choice == "3":
        test_with_imported_cases()
    elif choice == "4":
        import_from_excel_example()
        import_from_json_example()
        test_with_imported_cases()
    else:
        print("Invalid choice. Running Excel import example...")
        import_from_excel_example()
