"""
FastAPI REST API for RAG-based Test Case Management System
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import sys
import uvicorn

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import UserStory, TestCase, ComparisonResult, DecisionType
from engines.test_case_manager import TestCaseManager
from config.config import Config
from core.utils import generate_id

# Initialize FastAPI app
app = FastAPI(
    title="RAG Test Case Manager API",
    description="Intelligent test case management using Retrieval-Augmented Generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize manager
manager = TestCaseManager()


# ============================================================================
# Request/Response Models
# ============================================================================

class RequirementTextRequest(BaseModel):
    """Request model for processing requirement text"""
    requirement_text: str = Field(..., description="Requirement text to process")
    suite_name: str = Field(default="default", description="Test suite name")
    auto_apply: bool = Field(default=False, description="Auto-apply decisions")
    num_test_cases: Optional[int] = Field(
        default=None, 
        description="Number of test cases to generate (defaults to configured value)",
        ge=5,
        le=30
    )


class UserStoryRequest(BaseModel):
    """Request model for processing user story"""
    title: str = Field(..., description="User story title")
    description: str = Field(..., description="User story description")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance criteria")
    business_rules: List[str] = Field(default_factory=list, description="Business rules")
    context: Optional[str] = Field(None, description="Additional context")
    suite_name: str = Field(default="default", description="Test suite name")
    auto_apply: bool = Field(default=False, description="Auto-apply decisions")
    num_test_cases: Optional[int] = Field(
        default=None,
        description="Number of test cases to generate (defaults to configured value)",
        ge=5,
        le=30
    )


class ProcessingResult(BaseModel):
    """Response model for processing results"""
    success: bool
    message: str
    generated_test_cases: List[TestCase]
    results: List[Dict[str, Any]]
    actions_taken: List[str]
    summary: Dict[str, Any]


class ApplyDecisionRequest(BaseModel):
    """Request model for applying a decision"""
    test_case: TestCase
    comparison: ComparisonResult
    suite_name: str = Field(default="default")
    user_approved: bool = Field(default=True)


class ExportRequest(BaseModel):
    """Request model for export operations"""
    suite_name: str = Field(default="default")
    format: str = Field(default="excel", description="Export format: excel, csv, json")


class FilteredExportRequest(BaseModel):
    """Request model for filtered test suite export"""
    suite_name: str = Field(default="default", description="Test suite name")
    format: str = Field(default="excel", description="Export format: excel, csv, json")
    priorities: Optional[List[str]] = Field(None, description="Filter by priorities (e.g., ['High', 'Critical'])")
    test_types: Optional[List[str]] = Field(None, description="Filter by test types (e.g., ['Functional', 'Integration'])")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    is_regression: Optional[bool] = Field(None, description="Filter regression tests (true=only regression, false=only non-regression)")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    config_valid: bool
    total_test_cases: int


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["General"])
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Test Case Manager API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    stats = manager.get_statistics()
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        config_valid=Config.validate(),
        total_test_cases=stats['knowledge_base']['total_test_cases']
    )


@app.post("/process/requirement", response_model=ProcessingResult, tags=["Processing"])
async def process_requirement_text(request: RequirementTextRequest):
    """
    Process requirement text and generate test cases
    
    - **requirement_text**: The requirement text to process
    - **suite_name**: Name of the test suite (default: "default")
    - **auto_apply**: Automatically apply decisions (default: false)
    - **num_test_cases**: Number of test cases to generate (5-30, default: configured value)
    """
    try:
        results = manager.process_requirement_text(
            request.requirement_text,
            suite_name=request.suite_name,
            auto_apply=request.auto_apply,
            num_test_cases=request.num_test_cases
        )
        
        return ProcessingResult(
            success=True,
            message="Requirement processed successfully",
            generated_test_cases=results['generated_test_cases'],
            results=results['results'],
            actions_taken=results['actions_taken'],
            summary=results['summary']
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing requirement: {str(e)}"
        )


@app.post("/process/user-story", response_model=ProcessingResult, tags=["Processing"])
async def process_user_story(request: UserStoryRequest):
    """
    Process user story and generate test cases
    
    - **title**: User story title
    - **description**: User story description
    - **acceptance_criteria**: List of acceptance criteria
    - **business_rules**: List of business rules
    - **context**: Additional context (optional)
    - **suite_name**: Name of the test suite (default: "default")
    - **auto_apply**: Automatically apply decisions (default: false)
    """
    try:
        user_story = UserStory(
            id=generate_id(request.title),
            title=request.title,
            description=request.description,
            acceptance_criteria=request.acceptance_criteria,
            business_rules=request.business_rules,
            context=request.context
        )
        
        results = manager.process_user_story(
            user_story,
            suite_name=request.suite_name,
            auto_apply=request.auto_apply,
            num_test_cases=request.num_test_cases
        )
        
        return ProcessingResult(
            success=True,
            message="User story processed successfully",
            generated_test_cases=results['generated_test_cases'],
            results=results['results'],
            actions_taken=results['actions_taken'],
            summary=results['summary']
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing user story: {str(e)}"
        )


@app.post("/apply-decision", tags=["Processing"])
async def apply_decision(request: ApplyDecisionRequest):
    """
    Apply a decision for a test case
    
    - **test_case**: The test case
    - **comparison**: The comparison result
    - **suite_name**: Name of the test suite
    - **user_approved**: Whether the user approved the decision
    """
    try:
        action = manager.apply_decision(
            request.test_case,
            request.comparison,
            suite_name=request.suite_name,
            user_approved=request.user_approved
        )
        
        return {
            "success": True,
            "message": "Decision applied successfully",
            "action": action
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error applying decision: {str(e)}"
        )


@app.get("/test-cases", response_model=List[TestCase], tags=["Test Cases"])
async def get_test_cases(suite_name: str = "default"):
    """
    Get all test cases from a suite
    
    - **suite_name**: Name of the test suite (default: "default")
    """
    try:
        test_cases = manager.get_test_suite(suite_name)
        return test_cases
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving test cases: {str(e)}"
        )


@app.get("/test-cases/{test_case_id}", response_model=TestCase, tags=["Test Cases"])
async def get_test_case(test_case_id: str, suite_name: str = "default"):
    """
    Get a specific test case by ID
    
    - **test_case_id**: ID of the test case
    - **suite_name**: Name of the test suite (default: "default")
    """
    try:
        test_case = manager.knowledge_base.get_test_case_from_suite(suite_name, test_case_id)
        if not test_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test case {test_case_id} not found"
            )
        return test_case
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving test case: {str(e)}"
        )


@app.get("/suites", response_model=List[str], tags=["Test Suites"])
async def list_suites():
    """List all test suites"""
    try:
        suites = manager.knowledge_base.list_suites()
        return suites
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing suites: {str(e)}"
        )


@app.get("/statistics", tags=["Statistics"])
async def get_statistics():
    """Get system statistics"""
    try:
        stats = manager.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )


@app.post("/export/test-suite", tags=["Export"])
async def export_test_suite(request: ExportRequest, background_tasks: BackgroundTasks):
    """
    Export test suite to file
    
    - **suite_name**: Name of the test suite
    - **format**: Export format (excel, csv, json)
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{request.suite_name}_{timestamp}.{request.format if request.format != 'excel' else 'xlsx'}"
        output_path = os.path.join(Config.TEST_SUITE_OUTPUT, filename)
        
        manager.export_test_suite(
            request.suite_name,
            output_path,
            format=request.format
        )
        
        return FileResponse(
            path=output_path,
            filename=filename,
            media_type='application/octet-stream'
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting test suite: {str(e)}"
        )


@app.post("/export/filtered-test-suite", tags=["Export"])
async def export_filtered_test_suite(request: FilteredExportRequest, background_tasks: BackgroundTasks):
    """
    Export filtered test suite to file
    
    - **suite_name**: Name of the test suite
    - **format**: Export format (excel, csv, json)
    - **priorities**: Filter by priorities (e.g., ["High", "Critical"])
    - **test_types**: Filter by test types (e.g., ["Functional", "Integration"])
    - **tags**: Filter by tags (test case must have at least one matching tag)
    - **is_regression**: Filter regression tests (true=only regression, false=only non-regression)
    
    Example for regression suite:
    ```json
    {
        "suite_name": "default",
        "format": "excel",
        "priorities": ["High", "Critical"],
        "is_regression": true
    }
    ```
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Build descriptive filename based on filters
        filter_parts = []
        if request.is_regression is True:
            filter_parts.append("regression")
        elif request.is_regression is False:
            filter_parts.append("non_regression")
        if request.priorities:
            filter_parts.append("_".join(request.priorities))
        if request.test_types:
            filter_parts.append("_".join(request.test_types))
        if request.tags:
            filter_parts.append("_".join(request.tags))
        
        filter_suffix = "_" + "_".join(filter_parts) if filter_parts else ""
        filename = f"{request.suite_name}{filter_suffix}_{timestamp}.{request.format if request.format != 'excel' else 'xlsx'}"
        output_path = os.path.join(Config.TEST_SUITE_OUTPUT, filename)
        
        manager.export_test_suite(
            request.suite_name,
            output_path,
            format=request.format,
            priorities=request.priorities,
            test_types=request.test_types,
            tags=request.tags,
            is_regression=request.is_regression
        )
        
        return FileResponse(
            path=output_path,
            filename=filename,
            media_type='application/octet-stream'
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting filtered test suite: {str(e)}"
        )


@app.get("/test-cases/filtered", response_model=List[TestCase], tags=["Test Cases"])
async def get_filtered_test_cases(
    suite_name: str = "default",
    priorities: Optional[str] = None,
    test_types: Optional[str] = None,
    tags: Optional[str] = None,
    is_regression: Optional[bool] = None
):
    """
    Get filtered test cases from a suite
    
    - **suite_name**: Name of the test suite
    - **priorities**: Comma-separated priorities (e.g., "High,Critical")
    - **test_types**: Comma-separated test types (e.g., "Functional,Integration")
    - **tags**: Comma-separated tags (e.g., "login,authentication")
    - **is_regression**: Filter regression tests (true/false)
    
    Examples:
    - Regression tests only: `/test-cases/filtered?is_regression=true`
    - High priority regression: `/test-cases/filtered?priorities=High,Critical&is_regression=true`
    """
    try:
        # Parse comma-separated strings into lists
        priority_list = priorities.split(",") if priorities else None
        test_type_list = test_types.split(",") if test_types else None
        tag_list = tags.split(",") if tags else None
        
        test_cases = manager.get_filtered_test_cases(
            suite_name=suite_name,
            priorities=priority_list,
            test_types=test_type_list,
            tags=tag_list,
            is_regression=is_regression
        )
        return test_cases
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving filtered test cases: {str(e)}"
        )



@app.get("/config/thresholds", tags=["Configuration"])
async def get_thresholds():
    """Get current similarity thresholds"""
    return {
        "threshold_same": Config.THRESHOLD_SAME,
        "threshold_addon_min": Config.THRESHOLD_ADDON_MIN,
        "threshold_addon_max": Config.THRESHOLD_ADDON_MAX
    }


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    # Check configuration
    if not Config.validate():
        print("⚠️  Warning: Azure OpenAI credentials not configured")
        print("Please set up your .env file before running the API")
    
    print("🚀 Starting RAG Test Case Manager API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("📊 Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
