"""
Script to fix test step actions by removing number prefixes from existing data
"""
import sys
import os
import json
import re
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import has_existing_numbering, remove_existing_numbering


def fix_test_step_actions(data: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], int]:
    """
    Remove number prefixes from test step actions in the data
    
    Args:
        data: List of test case dictionaries
        
    Returns:
        Tuple of (fixed data, count of steps fixed)
    """
    fixed_count = 0
    
    for test_case in data:
        if "test_steps" in test_case and isinstance(test_case["test_steps"], list):
            for step in test_case["test_steps"]:
                if isinstance(step, dict) and "action" in step:
                    action = step["action"]
                    if has_existing_numbering(action):
                        clean_action = remove_existing_numbering(action)
                        step["action"] = clean_action
                        fixed_count += 1
                        print(f"  Fixed: '{action}' -> '{clean_action}'")
    
    return data, fixed_count


def main():
    """Main function to fix the knowledge base file"""
    knowledge_base_path = "./knowledge_base/default.json"
    backup_path = "./knowledge_base/default.json.backup"
    
    if not os.path.exists(knowledge_base_path):
        print(f"❌ Knowledge base file not found: {knowledge_base_path}")
        return
    
    print("=" * 70)
    print("FIX TEST STEP NUMBERING IN KNOWLEDGE BASE")
    print("=" * 70)
    
    # Load the data
    print(f"\n📂 Loading data from: {knowledge_base_path}")
    with open(knowledge_base_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both list and dict formats
    if isinstance(data, dict) and "test_cases" in data:
        test_cases = data["test_cases"]
    elif isinstance(data, list):
        test_cases = data
    else:
        print(f"❌ Unexpected data format in knowledge base")
        return
    
    print(f"✅ Loaded {len(test_cases)} test cases")
    
    # Create backup
    print(f"\n💾 Creating backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("✅ Backup created")
    
    # Fix the data
    print(f"\n🔧 Fixing test step actions...")
    fixed_test_cases, fixed_count = fix_test_step_actions(test_cases)
    
    if fixed_count == 0:
        print("✅ No test steps needed fixing")
    else:
        print(f"\n✅ Fixed {fixed_count} test steps")
        
        # Update the data with fixed test cases
        if isinstance(data, dict) and "test_cases" in data:
            data["test_cases"] = fixed_test_cases
        else:
            data = fixed_test_cases
        
        # Save the fixed data
        print(f"\n💾 Saving fixed data to: {knowledge_base_path}")
        with open(knowledge_base_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("✅ Data saved successfully")
    
    print("\n" + "=" * 70)
    print("COMPLETED")
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  - Total test cases: {len(test_cases)}")
    print(f"  - Steps fixed: {fixed_count}")
    print(f"  - Backup location: {backup_path}")
    

if __name__ == "__main__":
    main()
