"""
Test script for FastAPI endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_process_requirement():
    """Test requirement processing"""
    print("\n=== Testing Requirement Processing ===")
    
    data = {
        "requirement_text": """
        Feature: User Login
        
        The system shall allow users to log in using email and password.
        
        Requirements:
        1. User enters email and password
        2. System validates credentials
        3. User is redirected to dashboard on success
        4. Error message shown for invalid credentials
        
        Business Rules:
        - Password must be at least 8 characters
        - Maximum 3 login attempts allowed
        - Account locked after 3 failed attempts
        """,
        "suite_name": "authentication",
        "auto_apply": False
    }
    
    response = requests.post(f"{BASE_URL}/process/requirement", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")
        print(f"Generated {result['summary']['total_test_cases']} test cases")
        print(f"  - Same: {result['summary']['same_count']}")
        print(f"  - Add-on: {result['summary']['addon_count']}")
        print(f"  - New: {result['summary']['new_count']}")
    else:
        print(f"Error: {response.text}")


def test_process_user_story():
    """Test user story processing"""
    print("\n=== Testing User Story Processing ===")
    
    data = {
        "title": "Shopping Cart Checkout",
        "description": "As a user, I want to checkout my shopping cart so that I can complete my purchase",
        "acceptance_criteria": [
            "User can review cart items",
            "System calculates total with tax",
            "User can apply discount codes",
            "Payment is processed securely"
        ],
        "business_rules": [
            "Minimum order value: $10",
            "Free shipping over $50",
            "Discount codes can only be used once"
        ],
        "context": "E-commerce checkout flow",
        "suite_name": "checkout",
        "auto_apply": True
    }
    
    response = requests.post(f"{BASE_URL}/process/user-story", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")
        print(f"Generated {result['summary']['total_test_cases']} test cases")
        print(f"Actions taken: {len(result['actions_taken'])}")
        for action in result['actions_taken']:
            print(f"  - {action}")
    else:
        print(f"Error: {response.text}")


def test_get_test_cases():
    """Test getting test cases"""
    print("\n=== Testing Get Test Cases ===")
    
    response = requests.get(f"{BASE_URL}/test-cases?suite_name=authentication")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        test_cases = response.json()
        print(f"Found {len(test_cases)} test cases")
        for tc in test_cases[:3]:  # Show first 3
            print(f"  - {tc['title']} (ID: {tc['id']})")
    else:
        print(f"Error: {response.text}")


def test_get_suites():
    """Test listing suites"""
    print("\n=== Testing List Suites ===")
    
    response = requests.get(f"{BASE_URL}/suites")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        suites = response.json()
        print(f"Found {len(suites)} suites: {', '.join(suites)}")
    else:
        print(f"Error: {response.text}")


def test_get_statistics():
    """Test statistics endpoint"""
    print("\n=== Testing Statistics ===")
    
    response = requests.get(f"{BASE_URL}/statistics")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"Total test cases: {stats['knowledge_base']['total_test_cases']}")
    else:
        print(f"Error: {response.text}")


def test_get_thresholds():
    """Test thresholds endpoint"""
    print("\n=== Testing Thresholds ===")
    
    response = requests.get(f"{BASE_URL}/config/thresholds")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        thresholds = response.json()
        print(f"Same threshold: {thresholds['threshold_same']}")
        print(f"Add-on range: {thresholds['threshold_addon_min']} - {thresholds['threshold_addon_max']}")
    else:
        print(f"Error: {response.text}")


if __name__ == "__main__":
    print("="*60)
    print("FastAPI Test Suite")
    print("="*60)
    print("\nMake sure the API is running: python api.py")
    print("or: uvicorn api:app --reload")
    
    try:
        # Run tests
        test_health()
        test_get_thresholds()
        test_get_suites()
        test_get_statistics()
        
        # Uncomment to test processing (requires Azure OpenAI credentials)
        # test_process_requirement()
        # test_process_user_story()
        # test_get_test_cases()
        
        print("\n" + "="*60)
        print("Tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the API is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
