"""
Context Engineering Module for Enhanced RAG Performance
Implements advanced prompting techniques for better test case generation and analysis
"""
import os
import sys
import json
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import TestCase, UserStory
from config.config import Config


class ContextEngineer:
    """
    Advanced context engineering for RAG-based test case management.
    Implements techniques like:
    - Few-shot learning
    - Chain-of-thought prompting
    - Context augmentation
    - Dynamic example selection
    - Role-based prompting
    """
    
    def __init__(self):
        """Initialize context engineer with examples and templates"""
        self.examples = self._load_examples()
        self.context_templates = self._load_context_templates()
    
    def _load_examples(self) -> Dict[str, Dict[str, Any]]:
        """Load few-shot examples for different scenarios"""
        return {
            "simple_crud": {
                "requirement": "User can create a new account with email and password",
                "test_cases": [
                    {
                        "title": "Create account with valid email and strong password",
                        "description": "Verify user can successfully create an account with valid credentials",
                        "business_rule": "System must allow new user registration with valid email and password meeting security requirements",
                        "preconditions": ["User is on registration page", "No account exists with test email"],
                        "test_steps": [
                            {"step_number": 1, "action": "Enter valid email (test@example.com)", "expected_result": "Email field accepts input"},
                            {"step_number": 2, "action": "Enter strong password (Min 8 chars, 1 upper, 1 lower, 1 number)", "expected_result": "Password meets strength requirements"},
                            {"step_number": 3, "action": "Click 'Create Account' button", "expected_result": "Account creation process initiates"}
                        ],
                        "expected_outcome": "Account is created successfully and user is logged in",
                        "postconditions": ["User account exists in database", "User is authenticated", "Welcome email is sent"],
                        "tags": ["registration", "authentication", "happy-path"],
                        "priority": "High",
                        "test_type": "Functional",
                        "boundary_conditions": ["Minimum password length (8 characters)"],
                        "side_effects": ["Database entry created", "Email notification sent"]
                    }
                ]
            },
            "api_integration": {
                "requirement": "API endpoint returns user profile data in JSON format",
                "test_cases": [
                    {
                        "title": "GET /api/users/{id} returns valid user profile",
                        "description": "Verify API endpoint returns complete user profile for valid user ID",
                        "business_rule": "System must expose user profile data via REST API with proper authentication",
                        "preconditions": ["API service is running", "Valid user exists with ID=123", "Valid auth token is available"],
                        "test_steps": [
                            {"step_number": 1, "action": "Send GET request to /api/users/123 with auth token", "expected_result": "API accepts request"},
                            {"step_number": 2, "action": "Verify response status code", "expected_result": "Returns 200 OK"},
                            {"step_number": 3, "action": "Parse response body", "expected_result": "Valid JSON structure"}
                        ],
                        "expected_outcome": "API returns user profile with all required fields",
                        "postconditions": ["No database state changes", "Request logged in API logs"],
                        "tags": ["api", "integration", "backend"],
                        "priority": "High",
                        "test_type": "Integration",
                        "boundary_conditions": ["Invalid user ID (404)", "Missing auth token (401)"],
                        "side_effects": ["API call logged", "Rate limit counter incremented"]
                    }
                ]
            },
            "complex_workflow": {
                "requirement": "User can complete checkout process with payment and shipping",
                "test_cases": [
                    {
                        "title": "Complete checkout with credit card and standard shipping",
                        "description": "Verify end-to-end checkout process with payment processing and shipping selection",
                        "business_rule": "System must process complete order transaction including payment verification, inventory update, and shipping scheduling",
                        "preconditions": ["User is logged in", "Shopping cart has items", "Credit card payment gateway is available", "Shipping address is saved"],
                        "test_steps": [
                            {"step_number": 1, "action": "Review cart items", "expected_result": "Cart displays correct items and prices"},
                            {"step_number": 2, "action": "Proceed to checkout", "expected_result": "Checkout page loads"},
                            {"step_number": 3, "action": "Select shipping address", "expected_result": "Address is validated"},
                            {"step_number": 4, "action": "Choose standard shipping", "expected_result": "Shipping cost calculated"},
                            {"step_number": 5, "action": "Enter credit card details", "expected_result": "Payment form validates"},
                            {"step_number": 6, "action": "Submit order", "expected_result": "Payment processing initiated"}
                        ],
                        "expected_outcome": "Order is placed successfully, payment is charged, inventory is updated, and confirmation email is sent",
                        "postconditions": ["Order record created in database", "Inventory decreased", "Payment transaction completed", "Shipping label generated", "Confirmation email sent"],
                        "tags": ["checkout", "payment", "e2e", "critical"],
                        "priority": "High",
                        "test_type": "E2E",
                        "boundary_conditions": ["Insufficient inventory", "Payment declined", "Invalid shipping address"],
                        "side_effects": ["Inventory updated", "Payment processed", "Order history updated", "Analytics event triggered"]
                    }
                ]
            }
        }
    
    def _load_context_templates(self) -> Dict[str, str]:
        """Load context templates for different scenarios"""
        return {
            "domain_context": """
Domain Context:
- Industry: {industry}
- Application Type: {app_type}
- User Roles: {user_roles}
- Compliance Requirements: {compliance}
- Integration Points: {integrations}
""",
            "technical_context": """
Technical Context:
- Technology Stack: {tech_stack}
- Architecture: {architecture}
- Database: {database}
- APIs: {apis}
- Security: {security}
""",
            "quality_context": """
Quality Requirements:
- Test Coverage Goal: {coverage_goal}
- Priority Areas: {priority_areas}
- Risk Areas: {risk_areas}
- Performance Requirements: {performance}
- Accessibility: {accessibility}
"""
        }
    
    def enhance_generation_prompt(
        self,
        requirement: str,
        requirement_type: str = "user_story",
        domain_context: Optional[Dict[str, Any]] = None,
        similar_examples: Optional[List[TestCase]] = None,
        focus_areas: Optional[List[str]] = None,
        num_test_cases: int = 12,
        test_distribution: str = ""
    ) -> Dict[str, str]:
        """
        Enhance test case generation prompt with context engineering
        
        Args:
            requirement: The requirement text
            requirement_type: Type of requirement (user_story, brs, api, etc.)
            domain_context: Domain-specific context
            similar_examples: Similar test cases from knowledge base (RAG)
            focus_areas: Specific areas to focus on (security, performance, etc.)
        
        Returns:
            Enhanced prompt with system and user messages
        """
        # Base system prompt with role and expertise
        system_prompt = """You are an expert QA engineer and test case designer with 15+ years of experience.

Your Expertise:
- Comprehensive test coverage analysis
- Boundary condition identification
- Business rule extraction
- Risk-based testing strategies
- Test case optimization and parameterization

Your Task: Analyze requirements and generate comprehensive, structured test cases that ensure quality and minimize defects."""
        
        # Add domain context if provided
        if domain_context:
            system_prompt += f"\n\nDomain Context:\n"
            for key, value in domain_context.items():
                system_prompt += f"- {key}: {value}\n"
        
        # Build enhanced user prompt with chain-of-thought
        user_prompt = f"""Requirement Type: {requirement_type.upper()}

Requirement:
{requirement}

Step 1: ANALYZE the requirement
Think through:
- What is the core business rule?
- What are the user goals?
- What could go wrong?
- What are the edge cases?
- What are the security implications?

Step 2: IDENTIFY test scenarios
Consider:
- Happy path (normal flow)
- Alternative paths (different user choices)
- Error cases (invalid inputs, system errors)
- Boundary conditions (limits, extremes)
- Integration points (external systems)
"""
        
        # Add similar examples from RAG (few-shot learning)
        if similar_examples and len(similar_examples) > 0:
            user_prompt += "\nStep 3: LEARN from similar test cases in knowledge base:\n"
            for i, example in enumerate(similar_examples[:2], 1):  # Use top 2
                user_prompt += f"\nExample {i}:\n"
                user_prompt += f"Title: {example.title}\n"
                user_prompt += f"Business Rule: {example.business_rule}\n"
                user_prompt += f"Test Type: {example.test_type}\n"
                user_prompt += f"Coverage: {len(example.test_steps)} steps, {len(example.boundary_conditions)} boundary conditions\n"
        
        # Add focus areas
        if focus_areas:
            user_prompt += f"\nStep 4: FOCUS on these areas:\n"
            for area in focus_areas:
                user_prompt += f"- {area}\n"
        
        # Add few-shot example based on requirement type
        example_type = self._match_requirement_to_example(requirement)
        if example_type in self.examples:
            example_data: Dict[str, Any] = self.examples[example_type]
            user_prompt += f"\n\nExample of high-quality test case structure:\n"
            user_prompt += f"Requirement: {example_data['requirement']}\n"
            user_prompt += f"Generated Test Case:\n{json.dumps(example_data['test_cases'][0], indent=2)}\n"
        
        # Output format with strict schema
        user_prompt += """

Step 5: GENERATE test cases in JSON format

For each test case, provide:
1. title (string): MUST end with type suffix (- Positive/Negative/UI/Security/Edge Case)
   Examples:
   ✅ "Login with valid credentials - Positive"
   ✅ "Login with empty username - Negative"
   ✅ "Password visibility toggle - UI"
   ✅ "Account lockout after failed attempts - Security"
   ✅ "OTP expiry validation - Edge Case"
2. description (string): What is being tested and why
3. business_rule (string): The underlying business logic being validated
4. preconditions (array): Setup required before test execution
5. test_steps (array): Each object must have step_number, action, expected_result
   CRITICAL: Do NOT put numbers in the 'action' field - only use step_number
   ✅ CORRECT: {"step_number": 1, "action": "Open login page", "expected_result": "Page loads"}
   ❌ WRONG: {"step_number": 1, "action": "1. Open login page", "expected_result": "Page loads"}
6. expected_outcome (string): Overall success criteria
7. postconditions (array): System state after test completion
8. tags (array): Categorization for organization and filtering
9. priority (string): High/Medium/Low based on business impact
10. test_type (string): Functional/Integration/E2E/API/Security/Performance
11. boundary_conditions (array): Edge cases and limits to test
12. side_effects (array): System state changes and side effects

CRITICAL RULES:
- Generate EXACTLY """ + str(num_test_cases) + """ test cases total
- Follow this distribution:
""" + test_distribution + """
- EVERY title MUST end with: - Positive OR - Negative OR - UI OR - Security OR - Edge Case
- Negative tests: empty fields, invalid inputs, wrong credentials, boundary violations
- UI tests: field visibility, button states, animations, accessibility
- Security tests: account lockout, session management, password masking, XSS/CSRF
- Edge cases: timeouts, concurrent operations, network failures, race conditions
- ALWAYS include business_rule (infer if not explicit)
- Use arrays [] for list fields, never strings
- Make test steps actionable and verifiable

Return ONLY the JSON array of test cases, no markdown, no extra text."""
        
        return {
            "system": system_prompt,
            "user": user_prompt
        }
    
    def enhance_comparison_prompt(
        self,
        new_test_case: TestCase,
        existing_test_case: TestCase,
        similarity_score: float,
        historical_decisions: Optional[List[Dict]] = None
    ) -> Dict[str, str]:
        """
        Enhance comparison prompt with context and chain-of-thought reasoning
        
        Args:
            new_test_case: New test case to compare
            existing_test_case: Existing test case from knowledge base
            similarity_score: Pre-calculated semantic similarity
            historical_decisions: Similar past decisions for context
        
        Returns:
            Enhanced comparison prompt
        """
        system_prompt = """You are an expert test case analyst specializing in test suite optimization and deduplication.

Your Expertise:
- Test case equivalence analysis
- Business rule mapping
- Test coverage assessment
- Test case consolidation strategies

Your Task: Analyze if two test cases are testing the same thing, and determine if they should be kept separate, merged, or if one is redundant."""
        
        user_prompt = f"""Perform a detailed comparison using chain-of-thought reasoning:

STEP 1: Understand the semantic similarity
Embedding-based similarity score: {similarity_score:.2%}
This indicates: {"High similarity" if similarity_score > 0.8 else "Moderate similarity" if similarity_score > 0.6 else "Low similarity"}

STEP 2: Compare business rules
NEW TEST CASE Business Rule: {new_test_case.business_rule}
EXISTING TEST CASE Business Rule: {existing_test_case.business_rule}

Question: Are these testing the same business rule?
Think: Do they validate the same business logic/requirement?

STEP 3: Compare behavior and outcomes
NEW expected outcome: {new_test_case.expected_outcome}
EXISTING expected outcome: {existing_test_case.expected_outcome}

Question: Do they test the same behavior?
Think: Would they catch the same defects?

STEP 4: Analyze coverage differences
NEW test case coverage:
- Steps: {len(new_test_case.test_steps)}
- Boundary conditions: {new_test_case.boundary_conditions}
- Preconditions: {new_test_case.preconditions}

EXISTING test case coverage:
- Steps: {len(existing_test_case.test_steps)}
- Boundary conditions: {existing_test_case.boundary_conditions}
- Preconditions: {existing_test_case.preconditions}

Question: Does the new test case add unique coverage?
Think: Are there scenarios, edge cases, or conditions not covered by existing?

STEP 5: Determine relationship
Based on analysis above:
- If same rule + same behavior + no new coverage → "identical"
- If same rule + same behavior + adds coverage → "expanded"
- If different rule OR different behavior → "different"
"""
        
        # Add historical context if available
        if historical_decisions and len(historical_decisions) > 0:
            user_prompt += "\n\nSTEP 6: Learn from similar past decisions:\n"
            for decision in historical_decisions[:2]:
                user_prompt += f"- Similarity {decision['similarity']:.0%}: Decision was '{decision['decision']}' because {decision['reasoning'][:100]}...\n"
        
        user_prompt += """

STEP 7: Provide your analysis in JSON format

Return ONLY valid JSON (no markdown, no code blocks):
{
    "business_rule_match": true or false,
    "behavior_match": true or false,
    "coverage_expansion": ["list", "of", "new", "scenarios"],
    "relationship": "identical" or "expanded" or "different",
    "reasoning": "Detailed explanation of your analysis"
}

Be thorough in your reasoning. Explain your thought process."""
        
        return {
            "system": system_prompt,
            "user": user_prompt
        }
    
    def enhance_merge_prompt(
        self,
        existing_test_case: TestCase,
        new_test_case: TestCase,
        coverage_expansion: List[str]
    ) -> Dict[str, str]:
        """
        Enhance merge prompt for intelligent test case consolidation
        
        Args:
            existing_test_case: Base test case
            new_test_case: Test case to merge in
            coverage_expansion: Identified new coverage areas
        
        Returns:
            Enhanced merge prompt
        """
        system_prompt = """You are an expert test case architect specializing in test optimization and parameterization.

Your Expertise:
- Test case parameterization and data-driven testing
- Test suite optimization without losing coverage
- Maintainable test design patterns

Your Task: Merge two similar test cases into a single, optimized test case that maintains all coverage."""
        
        user_prompt = f"""Create an optimized, merged test case using these steps:

STEP 1: Identify the core business rule
Existing: {existing_test_case.business_rule}
New: {new_test_case.business_rule}

The merged business rule should encompass both.

STEP 2: Consolidate preconditions
Existing: {existing_test_case.preconditions}
New: {new_test_case.preconditions}

Keep all unique preconditions, eliminate duplicates.

STEP 3: Merge test steps intelligently
Existing has {len(existing_test_case.test_steps)} steps
New has {len(new_test_case.test_steps)} steps

Consider:
- Can steps be parameterized? (e.g., "Enter <username>" with test data)
- Can they be combined into decision points?
- Should they remain separate with clear flow?

STEP 4: Incorporate expanded coverage
New coverage identified: {', '.join(coverage_expansion)}

Add these as:
- Additional test steps
- New boundary conditions
- Extended postconditions

STEP 5: Update metadata
- Increment version number from {existing_test_case.version}
- Merge tags from both test cases
- Keep highest priority
- Update boundary_conditions with new edge cases

STEP 6: Generate the merged test case

EXISTING TEST CASE:
{json.dumps(existing_test_case.dict(), indent=2, default=str)}

NEW TEST CASE:
{json.dumps(new_test_case.dict(), indent=2, default=str)}

Return the merged test case in the same JSON structure. Ensure:
- All array fields remain arrays
- No information is lost
- Coverage is expanded
- Test is still maintainable and clear

Return ONLY the complete merged test case JSON."""
        
        return {
            "system": system_prompt,
            "user": user_prompt
        }
    
    def _match_requirement_to_example(self, requirement: str) -> str:
        """Match requirement to best example type"""
        requirement_lower = requirement.lower()
        
        if any(word in requirement_lower for word in ['api', 'endpoint', 'rest', 'json', 'get', 'post']):
            return "api_integration"
        elif any(word in requirement_lower for word in ['checkout', 'payment', 'order', 'cart', 'workflow']):
            return "complex_workflow"
        else:
            return "simple_crud"
    
    def extract_domain_context(self, existing_test_cases: List[TestCase]) -> Dict[str, Any]:
        """
        Extract domain context from existing test cases in knowledge base
        Uses RAG to understand the project context
        
        Args:
            existing_test_cases: Test cases from knowledge base
        
        Returns:
            Extracted domain context
        """
        if not existing_test_cases:
            return {}
        
        # Analyze tags to identify domain
        all_tags = []
        test_types = []
        priorities = []
        
        for tc in existing_test_cases:
            all_tags.extend(tc.tags)
            test_types.append(tc.test_type)
            priorities.append(tc.priority)
        
        # Count frequencies
        from collections import Counter
        tag_counts = Counter(all_tags)
        type_counts = Counter(test_types)
        
        return {
            "common_tags": [tag for tag, _ in tag_counts.most_common(5)],
            "primary_test_types": [t for t, _ in type_counts.most_common(3)],
            "total_test_cases": len(existing_test_cases),
            "average_steps": sum(len(tc.test_steps) for tc in existing_test_cases) / len(existing_test_cases),
            "high_priority_count": sum(1 for p in priorities if p.lower() == "high")
        }
    
    def get_focus_areas(self, requirement: str) -> List[str]:
        """
        Identify focus areas based on requirement keywords
        
        Args:
            requirement: Requirement text
        
        Returns:
            List of focus areas
        """
        focus_areas = []
        requirement_lower = requirement.lower()
        
        # Security keywords
        if any(word in requirement_lower for word in ['login', 'auth', 'password', 'secure', 'token', 'permission', 'admin']):
            focus_areas.append("Security testing (authentication, authorization, input validation)")
        
        # Performance keywords
        if any(word in requirement_lower for word in ['load', 'performance', 'speed', 'timeout', 'concurrent', 'scale']):
            focus_areas.append("Performance testing (response time, load handling, timeouts)")
        
        # Data keywords
        if any(word in requirement_lower for word in ['data', 'database', 'store', 'persist', 'save', 'update']):
            focus_areas.append("Data integrity (CRUD operations, consistency, validation)")
        
        # Integration keywords
        if any(word in requirement_lower for word in ['api', 'integration', 'external', 'service', 'third-party']):
            focus_areas.append("Integration testing (API contracts, error handling, fallbacks)")
        
        # UI keywords
        if any(word in requirement_lower for word in ['ui', 'interface', 'button', 'form', 'display', 'screen']):
            focus_areas.append("UI/UX testing (usability, accessibility, responsive design)")
        
        # Error handling keywords
        if any(word in requirement_lower for word in ['error', 'exception', 'fail', 'invalid', 'validation']):
            focus_areas.append("Error handling (validation, error messages, recovery)")
        
        return focus_areas if focus_areas else ["Comprehensive functional testing"]
