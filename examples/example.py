"""
Example usage of the RAG Test Case Management System
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.models import UserStory
from engines.test_case_manager import TestCaseManager
from utils import generate_id

def example_user_story():
    """Example: Process a user story"""
    
    # Create a user story
    user_story = UserStory(
        id=generate_id("login_feature"),
        title="User Login Feature",
        description="As a user, I want to log in to the system using my email and password so that I can access my account.",
        acceptance_criteria=[
            "User can enter email and password",
            "System validates credentials",
            "User is redirected to dashboard on successful login",
            "Error message is shown for invalid credentials",
            "Account is locked after 3 failed attempts"
        ],
        business_rules=[
            "Password must be at least 8 characters",
            "Email must be valid format",
            "Session expires after 30 minutes of inactivity",
            "Maximum 3 login attempts allowed"
        ],
        context="This is for a web application with standard authentication requirements."
    )
    
    # Initialize manager
    print("Initializing Test Case Manager...")
    manager = TestCaseManager()
    
    # Process the user story
    print(f"\nProcessing user story: {user_story.title}")
    results = manager.process_user_story(
        user_story,
        suite_name="authentication",
        auto_apply=False  # Set to True to automatically apply decisions
    )
    
    # Display results
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    
    summary = results['summary']
    print(f"\nGenerated {summary['total_test_cases']} test cases:")
    print(f"  - Same: {summary['same_count']} ({summary['same_percentage']:.1f}%)")
    print(f"  - Add-on: {summary['addon_count']} ({summary['addon_percentage']:.1f}%)")
    print(f"  - New: {summary['new_count']} ({summary['new_percentage']:.1f}%)")
    
    print("\n" + "-"*80)
    print("DETAILED RESULTS")
    print("-"*80)
    
    for i, result in enumerate(results['results'], 1):
        test_case = result['test_case']
        comparison = result['comparison']
        
        print(f"\n{i}. {test_case.title}")
        print(f"   Decision: {comparison.decision.value.upper()}")
        print(f"   Similarity: {comparison.similarity_score:.2%}")
        print(f"   Confidence: {comparison.confidence_score:.2%}")
        print(f"   Reasoning: {comparison.reasoning}")
        print(f"   Recommendation: {result['recommendation']}")
    
    # Apply decisions manually
    print("\n" + "="*80)
    print("APPLYING DECISIONS")
    print("="*80)
    
    for result in results['results']:
        action = manager.apply_decision(
            result['test_case'],
            result['comparison'],
            suite_name="authentication",
            user_approved=True
        )
        print(f"✓ {action}")
    
    # Export results
    print("\n" + "="*80)
    print("EXPORTING")
    print("="*80)
    
    manager.export_test_suite(
        "authentication",
        "./output/authentication_test_suite.xlsx",
        format="excel"
    )
    print("✓ Exported test suite to ./output/authentication_test_suite.xlsx")
    
    # Display statistics
    print("\n" + "="*80)
    print("STATISTICS")
    print("="*80)
    
    stats = manager.get_statistics()
    print(f"\nKnowledge Base:")
    print(f"  - Total test cases: {stats['knowledge_base']['total_test_cases']}")
    print(f"  - Test suites: {', '.join(stats['knowledge_base']['test_suites'])}")


def example_requirement_text():
    """Example: Process requirement text"""
    
    requirement = """
    Feature: Shopping Cart Checkout
    
    The system shall allow users to complete their purchase through a checkout process.
    
    Requirements:
    1. User must be able to review items in cart before checkout
    2. System shall calculate total including taxes and shipping
    3. User can apply discount codes
    4. Payment methods: Credit card, PayPal, Apple Pay
    5. Order confirmation email must be sent
    6. Inventory must be updated after successful payment
    
    Business Rules:
    - Minimum order value: $10
    - Free shipping for orders over $50
    - Discount codes can only be used once per user
    - Tax rate varies by shipping address
    - Payment must be processed within 30 seconds
    """
    
    # Initialize manager
    print("Initializing Test Case Manager...")
    manager = TestCaseManager()
    
    # Process requirement text
    print("\nProcessing requirement text...")
    results = manager.process_requirement_text(
        requirement,
        suite_name="checkout",
        auto_apply=True  # Automatically apply decisions
    )
    
    # Display summary
    summary = results['summary']
    print(f"\n✓ Generated {summary['total_test_cases']} test cases")
    print(f"  - Same: {summary['same_count']}")
    print(f"  - Add-on: {summary['addon_count']}")
    print(f"  - New: {summary['new_count']}")
    
    print(f"\n✓ Applied {len(results['actions_taken'])} actions")
    for action in results['actions_taken']:
        print(f"  - {action}")


if __name__ == "__main__":
    print("="*80)
    print("RAG TEST CASE MANAGEMENT SYSTEM - EXAMPLE USAGE")
    print("="*80)
    
    # Choose which example to run
    print("\nSelect example:")
    print("1. User Story Example")
    print("2. Requirement Text Example")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        example_user_story()
    elif choice == "2":
        example_requirement_text()
    else:
        print("Invalid choice. Running User Story example...")
        example_user_story()
