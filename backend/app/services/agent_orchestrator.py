"""
Agent Orchestrator Service
Coordinates all EB-1A agents using LangGraph workflow
"""
from typing import Dict, List, Optional, Any
from pathlib import Path
import asyncio
import logging
from datetime import datetime

from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from ..agents.exhibit_manager_agent import ExhibitManagerAgent
from ..agents.criterion_agents.critical_role_agent import CriticalRoleAgent
from ..agents.criterion_agents.original_contribution_agent import OriginalContributionAgent

logger = logging.getLogger(__name__)


class WorkflowState(TypedDict):
    """State for LangGraph workflow"""
    case_id: int
    evidence_path: str
    selected_folders: List[str]
    beneficiary_name: str
    field: Optional[str]

    # Agent states
    exhibit_manager: Any
    criterion_agents: Dict[str, Any]

    # Results
    agent_results: Dict[str, Dict]
    all_exhibits: List[Dict]
    letter_sections: Dict[str, str]

    # Progress tracking
    overall_progress: int
    current_step: str
    errors: List[str]

    # Final outputs
    complete_letter: Optional[str]
    exhibit_index: Optional[List[Dict]]


class AgentOrchestrator:
    """
    Orchestrates all EB-1A agents using LangGraph

    Workflow:
    1. Initialize exhibit manager and criterion agents
    2. Process selected folders in parallel
    3. Compile results
    4. Generate complete letter
    """

    # Mapping of folder names to agent classes
    FOLDER_TO_AGENT = {
        "1_Critical_role": CriticalRoleAgent,
        "2_Original_contribution": OriginalContributionAgent,
        # Add more agents as they are implemented
        # "3_High_salary": HighSalaryAgent,
        # "4_Judging": JudgingAgent,
        # etc.
    }

    # Mapping of folder names to criteria
    FOLDER_TO_CRITERION = {
        "1_Critical_role": "Leading or Critical Role",
        "2_Original_contribution": "Original Contributions of Major Significance",
        "3_High_salary": "High Salary or Remuneration",
        "4_Judging": "Judging the Work of Others",
        "5_Membership": "Membership in Associations",
        "6_Awards": "Awards and Prizes",
        "7_Authorship": "Scholarly Authorship",
        "8_Press": "Published Material About You",
        "9_Final_merits": "Final Merits Determination",
        "10_Performing_Arts": "Commercial Success in Performing Arts",
        "Personal": "Background Information"
    }

    def __init__(
        self,
        llm_provider: str = "gemini",
        api_key: str = None
    ):
        """
        Initialize orchestrator

        Args:
            llm_provider: "gemini" or "claude"
            api_key: API key for LLM provider
        """
        self.llm_provider = llm_provider
        self.api_key = api_key

        # Create LangGraph workflow
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile()

    def _create_workflow(self) -> StateGraph:
        """Create LangGraph workflow"""
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("initialize", self._initialize_agents)
        workflow.add_node("process_folders", self._process_folders)
        workflow.add_node("compile_results", self._compile_results)
        workflow.add_node("generate_letter", self._generate_complete_letter)

        # Add edges
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "process_folders")
        workflow.add_edge("process_folders", "compile_results")
        workflow.add_edge("compile_results", "generate_letter")
        workflow.add_edge("generate_letter", END)

        return workflow

    async def process_case(
        self,
        case_id: int,
        evidence_path: str,
        selected_folders: List[str],
        beneficiary_name: str,
        field: Optional[str] = None
    ) -> Dict:
        """
        Process a case with selected folders

        Args:
            case_id: Database case ID
            evidence_path: Path to Evidence folder
            selected_folders: List of folder names to process
            beneficiary_name: Beneficiary name
            field: Field of expertise (optional)

        Returns:
            Processing results
        """
        logger.info(f"[Orchestrator] Starting case processing: {case_id}")
        logger.info(f"[Orchestrator] Selected folders: {selected_folders}")

        # Initialize state
        initial_state: WorkflowState = {
            "case_id": case_id,
            "evidence_path": evidence_path,
            "selected_folders": selected_folders,
            "beneficiary_name": beneficiary_name,
            "field": field,
            "exhibit_manager": None,
            "criterion_agents": {},
            "agent_results": {},
            "all_exhibits": [],
            "letter_sections": {},
            "overall_progress": 0,
            "current_step": "initializing",
            "errors": [],
            "complete_letter": None,
            "exhibit_index": None
        }

        try:
            # Run workflow
            final_state = await self.app.ainvoke(initial_state)

            logger.info(f"[Orchestrator] Case processing completed")

            return {
                "success": True,
                "case_id": case_id,
                "agent_results": final_state["agent_results"],
                "complete_letter": final_state["complete_letter"],
                "exhibit_index": final_state["exhibit_index"],
                "total_exhibits": len(final_state["all_exhibits"]),
                "errors": final_state["errors"]
            }

        except Exception as e:
            logger.error(f"[Orchestrator] Error processing case: {e}")
            return {
                "success": False,
                "error": str(e),
                "case_id": case_id
            }

    async def _initialize_agents(self, state: WorkflowState) -> WorkflowState:
        """Initialize exhibit manager and criterion agents"""
        logger.info("[Orchestrator] Initializing agents")

        # Create exhibit manager
        state["exhibit_manager"] = ExhibitManagerAgent()

        # Create criterion agents for selected folders
        criterion_agents = {}
        for folder_name in state["selected_folders"]:
            agent_class = self.FOLDER_TO_AGENT.get(folder_name)

            if agent_class:
                # Create agent instance
                agent = agent_class(
                    llm_provider=self.llm_provider,
                    api_key=self.api_key
                )
                criterion_agents[folder_name] = agent
                logger.info(f"[Orchestrator] Created agent for {folder_name}")
            else:
                # Agent not yet implemented
                logger.warning(f"[Orchestrator] No agent implementation for {folder_name}")
                state["errors"].append(f"Agent not implemented for {folder_name}")

        state["criterion_agents"] = criterion_agents
        state["overall_progress"] = 10
        state["current_step"] = "agents_initialized"

        return state

    async def _process_folders(self, state: WorkflowState) -> WorkflowState:
        """Process all selected folders in parallel"""
        logger.info("[Orchestrator] Processing folders in parallel")

        state["current_step"] = "processing_folders"
        evidence_path = Path(state["evidence_path"])

        # Create tasks for parallel processing
        tasks = []
        for folder_name, agent in state["criterion_agents"].items():
            folder_path = evidence_path / folder_name

            if folder_path.exists():
                task = self._process_single_folder(
                    agent=agent,
                    folder_path=str(folder_path),
                    folder_name=folder_name,
                    exhibit_manager=state["exhibit_manager"]
                )
                tasks.append((folder_name, task))
            else:
                logger.warning(f"[Orchestrator] Folder not found: {folder_path}")
                state["errors"].append(f"Folder not found: {folder_name}")

        # Run all agents in parallel
        if tasks:
            results = await asyncio.gather(
                *[task for _, task in tasks],
                return_exceptions=True
            )

            # Collect results
            for (folder_name, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    logger.error(f"[Orchestrator] Error processing {folder_name}: {result}")
                    state["errors"].append(f"Error in {folder_name}: {str(result)}")
                else:
                    state["agent_results"][folder_name] = result
                    logger.info(f"[Orchestrator] Completed {folder_name}")

        state["overall_progress"] = 70
        state["current_step"] = "folders_processed"

        return state

    async def _process_single_folder(
        self,
        agent: Any,
        folder_path: str,
        folder_name: str,
        exhibit_manager: ExhibitManagerAgent
    ) -> Dict:
        """Process a single folder with its agent"""
        try:
            logger.info(f"[Orchestrator] Processing {folder_name}")
            result = await agent.process_folder(
                folder_path=folder_path,
                exhibit_manager=exhibit_manager
            )
            return result
        except Exception as e:
            logger.error(f"[Orchestrator] Error in {folder_name}: {e}")
            raise

    async def _compile_results(self, state: WorkflowState) -> WorkflowState:
        """Compile results from all agents"""
        logger.info("[Orchestrator] Compiling results")

        state["current_step"] = "compiling_results"

        # Collect all exhibits
        state["all_exhibits"] = state["exhibit_manager"].get_exhibit_index()

        # Collect letter sections
        letter_sections = {}
        for folder_name, result in state["agent_results"].items():
            criterion = self.FOLDER_TO_CRITERION.get(folder_name)
            if criterion and result.get("letter_section"):
                letter_sections[criterion] = result["letter_section"]

        state["letter_sections"] = letter_sections
        state["overall_progress"] = 85
        state["current_step"] = "results_compiled"

        return state

    async def _generate_complete_letter(self, state: WorkflowState) -> WorkflowState:
        """Generate complete attorney letter"""
        logger.info("[Orchestrator] Generating complete letter")

        state["current_step"] = "generating_letter"

        # Compile letter sections in order
        letter_parts = []

        # Header
        letter_parts.append(self._generate_letter_header(state))

        # Executive Summary
        letter_parts.append(self._generate_executive_summary(state))

        # Background Section (if available)
        letter_parts.append(self._generate_background_section(state))

        # Criterion Sections
        for criterion, section in state["letter_sections"].items():
            letter_parts.append(f"\n## {criterion}\n\n{section}\n")

        # Conclusion
        letter_parts.append(self._generate_conclusion(state))

        # Exhibit Index
        letter_parts.append(self._generate_exhibit_index_section(state))

        # Combine all parts
        state["complete_letter"] = "\n".join(letter_parts)
        state["exhibit_index"] = state["all_exhibits"]

        state["overall_progress"] = 100
        state["current_step"] = "completed"

        logger.info("[Orchestrator] Letter generation completed")

        return state

    def _generate_letter_header(self, state: WorkflowState) -> str:
        """Generate letter header"""
        return f"""# EB-1A Petition Support Letter

**Beneficiary**: {state['beneficiary_name']}
**Field**: {state.get('field', 'Not specified')}
**Date**: {datetime.utcnow().strftime('%B %d, %Y')}

---
"""

    def _generate_executive_summary(self, state: WorkflowState) -> str:
        """Generate executive summary"""
        num_criteria = len(state["letter_sections"])
        num_exhibits = len(state["all_exhibits"])

        return f"""## Executive Summary

This letter supports the EB-1A petition for {state['beneficiary_name']}, demonstrating extraordinary ability in {state.get('field', 'their field')}. The evidence submitted meets {num_criteria} criteria for extraordinary ability, supported by {num_exhibits} exhibits.

The beneficiary's exceptional achievements include:
"""

    def _generate_background_section(self, state: WorkflowState) -> str:
        """Generate background section"""
        return f"""## Background

{state['beneficiary_name']} is a distinguished professional in {state.get('field', 'their field')} with exceptional achievements that demonstrate extraordinary ability.
"""

    def _generate_conclusion(self, state: WorkflowState) -> str:
        """Generate conclusion"""
        return f"""## Conclusion

Based on the evidence presented, {state['beneficiary_name']} clearly meets the requirements for EB-1A classification. The submitted documentation demonstrates sustained national or international acclaim and recognition for achievements in {state.get('field', 'their field')}.

We respectfully request approval of this petition.

---
"""

    def _generate_exhibit_index_section(self, state: WorkflowState) -> str:
        """Generate exhibit index section"""
        exhibits_by_group = state["exhibit_manager"].get_exhibit_index_by_group()

        sections = ["\n## INDEX OF EXHIBITS\n"]

        for group_letter in sorted(exhibits_by_group.keys()):
            exhibits = exhibits_by_group[group_letter]
            if exhibits:
                group_title = exhibits[0]["group_title"]
                sections.append(f"\n### Group {group_letter}: {group_title}\n")

                for exhibit in exhibits:
                    sections.append(
                        f"- **Exhibit {exhibit['exhibit_id']}**: {exhibit['title']}\n"
                        f"  {exhibit['description']}\n"
                    )

        return "\n".join(sections)

    def get_agent_status(self, folder_name: str) -> Optional[Dict]:
        """Get status of a specific agent"""
        # This would be implemented to track real-time agent status
        pass
