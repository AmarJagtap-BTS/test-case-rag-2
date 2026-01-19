"""
Example: Using Context Engineering in Test Case Generation

This example demonstrates the difference between basic and advanced
context-engineered test case generation.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engines.test_case_generator import TestCaseGenerator
from engines.rag_engine import RAGEngine
from engines.context_engineering import ContextEngineer
import json


def example_basic_vs_advanced():
    """Compare basic vs context-engineered generation"""
    
    print("=" * 70)
    print("EXAMPLE: Context Engineering in Action")
    print("=" * 70)
    
    requirement = """
    As a user, I want to login to the system using my email and password
    so that I can access my personalized dashboard.
    """
    
    print("\n📋 Requirement:")
    print(requirement)
    
    # ===== BASIC GENERATION (Without Context Engineering) =====
    print("\n" + "=" * 70)
    print("🔷 BASIC GENERATION (Context Engineering: OFF)")
    print("=" * 70)
    
    generator_basic = TestCaseGenerator(use_context_engineering=False)
    basic_test_cases = generator_basic.generate_from_text(requirement)
    
    print(f"\n✅ Generated {len(basic_test_cases)} test cases")
    
    for i, tc in enumerate(basic_test_cases[:3], 1):  # Show first 3
        print(f"\n{i}. {tc.title}")
        print(f"   Business Rule: {tc.business_rule[:80]}...")
        print(f"   Steps: {len(tc.test_steps)}")
        print(f"   Boundary Conditions: {len(tc.boundary_conditions)}")
        print(f"   Tags: {', '.join(tc.tags[:3])}")
    
    # Calculate stats
    basic_stats = {
        "total_cases": len(basic_test_cases),
        "avg_steps": sum(len(tc.test_steps) for tc in basic_test_cases) / len(basic_test_cases),
        "total_boundary": sum(len(tc.boundary_conditions) for tc in basic_test_cases),
        "avg_boundary": sum(len(tc.boundary_conditions) for tc in basic_test_cases) / len(basic_test_cases)
    }
    
    print(f"\n📊 Basic Stats:")
    print(f"   Total test cases: {basic_stats['total_cases']}")
    print(f"   Avg steps per case: {basic_stats['avg_steps']:.1f}")
    print(f"   Total boundary conditions: {basic_stats['total_boundary']}")
    print(f"   Avg boundary per case: {basic_stats['avg_boundary']:.1f}")
    
    # ===== ADVANCED GENERATION (With Context Engineering) =====
    print("\n" + "=" * 70)
    print("🔶 ADVANCED GENERATION (Context Engineering: ON)")
    print("=" * 70)
    
    generator_advanced = TestCaseGenerator(use_context_engineering=True)
    
    # Simulate domain context (normally from knowledge base)
    domain_context = {
        "industry": "SaaS Application",
        "app_type": "Web Application",
        "user_roles": "admin, user, guest",
        "common_tags": "authentication, security, api",
        "total_test_cases": 150
    }
    
    # Simulate similar examples (normally from RAG search)
    # In real usage, you'd do: similar_cases = rag_engine.search_similar_test_cases(...)
    similar_examples = []  # Empty for this demo
    
    advanced_test_cases = generator_advanced.generate_from_text(
        requirement,
        domain_context=domain_context,
        similar_examples=similar_examples
    )
    
    print(f"\n✅ Generated {len(advanced_test_cases)} test cases")
    
    for i, tc in enumerate(advanced_test_cases[:3], 1):  # Show first 3
        print(f"\n{i}. {tc.title}")
        print(f"   Business Rule: {tc.business_rule[:80]}...")
        print(f"   Steps: {len(tc.test_steps)}")
        print(f"   Boundary Conditions: {len(tc.boundary_conditions)}")
        print(f"   Tags: {', '.join(tc.tags[:3])}")
    
    # Calculate stats
    advanced_stats = {
        "total_cases": len(advanced_test_cases),
        "avg_steps": sum(len(tc.test_steps) for tc in advanced_test_cases) / len(advanced_test_cases),
        "total_boundary": sum(len(tc.boundary_conditions) for tc in advanced_test_cases),
        "avg_boundary": sum(len(tc.boundary_conditions) for tc in advanced_test_cases) / len(advanced_test_cases)
    }
    
    print(f"\n📊 Advanced Stats:")
    print(f"   Total test cases: {advanced_stats['total_cases']}")
    print(f"   Avg steps per case: {advanced_stats['avg_steps']:.1f}")
    print(f"   Total boundary conditions: {advanced_stats['total_boundary']}")
    print(f"   Avg boundary per case: {advanced_stats['avg_boundary']:.1f}")
    
    # ===== COMPARISON =====
    print("\n" + "=" * 70)
    print("📈 COMPARISON: Context Engineering Impact")
    print("=" * 70)
    
    print(f"\nMetric                    | Basic | Advanced | Improvement")
    print("-" * 60)
    print(f"Test Cases Generated      | {basic_stats['total_cases']:5} | {advanced_stats['total_cases']:8} | {((advanced_stats['total_cases']/basic_stats['total_cases']-1)*100):+6.1f}%")
    print(f"Avg Steps per Case        | {basic_stats['avg_steps']:5.1f} | {advanced_stats['avg_steps']:8.1f} | {((advanced_stats['avg_steps']/basic_stats['avg_steps']-1)*100):+6.1f}%")
    print(f"Total Boundary Conditions | {basic_stats['total_boundary']:5} | {advanced_stats['total_boundary']:8} | {((advanced_stats['total_boundary']/(basic_stats['total_boundary']+0.1)-1)*100):+6.1f}%")
    print(f"Avg Boundary per Case     | {basic_stats['avg_boundary']:5.1f} | {advanced_stats['avg_boundary']:8.1f} | {((advanced_stats['avg_boundary']/(basic_stats['avg_boundary']+0.1)-1)*100):+6.1f}%")
    
    print("\n" + "=" * 70)
    print("💡 KEY INSIGHTS:")
    print("=" * 70)
    print("""
Context Engineering provides:
✅ More comprehensive test coverage
✅ Better edge case identification
✅ Consistent with project standards
✅ Domain-aware test generation
✅ Professional-grade test cases
    """)


def example_auto_focus_detection():
    """Demonstrate automatic focus area detection"""
    
    print("\n" + "=" * 70)
    print("EXAMPLE: Automatic Focus Area Detection")
    print("=" * 70)
    
    context_engineer = ContextEngineer()
    
    test_requirements = [
        "User can login with email and password",
        "API endpoint /users returns list with pagination",
        "System handles 1000 concurrent requests without timeout",
        "Payment data is encrypted and stored securely"
    ]
    
    for req in test_requirements:
        focus_areas = context_engineer.get_focus_areas(req)
        print(f"\n📋 Requirement: {req}")
        print(f"🎯 Auto-detected focus areas:")
        for area in focus_areas:
            print(f"   • {area}")


def example_context_templates():
    """Show different context templates"""
    
    print("\n" + "=" * 70)
    print("EXAMPLE: Context Templates")
    print("=" * 70)
    
    context_engineer = ContextEngineer()
    
    # Domain context example
    domain = {
        "industry": "E-commerce",
        "app_type": "Microservices",
        "user_roles": "customer, seller, admin",
        "compliance": "PCI-DSS, GDPR",
        "integrations": "Payment Gateway, Shipping API"
    }
    
    print("\n📊 Domain Context Template:")
    print(context_engineer.context_templates["domain_context"].format(
        industry=domain["industry"],
        app_type=domain["app_type"],
        user_roles=domain["user_roles"],
        compliance=domain["compliance"],
        integrations=domain["integrations"]
    ))
    
    # Technical context example
    technical = {
        "tech_stack": "React, Node.js, PostgreSQL",
        "architecture": "Microservices with API Gateway",
        "database": "PostgreSQL with Redis cache",
        "apis": "REST API, GraphQL",
        "security": "OAuth 2.0, JWT tokens"
    }
    
    print("\n🔧 Technical Context Template:")
    print(context_engineer.context_templates["technical_context"].format(
        tech_stack=technical["tech_stack"],
        architecture=technical["architecture"],
        database=technical["database"],
        apis=technical["apis"],
        security=technical["security"]
    ))


if __name__ == "__main__":
    print("\n🚀 Context Engineering Examples")
    print("=" * 70)
    print("This script demonstrates advanced context engineering techniques")
    print("in the RAG-based Test Case Management System")
    print("=" * 70)
    
    try:
        # Example 1: Basic vs Advanced
        example_basic_vs_advanced()
        
        # Example 2: Auto focus detection
        example_auto_focus_detection()
        
        # Example 3: Context templates
        example_context_templates()
        
        print("\n" + "=" * 70)
        print("✅ Examples completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure Azure OpenAI credentials are configured in .env file")
