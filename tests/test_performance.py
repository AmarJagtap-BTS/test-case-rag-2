"""
Performance Testing Script
Run this to test the optimizations
"""
import time
from test_case_manager import TestCaseManager
from models import UserStory

def test_performance():
    """Test the performance of the optimized system"""
    
    print("=" * 60)
    print("PERFORMANCE TEST - RAG Test Case Manager")
    print("=" * 60)
    
    # Initialize manager
    print("\n1. Initializing Test Case Manager...")
    start = time.time()
    manager = TestCaseManager()
    init_time = time.time() - start
    print(f"   ✓ Initialization completed in {init_time:.2f}s")
    
    # Test user story
    user_story = UserStory(
        id="test-001",
        title="User Login Feature",
        description="As a user, I want to log in to the system using my email and password",
        acceptance_criteria=[
            "User can enter email and password",
            "System validates credentials",
            "User is redirected to dashboard on success",
            "Error message shown on invalid credentials"
        ],
        business_rules=[
            "Email must be valid format",
            "Password must be at least 8 characters",
            "Account locks after 3 failed attempts"
        ]
    )
    
    # Test 1: Generate test cases
    print("\n2. Generating test cases from user story...")
    start = time.time()
    results = manager.process_user_story(
        user_story,
        suite_name="performance_test",
        auto_apply=False
    )
    generation_time = time.time() - start
    
    num_test_cases = len(results['generated_test_cases'])
    print(f"   ✓ Generated {num_test_cases} test cases in {generation_time:.2f}s")
    print(f"   ✓ Average time per test case: {generation_time/num_test_cases:.2f}s")
    
    # Display results summary
    print("\n3. Results Summary:")
    summary = results['summary']
    print(f"   - Total Test Cases: {summary['total_test_cases']}")
    print(f"   - Same: {summary['same_count']} ({summary['same_percentage']:.1f}%)")
    print(f"   - Add-on: {summary['addon_count']} ({summary['addon_percentage']:.1f}%)")
    print(f"   - New: {summary['new_count']} ({summary['new_percentage']:.1f}%)")
    
    # Performance metrics
    print("\n4. Performance Metrics:")
    print(f"   - Total Processing Time: {generation_time:.2f}s")
    print(f"   - Initialization Time: {init_time:.2f}s")
    print(f"   - Total Time: {init_time + generation_time:.2f}s")
    
    # Estimated improvement
    sequential_estimate = num_test_cases * 10  # Estimated 10s per test case sequentially
    improvement = ((sequential_estimate - generation_time) / sequential_estimate) * 100
    
    print("\n5. Estimated Performance Improvement:")
    print(f"   - Sequential Processing (estimated): {sequential_estimate:.2f}s")
    print(f"   - Parallel Processing (actual): {generation_time:.2f}s")
    print(f"   - Improvement: {improvement:.1f}% faster")
    
    print("\n" + "=" * 60)
    print("PERFORMANCE TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_performance()
