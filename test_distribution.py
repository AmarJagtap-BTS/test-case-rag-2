"""Test script to verify test case distribution"""
import sys
from core.utils import calculate_test_distribution
from config.config import Config

print("=" * 60)
print("TEST CASE DISTRIBUTION VERIFICATION")
print("=" * 60)

# Test with DEFAULT_TEST_CASES
print(f"\n1. Configuration Check:")
print(f"   DEFAULT_TEST_CASES: {Config.DEFAULT_TEST_CASES}")
print(f"   MIN_TEST_CASES: {Config.MIN_TEST_CASES}")
print(f"   MAX_TEST_CASES: {Config.MAX_TEST_CASES}")

# Calculate distribution
print(f"\n2. Distribution Calculation for {Config.DEFAULT_TEST_CASES} test cases:")
dist = calculate_test_distribution(Config.DEFAULT_TEST_CASES)

print(f"   Positive: {dist['positive']}")
print(f"   Negative: {dist['negative']}")
print(f"   UI: {dist['ui']}")
print(f"   Security: {dist['security']}")
print(f"   Edge Case: {dist['edge_case']}")
total = dist['positive'] + dist['negative'] + dist['ui'] + dist['security'] + dist['edge_case']
print(f"   ---")
print(f"   Total: {total}")

print(f"\n3. Distribution String that will be sent to LLM:")
print(dist['distribution_string'])

print(f"\n4. Percentages:")
print(f"   Positive: {(dist['positive']/total)*100:.1f}%")
print(f"   Negative: {(dist['negative']/total)*100:.1f}%")
print(f"   UI: {(dist['ui']/total)*100:.1f}%")
print(f"   Security: {(dist['security']/total)*100:.1f}%")
print(f"   Edge Case: {(dist['edge_case']/total)*100:.1f}%")

print("\n" + "=" * 60)
