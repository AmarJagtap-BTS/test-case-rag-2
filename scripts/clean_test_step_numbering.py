"""
Clean test step numbering from all test cases in knowledge base
Removes "1.", "2.", "Step 1:", etc. from action fields
"""
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import has_existing_numbering, remove_existing_numbering


def clean_knowledge_base(kb_path: str):
    """Clean all test step numbering from knowledge base"""
    
    print(f"🔧 Cleaning test step numbering from: {kb_path}")
    print("=" * 70)
    
    # Load knowledge base
    with open(kb_path, 'r', encoding='utf-8') as f:
        kb_data = json.load(f)
    
    test_cases = kb_data.get('test_cases', [])
    total_cases = len(test_cases)
    cleaned_steps = 0
    cleaned_cases = 0
    
    print(f"\n📊 Total test cases: {total_cases}")
    print("\n🔍 Processing test cases...\n")
    
    for tc_idx, tc in enumerate(test_cases, 1):
        case_modified = False
        title = tc.get('title', f'Test Case {tc_idx}')
        
        for step in tc.get('test_steps', []):
            action = step.get('action', '')
            
            if has_existing_numbering(action):
                old_action = action
                new_action = remove_existing_numbering(action)
                step['action'] = new_action
                
                print(f"✨ Fixed in '{title}':")
                print(f"   OLD: {old_action}")
                print(f"   NEW: {new_action}")
                print()
                
                cleaned_steps += 1
                case_modified = True
        
        if case_modified:
            cleaned_cases += 1
    
    # Update timestamp
    kb_data['updated_at'] = datetime.now().isoformat()
    
    # Save cleaned data
    backup_path = kb_path + '.backup_numbering'
    print(f"\n💾 Creating backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(kb_data, f, indent=2)
    
    print(f"💾 Saving cleaned knowledge base...")
    with open(kb_path, 'w', encoding='utf-8') as f:
        json.dump(kb_data, f, indent=2)
    
    print("\n" + "=" * 70)
    print("✅ CLEANUP COMPLETE!")
    print(f"   Test cases processed: {total_cases}")
    print(f"   Test cases modified: {cleaned_cases}")
    print(f"   Steps cleaned: {cleaned_steps}")
    print("=" * 70)
    
    return cleaned_steps, cleaned_cases


if __name__ == "__main__":
    kb_path = "knowledge_base/default.json"
    
    if not os.path.exists(kb_path):
        print(f"❌ Error: Knowledge base not found at {kb_path}")
        sys.exit(1)
    
    cleaned_steps, cleaned_cases = clean_knowledge_base(kb_path)
    
    if cleaned_steps > 0:
        print(f"\n🎉 Successfully cleaned {cleaned_steps} test steps across {cleaned_cases} test cases!")
    else:
        print(f"\n✅ No test steps needed cleaning - all test steps are already properly formatted!")
