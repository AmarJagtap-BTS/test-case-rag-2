"""
Knowledge base management for test cases
"""
import os
import sys
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import TestCase, TestSuite
from core.utils import save_json, load_json, generate_id
from config.config import Config


class KnowledgeBase:
    """Manage test case storage and retrieval"""
    
    def __init__(self):
        """Initialize knowledge base"""
        self.base_path = Config.KNOWLEDGE_BASE_PATH
        self.test_suites: Dict[str, TestSuite] = {}
        self._load_existing_suites()
    
    def _load_existing_suites(self):
        """Load existing test suites from disk"""
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path, exist_ok=True)
            return
        
        for filename in os.listdir(self.base_path):
            if filename.endswith('.json'):
                filepath = os.path.join(self.base_path, filename)
                try:
                    data = load_json(filepath)
                    suite = TestSuite(**data)
                    self.test_suites[suite.name] = suite
                except Exception as e:
                    print(f"Error loading suite {filename}: {e}")
    
    def create_test_suite(
        self, 
        name: str, 
        description: str = ""
    ) -> TestSuite:
        """
        Create a new test suite
        
        Args:
            name: Suite name
            description: Suite description
            
        Returns:
            Created TestSuite
        """
        suite = TestSuite(
            name=name,
            description=description
        )
        self.test_suites[name] = suite
        self._save_suite(suite)
        return suite
    
    def get_test_suite(self, name: str) -> Optional[TestSuite]:
        """
        Get test suite by name
        
        Args:
            name: Suite name
            
        Returns:
            TestSuite or None
        """
        return self.test_suites.get(name)
    
    def add_test_case_to_suite(
        self, 
        suite_name: str, 
        test_case: TestCase
    ):
        """
        Add test case to a suite
        
        Args:
            suite_name: Name of the suite
            test_case: TestCase to add
        """
        suite = self.test_suites.get(suite_name)
        if not suite:
            suite = self.create_test_suite(suite_name)
        
        suite.add_test_case(test_case)
        self._save_suite(suite)
    
    def update_test_case_in_suite(
        self, 
        suite_name: str, 
        test_case: TestCase
    ):
        """
        Update test case in a suite
        
        Args:
            suite_name: Name of the suite
            test_case: Updated TestCase
        """
        suite = self.test_suites.get(suite_name)
        if suite:
            suite.update_test_case(test_case)
            self._save_suite(suite)
    
    def get_test_case_from_suite(
        self, 
        suite_name: str, 
        test_case_id: str
    ) -> Optional[TestCase]:
        """
        Get test case from suite
        
        Args:
            suite_name: Suite name
            test_case_id: Test case ID
            
        Returns:
            TestCase or None
        """
        suite = self.test_suites.get(suite_name)
        if suite:
            return suite.get_test_case_by_id(test_case_id)
        return None
    
    def get_all_test_cases(self, suite_name: str = None) -> List[TestCase]:
        """
        Get all test cases from a suite or all suites
        
        Args:
            suite_name: Optional suite name filter
            
        Returns:
            List of TestCases
        """
        if suite_name:
            suite = self.test_suites.get(suite_name)
            return suite.test_cases if suite else []
        
        # Get from all suites
        all_cases = []
        for suite in self.test_suites.values():
            all_cases.extend(suite.test_cases)
        return all_cases
    
    def list_suites(self) -> List[str]:
        """
        List all test suite names
        
        Returns:
            List of suite names
        """
        return list(self.test_suites.keys())
    
    def _save_suite(self, suite: TestSuite):
        """
        Save test suite to disk
        
        Args:
            suite: TestSuite to save
        """
        filepath = os.path.join(
            self.base_path, 
            f"{suite.name.replace(' ', '_')}.json"
        )
        
        # Convert to dict for JSON serialization
        suite_dict = suite.model_dump()
        save_json(suite_dict, filepath)
    
    def export_suite(
        self, 
        suite_name: str, 
        output_path: str,
        format: str = "json"
    ):
        """
        Export test suite to file
        
        Args:
            suite_name: Suite name
            output_path: Output file path
            format: Export format (json, excel, csv)
        """
        from core.utils import export_to_excel, export_to_csv
        
        suite = self.test_suites.get(suite_name)
        if not suite:
            raise ValueError(f"Suite '{suite_name}' not found")
        
        if format == "json":
            save_json(suite.model_dump(), output_path)
        elif format == "excel":
            export_to_excel(suite.test_cases, output_path)
        elif format == "csv":
            export_to_csv(suite.test_cases, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
