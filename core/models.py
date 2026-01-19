"""
Pydantic models for test case management system
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class DecisionType(str, Enum):
    """Decision types for test case comparison"""
    SAME = "same"
    ADDON = "add-on"
    NEW = "new"


class TestStep(BaseModel):
    """Individual test step"""
    step_number: int
    action: str
    expected_result: str


class TestCase(BaseModel):
    """Structured test case model"""
    id: str = Field(default="", description="Unique identifier")
    title: str
    description: str
    business_rule: str = Field(default="Functional requirement validation", description="Business rule being tested")
    preconditions: List[str] = Field(default_factory=list)
    test_steps: List[TestStep]
    expected_outcome: str
    postconditions: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    priority: str = "Medium"
    test_type: str = "Frontend"  # Frontend or Backend
    is_regression: bool = Field(default=False, description="Whether this is a regression test case")
    boundary_conditions: List[str] = Field(default_factory=list)
    side_effects: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: int = 1
    source_document: Optional[str] = None
    
    def to_text(self) -> str:
        """Convert test case to searchable text"""
        # Format steps without adding numbers since step_number is already part of the structure
        steps_text = "\n".join([
            f"Step {s.step_number}: {s.action} -> {s.expected_result}"
            for s in self.test_steps
        ])
        
        return f"""
Title: {self.title}
Description: {self.description}
Business Rule: {self.business_rule}
Preconditions: {', '.join(self.preconditions)}
Test Steps:
{steps_text}
Expected Outcome: {self.expected_outcome}
Postconditions: {', '.join(self.postconditions)}
Boundary Conditions: {', '.join(self.boundary_conditions)}
Side Effects: {', '.join(self.side_effects)}
Tags: {', '.join(self.tags)}
        """.strip()


class ComparisonResult(BaseModel):
    """Result of comparing two test cases"""
    new_test_case_id: str
    existing_test_case_id: Optional[str] = None
    similarity_score: float
    decision: DecisionType
    reasoning: str
    business_rule_match: bool
    behavior_match: bool
    coverage_expansion: List[str] = Field(default_factory=list)
    confidence_score: float
    timestamp: datetime = Field(default_factory=datetime.now)


class TestSuite(BaseModel):
    """Collection of test cases"""
    name: str
    description: str
    test_cases: List[TestCase] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: int = 1
    
    def add_test_case(self, test_case: TestCase):
        """Add a test case to the suite"""
        self.test_cases.append(test_case)
        self.updated_at = datetime.now()
    
    def get_test_case_by_id(self, test_case_id: str) -> Optional[TestCase]:
        """Retrieve test case by ID"""
        for tc in self.test_cases:
            if tc.id == test_case_id:
                return tc
        return None
    
    def update_test_case(self, test_case: TestCase):
        """Update existing test case"""
        for i, tc in enumerate(self.test_cases):
            if tc.id == test_case.id:
                test_case.version += 1
                test_case.updated_at = datetime.now()
                self.test_cases[i] = test_case
                self.updated_at = datetime.now()
                break


class UserStory(BaseModel):
    """User story or requirement document"""
    id: str
    title: str
    description: str
    acceptance_criteria: List[str] = Field(default_factory=list)
    business_rules: List[str] = Field(default_factory=list)
    context: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
