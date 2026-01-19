"""
Format test cases for Excel export in user's preferred format
- Test steps are numbered and separated by line breaks in a single cell
- All test case info in one row
"""
import sys
import os
import pandas as pd
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import TestCase
from core.knowledge_base import KnowledgeBase


def format_test_case_for_excel(tc: TestCase) -> dict:
    """
    Format a single test case for Excel export
    
    Returns dict with all fields in the user's format
    """
    # Combine test steps into multi-line string
    test_steps_text = "\n".join([
        f"{step.step_number}. {step.action}"
        for step in tc.test_steps
    ])
    
    # Combine expected results into multi-line string
    expected_results_text = "\n".join([
        step.expected_result if step.expected_result else ""
        for step in tc.test_steps
    ])
    
    # Combine preconditions into single text
    preconditions_text = " ".join(tc.preconditions) if tc.preconditions else ""
    
    # Extract test case scenario from title (remove suffix if present)
    title = tc.title
    for suffix in [" - Positive", " - Negative", " - UI", " - Security", " - Edge Case"]:
        if title.endswith(suffix):
            title = title[:-len(suffix)].strip()
            break
    
    # Determine test case type from title suffix or test_type
    if " - Negative" in tc.title or "Negative" in tc.test_type:
        test_case_type = "Negative"
    elif " - Positive" in tc.title or "Positive" in tc.test_type:
        test_case_type = "Positive"
    elif " - UI" in tc.title:
        test_case_type = "UI"
    elif " - Security" in tc.title:
        test_case_type = "Security"
    elif " - Edge Case" in tc.title:
        test_case_type = "Edge Case"
    else:
        test_case_type = tc.test_type
    
    return {
        "Test Case ID": tc.id,
        "Layer": tc.business_rule,
        "Test Case Scenario": tc.description,
        "Test Case": title,
        "Pre-Condition": preconditions_text,
        "Test Case Type": test_case_type,
        "Test Steps": test_steps_text,
        "Expected Result": expected_results_text,
        "Priority": tc.priority
    }


def export_to_excel_format(test_cases: List[TestCase], output_path: str):
    """
    Export test cases to Excel in the user's preferred format
    """
    print(f"\n📊 Formatting {len(test_cases)} test cases for Excel...")
    
    # Format each test case
    formatted_data = [format_test_case_for_excel(tc) for tc in test_cases]
    
    # Create DataFrame
    df = pd.DataFrame(formatted_data)
    
    # Create Excel writer with xlsxwriter engine for better formatting
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Test Cases', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Test Cases']
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True
        })
        
        # Set column widths
        worksheet.set_column('A:A', 20)  # Test Case ID
        worksheet.set_column('B:B', 25)  # Layer
        worksheet.set_column('C:C', 40)  # Test Case Scenario
        worksheet.set_column('D:D', 40)  # Test Case
        worksheet.set_column('E:E', 50)  # Pre-Condition
        worksheet.set_column('F:F', 15)  # Test Case Type
        worksheet.set_column('G:G', 50)  # Test Steps
        worksheet.set_column('H:H', 50)  # Expected Result
        worksheet.set_column('I:I', 12)  # Priority
        
        # Write headers with formatting
        for col_num, column_name in enumerate(df.columns):
            worksheet.write(0, col_num, column_name, header_format)
        
        # Apply cell formatting to all data rows
        for row_num in range(len(df)):
            for col_num in range(len(df.columns)):
                worksheet.write(row_num + 1, col_num, df.iloc[row_num, col_num], cell_format)
        
        # Set row heights for better readability
        worksheet.set_row(0, 30)  # Header row
        for row_num in range(1, len(df) + 1):
            worksheet.set_row(row_num, 100)  # Data rows - taller for multi-line content
    
    print(f"✅ Excel file created: {output_path}")
    print(f"   Format: User's preferred layout with test steps in single cells")


if __name__ == "__main__":
    # Load test cases from knowledge base
    kb = KnowledgeBase()
    suite_name = "default"
    
    # Get test cases from suite
    test_cases = kb.get_test_cases(suite_name)
    
    if not test_cases:
        print("❌ No test cases found in knowledge base!")
        sys.exit(1)
    
    # Export to Excel
    output_path = "output/test_cases_formatted.xlsx"
    os.makedirs("output", exist_ok=True)
    
    export_to_excel_format(test_cases, output_path)
    
    print(f"\n✅ Successfully exported {len(test_cases)} test cases!")
    print(f"📁 File saved to: {output_path}")
