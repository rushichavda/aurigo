"""
Case Orchestrator Service
Coordinates the complete EB-1A case processing workflow
"""
from typing import Dict, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime

from .folder_validator import FolderValidator
from .document_parser import DocumentParser
from .criteria_mapper import CriteriaMapper
from .information_extractor import InformationExtractor
from .exhibit_manager import ExhibitManager
from .letter_generator import LetterGenerator
from .document_exporter import DocumentExporter

from ..models import Case, Document, CaseExhibit, GeneratedLetter


class CaseOrchestrator:
    """
    Orchestrates the complete case processing workflow:
    1. Validate folder structure
    2. Parse all documents
    3. Map criteria
    4. Extract information
    5. Manage exhibits
    6. Generate letter
    7. Export to DOCX
    """

    def __init__(self, db: Session):
        self.db = db
        self.validator = FolderValidator()
        self.parser = DocumentParser()
        self.criteria_mapper = CriteriaMapper()
        self.extractor = InformationExtractor()
        self.exhibit_manager = ExhibitManager()
        self.letter_generator = LetterGenerator()
        self.exporter = DocumentExporter()

    async def process_case(
        self,
        case_id: int,
        folder_path: str,
        beneficiary_name: str
    ) -> Dict:
        """
        Process a complete EB-1A case

        Args:
            case_id: Database case ID
            folder_path: Path to uploaded case folder
            beneficiary_name: Name of the beneficiary

        Returns:
            Processing result dictionary
        """
        case = self.db.query(Case).filter(Case.id == case_id).first()
        if not case:
            return {"success": False, "error": "Case not found"}

        try:
            # Step 1: Validate structure
            await self._update_progress(case, "validating", 5)
            validation = await self.validator.validate_structure(folder_path)

            if not validation["valid"]:
                case.status = "failed"
                self.db.commit()
                return {
                    "success": False,
                    "error": "Folder validation failed",
                    "details": validation["errors"]
                }

            # Step 2: Map criteria from folder names (LLM-based with confidence scoring)
            await self._update_progress(case, "mapping_criteria", 10)
            evidence_path = Path(validation["evidence_path"])
            criteria_mapping_full = await self.criteria_mapper.map_folders(evidence_path)

            # Extract just the criterion names for backward compatibility
            criteria_mapping = {
                folder: info['criterion']
                for folder, info in criteria_mapping_full.items()
            }

            case.criteria_matched = list(set(criteria_mapping.values()))
            case.num_criteria = len(set(criteria_mapping.values()))
            self.db.commit()

            # Step 3: Parse all documents
            await self._update_progress(case, "parsing_documents", 20)
            evidence_path = validation["evidence_path"]
            parsed_docs = await self._parse_all_documents(case, evidence_path, criteria_mapping)

            # Step 4: Extract case overview
            await self._update_progress(case, "extracting_overview", 35)
            beneficiary_info = await self._extract_case_overview(
                case,
                validation["case_overview_path"],
                beneficiary_name
            )

            # Step 5: Extract information from documents
            await self._update_progress(case, "extracting_information", 45)
            criteria_data = await self._extract_all_information(case, criteria_mapping)

            # Step 6: Create exhibits
            await self._update_progress(case, "creating_exhibits", 60)
            await self._create_exhibits(case, beneficiary_info, criteria_data)

            # Step 7: Generate letter
            await self._update_progress(case, "generating_letter", 75)
            letter_content = await self.letter_generator.generate_complete_letter(
                beneficiary_info=beneficiary_info,
                field=case.field,
                criteria_data=criteria_data,
                exhibit_manager=self.exhibit_manager
            )

            # Save letter to database
            generated_letter = GeneratedLetter(
                case_id=case.id,
                content=letter_content,
                version=1,
                is_polished=self.letter_generator.use_claude
            )
            self.db.add(generated_letter)
            self.db.commit()

            # Step 8: Export to DOCX
            await self._update_progress(case, "exporting", 90)
            output_path = Path(case.workspace_path) / "output"
            output_path.mkdir(exist_ok=True)

            exported_files = self.exporter.create_case_package(
                letter_content=letter_content,
                exhibit_data=self.exhibit_manager.get_exhibit_index(),
                output_path=str(output_path),
                beneficiary_name=beneficiary_name,
                metadata=self.exhibit_manager.get_summary()
            )

            # Update case with output paths
            case.letter_path = exported_files.get("attorney_letter")
            case.exhibit_index_path = exported_files.get("exhibit_index")
            case.metadata_path = exported_files.get("metadata")

            # Mark as completed
            await self._update_progress(case, "completed", 100)
            case.status = "completed"
            case.completed_at = datetime.utcnow()
            self.db.commit()

            return {
                "success": True,
                "case_id": case.id,
                "criteria_matched": case.num_criteria,
                "total_documents": case.total_documents,
                "total_exhibits": case.total_exhibits,
                "output_files": exported_files
            }

        except Exception as e:
            case.status = "failed"
            case.current_step = f"error: {str(e)}"
            self.db.commit()

            return {
                "success": False,
                "error": str(e),
                "case_id": case.id
            }

    async def _parse_all_documents(
        self,
        case: Case,
        evidence_path: str,
        criteria_mapping: Dict[str, str]
    ) -> Dict:
        """Parse all documents in evidence folders"""

        all_parsed = {}

        for folder_name, criterion in criteria_mapping.items():
            folder_path = Path(evidence_path) / folder_name

            if not folder_path.exists():
                continue

            # Parse all files in this criterion folder
            parsed_docs = self.parser.extract_from_folder(str(folder_path), recursive=False)

            # Save to database
            for doc in parsed_docs:
                if doc["success"]:
                    document = Document(
                        case_id=case.id,
                        file_name=doc["metadata"]["filename"],
                        file_path=doc["file_path"],
                        file_type=doc["format"],
                        file_size=doc["metadata"].get("size_bytes", 0),
                        criterion=criterion,
                        parsed_text=doc["text"],
                        parsed_tables=doc["tables"],
                        parsed_metadata=doc["metadata"],
                        parsed=True
                    )
                    self.db.add(document)

            all_parsed[criterion] = parsed_docs

        case.total_documents = self.db.query(Document).filter(Document.case_id == case.id).count()
        self.db.commit()

        return all_parsed

    async def _extract_case_overview(
        self,
        case: Case,
        case_overview_path: Optional[str],
        beneficiary_name: str
    ) -> Dict:
        """Extract beneficiary information from case overview"""

        if case_overview_path:
            overview_result = await self.extractor.extract_case_overview(case_overview_path)

            if overview_result["success"]:
                beneficiary_info = overview_result["beneficiary_info"]
            else:
                beneficiary_info = {"name": beneficiary_name}
        else:
            beneficiary_info = {"name": beneficiary_name}

        # Ensure required fields
        if "name" not in beneficiary_info:
            beneficiary_info["name"] = beneficiary_name

        # Try to infer field from case
        if "field" in beneficiary_info and case.field is None:
            case.field = beneficiary_info["field"]
            self.db.commit()

        return beneficiary_info

    async def _extract_all_information(
        self,
        case: Case,
        criteria_mapping: Dict[str, str]
    ) -> Dict[str, Dict]:
        """Extract structured information from all documents"""

        criteria_data = {}

        # Get documents by criterion
        for folder_name, criterion in criteria_mapping.items():
            # Get documents for this criterion
            documents = self.db.query(Document).filter(
                Document.case_id == case.id,
                Document.criterion == criterion
            ).all()

            if not documents:
                continue

            extracted_docs = []

            for doc in documents:
                # Extract information
                extracted = await self.extractor.extract_from_document(
                    file_path=doc.file_path,
                    criterion=criterion,
                    document_hint=doc.file_name
                )

                if extracted["success"]:
                    # Update document with extracted info
                    doc.extracted_info = extracted["extracted_info"]
                    doc.key_facts = extracted.get("key_facts", [])
                    doc.entities = extracted.get("entities", {})
                    doc.summary = extracted.get("summary", "")
                    doc.document_type = extracted.get("document_type", "unknown")
                    doc.extracted = True

                    extracted_docs.append(extracted)

            self.db.commit()

            # Aggregate criterion data
            if extracted_docs:
                aggregated = await self.extractor.aggregate_criterion_data(extracted_docs)
                criteria_data[criterion] = aggregated

        return criteria_data

    async def _create_exhibits(
        self,
        case: Case,
        beneficiary_info: Dict,
        criteria_data: Dict[str, Dict]
    ):
        """Create exhibit assignments"""

        # Create background exhibits
        background_exhibits = self.exhibit_manager.create_background_exhibits(
            case_overview_path=case.case_overview_path
        )

        # Create field exhibits
        field_exhibits = self.exhibit_manager.create_field_exhibits(
            field_name=case.field or "the field",
            statement_of_intent_path=None
        )

        # Create criterion exhibits
        for criterion, data in criteria_data.items():
            # Get documents for this criterion
            documents = self.db.query(Document).filter(
                Document.case_id == case.id,
                Document.criterion == criterion
            ).all()

            doc_list = [{"file_path": doc.file_path} for doc in documents]
            extracted_list = [{"document_type": doc.document_type, "summary": doc.summary, "entities": doc.entities} for doc in documents]

            criterion_exhibits = self.exhibit_manager.create_criterion_exhibits(
                criterion=criterion,
                documents=doc_list,
                extracted_info=extracted_list
            )

            # Update documents with exhibit IDs
            for doc, exhibit in zip(documents, criterion_exhibits):
                doc.exhibit_id = exhibit.exhibit_id

        self.db.commit()

        # Save exhibits to database
        for exhibit in self.exhibit_manager.exhibits:
            case_exhibit = CaseExhibit(
                case_id=case.id,
                exhibit_id=exhibit.exhibit_id,
                group_letter=exhibit.group_letter,
                group_title=exhibit.group_title,
                number=exhibit.number,
                title=exhibit.title,
                description=exhibit.description,
                criterion=exhibit.criterion
            )
            self.db.add(case_exhibit)

        case.total_exhibits = len(self.exhibit_manager.exhibits)
        self.db.commit()

    async def _update_progress(self, case: Case, step: str, progress: int):
        """Update case progress"""
        case.current_step = step
        case.progress = progress
        case.status = "processing"
        self.db.commit()

    def get_case_status(self, case_id: int) -> Optional[Dict]:
        """Get current status of a case"""
        case = self.db.query(Case).filter(Case.id == case_id).first()

        if not case:
            return None

        return {
            "case_id": case.id,
            "status": case.status,
            "current_step": case.current_step,
            "progress": case.progress,
            "criteria_matched": case.num_criteria,
            "total_documents": case.total_documents,
            "total_exhibits": case.total_exhibits
        }
