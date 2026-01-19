"""
Utility functions for the test case management system
"""
import json
import hashlib
import re
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
from core.models import TestCase, TestStep
from config.config import Config


def generate_id(text: str) -> str:
    """Generate a unique ID from text"""
    return hashlib.md5(text.encode()).hexdigest()[:12]


def calculate_test_distribution(num_test_cases: int) -> Dict[str, Any]:
    """
    Calculate test case distribution based on total count and configured percentages.
    
    Args:
        num_test_cases: Total number of test cases to generate
        
    Returns:
        Dictionary with count for each test type and formatted distribution string
    """
    # Calculate counts based on percentages
    negative_count = max(1, int(num_test_cases * Config.NEGATIVE_MIN_PERCENT))
    ui_count = max(1, int(num_test_cases * Config.UI_MIN_PERCENT))
    security_count = max(1, int(num_test_cases * Config.SECURITY_MIN_PERCENT))
    edge_case_count = max(1, int(num_test_cases * Config.EDGE_CASE_MIN_PERCENT))
    
    # Calculate positive count (remaining after others)
    positive_count = max(1, num_test_cases - (negative_count + ui_count + security_count + edge_case_count))
    
    # Adjust if total exceeds num_test_cases
    total = positive_count + negative_count + ui_count + security_count + edge_case_count
    if total > num_test_cases:
        # Reduce positive count to fit
        positive_count = max(1, num_test_cases - (negative_count + ui_count + security_count + edge_case_count))
    
    # Format distribution string for prompt
    distribution_str = f"""- At least {positive_count} POSITIVE test cases
- At least {negative_count} NEGATIVE test cases
- At least {ui_count} UI/UX test cases
- At least {security_count} SECURITY test cases
- At least {edge_case_count} EDGE CASE test cases"""
    
    return {
        "positive": positive_count,
        "negative": negative_count,
        "ui": ui_count,
        "security": security_count,
        "edge_case": edge_case_count,
        "total": num_test_cases,
        "distribution_string": distribution_str
    }


def validate_test_type(test_type: str) -> str:
    """
    Validate and normalize test type.
    
    Test types must be either "Frontend" or "Backend".
    
    Args:
        test_type: Test type to validate
        
    Returns:
        Normalized test type string - either "Frontend" or "Backend"
    """
    if not test_type or not test_type.strip():
        return "Frontend"
    
    # Normalize: strip whitespace and convert to title case
    normalized = test_type.strip().title()
    
    # Map common variations to Frontend or Backend
    frontend_keywords = ['frontend', 'front-end', 'front end', 'ui', 'ux', 'user interface', 'client', 'web', 'mobile']
    backend_keywords = ['backend', 'back-end', 'back end', 'api', 'server', 'database', 'service', 'integration', 'security']
    
    # Check if it's already Frontend or Backend
    if normalized in ['Frontend', 'Backend']:
        return normalized
    
    # Try to map based on keywords
    normalized_lower = normalized.lower()
    
    for keyword in backend_keywords:
        if keyword in normalized_lower:
            return "Backend"
    
    for keyword in frontend_keywords:
        if keyword in normalized_lower:
            return "Frontend"
    
    # Default to Frontend if can't determine
    return "Frontend"


def has_existing_numbering(text: str) -> bool:
    """
    Check if text already has numbering at the start.
    
    Detects patterns like:
    - "1.", "2)", "3:"
    - "Step 1:", "Step 2."
    - "1 -", "2-", "1-"
    
    Args:
        text: Text to check
        
    Returns:
        True if text has numbering, False otherwise
    """
    numbering_pattern = r'^\s*(?:\d+[\.\):\-]\s*|\d+\s+\-\s*|\bstep\s+\d+[\.\):\-]?\s*)'
    return bool(re.match(numbering_pattern, text.strip(), re.IGNORECASE))


def remove_existing_numbering(text: str) -> str:
    """
    Remove existing numbering from text.
    Handles multiple levels of numbering like "1. 1. Open page" or "1. 2. Enter text"
    
    Args:
        text: Text with potential numbering
        
    Returns:
        Text without any numbering
    """
    numbering_pattern = r'^\s*(?:\d+[\.\):\-]\s*|\d+\s+\-\s*|\bstep\s+\d+[\.\):\-]?\s*)'
    
    # Keep removing numbering until no more found (handles multiple levels)
    result = text
    max_iterations = 5  # Safety limit to prevent infinite loop
    iterations = 0
    
    while iterations < max_iterations and has_existing_numbering(result):
        new_result = re.sub(numbering_pattern, '', result, flags=re.IGNORECASE).strip()
        if new_result == result:  # No change, break to avoid infinite loop
            break
        result = new_result
        iterations += 1
    
    return result


def format_step_with_number(number: int, text: str, preserve_existing: bool = True) -> str:
    """
    Format a step with numbering, optionally preserving existing numbering.
    
    Args:
        number: Step number to use
        text: Step text
        preserve_existing: If True, keeps existing numbering format; if False, normalizes to "N. text"
        
    Returns:
        Formatted step text
    """
    text = text.strip()
    
    if preserve_existing and has_existing_numbering(text):
        # Keep the original numbering format
        return text
    else:
        # Remove any existing numbering and apply standard format
        clean_text = remove_existing_numbering(text)
        return f"{number}. {clean_text}"


def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON file - handles both absolute and relative paths"""
    import os
    
    # If it's just a filename (like 'prompts.json'), look in config folder
    if not os.path.isabs(file_path) and '/' not in file_path:
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        file_path = os.path.join(project_root, 'config', file_path)
    
    with open(file_path, 'r') as f:
        return json.load(f)


def save_json(data: Any, file_path: str):
    """Save data to JSON file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def export_to_excel(test_cases: List[TestCase], output_path: str):
    """Export test cases to Excel"""
    data = []
    for tc in test_cases:
        steps_text = "\n".join([
            f"{s.step_number}. {s.action} -> {s.expected_result}"
            for s in tc.test_steps
        ])
        
        data.append({
            "ID": tc.id,
            "Title": tc.title,
            "Description": tc.description,
            "Preconditions": ", ".join(tc.preconditions),
            "Test Steps": steps_text,
            "Expected Outcome": tc.expected_outcome,
            "Tags": ", ".join(tc.tags),
            "Priority": tc.priority,
            "Test Type": tc.test_type
        })
    
    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False, engine='openpyxl')


def export_results_to_excel_with_sheets(results: Dict[str, Any], output_path: str):
    """
    Export test case results to Excel with separate sheets for each decision type
    
    Creates multiple sheets:
    - Sheet 1: All Test Cases
    - Sheet 2: Modified (ADD-ON decisions)
    - Sheet 3: New (NEW decisions)
    
    Args:
        results: Results dictionary from process_user_story or process_requirement_text
        output_path: Path to save the Excel file
    """
    from core.models import DecisionType
    
    def test_case_to_dict(tc: TestCase, comparison=None):
        """Convert test case to dictionary for DataFrame"""
        steps_text = "\n".join([
            f"{s.step_number}. {s.action} -> {s.expected_result}"
            for s in tc.test_steps
        ])
        
        data = {
            "ID": tc.id,
            "Title": tc.title,
            "Description": tc.description,
            "Preconditions": ", ".join(tc.preconditions),
            "Test Steps": steps_text,
            "Expected Outcome": tc.expected_outcome,
            "Tags": ", ".join(tc.tags),
            "Priority": tc.priority,
            "Test Type": tc.test_type
        }
        
        # Add comparison details if available
        if comparison:
            data["Decision"] = comparison.decision.value.upper()
            data["Similarity"] = f"{comparison.similarity_score:.2%}"
            data["Confidence"] = f"{comparison.confidence_score:.2%}"
            data["Reasoning"] = comparison.reasoning
            
            if comparison.coverage_expansion:
                data["Coverage Expansion"] = ", ".join(comparison.coverage_expansion)
        
        return data
    
    # Prepare data for each sheet
    all_data = []
    modified_data = []
    new_data = []
    
    for result in results.get('results', []):
        tc = result['test_case']
        comparison = result['comparison']
        
        tc_dict = test_case_to_dict(tc, comparison)
        
        # Add to all test cases
        all_data.append(tc_dict)
        
        # Categorize by decision
        if comparison.decision == DecisionType.ADDON:
            modified_data.append(tc_dict)
        elif comparison.decision == DecisionType.NEW:
            new_data.append(tc_dict)
    
    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Sheet 1: All Test Cases
        if all_data:
            df_all = pd.DataFrame(all_data)
            df_all.to_excel(writer, sheet_name='All Test Cases', index=False)
        
        # Sheet 2: Modified (ADD-ON)
        if modified_data:
            df_modified = pd.DataFrame(modified_data)
            df_modified.to_excel(writer, sheet_name='Modified', index=False)
        else:
            # Create empty sheet with headers
            df_empty = pd.DataFrame(columns=["ID", "Title", "Description", "Decision", "Reasoning"])
            df_empty.to_excel(writer, sheet_name='Modified', index=False)
        
        # Sheet 3: New
        if new_data:
            df_new = pd.DataFrame(new_data)
            df_new.to_excel(writer, sheet_name='New', index=False)
        else:
            # Create empty sheet with headers
            df_empty = pd.DataFrame(columns=["ID", "Title", "Description", "Decision", "Reasoning"])
            df_empty.to_excel(writer, sheet_name='New', index=False)
        
        #Adjust column widths for better readability
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if cell.value and len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # Cap at 50
                worksheet.column_dimensions[column_letter].width = adjusted_width


def export_test_cases_user_format(test_cases: List[TestCase], output_path: str):
    """
    Export test cases to Excel in user's preferred format:
    - Test Case ID, Layer, Test Case Scenario, Test Case, Pre-Condition, 
      Test Case Type, Test Steps, Expected Result, Priority
    - Test steps are numbered and combined in single cell
    - Expected results are combined in single cell
    """
    data = []
    
    for tc in test_cases:
        # Combine test steps into multi-line string with numbering
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
        
        data.append({
            "Test Case ID": tc.id,
            "Layer": tc.business_rule,
            "Test Case Scenario": tc.description,
            "Test Case": title,
            "Pre-Condition": preconditions_text,
            "Test Case Type": test_case_type,
            "Test Steps": test_steps_text,
            "Expected Result": expected_results_text,
            "Priority": tc.priority
        })
    
    # Create DataFrame and export
    df = pd.DataFrame(data)
    
    # Use openpyxl for better control
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Test Cases', index=False)
        
        # Get worksheet
        worksheet = writer.sheets['Test Cases']
        
        # Set column widths for better readability
        column_widths = {
            'A': 20,  # Test Case ID
            'B': 25,  # Layer
            'C': 40,  # Test Case Scenario
            'D': 40,  # Test Case
            'E': 50,  # Pre-Condition
            'F': 15,  # Test Case Type
            'G': 50,  # Test Steps
            'H': 50,  # Expected Result
            'I': 12   # Priority
        }
        
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width
        
        # Enable text wrapping for all cells
        from openpyxl.styles import Alignment
        for row in worksheet.iter_rows(min_row=2):  # Skip header
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical='top')


def export_to_csv(test_cases: List[TestCase], output_path: str):
    """Export test cases to CSV"""
    data = []
    for tc in test_cases:
        steps_text = " | ".join([
            f"{s.step_number}. {s.action} -> {s.expected_result}"
            for s in tc.test_steps
        ])
        
        data.append({
            "ID": tc.id,
            "Title": tc.title,
            "Description": tc.description,
            "Preconditions": " | ".join(tc.preconditions),
            "Test Steps": steps_text,
            "Expected Outcome": tc.expected_outcome,
            "Tags": " | ".join(tc.tags),
            "Priority": tc.priority,
            "Test Type": tc.test_type
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)


def parse_test_case_json(json_data: Dict[str, Any]) -> TestCase:
    """Parse JSON data into TestCase model"""
    
    def ensure_list(value) -> List[str]:
        """Convert value to list if it's a string or None"""
        if value is None:
            return []
        elif isinstance(value, str):
            # If it's a non-empty string, wrap it in a list
            return [value] if value.strip() else []
        elif isinstance(value, list):
            # Ensure all items in list are strings
            return [str(item) if not isinstance(item, str) else item for item in value]
        else:
            return []
    
    # Parse test steps
    test_steps = []
    for i, step in enumerate(json_data.get("test_steps", []), 1):
        if isinstance(step, dict):
            # Handle dict format with action/expected_result
            action = step.get("action", "")
            # Remove any existing numbering from action if present
            if has_existing_numbering(action):
                action = remove_existing_numbering(action)
            
            test_steps.append(TestStep(
                step_number=step.get("step_number", i),
                action=action,
                expected_result=step.get("expected_result", "")
            ))
        elif isinstance(step, str):
            # Handle simple string steps
            # Remove any existing numbering since we'll use step_number field
            clean_action = remove_existing_numbering(step) if has_existing_numbering(step) else step
            test_steps.append(TestStep(
                step_number=i,
                action=clean_action,
                expected_result=""
            ))
    
    # Generate ID if not provided
    test_id = json_data.get("id", "")
    if not test_id:
        test_id = generate_id(json_data.get("title", "") + json_data.get("description", ""))
    
    # Get priority
    priority = json_data.get("priority", "Medium")
    
    # Get is_regression flag
    # Option 1: Try to read from JSON if present
    is_regression = json_data.get("is_regression", None)
    
    # Option 2: If not explicitly set, auto-determine based on priority
    if is_regression is None:
        # Automatically mark High and Critical priority tests as regression
        is_regression = priority in ['High', 'Critical']
    
    # Get title and description - ensure description is never blank
    title = json_data.get("title", "").strip()
    description = json_data.get("description", "").strip()
    
    # If title is missing or empty, generate one from description or test steps
    if not title:
        if description:
            # Use first 80 characters of description as title
            title = description[:80].strip()
            if len(description) > 80:
                title = title.rsplit(' ', 1)[0] + "..."
        elif test_steps:
            # Generate title from first test step
            first_step_action = test_steps[0].action if test_steps else ""
            if first_step_action:
                title = f"Verify {first_step_action[:70]}"
                if len(first_step_action) > 70:
                    title = title.rsplit(' ', 1)[0] + "..."
            else:
                title = "Test functional requirement"
        else:
            title = "Test functional requirement"
    
    # If description is blank, use title or generate a default description
    if not description:
        if title:
            description = title
        else:
            description = "Functional requirement validation"
    
    # Validate test type - must be Positive or Negative
    test_type = validate_test_type(json_data.get("test_type", ""))
    
    return TestCase(
        id=test_id,
        title=title,
        description=description,
        business_rule=json_data.get("business_rule", "Functional requirement validation"),
        preconditions=ensure_list(json_data.get("preconditions")),
        test_steps=test_steps,
        expected_outcome=json_data.get("expected_outcome", ""),
        postconditions=ensure_list(json_data.get("postconditions")),
        tags=ensure_list(json_data.get("tags")),
        priority=priority,
        test_type=test_type,
        is_regression=is_regression,
        boundary_conditions=ensure_list(json_data.get("boundary_conditions")),
        side_effects=ensure_list(json_data.get("side_effects")),
        source_document=json_data.get("source_document")
    )


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Simple text similarity calculation (Jaccard similarity)
    This is a fallback if embedding similarity is not available
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)


def format_timestamp(dt: datetime) -> str:
    """Format datetime for display"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def import_from_excel(file_path: str) -> List[TestCase]:
    """
    Import test cases from Excel file
    
    Supports multiple column naming conventions:
    
    Standard format:
    - Title, Description, Test Steps, Expected Outcome (required)
    - Business Rule, Preconditions, Tags, Priority, Test Type, ID (optional)
    
    Custom format (user's format):
    - Test Case ID, Layer, Test Case Scenario, Test Case, Pre-Condition,
      Test Case Type, Test Steps, Expected Result
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        List of TestCase objects
    """
    df = pd.read_excel(file_path, engine='openpyxl')
    test_cases = []
    
    # Column mapping: map various possible column names to our standard names
    column_mapping = {
        # ID mappings
        'id': ['ID', 'Test Case ID', 'TestCaseID', 'Test_Case_ID'],
        # Title mappings  
        'title': ['Title', 'Test Case', 'TestCase', 'Test Case Scenario', 'Scenario'],
        # Description mappings
        'description': ['Description', 'Test Case Scenario', 'Scenario', 'Summary'],
        # Business Rule mappings
        'business_rule': ['Business Rule', 'Layer', 'Module', 'Feature'],
        # Preconditions mappings
        'preconditions': ['Preconditions', 'Pre-Condition', 'Pre-Conditions', 'Prerequisites'],
        # Test Steps mappings
        'test_steps': ['Test Steps', 'Steps', 'Test_Steps', 'Procedure'],
        # Expected Outcome mappings  
        'expected_outcome': ['Expected Outcome', 'Expected Result', 'Expected_Result', 'Expected'],
        # Priority mappings
        'priority': ['Priority', 'Severity', 'Importance'],
        # Test Type mappings
        'test_type': ['Test Type', 'Test_Type', 'Type', 'Test Case Type', 'Category'],
        # Tags mappings
        'tags': ['Tags', 'Labels', 'Categories'],
        # Postconditions mappings
        'postconditions': ['Postconditions', 'Post-Condition', 'Post-Conditions'],
        # Regression flag mappings
        'is_regression': ['is_regression', 'Is Regression', 'Regression', 'Regression Test', 'Is_Regression']
    }
    
    def find_column(field_name: str) -> str | None:
        """Find the actual column name in DataFrame for a given field"""
        possible_names = column_mapping.get(field_name, [])
        for col_name in df.columns:
            if col_name in possible_names:
                return col_name
        return None
    
    # Find actual column names from DataFrame
    id_col = find_column('id')
    title_col = find_column('title')
    desc_col = find_column('description')
    business_rule_col = find_column('business_rule')
    precond_col = find_column('preconditions')
    steps_col = find_column('test_steps')
    expected_col = find_column('expected_outcome')
    priority_col = find_column('priority')
    type_col = find_column('test_type')
    tags_col = find_column('tags')
    postcond_col = find_column('postconditions')
    is_regression_col = find_column('is_regression')
    
    for row_idx, row in df.iterrows():
        try:
            # Parse test steps
            test_steps = []
            steps_text = str(row.get(steps_col, '')) if steps_col else ''
            
            if steps_text and steps_text != 'nan':
                # Split by newlines or numbered format
                step_lines = [s.strip() for s in steps_text.split('\n') if s.strip()]
                
                for i, step_line in enumerate(step_lines, 1):
                    # Try to parse "action -> expected_result" format
                    if '->' in step_line:
                        parts = step_line.split('->', 1)
                        action = parts[0].strip()
                        expected = parts[1].strip() if len(parts) > 1 else ""
                        
                        # Remove any existing numbering from action
                        if has_existing_numbering(action):
                            action = remove_existing_numbering(action)
                    else:
                        action = step_line
                        # Remove any existing numbering from action
                        if has_existing_numbering(action):
                            action = remove_existing_numbering(action)
                        expected = ""
                    
                    test_steps.append(TestStep(
                        step_number=i,
                        action=action,
                        expected_result=expected
                    ))
            
            # If no test steps, create a default one
            if not test_steps:
                desc_value = str(row.get(desc_col, 'Execute test')) if desc_col else 'Execute test'
                expected_value = str(row.get(expected_col, 'Test passes')) if expected_col else 'Test passes'
                
                test_steps.append(TestStep(
                    step_number=1,
                    action=desc_value,
                    expected_result=expected_value
                ))
            
            # Helper to parse comma-separated lists
            def parse_list(value) -> List[str]:
                if pd.isna(value) or value == '':
                    return []
                return [item.strip() for item in str(value).split(',') if item.strip()]
            
            # Generate ID if not provided
            test_id = row.get(id_col, '') if id_col else ''
            if pd.isna(test_id) or test_id == '':
                title_val = str(row.get(title_col, '')) if title_col else ''
                desc_val = str(row.get(desc_col, '')) if desc_col else ''
                test_id = generate_id(title_val + desc_val)
            
            # Get title (use Test Case or Test Case Scenario)
            title = str(row.get(title_col, 'Untitled Test')) if title_col else 'Untitled Test'
            if pd.isna(title) or not title.strip() or title == 'nan':
                title = 'Untitled Test'
            
            # Get description (fallback to title if description column not found or blank)
            description = str(row.get(desc_col, '')) if desc_col else ''
            if pd.isna(description) or not description.strip() or description == 'nan':
                # If description is blank, use title or generate a default
                description = title if title != 'Untitled Test' else "Functional requirement validation"
            
            # Get business rule (Layer or Business Rule)
            business_rule = str(row.get(business_rule_col, 'Functional requirement validation')) if business_rule_col else 'Functional requirement validation'
            
            # Get preconditions
            preconditions = parse_list(row.get(precond_col, '')) if precond_col else []
            
            # Get expected outcome
            expected_outcome = str(row.get(expected_col, 'Test completes successfully')) if expected_col else 'Test completes successfully'
            
            # Get priority
            priority = str(row.get(priority_col, 'Medium')) if priority_col else 'Medium'
            
            # Get test type and validate (must be Positive or Negative)
            test_type_raw = str(row.get(type_col, '')) if type_col else ''
            test_type = validate_test_type(test_type_raw)
            
            # Get tags
            tags = parse_list(row.get(tags_col, '')) if tags_col else []
            
            # Get postconditions
            postconditions = parse_list(row.get(postcond_col, '')) if postcond_col else []
            
            # Get priority (defaults to Medium)
            priority = str(row.get(priority_col, 'Medium')) if priority_col else 'Medium'
            
            # Get is_regression flag
            # Option 1: Try to read from Excel column if present
            is_regression = False
            if is_regression_col:
                regression_value = row.get(is_regression_col, '')
                if not pd.isna(regression_value):
                    # Handle various boolean representations
                    if isinstance(regression_value, bool):
                        is_regression = regression_value
                    elif isinstance(regression_value, str):
                        is_regression = regression_value.lower() in ['true', 'yes', '1', 'y']
                    else:
                        is_regression = bool(regression_value)
            
            # Option 2: If not explicitly set, auto-determine based on priority
            if not is_regression:
                # Automatically mark High and Critical priority tests as regression
                is_regression = priority in ['High', 'Critical']
            
            # Create TestCase
            test_case = TestCase(
                id=str(test_id),
                title=title,
                description=description,
                business_rule=business_rule,
                preconditions=preconditions,
                test_steps=test_steps,
                expected_outcome=expected_outcome,
                postconditions=postconditions,
                tags=tags,
                priority=priority,
                test_type=test_type,
                is_regression=is_regression,
                boundary_conditions=[],
                side_effects=[]
            )
            
            test_cases.append(test_case)
            
        except Exception as e:
            # Convert row_idx to int for arithmetic operation
            row_num = int(row_idx) + 2 if isinstance(row_idx, (int, float)) else 0
            print(f"Warning: Failed to parse row {row_num}: {str(e)}")
            continue
    
    return test_cases



def import_from_json(file_path: str) -> List[TestCase]:
    """
    Import test cases from JSON file
    
    Expected format - either:
    1. Array of test case objects
    2. Object with "test_cases" array
    
    Each test case should have at minimum:
    - title
    - description
    - test_steps (array of step objects or strings)
    - expected_outcome
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        List of TestCase objects
    """
    data = load_json(file_path)
    test_cases = []
    
    # Handle different JSON structures
    if isinstance(data, list):
        test_cases_data = data
    elif isinstance(data, dict):
        if 'test_cases' in data:
            test_cases_data = data['test_cases']
        elif 'testCases' in data:
            test_cases_data = data['testCases']
        else:
            # Try to treat the dict as a single test case
            test_cases_data = [data]
    else:
        raise ValueError("Invalid JSON format: must be array or object with 'test_cases' field")
    
    # Parse each test case
    for tc_data in test_cases_data:
        try:
            # Ensure tc_data is a dict before parsing
            if not isinstance(tc_data, dict):
                print(f"Warning: Skipping invalid test case data (not a dict): {type(tc_data)}")
                continue
                
            test_case = parse_test_case_json(tc_data)
            test_cases.append(test_case)
        except Exception as e:
            # Safely get title if tc_data is a dict
            title = tc_data.get('title', 'unknown') if isinstance(tc_data, dict) else 'unknown'
            print(f"Warning: Failed to parse test case '{title}': {str(e)}")
            continue
    
    return test_cases
