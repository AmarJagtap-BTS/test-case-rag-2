"""
Test case manager - orchestrates the entire workflow
"""
import os
import sys
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import TestCase, UserStory, ComparisonResult, DecisionType
from engines.rag_engine import RAGEngine
from engines.test_case_generator import TestCaseGenerator
from engines.comparison_engine import ComparisonEngine
from core.knowledge_base import KnowledgeBase
from config.config import Config
from core.utils import parse_test_case_json


class TestCaseManager:
    """Main orchestrator for test case management"""
    
    def __init__(self):
        """Initialize all components"""
        self.rag_engine = RAGEngine()
        self.generator = TestCaseGenerator()
        self.comparison_engine = ComparisonEngine()
        self.knowledge_base = KnowledgeBase()
    
    def _analyze_new_test_case(
        self, 
        new_test_case: TestCase,
        top_k: Optional[int] = None
    ) -> ComparisonResult:
        """
        Analyze a new test case against existing knowledge base
        
        Args:
            new_test_case: New test case to analyze
            top_k: Number of similar cases to retrieve (defaults to Config.RAG_TOP_K)
            
        Returns:
            ComparisonResult with decision
        """
        # Use config default if not specified
        if top_k is None:
            top_k = Config.RAG_TOP_K
            
        # Search for similar test cases
        similar_cases = self.rag_engine.search_similar_test_cases(
            new_test_case, 
            top_k=top_k
        )
        
        # If no existing cases, it's a new test case
        if not similar_cases:
            return ComparisonResult(
                new_test_case_id=new_test_case.id,
                existing_test_case_id=None,
                similarity_score=0.0,
                decision=DecisionType.NEW,
                reasoning="No similar test cases found in knowledge base. This is a new test case.",
                business_rule_match=False,
                behavior_match=False,
                coverage_expansion=[],
                confidence_score=1.0
            )
        
        # Get the most similar case
        most_similar = similar_cases[0]
        
        # If similarity is very low, it's a new test case
        if most_similar['similarity'] < Config.THRESHOLD_ADDON_MIN:
            return ComparisonResult(
                new_test_case_id=new_test_case.id,
                existing_test_case_id=most_similar['id'],
                similarity_score=most_similar['similarity'],
                decision=DecisionType.NEW,
                reasoning=f"Low similarity ({most_similar['similarity']:.2%}) with existing test cases. This is a new test case.",
                business_rule_match=False,
                behavior_match=False,
                coverage_expansion=[],
                confidence_score=0.9
            )
        
        # Reconstruct existing test case from stored data
        existing_test_case = self._reconstruct_test_case(most_similar)
        
        # Perform detailed comparison
        comparison_result = self.comparison_engine.compare_test_cases(
            new_test_case,
            existing_test_case
        )
        
        return comparison_result
    
    def _get_recommendation(self, comparison_result: ComparisonResult) -> str:
        """
        Get action recommendation based on comparison result
        
        Args:
            comparison_result: Comparison result
            
        Returns:
            Recommendation text
        """
        if comparison_result.decision == DecisionType.SAME:
            return f"Keep existing test case (ID: {comparison_result.existing_test_case_id}). The new test case is identical."
        
        elif comparison_result.decision == DecisionType.ADDON:
            return f"Modify existing test case (ID: {comparison_result.existing_test_case_id}) to incorporate expanded coverage: {', '.join(comparison_result.coverage_expansion)}"
        
        else:  # NEW
            return f"Create new test case (ID: {comparison_result.new_test_case_id}). No equivalent found in knowledge base."
    
    def _reconstruct_test_case(self, similar_case_data: dict) -> TestCase:
        """
        Reconstruct TestCase object from ChromaDB data
        
        Args:
            similar_case_data: Data from ChromaDB
            
        Returns:
            Reconstructed TestCase
        """
        metadata = similar_case_data['metadata']
        
        # Create a minimal test case from metadata
        test_case_dict = {
            "id": metadata['id'],
            "title": metadata['title'],
            "description": similar_case_data['document'].split('\n')[1].replace('Description: ', ''),
            "business_rule": metadata['business_rule'],
            "preconditions": [],
            "test_steps": [],
            "expected_outcome": "",
            "postconditions": [],
            "tags": metadata['tags'].split(',') if metadata['tags'] else [],
            "priority": metadata['priority'],
            "test_type": metadata['test_type'],
            "boundary_conditions": [],
            "side_effects": [],
            "version": int(metadata['version'])
        }
        
        return parse_test_case_json(test_case_dict)
    
    def process_user_story(
        self,
        user_story: UserStory,
        suite_name: str = "default",
        auto_apply: bool = False,
        num_test_cases: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a user story and generate/compare test cases
        
        Args:
            user_story: UserStory to process
            suite_name: Test suite name
            auto_apply: Automatically apply decisions without review
            num_test_cases: Number of test cases to generate
            
        Returns:
            Dictionary with results
        """
        # Step 1: Generate test cases from user story
        print(f"Generating test cases from user story: {user_story.title} (num_test_cases={num_test_cases or 'default'})")
        new_test_cases = self.generator.generate_from_user_story(
            user_story,
            num_test_cases=num_test_cases
        )
        print(f"Generated {len(new_test_cases)} test cases")
        
        # Step 2: Analyze each test case in parallel for better performance
        results = []
        actions_taken = []
        
        # Determine number of workers (max 4 to avoid rate limits)
        max_workers = min(4, len(new_test_cases))
        
        def analyze_test_case(test_case):
            """Analyze a single test case"""
            print(f"\nAnalyzing: {test_case.title}")
            
            # Compare with existing test cases
            comparison = self._analyze_new_test_case(test_case)
            
            # Get recommendation
            recommendation = self._get_recommendation(comparison)
            
            print(f"Decision: {comparison.decision.value}")
            print(f"Similarity: {comparison.similarity_score:.2%}")
            print(f"Recommendation: {recommendation}")
            
            return {
                "test_case": test_case,
                "comparison": comparison,
                "recommendation": recommendation
            }
        
        # Process test cases in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_tc = {executor.submit(analyze_test_case, tc): tc for tc in new_test_cases}
            
            for future in as_completed(future_to_tc):
                result = future.result()
                results.append(result)
                
                # Apply decision if auto_apply is True
                if auto_apply:
                    action = self._apply_decision(
                        result["test_case"], 
                        result["comparison"], 
                        suite_name
                    )
                    actions_taken.append(action)
        
        return {
            "user_story": user_story,
            "generated_test_cases": new_test_cases,
            "results": results,
            "actions_taken": actions_taken if auto_apply else [],
            "summary": self._generate_summary(results)
        }
    
    def process_requirement_text(
        self,
        requirement_text: str,
        suite_name: str = "default",
        auto_apply: bool = False,
        num_test_cases: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process requirement text and generate/compare test cases
        
        Args:
            requirement_text: Requirement text
            suite_name: Test suite name
            auto_apply: Automatically apply decisions
            num_test_cases: Number of test cases to generate
            
        Returns:
            Dictionary with results
        """
        # Generate test cases
        print(f"Generating test cases from requirement text (num_test_cases={num_test_cases or 'default'})")
        new_test_cases = self.generator.generate_from_text(
            requirement_text,
            num_test_cases=num_test_cases
        )
        print(f"Generated {len(new_test_cases)} test cases")
        
        # Analyze each test case in parallel
        results = []
        actions_taken = []
        
        # Determine number of workers (max 4 to avoid rate limits)
        max_workers = min(10, len(new_test_cases))
        
        def analyze_test_case(test_case):
            """Analyze a single test case"""
            print(f"\nAnalyzing: {test_case.title}")
            
            comparison = self._analyze_new_test_case(test_case)
            recommendation = self._get_recommendation(comparison)
            
            print(f"Decision: {comparison.decision.value}")
            print(f"Similarity: {comparison.similarity_score:.2%}")
            
            return {
                "test_case": test_case,
                "comparison": comparison,
                "recommendation": recommendation
            }
        
        # Process test cases in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_tc = {executor.submit(analyze_test_case, tc): tc for tc in new_test_cases}
            
            for future in as_completed(future_to_tc):
                result = future.result()
                results.append(result)
                
                if auto_apply:
                    action = self._apply_decision(result["test_case"], result["comparison"], suite_name)
                    actions_taken.append(action)
        
        return {
            "requirement_text": requirement_text,
            "generated_test_cases": new_test_cases,
            "results": results,
            "actions_taken": actions_taken if auto_apply else [],
            "summary": self._generate_summary(results)
        }
    
    def apply_decision(
        self,
        test_case: TestCase,
        comparison: ComparisonResult,
        suite_name: str = "default",
        user_approved: bool = True
    ) -> str:
        """
        Apply a decision for a test case
        
        Args:
            test_case: Test case
            comparison: Comparison result
            suite_name: Test suite name
            user_approved: Whether user approved
            
        Returns:
            Action description
        """
        action = self._apply_decision(test_case, comparison, suite_name)
        
        return action
    
    def _apply_decision(
        self,
        test_case: TestCase,
        comparison: ComparisonResult,
        suite_name: str
    ) -> str:
        """Internal method to apply decision"""
        
        if comparison.decision == DecisionType.SAME:
            # Keep existing, don't add new
            return f"Kept existing test case (ID: {comparison.existing_test_case_id})"
        
        elif comparison.decision == DecisionType.ADDON:
            # Merge with existing
            if comparison.existing_test_case_id:
                existing_tc = self.knowledge_base.get_test_case_from_suite(
                    suite_name,
                    comparison.existing_test_case_id
                )
                
                if existing_tc:
                    merged_tc = self.generator.merge_test_cases(existing_tc, test_case)
                    
                    # Update in knowledge base
                    self.knowledge_base.update_test_case_in_suite(suite_name, merged_tc)
                    
                    # Update in RAG engine
                    self.rag_engine.update_test_case(merged_tc)
                    
                    return f"Merged test case into existing (ID: {comparison.existing_test_case_id})"
            
            # Fallback: add as new if no existing ID or existing not found
            self.knowledge_base.add_test_case_to_suite(suite_name, test_case)
            self.rag_engine.add_test_case(test_case)
            return f"Added as new test case (existing not found)"
        
        else:  # NEW
            # Add new test case
            self.knowledge_base.add_test_case_to_suite(suite_name, test_case)
            self.rag_engine.add_test_case(test_case)
            return f"Created new test case (ID: {test_case.id})"
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of results"""
        total = len(results)
        same = len([r for r in results if r['comparison'].decision == DecisionType.SAME])
        addon = len([r for r in results if r['comparison'].decision == DecisionType.ADDON])
        new = len([r for r in results if r['comparison'].decision == DecisionType.NEW])
        
        return {
            "total_test_cases": total,
            "same_count": same,
            "addon_count": addon,
            "new_count": new,
            "same_percentage": (same / total * 100) if total > 0 else 0,
            "addon_percentage": (addon / total * 100) if total > 0 else 0,
            "new_percentage": (new / total * 100) if total > 0 else 0
        }
    
    def get_test_suite(self, suite_name: str = "default") -> List[TestCase]:
        """Get all test cases from a suite"""
        return self.knowledge_base.get_all_test_cases(suite_name)
    
    def get_filtered_test_cases(
        self,
        suite_name: str = "default",
        priorities: Optional[List[str]] = None,
        test_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        is_regression: Optional[bool] = None
    ) -> List[TestCase]:
        """
        Get filtered test cases from a suite
        
        Args:
            suite_name: Name of the test suite
            priorities: List of priorities to include (e.g., ["High", "Critical"])
            test_types: List of test types to include (e.g., ["Functional", "Integration"])
            tags: List of tags - test case must have at least one of these tags
            is_regression: If True, only regression tests; if False, only non-regression
            
        Returns:
            Filtered list of TestCases
        """
        all_test_cases = self.knowledge_base.get_all_test_cases(suite_name)
        filtered = []
        
        for tc in all_test_cases:
            # Check priority filter
            if priorities and tc.priority not in priorities:
                continue
            
            # Check test type filter
            if test_types and tc.test_type not in test_types:
                continue
            
            # Check tags filter (test case must have at least one matching tag)
            if tags and not any(tag in tc.tags for tag in tags):
                continue
            
            # Check regression filter
            if is_regression is not None and tc.is_regression != is_regression:
                continue
            
            filtered.append(tc)
        
        return filtered
    
    def export_test_suite(
        self,
        suite_name: str,
        output_path: str,
        format: str = "excel",
        priorities: Optional[List[str]] = None,
        test_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        is_regression: Optional[bool] = None
    ):
        """
        Export test suite to file with optional filtering
        
        Args:
            suite_name: Name of the test suite
            output_path: Path to save the exported file
            format: Export format (excel, csv, json)
            priorities: Filter by priorities (e.g., ["High", "Critical"])
            test_types: Filter by test types
            tags: Filter by tags
            is_regression: Filter by regression flag
        """
        from core.utils import export_to_excel, export_to_csv, save_json
        
        # Get filtered test cases if filters are provided
        if priorities or test_types or tags or is_regression is not None:
            test_cases = self.get_filtered_test_cases(
                suite_name, priorities, test_types, tags, is_regression
            )
            
            # Export filtered test cases directly
            if format == "json":
                data = [tc.model_dump() for tc in test_cases]
                save_json(data, output_path)
            elif format == "excel":
                export_to_excel(test_cases, output_path)
            elif format == "csv":
                export_to_csv(test_cases, output_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
        else:
            # Export entire suite without filtering
            self.knowledge_base.export_suite(suite_name, output_path, format)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            "knowledge_base": {
                "total_test_cases": self.rag_engine.count(),
                "test_suites": self.knowledge_base.list_suites()
            }
        }
    
    def import_existing_test_cases(
        self,
        file_path: str,
        suite_name: str = "imported",
        file_format: str = "auto"
    ) -> Dict[str, Any]:
        """
        Import existing test cases from a file into the knowledge base
        
        This method allows you to seed the system with pre-existing test cases,
        which will be added to both the knowledge base and RAG engine for
        semantic search and comparison.
        
        Args:
            file_path: Path to the file containing test cases
            suite_name: Name of the test suite to import into
            file_format: Format of the file ('excel', 'json', or 'auto' to detect)
            
        Returns:
            Dictionary with import results:
            {
                'success': bool,
                'imported_count': int,
                'failed_count': int,
                'errors': List[str],
                'test_cases': List[TestCase]
            }
        """
        from core.utils import import_from_excel, import_from_json
        
        # Auto-detect format
        if file_format == "auto":
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.xlsx', '.xls']:
                file_format = "excel"
            elif ext == '.json':
                file_format = "json"
            else:
                return {
                    'success': False,
                    'imported_count': 0,
                    'failed_count': 0,
                    'errors': [f"Unsupported file format: {ext}"],
                    'test_cases': []
                }
        
        # Import test cases from file
        print(f"Importing test cases from {file_path} ({file_format} format)...")
        
        try:
            if file_format == "excel":
                test_cases = import_from_excel(file_path)
            elif file_format == "json":
                test_cases = import_from_json(file_path)
            else:
                return {
                    'success': False,
                    'imported_count': 0,
                    'failed_count': 0,
                    'errors': [f"Unsupported format: {file_format}"],
                    'test_cases': []
                }
            
            if not test_cases:
                return {
                    'success': False,
                    'imported_count': 0,
                    'failed_count': 0,
                    'errors': ["No test cases found in file"],
                    'test_cases': []
                }
            
            print(f"Found {len(test_cases)} test cases in file")
            
            # Add test cases to knowledge base and RAG engine
            imported_count = 0
            failed_count = 0
            errors = []
            
            for test_case in test_cases:
                try:
                    # Add to knowledge base
                    self.knowledge_base.add_test_case_to_suite(suite_name, test_case)
                    imported_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Failed to import {test_case.title}: {str(e)}")
            
            # Add all test cases to RAG engine in batch for efficiency
            try:
                print("Adding test cases to RAG engine for semantic search...")
                self.rag_engine.add_test_cases_batch(test_cases)
                print(f"✓ Added {len(test_cases)} test cases to RAG engine")
            except Exception as e:
                errors.append(f"Failed to add to RAG engine: {str(e)}")
            
            success = imported_count > 0
            
            if success:
                print(f"\n✓ Successfully imported {imported_count} test cases")
                if failed_count > 0:
                    print(f"⚠ Failed to import {failed_count} test cases")
            
            return {
                'success': success,
                'imported_count': imported_count,
                'failed_count': failed_count,
                'errors': errors,
                'test_cases': test_cases
            }
            
        except Exception as e:
            return {
                'success': False,
                'imported_count': 0,
                'failed_count': 0,
                'errors': [f"Import failed: {str(e)}"],
                'test_cases': []
            }
