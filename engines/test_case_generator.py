"""
Test case generator using Azure OpenAI with Context Engineering
"""
import os
import sys
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import AzureOpenAI
from config.config import Config
from core.models import TestCase, UserStory
from core.utils import load_json, parse_test_case_json, generate_id, calculate_test_distribution
from engines.context_engineering import ContextEngineer
import json


class TestCaseGenerator:
    """Generate test cases from user stories using LLM with advanced context engineering"""
    
    def __init__(self, use_context_engineering: bool = True):
        """
        Initialize Azure OpenAI client
        
        Args:
            use_context_engineering: Enable advanced context engineering techniques
        """
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
        self.deployment = Config.AZURE_OPENAI_DEPLOYMENT_NAME
        self.prompts = load_json("prompts.json")
        self.use_context_engineering = use_context_engineering
        
        # Initialize context engineer if enabled
        if self.use_context_engineering:
            self.context_engineer = ContextEngineer()
    
    def generate_from_user_story(
        self, 
        user_story: UserStory,
        num_test_cases: Optional[int] = None
    ) -> List[TestCase]:
        """
        Generate test cases from a user story
        
        Args:
            user_story: UserStory object
            num_test_cases: Number of test cases to generate
            
        Returns:
            List of generated TestCases
        """
        # Prepare requirement text
        requirement = f"""
Title: {user_story.title}

Description:
{user_story.description}

Acceptance Criteria:
{chr(10).join(f"- {ac}" for ac in user_story.acceptance_criteria)}

Business Rules:
{chr(10).join(f"- {br}" for br in user_story.business_rules)}
"""
        
        if user_story.context:
            requirement += f"\n\nContext:\n{user_story.context}"
        
        return self.generate_from_text(
            requirement, 
            user_story.id,
            num_test_cases=num_test_cases
        )
    
    def generate_from_text(
        self, 
        requirement_text: str,
        source_document: Optional[str] = None,
        similar_examples: Optional[List[TestCase]] = None,
        domain_context: Optional[Dict[str, Any]] = None,
        num_test_cases: Optional[int] = None
    ) -> List[TestCase]:
        """
        Generate test cases from requirement text with context engineering.
        Automatically uses parallel batch generation if enabled and falls back on errors.
        
        Args:
            requirement_text: Text describing the requirement
            source_document: Optional source document identifier
            similar_examples: Similar test cases from knowledge base (RAG)
            domain_context: Domain-specific context
            num_test_cases: Number of test cases to generate (uses default if not specified)
            
        Returns:
            List of generated TestCases
        """
        # Use configured default if not specified
        if num_test_cases is None:
            num_test_cases = Config.DEFAULT_TEST_CASES
        
        # Validate num_test_cases is within bounds
        num_test_cases = max(Config.MIN_TEST_CASES, min(num_test_cases, Config.MAX_TEST_CASES))
        
        # Check if parallel generation is enabled
        if Config.USE_PARALLEL_GENERATION:
            try:
                print("🚀 Using parallel batch generation...")
                return self._generate_with_parallel_batches(
                    requirement_text, 
                    source_document, 
                    similar_examples, 
                    domain_context,
                    num_test_cases
                )
            except Exception as e:
                print(f"⚠️ Parallel generation failed: {e}")
                print("🔄 Falling back to single request generation...")
                # Fall through to single request method
        
        # Single request generation (original method)
        return self._generate_single_request(
            requirement_text,
            source_document,
            similar_examples,
            domain_context,
            num_test_cases
        )
    
    def _generate_single_request(
        self,
        requirement_text: str,
        source_document: Optional[str] = None,
        similar_examples: Optional[List[TestCase]] = None,
        domain_context: Optional[Dict[str, Any]] = None,
        num_test_cases: Optional[int] = None
    ) -> List[TestCase]:
        """Generate test cases using a single API request"""
        # Use default if not specified
        if num_test_cases is None:
            num_test_cases = Config.DEFAULT_TEST_CASES
        
        # Calculate test distribution
        distribution = calculate_test_distribution(num_test_cases)
        
        # Debug: Print distribution
        print(f"\n🔍 DEBUG - Test Distribution:")
        print(f"   Total requested: {num_test_cases}")
        print(f"   Positive: {distribution['positive']}")
        print(f"   Negative: {distribution['negative']}")
        print(f"   UI: {distribution['ui']}")
        print(f"   Security: {distribution['security']}")
        print(f"   Edge Case: {distribution['edge_case']}")
        print(f"   Distribution string:\n{distribution['distribution_string']}\n")
        
        # Use context engineering if enabled
        if self.use_context_engineering and hasattr(self, 'context_engineer'):
            # Get focus areas automatically
            focus_areas = self.context_engineer.get_focus_areas(requirement_text)
            
            # Enhance the prompt with context engineering
            enhanced_prompts = self.context_engineer.enhance_generation_prompt(
                requirement=requirement_text,
                requirement_type="text",
                domain_context=domain_context,
                similar_examples=similar_examples,
                focus_areas=focus_areas,
                num_test_cases=num_test_cases,
                test_distribution=distribution["distribution_string"]
            )
            system_prompt = enhanced_prompts["system"]
            user_prompt = enhanced_prompts["user"]
            print(f"🔍 DEBUG - Using CONTEXT ENGINEERING")
        else:
            # Use basic prompts with dynamic test case counts
            system_prompt = self.prompts["test_case_generation"]["system"]
            user_prompt = self.prompts["test_case_generation"]["user"].format(
                requirement=requirement_text,
                num_test_cases=num_test_cases,
                test_distribution=distribution["distribution_string"]
            )
            print(f"🔍 DEBUG - Using BASIC PROMPTS")
        
        try:
            # Call Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent JSON formatting
                max_tokens=16000  # Increased to handle up to 25 detailed test cases
            )
            
            # Check if response was truncated
            finish_reason = response.choices[0].finish_reason
            if finish_reason == "length":
                print("⚠️ WARNING: Response was truncated due to token limit")
                print("🔧 This may result in incomplete JSON. Consider reducing complexity or splitting the request.")
            
            # Parse response
            content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Clean JSON content
            content = self._clean_json_content(content)
            
            # Parse JSON with better error handling
            try:
                test_cases_data = json.loads(content)
            except json.JSONDecodeError as json_err:
                # Try to fix common issues and retry
                print(f"⚠️ Initial JSON parse failed: {json_err}")
                print(f"🔧 Attempting to fix JSON...")
                
                # Additional cleaning attempts
                import re
                
                # Attempt 1: Remove any text before the first [ or {
                if '[' in content:
                    content = content[content.index('['):]
                elif '{' in content:
                    content = content[content.index('{'):]
                
                # Attempt 2: Fix more aggressive patterns
                # Fix missing commas between properties
                content = re.sub(r'"\s+\n\s+"', '",\n"', content)
                content = re.sub(r'(["\d\]\}])\s*\n\s*"', r'\1,\n"', content)
                
                # Try parsing again
                try:
                    test_cases_data = json.loads(content)
                    print("✅ JSON successfully parsed after cleanup")
                except json.JSONDecodeError as retry_err:
                    # Attempt 3: Try to salvage by finding valid JSON objects
                    print(f"⚠️ Second parse attempt failed: {retry_err}")
                    print(f"🔧 Attempting aggressive JSON repair...")
                    
                    try:
                        # Try to extract just the array part if it's wrapped
                        array_match = re.search(r'\[.*\]', content, re.DOTALL)
                        if array_match:
                            content = array_match.group(0)
                            # Apply cleaning again
                            content = self._clean_json_content(content)
                            test_cases_data = json.loads(content)
                            print("✅ JSON successfully parsed after aggressive repair")
                        else:
                            raise retry_err
                    except json.JSONDecodeError as final_err:
                        # If still failing, show detailed error
                        print(f"❌ JSON parsing failed after all attempts: {final_err}")
                        print(f"📄 Problematic JSON snippet (first 500 chars):")
                        print(content[:500])
                        print(f"\n🔍 Problematic area around error (position {final_err.pos}):")
                        error_pos = final_err.pos
                        start = max(0, error_pos - 150)
                        end = min(len(content), error_pos + 150)
                        snippet = content[start:end]
                        # Mark the exact error position
                        marker_pos = min(error_pos - start, len(snippet))
                        print(snippet[:marker_pos] + " 👈 ERROR HERE 👉 " + snippet[marker_pos:])
                        
                        # Save to file for debugging
                        try:
                            with open('problematic_json.txt', 'w', encoding='utf-8') as f:
                                f.write(content)
                            print(f"💾 Full JSON saved to 'problematic_json.txt' for debugging")
                        except:
                            pass
                        
                        raise Exception(f"Failed to parse test case JSON: {final_err}. Check the console for details.")
            
            # Convert to TestCase objects
            test_cases = []
            for tc_data in test_cases_data:
                tc = parse_test_case_json(tc_data)
                if source_document:
                    tc.source_document = source_document
                test_cases.append(tc)
            
            return test_cases
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response content: {content[:1000] if len(content) > 1000 else content}")
            raise Exception(f"Failed to parse test case JSON: {e}")
        except ConnectionError as e:
            print(f"Connection error: {e}")
            raise Exception(f"Connection error. Please check your Azure OpenAI endpoint and network connection: {e}")
        except TimeoutError as e:
            print(f"Timeout error: {e}")
            raise Exception(f"Request timed out. Please try again: {e}")
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                raise Exception(f"Connection error. Please verify Azure OpenAI credentials and endpoint: {e}")
            print(f"Error generating test cases: {e}")
            raise Exception(f"Error generating test cases: {e}")
    
    def _escape_quotes_in_strings(self, content: str) -> str:
        """
        Fix unescaped double quotes within JSON string values
        
        This handles cases like:
        "key": "value with "unescaped" quotes"
        
        Args:
            content: JSON string with potential unescaped quotes
            
        Returns:
            JSON string with properly escaped quotes
        """
        import re
        
        # Process line by line to handle multi-line strings
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Look for lines with key-value pairs: "key": "value..."
            if '": "' in line or '":\n' in line:
                # Find all matches of "key": "value"
                # We need to escape quotes within the value part
                
                # Pattern: "key": "value with possible "quotes" inside"
                # Split by ": " to separate key from value
                parts = line.split('": "', 1)
                
                if len(parts) == 2:
                    key_part = parts[0]
                    value_part = parts[1]
                    
                    # Find the proper end of the string value
                    # It should end with ", or " at end of line, or "}
                    
                    # Count quotes in value_part to find where string actually ends
                    in_string = True
                    escaped = False
                    end_pos = -1
                    
                    for i, char in enumerate(value_part):
                        if escaped:
                            escaped = False
                            continue
                        
                        if char == '\\':
                            escaped = True
                            continue
                        
                        if char == '"' and not escaped:
                            # This might be the end of the string
                            # Check what comes after
                            if i + 1 < len(value_part):
                                next_char = value_part[i + 1]
                                if next_char in [',', '\n', '\r', ' ', '}', ']']:
                                    # This is likely the end quote
                                    end_pos = i
                                    break
                            else:
                                # End of line
                                end_pos = i
                                break
                    
                    if end_pos > 0:
                        # Extract the actual value
                        actual_value = value_part[:end_pos]
                        rest_of_line = value_part[end_pos:]
                        
                        # Escape any unescaped quotes in the actual value
                        fixed_value = actual_value.replace('\\"', '___ALREADY_ESCAPED___')
                        fixed_value = fixed_value.replace('"', '\\"')
                        fixed_value = fixed_value.replace('___ALREADY_ESCAPED___', '\\"')
                        
                        # Reconstruct the line
                        line = f'{key_part}": "{fixed_value}{rest_of_line}'
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _clean_json_content(self, content: str) -> str:
        """
        Clean JSON content by removing common issues from LLM responses
        
        Args:
            content: Raw JSON string
            
        Returns:
            Cleaned JSON string
        """
        import re
        
        # Remove any leading/trailing whitespace
        content = content.strip()
        
        # Replace Unicode smart quotes with regular quotes (must be done FIRST)
        content = content.replace('"', '"').replace('"', '"')  # Curly double quotes
        content = content.replace(''', "'").replace(''', "'")  # Curly single quotes
        content = content.replace('„', '"').replace('‟', '"')  # German-style quotes
        content = content.replace('«', '"').replace('»', '"')  # French-style quotes
        
        # Fix unescaped quotes within JSON string values FIRST (most critical)
        content = self._escape_quotes_in_strings(content)
        
        # Remove comments (// style and /* */ style)
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Remove trailing commas before closing brackets/braces (multiple patterns)
        content = re.sub(r',\s*}', '}', content)
        content = re.sub(r',\s*]', ']', content)
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        # Fix missing commas between objects in array (common LLM error)
        # Pattern: }{ should be },{
        content = re.sub(r'}\s*{', '},{', content)
        # Pattern: }" should be },"
        content = re.sub(r'}(\s*)"', r'},\1"', content)
        
        # Fix missing commas between array elements
        # Pattern: ][ should be ],[
        content = re.sub(r']\s*\[', '],[', content)
        
        # Fix missing commas after string values before next property
        # Pattern: "value" "property" should be "value", "property"
        content = re.sub(r'"\s*\n\s*"', '",\n"', content)
        
        # Fix missing commas after closing braces/brackets before property names
        # Pattern: } "property" should be }, "property"
        content = re.sub(r'}(\s+)"', r'},\1"', content)
        # Pattern: ] "property" should be ], "property"  
        content = re.sub(r'](\s+)"', r'],\1"', content)
        
        # Fix single quotes to double quotes for property names
        content = re.sub(r"'([^'\"]+)'(\s*):", r'"\1"\2:', content)
        
        # Fix Python True/False/None to JSON true/false/null
        content = re.sub(r'\bTrue\b', 'true', content)
        content = re.sub(r'\bFalse\b', 'false', content)
        content = re.sub(r'\bNone\b', 'null', content)
        
        # Remove any markdown or text before/after JSON
        if '[' in content or '{' in content:
            # Find the first JSON start
            first_bracket = content.find('[')
            first_brace = content.find('{')
            
            if first_bracket != -1 and (first_brace == -1 or first_bracket < first_brace):
                # Array is first
                content = content[first_bracket:]
                last_bracket = content.rfind(']')
                if last_bracket != -1:
                    content = content[:last_bracket + 1]
                
            elif first_brace != -1:
                # Object is first
                content = content[first_brace:]
                last_brace = content.rfind('}')
                if last_brace != -1:
                    content = content[:last_brace + 1]
        
        # Fix truncated JSON - balance brackets and braces
        open_brackets = content.count('[')
        close_brackets = content.count(']')
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        # Handle truncated JSON by removing incomplete last object
        if open_brackets > close_brackets or open_braces > close_braces:
            print(f"⚠️ Detected unbalanced brackets/braces. Open: [{open_brackets}, {{{open_braces}}} | Close: ]{close_brackets}, }}{close_braces}")
            
            # For arrays of objects, find the last complete object
            if content.strip().startswith('['):
                # Find the last complete object (ends with })
                last_complete_obj = content.rfind('\n  }')
                if last_complete_obj != -1:
                    print(f"🔧 Truncating at last complete object at position {last_complete_obj}")
                    # Check if there's content after this closing brace
                    remaining = content[last_complete_obj + 4:].strip()
                    if remaining and not remaining.startswith(']'):
                        # There's incomplete content, remove it
                        content = content[:last_complete_obj + 4] + '\n]'
                    else:
                        # Just add closing bracket
                        content = content + '\n]'
                else:
                    # No complete objects found, try to close with missing brackets/braces
                    if open_braces > close_braces:
                        missing = open_braces - close_braces
                        print(f"🔧 Adding {missing} missing closing brace(s)")
                        content = content + ('}' * missing)
                    if open_brackets > close_brackets:
                        missing = open_brackets - close_brackets
                        print(f"🔧 Adding {missing} missing closing bracket(s)")
                        content = content + (']' * missing)
            else:
                # For objects, try to close with missing braces
                if open_braces > close_braces:
                    missing = open_braces - close_braces
                    print(f"🔧 Adding {missing} missing closing brace(s)")
                    content = content + ('}' * missing)
                if open_brackets > close_brackets:
                    missing = open_brackets - close_brackets
                    print(f"🔧 Adding {missing} missing closing bracket(s)")
                    content = content + (']' * missing)
        
        # Remove any non-printable characters except newlines, tabs, and spaces
        content = ''.join(char for char in content if char.isprintable() or char in '\n\t ')
        
        # Fix common escaping issues
        content = content.replace("\\'", "'")
        
        # Fix double commas
        content = re.sub(r',\s*,', ',', content)
        
        return content
    
    def _fix_json_errors(self, content: str) -> str:
        """
        Advanced JSON error fixing for common LLM mistakes
        
        Args:
            content: JSON string with potential errors
            
        Returns:
            Fixed JSON string
        """
        import re
        
        # First, don't escape single quotes - they're valid in JSON strings
        # JSON allows single quotes in string values without escaping
        
        # Fix missing commas between properties (more aggressive)
        # Pattern: "value"\n  "property" should be "value",\n  "property"
        content = re.sub(r'"(\s*\n\s+)"', r'",\1"', content)
        
        # Balance braces and brackets
        open_brackets = content.count('[')
        close_brackets = content.count(']')
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        if open_brackets != close_brackets or open_braces != close_braces:
            print(f"🔧 Final balancing - Brackets: {open_brackets}/{close_brackets}, Braces: {open_braces}/{close_braces}")
            
            if open_brackets > close_brackets:
                content = content + (']' * (open_brackets - close_brackets))
            if open_braces > close_braces:
                content = content + ('}' * (open_braces - close_braces))
        
        return content
    
    def extract_business_rule(self, test_case: TestCase) -> str:
        """
        Extract business rule from a test case
        
        Args:
            test_case: TestCase to analyze
            
        Returns:
            Extracted business rule
        """
        # If business rule already exists, return it
        if test_case.business_rule:
            return test_case.business_rule
        
        # Get prompts
        system_prompt = self.prompts["business_rule_extraction"]["system"]
        user_prompt = self.prompts["business_rule_extraction"]["user"].format(
            test_case=test_case.to_text()
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Very low for consistent extraction
                max_tokens=150
            )
            
            result = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
            return result
            
        except Exception as e:
            print(f"Error extracting business rule: {e}")
            return ""
    
    def merge_test_cases(
        self, 
        existing_test_case: TestCase, 
        new_test_case: TestCase
    ) -> TestCase:
        """
        Merge two test cases into one parameterized test case
        
        Args:
            existing_test_case: Existing test case
            new_test_case: New test case to merge
            
        Returns:
            Merged TestCase
        """
        # Get prompts
        system_prompt = self.prompts["merge_test_cases"]["system"]
        user_prompt = self.prompts["merge_test_cases"]["user"].format(
            existing_test_case=existing_test_case.model_dump_json(indent=2),
            new_test_case=new_test_case.model_dump_json(indent=2)
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,  # Balanced for merging
                max_tokens=1500  # Reduced tokens
            )
            
            # Parse response
            content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Clean JSON content
            content = self._clean_json_content(content)
            
            try:
                merged_data = json.loads(content)
            except json.JSONDecodeError as json_err:
                # Save problematic JSON for debugging
                debug_file = "problematic_merge_json.txt"
                with open(debug_file, 'w') as f:
                    f.write(content)
                print(f"⚠️  JSON parsing error: {json_err}")
                print(f"⚠️  Problematic JSON saved to {debug_file}")
                # Try to fix common issues
                content = self._fix_json_errors(content)
                merged_data = json.loads(content)
            
            merged_test_case = parse_test_case_json(merged_data)
            
            # Preserve the existing test case ID and increment version
            merged_test_case.id = existing_test_case.id
            merged_test_case.version = existing_test_case.version + 1
            
            return merged_test_case
            
        except json.JSONDecodeError as json_err:
            print(f"❌ JSON parsing error during merge: {json_err}")
            print(f"   Test cases: '{existing_test_case.title}' + '{new_test_case.title}'")
            print(f"   Falling back to existing test case")
            return existing_test_case
            
        except Exception as e:
            print(f"❌ Error merging test cases: {e}")
            print(f"   Test cases: '{existing_test_case.title}' + '{new_test_case.title}'")
            print(f"   Falling back to existing test case")
            # Fallback: return existing test case
            return existing_test_case
    
    def _generate_with_parallel_batches(
        self,
        requirement_text: str,
        source_document: Optional[str] = None,
        similar_examples: Optional[List[TestCase]] = None,
        domain_context: Optional[Dict[str, Any]] = None,
        num_test_cases: Optional[int] = None
    ) -> List[TestCase]:
        """
        Generate test cases using parallel batch processing for better reliability
        
        Args:
            requirement_text: Text describing the requirement
            source_document: Optional source document identifier
            similar_examples: Similar test cases from knowledge base
            domain_context: Domain-specific context
            num_test_cases: Number of test cases to generate
            
        Returns:
            List of generated TestCases from all batches
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
        
        # Use default if not specified
        if num_test_cases is None:
            num_test_cases = Config.DEFAULT_TEST_CASES
        
        # Calculate distribution for parallel batches
        distribution = calculate_test_distribution(num_test_cases)
        
        # Define batch configurations based on actual distribution
        positive_count = distribution["positive"]
        negative_count = distribution["negative"] 
        ui_count = distribution["ui"]
        security_count = distribution["security"]
        edge_count = distribution["edge_case"]
        
        batches = [
            {
                "focus": "positive and happy path scenarios",
                "count": f"{positive_count}",
                "description": "Valid inputs, expected behaviors, successful flows"
            },
            {
                "focus": "negative and error handling scenarios",
                "count": f"{negative_count}",
                "description": "Invalid inputs, errors, exceptions, failure cases"
            },
            {
                "focus": "UI and user interface scenarios",
                "count": f"{ui_count}",
                "description": "Field visibility, button states, animations, user interactions"
            },
            {
                "focus": "security scenarios",
                "count": f"{security_count}",
                "description": "Authentication, authorization, data protection, session management"
            },
            {
                "focus": "edge cases and boundary conditions",
                "count": f"{edge_count}",
                "description": "Boundary values, timeouts, race conditions, network failures"
            }
        ]
        
        print(f"📦 Generating {num_test_cases} test cases in {len(batches)} parallel batches...")
        print(f"   Distribution: Positive={positive_count}, Negative={negative_count}, UI={ui_count}, Security={security_count}, Edge={edge_count}")
        
        all_test_cases = []
        failed_batches = []
        
        # Execute batches in parallel
        with ThreadPoolExecutor(max_workers=Config.PARALLEL_BATCH_SIZE) as executor:
            # Submit all batch generation tasks
            future_to_batch = {
                executor.submit(
                    self._generate_single_batch,
                    requirement_text,
                    batch["focus"],
                    batch["count"],
                    batch["description"],
                    source_document,
                    similar_examples,
                    domain_context
                ): batch
                for batch in batches
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                batch_name = batch["focus"]
                
                try:
                    # Get result with timeout
                    test_cases = future.result(timeout=Config.BATCH_TIMEOUT_SECONDS)
                    
                    if test_cases:
                        all_test_cases.extend(test_cases)
                        print(f"✅ Batch '{batch_name}': Generated {len(test_cases)} test cases")
                    else:
                        print(f"⚠️ Batch '{batch_name}': No test cases generated")
                        failed_batches.append(batch_name)
                        
                except TimeoutError:
                    print(f"❌ Batch '{batch_name}': Timeout after {Config.BATCH_TIMEOUT_SECONDS}s")
                    failed_batches.append(batch_name)
                    
                except Exception as e:
                    print(f"❌ Batch '{batch_name}': Failed with error: {str(e)}")
                    failed_batches.append(batch_name)
        
        # Report results
        total_batches = len(batches)
        successful_batches = total_batches - len(failed_batches)
        
        print(f"\n📊 Batch Generation Summary:")
        print(f"   ✅ Successful: {successful_batches}/{total_batches} batches")
        print(f"   📝 Total test cases: {len(all_test_cases)}")
        
        if failed_batches:
            print(f"   ⚠️ Failed batches: {', '.join(failed_batches)}")
        
        # If no test cases were generated at all, raise error to trigger fallback
        if not all_test_cases:
            raise Exception("All parallel batches failed to generate test cases")
        
        return all_test_cases
    
    def _generate_single_batch(
        self,
        requirement_text: str,
        focus: str,
        count: str,
        description: str,
        source_document: Optional[str] = None,
        similar_examples: Optional[List[TestCase]] = None,
        domain_context: Optional[Dict[str, Any]] = None
    ) -> List[TestCase]:
        """
        Generate a single batch of test cases with specific focus
        
        Args:
            requirement_text: Text describing the requirement
            focus: What to focus on (e.g., "happy path scenarios")
            count: How many test cases (e.g., "3-4")
            description: Description of what to test
            source_document: Optional source document identifier
            similar_examples: Similar test cases from knowledge base
            domain_context: Domain-specific context
            
        Returns:
            List of TestCases for this batch
        """
        # Build focused prompt
        system_prompt = self.prompts["test_case_generation"]["system"]
        
        # Create batch-specific user prompt
        batch_prompt = f"""
Based on the following requirement, generate {count} test cases focusing SPECIFICALLY on: {focus}

Requirement:
{requirement_text}

Focus Area: {focus}
What to test: {description}

Generate ONLY {count} test cases that cover {focus}.
Follow all the same formatting rules as before.

Return ONLY a valid JSON array starting with [ and ending with ].
NO markdown, NO explanations, JUST the JSON array.
"""
        
        try:
            # Call Azure OpenAI with reduced token limit for batch
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": batch_prompt}
                ],
                temperature=0.3,
                max_tokens=2048  # Smaller per batch to avoid truncation
            )
            
            # Check for truncation
            finish_reason = response.choices[0].finish_reason
            if finish_reason == "length":
                print(f"⚠️ Batch '{focus}' was truncated - may have incomplete test cases")
            
            # Parse response
            content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
            
            if not content:
                print(f"⚠️ Empty response for batch '{focus}'")
                return []
            
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Clean JSON content
            content = self._clean_json_content(content)
            
            # Parse JSON
            try:
                test_cases_data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parse error in batch '{focus}': {e}")
                # Try aggressive cleaning
                content = self._clean_json_content(content)
                test_cases_data = json.loads(content)
            
            # Convert to TestCase objects
            test_cases = []
            for tc_data in test_cases_data:
                tc = parse_test_case_json(tc_data)
                if source_document:
                    tc.source_document = source_document
                test_cases.append(tc)
            
            return test_cases
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON for batch '{focus}': {e}")
            return []
        except Exception as e:
            print(f"Error generating batch '{focus}': {e}")
            return []
