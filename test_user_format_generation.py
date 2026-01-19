"""
Test script to generate test cases in user's preferred format
and export to Excel
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.test_case_generator import TestCaseGenerator
from core.utils import export_test_cases_user_format
from config.config import Config

# User story for asset batch upload validation
user_story = """
As a Financial Advisor,
I want to upload asset details in bulk using an Excel file,
So that I can efficiently manage multiple client assets without manual entry.

Acceptance Criteria:
1. System must validate PAN field as mandatory for all asset records
2. Records with missing or blank PAN should be rejected
3. System should generate error log file for failed records
4. Valid records should be processed successfully
5. No record with missing PAN should be inserted into database
6. Upload supports .xlsx format with size limit of 10MB
7. Mandatory fields: PAN, Name, Mobile, DOB, Asset Type, Invested Value, Date

Business Rules:
- PAN is mandatory for KYC compliance
- Backend validation occurs before database insertion
- Batch operations must be atomic for error handling
- Error logs must be downloadable for correction
"""

print("="*80)
print("GENERATING TEST CASES IN USER'S FORMAT")
print("="*80)
print(f"\nUser Story:\n{user_story}\n")
print("-"*80)

# Initialize generator
generator = TestCaseGenerator()

# Generate test cases (will use updated prompts)
print("\n🔄 Generating 12 test cases with diverse coverage...")
test_cases = generator.generate_from_text(user_story, num_test_cases=12)

print(f"\n✅ Generated {len(test_cases)} test cases!")
print("\nTest Case Summary:")
print("-"*80)

# Count by type
type_counts = {}
for tc in test_cases:
    # Determine type from title
    test_type = "Other"
    if " - Negative" in tc.title:
        test_type = "Negative"
    elif " - Positive" in tc.title:
        test_type = "Positive"
    elif " - UI" in tc.title:
        test_type = "UI"
    elif " - Security" in tc.title:
        test_type = "Security"
    elif " - Edge Case" in tc.title:
        test_type = "Edge Case"
    
    type_counts[test_type] = type_counts.get(test_type, 0) + 1

for test_type, count in sorted(type_counts.items()):
    print(f"  {test_type:15} : {count} test cases")

print("\n" + "-"*80)
print("\nSample Test Cases:")
print("="*80)

# Show first 3 test cases in detail
for i, tc in enumerate(test_cases[:3], 1):
    print(f"\n[{i}] {tc.title}")
    print(f"    Layer: {tc.business_rule}")
    print(f"    Type: {tc.test_type}")
    print(f"    Priority: {tc.priority}")
    print(f"    Scenario: {tc.description}")
    print(f"    Preconditions ({len(tc.preconditions)}):")
    for j, pc in enumerate(tc.preconditions[:3], 1):
        print(f"      {j}. {pc[:80]}...")
    print(f"    Steps: {len(tc.test_steps)}")
    for step in tc.test_steps[:3]:
        print(f"      {step.step_number}. {step.action[:60]}...")
    print("-"*80)

# Export to Excel in user's format
output_path = "output/generated_user_format.xlsx"
os.makedirs("output", exist_ok=True)

print(f"\n📤 Exporting to Excel in user's format...")
export_test_cases_user_format(test_cases, output_path)

print(f"\n✅ SUCCESS! Test cases exported to: {output_path}")
print("\n📋 Excel columns:")
print("   1. Test Case ID")
print("   2. Layer")
print("   3. Test Case Scenario")
print("   4. Test Case")
print("   5. Pre-Condition")
print("   6. Test Case Type")
print("   7. Test Steps")
print("   8. Expected Result")
print("   9. Priority")

print("\n" + "="*80)
print("NEXT STEPS:")
print("="*80)
print("1. Open the Excel file: output/generated_user_format.xlsx")
print("2. Review the test cases")
print("3. Upload to your test management system")
print("4. Run the Streamlit app to generate more test cases")
print("\nCommand to start app: streamlit run ui/app.py")
print("="*80)
