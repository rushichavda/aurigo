"""
Streamlit UI for EB-1A Agent System
Testing interface for agent-based letter generation
"""
import streamlit as st
import asyncio
import sys
from pathlib import Path
from typing import List, Dict
import json
import os

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.strict_folder_validator import StrictFolderValidator, REQUIRED_CRITERION_FOLDERS, FOLDER_TO_CRITERION
from app.services.agent_orchestrator import AgentOrchestrator


# Page config
st.set_page_config(
    page_title="EB-1A Agent System",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.agent-card {
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #ddd;
    margin: 0.5rem 0;
}
.agent-active {
    background-color: #e3f2fd;
    border-color: #2196f3;
}
.agent-completed {
    background-color: #e8f5e9;
    border-color: #4caf50;
}
.agent-failed {
    background-color: #ffebee;
    border-color: #f44336;
}
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if "validator" not in st.session_state:
        st.session_state.validator = StrictFolderValidator()

    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = None

    if "validated" not in st.session_state:
        st.session_state.validated = False

    if "validation_result" not in st.session_state:
        st.session_state.validation_result = None

    if "processing" not in st.session_state:
        st.session_state.processing = False

    if "processing_result" not in st.session_state:
        st.session_state.processing_result = None

    if "selected_folders" not in st.session_state:
        st.session_state.selected_folders = []


def validate_folder_structure(case_path: str):
    """Validate folder structure"""
    with st.spinner("Validating folder structure..."):
        result = st.session_state.validator.validate_structure(case_path)
        st.session_state.validation_result = result
        st.session_state.validated = result["valid"]
        return result


def render_sidebar():
    """Render sidebar with configuration"""
    st.sidebar.title("⚙️ Configuration")

    # LLM Provider
    st.sidebar.subheader("LLM Settings")
    llm_provider = st.sidebar.selectbox(
        "LLM Provider",
        ["gemini", "claude"],
        help="Primary LLM for document analysis"
    )

    # API Key
    api_key = st.sidebar.text_input(
        f"{llm_provider.capitalize()} API Key",
        type="password",
        help=f"Enter your {llm_provider.capitalize()} API key"
    )

    # Store in session state
    st.session_state.llm_provider = llm_provider
    st.session_state.api_key = api_key

    # About
    st.sidebar.markdown("---")
    st.sidebar.subheader("About")
    st.sidebar.info(
        "**EB-1A Agent System v1.0**\n\n"
        "Specialized AI agents for processing EB-1A visa petition evidence.\n\n"
        "Built with LangChain, LangGraph, and Streamlit."
    )


def render_folder_selection():
    """Render folder structure validation and selection"""
    st.header("📁 Folder Selection")

    # Case folder path input
    col1, col2 = st.columns([3, 1])

    with col1:
        case_path = st.text_input(
            "Case Folder Path",
            placeholder="C:/path/to/case/folder",
            help="Path to the root case folder (containing Evidence subfolder)"
        )

    with col2:
        st.write("")
        st.write("")
        validate_btn = st.button("Validate", type="primary", use_container_width=True)

    # Validate on button click
    if validate_btn and case_path:
        result = validate_folder_structure(case_path)

        if result["valid"]:
            st.success("✅ Folder structure is valid!")
        else:
            st.error("❌ Folder structure validation failed")

    # Display validation results
    if st.session_state.validation_result:
        result = st.session_state.validation_result

        # Display errors
        if result["errors"]:
            st.error("**Errors:**")
            for error in result["errors"]:
                st.markdown(f"- {error}")

        # Display warnings
        if result["warnings"]:
            st.warning("**Warnings:**")
            for warning in result["warnings"]:
                st.markdown(f"- {warning}")

        # Display found folders
        if result["folders_found"]:
            st.success(f"**Found {len(result['folders_found'])} criterion folders:**")

            # Create folder selection checkboxes
            st.subheader("Select Folders to Process")

            selected_folders = []

            # Create columns for better layout
            cols = st.columns(3)

            for i, (folder_name, folder_info) in enumerate(result["folders_found"].items()):
                with cols[i % 3]:
                    criterion = folder_info["criterion"]
                    file_count = folder_info["file_count"]

                    # Checkbox for folder selection
                    selected = st.checkbox(
                        f"**{folder_name}**\n{criterion}\n({file_count} files)",
                        key=f"folder_{folder_name}",
                        value=folder_name in ["1_Critical_role", "2_Original_contribution"]  # Default selection
                    )

                    if selected:
                        selected_folders.append(folder_name)

            st.session_state.selected_folders = selected_folders

            # Display selection summary
            if selected_folders:
                st.info(f"✓ Selected {len(selected_folders)} folders for processing")
            else:
                st.warning("⚠️ Please select at least one folder to process")


async def process_case_async(
    evidence_path: str,
    selected_folders: List[str],
    beneficiary_name: str,
    field: str,
    llm_provider: str,
    api_key: str
):
    """Process case asynchronously"""
    # Create orchestrator
    orchestrator = AgentOrchestrator(
        llm_provider=llm_provider,
        api_key=api_key
    )

    # Process case
    result = await orchestrator.process_case(
        case_id=1,  # Dummy case ID for testing
        evidence_path=evidence_path,
        selected_folders=selected_folders,
        beneficiary_name=beneficiary_name,
        field=field
    )

    return result


def render_processing_section():
    """Render processing section"""
    if not st.session_state.validated:
        st.info("👆 Please validate a case folder first")
        return

    if not st.session_state.selected_folders:
        st.warning("⚠️ Please select at least one folder to process")
        return

    st.header("🚀 Processing")

    # Beneficiary information
    col1, col2 = st.columns(2)

    with col1:
        beneficiary_name = st.text_input(
            "Beneficiary Name",
            placeholder="John Doe",
            help="Full name of the beneficiary"
        )

    with col2:
        field = st.text_input(
            "Field of Expertise",
            placeholder="Artificial Intelligence",
            help="Beneficiary's field of expertise"
        )

    # Start processing button
    if st.button("Start Processing", type="primary", disabled=st.session_state.processing):
        if not beneficiary_name or not field:
            st.error("Please provide beneficiary name and field")
            return

        if not st.session_state.api_key:
            st.error("Please provide API key in the sidebar")
            return

        # Start processing
        st.session_state.processing = True

        with st.spinner("Processing case with AI agents..."):
            result = asyncio.run(
                process_case_async(
                    evidence_path=st.session_state.validation_result["evidence_path"],
                    selected_folders=st.session_state.selected_folders,
                    beneficiary_name=beneficiary_name,
                    field=field,
                    llm_provider=st.session_state.llm_provider,
                    api_key=st.session_state.api_key
                )
            )

            st.session_state.processing_result = result
            st.session_state.processing = False

        # Show results
        if result["success"]:
            st.success("✅ Processing completed successfully!")
        else:
            st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")


def render_results():
    """Render processing results"""
    if not st.session_state.processing_result:
        return

    result = st.session_state.processing_result

    if not result["success"]:
        st.error(f"Processing failed: {result.get('error', 'Unknown error')}")
        return

    st.header("📊 Results")

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Criteria Processed",
            len(result["agent_results"])
        )

    with col2:
        st.metric(
            "Total Exhibits",
            result["total_exhibits"]
        )

    with col3:
        errors = result.get("errors", [])
        st.metric(
            "Errors",
            len(errors),
            delta="0" if not errors else f"-{len(errors)}"
        )

    # Agent results
    st.subheader("Agent Results")

    for folder_name, agent_result in result["agent_results"].items():
        with st.expander(f"📁 {folder_name} - {agent_result['criterion']}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Documents Processed:**", agent_result["documents_processed"])
                st.write("**Exhibits Created:**", len(agent_result["exhibits"]))

            with col2:
                confidence = agent_result.get("confidence_score", 0)
                st.write("**Confidence Score:**")
                st.progress(confidence)
                st.write(f"{confidence:.1%}")

            # Key facts
            if agent_result.get("key_facts"):
                st.write("**Key Facts:**")
                for fact in agent_result["key_facts"][:5]:
                    st.markdown(f"- {fact}")

    # Generated letter
    st.subheader("Generated Letter")

    letter = result.get("complete_letter", "")

    if letter:
        # Preview
        with st.expander("📄 Letter Preview", expanded=True):
            st.markdown(letter)

        # Download button
        st.download_button(
            label="Download Letter (Markdown)",
            data=letter,
            file_name="attorney_letter.md",
            mime="text/markdown"
        )

    # Exhibit index
    st.subheader("Exhibit Index")

    exhibit_index = result.get("exhibit_index", [])

    if exhibit_index:
        # Convert to table
        exhibit_data = []
        for exhibit in exhibit_index:
            exhibit_data.append({
                "Exhibit ID": exhibit["exhibit_id"],
                "Title": exhibit["title"],
                "Criterion": exhibit["criterion"]
            })

        st.dataframe(exhibit_data, use_container_width=True)

        # Download exhibit index
        st.download_button(
            label="Download Exhibit Index (JSON)",
            data=json.dumps(exhibit_index, indent=2),
            file_name="exhibit_index.json",
            mime="application/json"
        )


def main():
    """Main application"""
    # Initialize session state
    init_session_state()

    # Render sidebar
    render_sidebar()

    # Main content
    st.title("⚖️ EB-1A Agent System")
    st.markdown("**AI-Powered Attorney Letter Generation with Specialized Agents**")

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📁 Folder Selection", "🚀 Processing", "📊 Results"])

    with tab1:
        render_folder_selection()

    with tab2:
        render_processing_section()

    with tab3:
        render_results()


if __name__ == "__main__":
    main()
