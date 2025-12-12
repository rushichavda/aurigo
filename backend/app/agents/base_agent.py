"""
Base Agent Class
Foundation for all EB-1A criterion agents
"""
from typing import Dict, List, Optional, Any
from pathlib import Path
from abc import ABC, abstractmethod
import logging
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

from ..services.document_parser import DocumentParser

logger = logging.getLogger(__name__)


class AgentState:
    """Agent state management"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.status = "idle"  # idle | active | completed | failed
        self.progress = 0  # 0-100
        self.current_task = ""
        self.outputs = {}
        self.errors = []
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def start(self, task: str):
        """Mark agent as active"""
        self.status = "active"
        self.current_task = task
        self.started_at = datetime.utcnow()
        logger.info(f"[{self.agent_id}] Started: {task}")

    def update_progress(self, progress: int, task: str = None):
        """Update progress"""
        self.progress = min(100, max(0, progress))
        if task:
            self.current_task = task
        logger.info(f"[{self.agent_id}] Progress: {self.progress}% - {self.current_task}")

    def complete(self, outputs: Dict):
        """Mark agent as completed"""
        self.status = "completed"
        self.progress = 100
        self.outputs = outputs
        self.completed_at = datetime.utcnow()
        logger.info(f"[{self.agent_id}] Completed")

    def fail(self, error: str):
        """Mark agent as failed"""
        self.status = "failed"
        self.errors.append(error)
        logger.error(f"[{self.agent_id}] Failed: {error}")

    def to_dict(self) -> Dict:
        """Convert state to dictionary"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "progress": self.progress,
            "current_task": self.current_task,
            "outputs": self.outputs,
            "errors": self.errors,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class BaseAgent(ABC):
    """
    Base class for all EB-1A criterion agents

    Each agent is responsible for:
    1. Parsing documents in its criterion folder using Docling
    2. Analyzing evidence and extracting key facts
    3. Coordinating with ExhibitManagerAgent for exhibit IDs
    4. Generating its section of the attorney letter
    """

    def __init__(
        self,
        agent_id: str,
        criterion: str,
        llm_provider: str = "gemini",
        api_key: str = None,
        model_name: str = None
    ):
        """
        Initialize base agent

        Args:
            agent_id: Unique identifier for this agent
            criterion: EB-1A criterion name
            llm_provider: "gemini" or "claude"
            api_key: API key for LLM provider
            model_name: Specific model to use
        """
        self.agent_id = agent_id
        self.criterion = criterion
        self.state = AgentState(agent_id)

        # Initialize document parser (Docling)
        self.parser = DocumentParser()

        # Initialize LLM
        self.llm = self._initialize_llm(llm_provider, api_key, model_name)

        # Storage
        self.documents = []
        self.parsed_documents = []
        self.extracted_facts = []
        self.exhibits = []
        self.letter_section = ""
        self.confidence_score = 0.0

    def _initialize_llm(
        self,
        provider: str,
        api_key: str = None,
        model_name: str = None
    ) -> BaseChatModel:
        """Initialize LangChain LLM"""
        if provider == "gemini":
            model = model_name or "gemini-2.0-flash-exp"
            return ChatGoogleGenerativeAI(
                model=model,
                google_api_key=api_key,
                temperature=0.1
            )
        elif provider == "claude":
            model = model_name or "claude-sonnet-4-20250514"
            return ChatAnthropic(
                model=model,
                anthropic_api_key=api_key,
                temperature=0.1
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    async def process_folder(
        self,
        folder_path: str,
        exhibit_manager: Any
    ) -> Dict:
        """
        Main entry point: process all documents in criterion folder

        Args:
            folder_path: Path to criterion folder
            exhibit_manager: ExhibitManagerAgent instance

        Returns:
            Processing result with exhibits, letter section, and confidence
        """
        try:
            self.state.start(f"Processing {self.criterion}")

            # Step 1: Parse documents
            self.state.update_progress(10, "Parsing documents with Docling")
            await self._parse_documents(folder_path)

            # Step 2: Analyze documents
            self.state.update_progress(30, "Analyzing evidence")
            await self._analyze_documents()

            # Step 3: Extract key facts
            self.state.update_progress(50, "Extracting key facts")
            await self._extract_facts()

            # Step 4: Create exhibits
            self.state.update_progress(70, "Creating exhibits")
            await self._create_exhibits(exhibit_manager)

            # Step 5: Generate letter section
            self.state.update_progress(85, "Generating letter section")
            await self._generate_letter_section()

            # Step 6: Calculate confidence
            self.state.update_progress(95, "Calculating confidence score")
            self.confidence_score = await self._calculate_confidence()

            # Complete
            result = {
                "criterion": self.criterion,
                "documents_processed": len(self.documents),
                "exhibits": [e.to_dict() for e in self.exhibits],
                "letter_section": self.letter_section,
                "key_facts": self.extracted_facts,
                "confidence_score": self.confidence_score
            }

            self.state.complete(result)
            return result

        except Exception as e:
            self.state.fail(str(e))
            logger.error(f"[{self.agent_id}] Error processing folder: {e}")
            raise

    async def _parse_documents(self, folder_path: str):
        """Parse all documents in folder using Docling"""
        folder = Path(folder_path)

        if not folder.exists():
            raise ValueError(f"Folder not found: {folder_path}")

        # Get all supported files
        supported_extensions = [
            '.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png',
            '.tiff', '.tif', '.ppt', '.pptx', '.html', '.htm', '.md'
        ]

        files = [
            f for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in supported_extensions
        ]

        logger.info(f"[{self.agent_id}] Found {len(files)} documents to parse")

        # Parse each document
        for i, file_path in enumerate(files):
            try:
                logger.info(f"[{self.agent_id}] Parsing {file_path.name}")

                parsed = self.parser.extract_from_document(str(file_path))

                if parsed["success"]:
                    self.documents.append({
                        "file_path": str(file_path),
                        "file_name": file_path.name,
                        "format": parsed["format"],
                        "text": parsed["text"],
                        "tables": parsed["tables"],
                        "metadata": parsed["metadata"]
                    })
                    self.parsed_documents.append(parsed)
                else:
                    logger.warning(f"[{self.agent_id}] Failed to parse {file_path.name}")

                # Update progress within parsing step
                progress = 10 + int((i + 1) / len(files) * 20)
                self.state.update_progress(progress, f"Parsing documents ({i+1}/{len(files)})")

            except Exception as e:
                logger.error(f"[{self.agent_id}] Error parsing {file_path.name}: {e}")

        logger.info(f"[{self.agent_id}] Successfully parsed {len(self.documents)} documents")

    @abstractmethod
    async def _analyze_documents(self):
        """
        Analyze parsed documents to extract criterion-specific information
        Must be implemented by each criterion agent
        """
        pass

    @abstractmethod
    async def _extract_facts(self):
        """
        Extract key facts relevant to this criterion
        Must be implemented by each criterion agent
        """
        pass

    async def _create_exhibits(self, exhibit_manager: Any):
        """
        Create exhibits through ExhibitManagerAgent

        Args:
            exhibit_manager: ExhibitManagerAgent instance
        """
        for i, doc in enumerate(self.documents):
            # Request exhibit ID from manager
            exhibit = await exhibit_manager.create_exhibit(
                criterion=self.criterion,
                file_path=doc["file_path"],
                title=self._generate_exhibit_title(doc),
                description=self._generate_exhibit_description(doc),
                key_points=self._extract_document_key_points(doc)
            )

            self.exhibits.append(exhibit)

            # Update progress
            progress = 70 + int((i + 1) / len(self.documents) * 15)
            self.state.update_progress(progress, f"Creating exhibits ({i+1}/{len(self.documents)})")

    @abstractmethod
    def _generate_exhibit_title(self, document: Dict) -> str:
        """Generate descriptive title for exhibit"""
        pass

    @abstractmethod
    def _generate_exhibit_description(self, document: Dict) -> str:
        """Generate detailed description for exhibit"""
        pass

    @abstractmethod
    def _extract_document_key_points(self, document: Dict) -> List[str]:
        """Extract key points from document"""
        pass

    @abstractmethod
    async def _generate_letter_section(self):
        """
        Generate attorney letter section for this criterion
        Must be implemented by each criterion agent
        """
        pass

    async def _calculate_confidence(self) -> float:
        """
        Calculate confidence score for evidence quality

        Returns:
            Float between 0.0 and 1.0
        """
        # Base calculation - can be overridden by specific agents
        if not self.documents:
            return 0.0

        # Factors:
        # - Number of documents (more is better)
        # - Document quality (extracted text length)
        # - Key facts extracted

        doc_score = min(len(self.documents) / 10, 1.0) * 0.4
        content_score = min(sum(len(d.get("text", "")) for d in self.documents) / 10000, 1.0) * 0.3
        facts_score = min(len(self.extracted_facts) / 5, 1.0) * 0.3

        return doc_score + content_score + facts_score

    def get_state(self) -> Dict:
        """Get current agent state"""
        return self.state.to_dict()

    async def invoke_llm(self, prompt: str, system_prompt: str = None) -> str:
        """
        Invoke LLM with prompt

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            LLM response text
        """
        messages = []

        if system_prompt:
            messages.append(HumanMessage(content=f"System: {system_prompt}"))

        messages.append(HumanMessage(content=prompt))

        response = await self.llm.ainvoke(messages)
        return response.content
