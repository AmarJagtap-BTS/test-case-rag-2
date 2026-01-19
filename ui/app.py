"""
Streamlit UI for RAG-based Test Case Management System
"""
import streamlit as st
import os
import sys
import tempfile
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import UserStory, TestCase, DecisionType
from engines.test_case_manager import TestCaseManager
from config.config import Config
from core.utils import generate_id

# Page configuration
st.set_page_config(
    page_title="RAG Test Case Manager",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .decision-same {
        background-color: #d4edda;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 4px solid #28a745;
    }
    .decision-addon {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 4px solid #ffc107;
    }
    .decision-new {
        background-color: #d1ecf1;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 4px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'manager' not in st.session_state:
    st.session_state.manager = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'suite_name' not in st.session_state:
    st.session_state.suite_name = "default"

def initialize_manager():
    """Initialize the test case manager"""
    if st.session_state.manager is None:
        with st.spinner("Initializing system..."):
            try:
                st.session_state.manager = TestCaseManager()
                st.success(" System initialized successfully!")
            except Exception as e:
                st.error(f" Error initializing system: {e}")
                st.info("Please check your .env file and ensure all credentials are set correctly.")
                return False
    return True

def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">RAG Test Case Manager</div>', unsafe_allow_html=True)
    st.markdown("**Intelligent test case management using Retrieval-Augmented Generation**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check configuration
        if Config.validate():
            st.success("Configuration valid")
        else:
            st.error("Missing Azure OpenAI credentials")
            st.info("Please set up your .env file with Azure OpenAI credentials")
            return
        
        # Initialize manager
        if not initialize_manager():
            return
        
        st.divider()
        
        # Test suite selection
        st.subheader("Test Suite")
        suites = st.session_state.manager.knowledge_base.list_suites()
        
        if suites:
            st.session_state.suite_name = st.selectbox(
                "Select Suite",
                options=suites,
                index=0 if "default" not in suites else suites.index("default")
            )
        else:
            st.session_state.suite_name = st.text_input(
                "Suite Name",
                value="default"
            )
        
        st.divider()
        
        # Statistics
        st.subheader("Statistics")
        stats = st.session_state.manager.get_statistics()
        
        st.metric("Total Test Cases", stats['knowledge_base']['total_test_cases'])
        
        st.divider()
        
        # Export options
        st.subheader("📤 Export")
        
        # Standard export
        if st.button("📄 Export All Test Cases", use_container_width=True):
            output_path = os.path.join(
                Config.TEST_SUITE_OUTPUT,
                f"{st.session_state.suite_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            try:
                st.session_state.manager.export_test_suite(
                    st.session_state.suite_name,
                    output_path,
                    format="excel"
                )
                st.success(f"✅ Exported to {output_path}")
                
                # Add download button
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Download File",
                        data=file,
                        file_name=os.path.basename(output_path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"❌ Export failed: {e}")
        
        # Regression suite export
        st.markdown("---")
        st.markdown("**🎯 Regression Test Suites**")
        
        if st.button("📋 All Regression Tests", use_container_width=True, help="Export all tests marked as regression"):
            output_path = os.path.join(
                Config.TEST_SUITE_OUTPUT,
                f"regression_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            try:
                st.session_state.manager.export_test_suite(
                    st.session_state.suite_name,
                    output_path,
                    format="excel",
                    is_regression=True
                )
                # Count test cases
                test_cases = st.session_state.manager.get_filtered_test_cases(
                    st.session_state.suite_name,
                    is_regression=True
                )
                st.success(f"✅ Exported {len(test_cases)} tests")
                
                # Add download button
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Download File",
                        data=file,
                        file_name=os.path.basename(output_path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"❌ Export failed: {e}")
        
        # Advanced filtering expander
        with st.expander("🔧 Advanced Export Filters"):
            st.markdown("**Custom Filter Options**")
            
            filter_priorities = st.multiselect(
                "Priorities",
                ["Critical", "High", "Medium", "Low"],
                default=None
            )
            
            filter_test_types = st.multiselect(
                "Test Types",
                ["Functional", "Integration", "Regression", "Smoke", "E2E", "UI"],
                default=None
            )
            
            filter_tags = st.text_input(
                "Tags (comma-separated)",
                placeholder="e.g., login, authentication, api"
            )
            
            filter_regression = st.selectbox(
                "Regression Filter",
                ["All", "Regression Only", "Non-Regression Only"],
                index=0
            )
            
            if st.button("📥 Export with Custom Filters", use_container_width=True):
                output_path = os.path.join(
                    Config.TEST_SUITE_OUTPUT,
                    f"custom_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                )
                try:
                    # Parse filters
                    priorities = filter_priorities if filter_priorities else None
                    test_types = filter_test_types if filter_test_types else None
                    tags = [t.strip() for t in filter_tags.split(",")] if filter_tags else None
                    is_regression = True if filter_regression == "Regression Only" else (False if filter_regression == "Non-Regression Only" else None)
                    
                    st.session_state.manager.export_test_suite(
                        st.session_state.suite_name,
                        output_path,
                        format="excel",
                        priorities=priorities,
                        test_types=test_types,
                        tags=tags,
                        is_regression=is_regression
                    )
                    
                    # Count test cases
                    test_cases = st.session_state.manager.get_filtered_test_cases(
                        st.session_state.suite_name,
                        priorities=priorities,
                        test_types=test_types,
                        tags=tags,
                        is_regression=is_regression
                    )
                    st.success(f"✅ Exported {len(test_cases)} tests")
                    
                    # Add download button
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="⬇️ Download File",
                            data=file,
                            file_name=os.path.basename(output_path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"❌ Export failed: {e}")
    
    # Main content
    tabs = st.tabs(["📥 Import KB", "📝 Process Requirements", "📋 View Test Cases", "🎯 Regression Suite"])
    
    # Tab 0: Import KB (Existing Test Cases)
    with tabs[0]:
        st.header("📥 Import Existing Test Cases")
        st.markdown("Upload your existing test cases from **Excel** or **JSON** files to seed the Knowledge Base.")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['xlsx', 'xls', 'json'],
            help="Upload Excel (.xlsx, .xls) or JSON (.json) file containing test cases"
        )
        
        if uploaded_file is not None:
            st.info(f" File uploaded: **{uploaded_file.name}** ({uploaded_file.size} bytes)")
            
            # Use the current suite name from session state
            import_suite_name = st.session_state.suite_name
            
            # Show file format info
            file_ext = uploaded_file.name.split('.')[-1].lower()
            if file_ext in ['xlsx', 'xls']:
                st.markdown("""
                **Excel Format Requirements:**
                - **Required columns**: Title, Description, Test Steps, Expected Outcome
                - **Optional columns**: Preconditions, Postconditions, Tags, Priority, Test Type, ID
                """)
            else:
                st.markdown("""
                **JSON Format Requirements:**
                - Array of test case objects OR object with `test_cases` array
                - Each test case must have: title, description, test_steps, expected_outcome
                """)
            
            if st.button("🚀 Import Test Cases", type="primary"):
                with st.spinner("Importing test cases..."):
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    try:
                        # Import test cases
                        result = st.session_state.manager.import_existing_test_cases(
                            file_path=tmp_path,
                            suite_name=import_suite_name,
                            file_format="auto"
                        )
                        
                        # Clean up temp file
                        os.unlink(tmp_path)
                        
                        # Display results
                        if result['success']:
                            st.success(f" Successfully imported **{result['imported_count']} test cases** into suite `{import_suite_name}`")
                            
                            if result['failed_count'] > 0:
                                st.warning(f"⚠ Failed to import {result['failed_count']} test cases")
                                with st.expander("View Errors"):
                                    for error in result['errors']:
                                        st.error(error)
                            
                            # Show imported test cases
                            st.divider()
                            st.subheader("Imported Test Cases")
                            
                            for i, tc in enumerate(result['test_cases'][:10], 1):
                                with st.expander(f"{i}. {tc.title}"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.markdown(f"**ID:** {tc.id}")
                                        st.markdown(f"**Description:** {tc.description}")
                                    with col2:
                                        st.markdown(f"**Priority:** {tc.priority}")
                                        st.markdown(f"**Type:** {tc.test_type}")
                                        st.markdown(f"**Tags:** {', '.join(tc.tags) if tc.tags else 'None'}")
                            
                            if len(result['test_cases']) > 10:
                                st.info(f"Showing first 10 of {len(result['test_cases'])} imported test cases")
                            
                            # Update statistics
                            stats = st.session_state.manager.get_statistics()
                            st.divider()
                            st.subheader("Updated Statistics")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Total Test Cases in KB", stats['knowledge_base']['total_test_cases'])
                            with col2:
                                st.metric("Test Suites", len(stats['knowledge_base']['test_suites']))
                            
                        else:
                            st.error(" Import failed!")
                            for error in result['errors']:
                                st.error(f"  {error}")
                    
                    except Exception as e:
                        st.error(f" Error during import: {str(e)}")
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
    
    # Tab 1: Process Requirements
    with tabs[1]:
        st.header("Process Requirements")
        
        input_method = st.radio(
            "Input Method",
            options=["Text Input", "User Story Form"],
            horizontal=True
        )
        
        if input_method == "Text Input":
            requirement_text = st.text_area(
                "Enter Requirement (User Story, BRS, or PRD)",
                height=200,
                placeholder="Enter your requirement text here..."
            )
            
            # auto_apply is always enabled
            auto_apply = True
            
            # Use session state to track button click
            if 'generate_clicked' not in st.session_state:
                st.session_state.generate_clicked = False
            
            if st.button(" Generate & Analyze Test Cases", type="primary") or st.session_state.generate_clicked:
                if requirement_text:
                    if not st.session_state.generate_clicked:
                        with st.spinner("Processing requirement..."):
                            try:
                                results = st.session_state.manager.process_requirement_text(
                                    requirement_text,
                                    suite_name=st.session_state.suite_name,
                                    auto_apply=auto_apply
                                )
                                st.session_state.results = results
                                st.session_state.generate_clicked = True
                                st.rerun()
                            except Exception as e:
                                st.error(f" Error: {e}")
                                st.session_state.generate_clicked = False
                    else:
                        st.success(" Processing complete!")
                        st.session_state.generate_clicked = False
                else:
                    st.warning("Please enter requirement text")
        
        else:  # User Story Form
            st.subheader("User Story Details")
            
            title = st.text_input("Title")
            description = st.text_area("Description", height=100)
            
            col1, col2 = st.columns(2)
            with col1:
                acceptance_criteria = st.text_area(
                    "Acceptance Criteria (one per line)",
                    height=100
                )
            with col2:
                business_rules = st.text_area(
                    "Business Rules (one per line)",
                    height=100
                )
            
            context = st.text_area("Additional Context (optional)", height=80)
            
            # auto_apply is always enabled for user story form
            auto_apply = True
            
            # Use session state to track button click
            if 'generate_story_clicked' not in st.session_state:
                st.session_state.generate_story_clicked = False
            
            if st.button(" Generate & Analyze Test Cases", type="primary", key="process_story") or st.session_state.generate_story_clicked:
                if title and description:
                    if not st.session_state.generate_story_clicked:
                        user_story = UserStory(
                            id=generate_id(title),
                            title=title,
                            description=description,
                            acceptance_criteria=[ac.strip() for ac in acceptance_criteria.split('\n') if ac.strip()],
                            business_rules=[br.strip() for br in business_rules.split('\n') if br.strip()],
                            context=context if context else None
                        )
                        
                        with st.spinner("Processing user story..."):
                            try:
                                results = st.session_state.manager.process_user_story(
                                    user_story,
                                    suite_name=st.session_state.suite_name,
                                    auto_apply=auto_apply
                                )
                                st.session_state.results = results
                                st.session_state.generate_story_clicked = True
                                st.rerun()
                            except Exception as e:
                                st.error(f" Error: {e}")
                                st.session_state.generate_story_clicked = False
                    else:
                        st.success(" Processing complete!")
                        st.session_state.generate_story_clicked = False
                else:
                    st.warning("Please fill in title and description")
        
        # Display results
        if st.session_state.results:
            st.divider()
            st.header(" Results")
            
            summary = st.session_state.results['summary']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Test Cases", summary['total_test_cases'])
            with col2:
                st.metric("Same", summary['same_count'], 
                         delta=f"{summary['same_percentage']:.1f}%")
            with col3:
                st.metric("Add-on", summary['addon_count'],
                         delta=f"{summary['addon_percentage']:.1f}%")
            with col4:
                st.metric("New", summary['new_count'],
                         delta=f"{summary['new_percentage']:.1f}%")
            
            st.divider()
            
            # Export results buttons
            col1, col2, col3 = st.columns([2, 1, 1])
            with col2:
                if st.button("📥 Export (Multi-Sheet)", use_container_width=True):
                    from core.utils import export_results_to_excel_with_sheets
                    
                    output_path = os.path.join(
                        Config.TEST_SUITE_OUTPUT,
                        f"results_{st.session_state.suite_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    )
                    
                    try:
                        export_results_to_excel_with_sheets(st.session_state.results, output_path)
                        st.success(f"✓ Exported to {output_path}")
                        
                        # Add download button
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ Download File",
                                data=file,
                                file_name=os.path.basename(output_path),
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                        
                        st.info("""
                        **Export includes 3 sheets:**
                        - Sheet 1: All Test Cases
                        - Sheet 2: Modified (ADD-ON)
                        - Sheet 3: New
                        """)
                    except Exception as e:
                        st.error(f"Export failed: {e}")
            
            with col3:
                if st.button("📄 Export (User Format)", use_container_width=True):
                    from core.utils import export_test_cases_user_format
                    
                    output_path = os.path.join(
                        Config.TEST_SUITE_OUTPUT,
                        f"testcases_{st.session_state.suite_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    )
                    
                    # Extract test cases from results
                    test_cases = [result['test_case'] for result in st.session_state.results['results']]
                    
                    try:
                        export_test_cases_user_format(test_cases, output_path)
                        st.success(f"✓ Exported to {output_path}")
                        
                        # Add download button
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ Download File",
                                data=file,
                                file_name=os.path.basename(output_path),
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                        
                        st.info("""
                        **Columns:** Test Case ID | Layer | Test Case Scenario | 
                        Test Case | Pre-Condition | Test Case Type | 
                        Test Steps | Expected Result | Priority
                        """)
                    except Exception as e:
                        st.error(f"Export failed: {e}")
            
            st.divider()
            
            # Display each result
            for i, result in enumerate(st.session_state.results['results'], 1):
                test_case = result['test_case']
                comparison = result['comparison']
                recommendation = result['recommendation']
                
                # Decision styling
                decision_class = f"decision-{comparison.decision.value}"
                
                with st.expander(f"**{i}. {test_case.title}** - {comparison.decision.value.upper()}", expanded=True):
                    st.markdown(f'<div class="{decision_class}">', unsafe_allow_html=True)
                    st.markdown(f"**Decision:** {comparison.decision.value.upper()}")
                    st.markdown(f"**Similarity:** {comparison.similarity_score:.2%}")
                    st.markdown(f"**Confidence:** {comparison.confidence_score:.2%}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown(f"**Reasoning:** {comparison.reasoning}")
                    st.markdown(f"**Recommendation:** {recommendation}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Test Case Details:**")
                        st.markdown(f"- **Description:** {test_case.description}")
                        st.markdown(f"- **Priority:** {test_case.priority}")
                        st.markdown(f"- **Type:** {test_case.test_type}")
                    
                    with col2:
                        if comparison.coverage_expansion:
                            st.markdown("**Coverage Expansion:**")
                            for ce in comparison.coverage_expansion:
                                st.markdown(f"  - {ce}")
                    
                    # Test Steps
                    if test_case.test_steps:
                        st.markdown("**Test Steps:**")
                        for step in test_case.test_steps:
                            st.markdown(f"{step.step_number}. {step.action}")
                            # st.markdown(f"   *Expected:* {step.expected_result}")
                    
                    # Expected Outcome
                    st.markdown(f"**Expected Outcome:** {test_case.expected_outcome}")
                    
                    # Decisions are auto-applied by default; manual apply button removed
    
    # Tab 2: View Test Cases
    with tabs[2]:
        st.header("Test Cases")
        
        test_cases = st.session_state.manager.get_test_suite(st.session_state.suite_name)
        
        if test_cases:
            # Header with export button
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"{len(test_cases)} test cases in suite '{st.session_state.suite_name}'")
            with col2:
                if st.button("📄 Export All (User Format)", use_container_width=True):
                    from core.utils import export_test_cases_user_format
                    
                    output_path = os.path.join(
                        Config.TEST_SUITE_OUTPUT,
                        f"suite_{st.session_state.suite_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    )
                    
                    try:
                        export_test_cases_user_format(test_cases, output_path)
                        st.success(f"✓ Exported {len(test_cases)} test cases")
                        
                        # Add download button
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ Download File",
                                data=file,
                                file_name=os.path.basename(output_path),
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"Export failed: {e}")
            
            st.divider()
            
            for i, tc in enumerate(test_cases, 1):
                with st.expander(f"{i}. {tc.title} (v{tc.version})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**ID:** {tc.id}")
                        st.markdown(f"**Description:** {tc.description}")
                        st.markdown(f"**Priority:** {tc.priority}")
                        st.markdown(f"**Type:** {tc.test_type}")
                    
                    with col2:
                        st.markdown(f"**Tags:** {', '.join(tc.tags)}")
                        st.markdown(f"**Version:** {tc.version}")
                        st.markdown(f"**Created:** {tc.created_at.strftime('%Y-%m-%d %H:%M')}")
                        st.markdown(f"**Updated:** {tc.updated_at.strftime('%Y-%m-%d %H:%M')}")
                    
                    if tc.preconditions:
                        st.markdown("**Preconditions:**")
                        for pc in tc.preconditions:
                            st.markdown(f"- {pc}")
                    
                    if tc.test_steps:
                        st.markdown("**Test Steps:**")
                        for step in tc.test_steps:
                            st.markdown(f"{step.step_number}. {step.action}")
                            st.markdown(f"   *Expected:* {step.expected_result}")
                    
                    st.markdown(f"**Expected Outcome:** {tc.expected_outcome}")
        else:
            st.info("No test cases in this suite yet. Process some requirements to get started!")
    
    # Tab 3: Regression Suite
    with tabs[3]:
        st.header("🎯 Regression Test Suite")
        st.markdown("View and export test cases marked for regression testing")
        
        # Get regression statistics
        try:
            all_tests = st.session_state.manager.get_test_suite(st.session_state.suite_name)
            regression_tests = st.session_state.manager.get_filtered_test_cases(
                st.session_state.suite_name,
                is_regression=True
            )
            high_critical_regression = st.session_state.manager.get_filtered_test_cases(
                st.session_state.suite_name,
                priorities=["High", "Critical"],
                is_regression=True
            )
            critical_only = st.session_state.manager.get_filtered_test_cases(
                st.session_state.suite_name,
                priorities=["Critical"],
                is_regression=True
            )
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total Tests", len(all_tests))
            with col2:
                st.metric("🎯 Regression Tests", len(regression_tests))
            with col3:
                st.metric("🔥 High/Critical", len(high_critical_regression))
            with col4:
                st.metric("⚡ Critical Only", len(critical_only))
            
            # Coverage percentage
            if len(all_tests) > 0:
                coverage = (len(regression_tests) / len(all_tests)) * 100
                st.progress(coverage / 100)
                st.caption(f"Regression Coverage: {coverage:.1f}% of total tests")
            
            st.divider()
            
            # Filter options
            st.subheader("📋 View Regression Tests")
            
            filter_option = st.radio(
                "Filter by priority:",
                ["All Regression", "High & Critical", "Critical Only"],
                horizontal=True
            )
            
            # Get filtered tests based on selection
            if filter_option == "All Regression":
                display_tests = regression_tests
            elif filter_option == "High & Critical":
                display_tests = high_critical_regression
            else:
                display_tests = critical_only
            
            st.info(f"Showing {len(display_tests)} test case(s)")
            
            # Display test cases
            if display_tests:
                for idx, tc in enumerate(display_tests, 1):
                    with st.expander(f"**{idx}. {tc.title}** - Priority: {tc.priority} | Type: {tc.test_type}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**ID:** `{tc.id}`")
                            st.markdown(f"**Description:** {tc.description}")
                        
                        with col2:
                            st.markdown(f"**Priority:** {tc.priority}")
                            st.markdown(f"**Type:** {tc.test_type}")
                            st.markdown(f"**Regression:** {'✅ Yes' if tc.is_regression else '❌ No'}")
                        
                        if tc.preconditions:
                            st.markdown("**Preconditions:**")
                            for precond in tc.preconditions:
                                st.markdown(f"- {precond}")
                        
                        st.markdown("**Test Steps:**")
                        for step in tc.test_steps:
                            st.markdown(f"{step.step_number}. **{step.action}**")
                            st.markdown(f"   ➜ *Expected:* {step.expected_result}")
                        
                        st.markdown(f"**Expected Outcome:** {tc.expected_outcome}")
                        
                        if tc.postconditions:
                            st.markdown("**Postconditions:**")
                            for postcond in tc.postconditions:
                                st.markdown(f"- {postcond}")
                        
                        if tc.tags:
                            st.markdown(f"**Tags:** {', '.join(tc.tags)}")
                        
                        if tc.boundary_conditions:
                            st.markdown("**Boundary Conditions:**")
                            for bc in tc.boundary_conditions:
                                st.markdown(f"- {bc}")
            else:
                st.warning("No regression test cases found. Generate test cases or import existing ones.")
                st.info("💡 Tip: High and Critical priority tests are automatically marked as regression tests when generated or imported.")
        
        except Exception as e:
            st.error(f"Error loading regression tests: {e}")

if __name__ == "__main__":
    main()
