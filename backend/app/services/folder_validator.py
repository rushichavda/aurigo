"""
Folder Structure Validator for EB-1A Cases
"""
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import shutil
from ..llm.gemini import GeminiLLM


class FolderValidator:
    """
    Validates uploaded case folder structure using intelligent LLM-based detection

    Expected structure:
        Case_Folder/
        ├── Case_Overview.docx (or similar - flexibly detected)
        └── Evidence/ (or similar - flexibly detected)
            ├── [Criterion folders]
            └── ...
    """

    # Exact match patterns for Evidence folder (tried first)
    EVIDENCE_FOLDER_EXACT_MATCHES = ['evidence', 'evidences', 'documents', 'proofs']

    # Confidence threshold for LLM-based detection
    LLM_CONFIDENCE_THRESHOLD = 0.6

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.llm = GeminiLLM()

    async def validate_structure(self, folder_path: str) -> Dict:
        """
        Validate the case folder structure using intelligent LLM-based detection

        Args:
            folder_path: Path to the uploaded case folder

        Returns:
            Dictionary with:
                - valid: bool
                - errors: List[str]
                - warnings: List[str]
                - case_overview_path: Optional[str]
                - evidence_path: Optional[str]
                - evidence_folders: List[str]
                - total_files: int
        """
        self.errors = []
        self.warnings = []

        path = Path(folder_path)

        if not path.exists():
            self.errors.append(f"Folder does not exist: {folder_path}")
            return self._build_response(False, None, None, [])

        if not path.is_dir():
            self.errors.append(f"Path is not a directory: {folder_path}")
            return self._build_response(False, None, None, [])

        # Find case overview document (LLM-based)
        case_overview_path = await self._find_case_overview(path)

        # Find evidence folder (exact match first, then LLM)
        evidence_path = await self._find_evidence_folder(path)

        if not evidence_path:
            self.errors.append(
                "Evidence folder not found. Please ensure your case has a folder containing organized evidence documents."
            )
            return self._build_response(False, case_overview_path, None, [])

        # Get evidence subfolders (criteria folders)
        evidence_folders = self._get_evidence_folders(evidence_path)

        if not evidence_folders:
            self.errors.append("No criterion folders found in Evidence directory")

        # Count total files
        total_files = len(list(evidence_path.rglob('*.*')))

        # Add warnings
        if not case_overview_path:
            self.warnings.append(
                "Case overview document not found. Letter generation will require manual input."
            )

        if total_files == 0:
            self.warnings.append("Evidence folder is empty")

        # Validation passes if evidence folder exists
        valid = len(self.errors) == 0

        return self._build_response(
            valid, case_overview_path, evidence_path, evidence_folders, total_files
        )

    async def _find_case_overview(self, folder_path: Path) -> Optional[str]:
        """Find case overview document in the folder using LLM intelligence"""
        # Get all files in root directory
        files = [f.name for f in folder_path.iterdir() if f.is_file()]

        if not files:
            return None

        # Use LLM to identify case overview
        try:
            result = await self.llm.identify_case_overview(files)

            if result.get('case_overview_file') and result.get('confidence', 0) >= self.LLM_CONFIDENCE_THRESHOLD:
                overview_path = folder_path / result['case_overview_file']
                if overview_path.exists():
                    # Log the reasoning for debugging
                    print(f"[Case Overview Detection] Found: {result['case_overview_file']} (confidence: {result['confidence']:.2f})")
                    print(f"[Reasoning] {result.get('reasoning', 'N/A')}")
                    return str(overview_path)

            # Low confidence warning
            if result.get('case_overview_file'):
                self.warnings.append(
                    f"Case overview detection has low confidence ({result.get('confidence', 0):.2f}). "
                    f"Detected: {result['case_overview_file']}"
                )

        except Exception as e:
            print(f"[LLM Error] Case overview detection failed: {str(e)}")
            self.warnings.append("Could not automatically detect case overview document.")

        return None

    async def _find_evidence_folder(self, folder_path: Path) -> Optional[Path]:
        """Find the Evidence folder using exact match first, then LLM intelligence"""
        folders = [item for item in folder_path.iterdir() if item.is_dir()]

        if not folders:
            return None

        # STEP 1: Try exact matching first (fast path)
        for folder in folders:
            if folder.name.lower() in self.EVIDENCE_FOLDER_EXACT_MATCHES:
                print(f"[Evidence Detection] Exact match found: {folder.name}")
                return folder

        # STEP 2: Use LLM for flexible detection
        folder_names = [f.name for f in folders]
        try:
            result = await self.llm.identify_evidence_folder(folder_names)

            if result.get('evidence_folder') and result.get('confidence', 0) >= self.LLM_CONFIDENCE_THRESHOLD:
                evidence_path = folder_path / result['evidence_folder']
                if evidence_path.exists() and evidence_path.is_dir():
                    print(f"[Evidence Detection] LLM match found: {result['evidence_folder']} (confidence: {result['confidence']:.2f})")
                    print(f"[Reasoning] {result.get('reasoning', 'N/A')}")
                    return evidence_path

            # Low confidence warning
            if result.get('evidence_folder'):
                self.warnings.append(
                    f"Evidence folder detection has low confidence ({result.get('confidence', 0):.2f}). "
                    f"Detected: {result['evidence_folder']}"
                )

        except Exception as e:
            print(f"[LLM Error] Evidence folder detection failed: {str(e)}")

        return None

    def _get_evidence_folders(self, evidence_path: Path) -> List[str]:
        """Get list of criterion folders in Evidence directory"""
        folders = []

        for item in evidence_path.iterdir():
            if item.is_dir():
                # Count files in folder
                file_count = len([f for f in item.rglob('*') if f.is_file()])
                folders.append({
                    "name": item.name,
                    "path": str(item),
                    "file_count": file_count
                })

        # Sort by folder name
        folders.sort(key=lambda x: x["name"])

        return folders

    def _build_response(
        self,
        valid: bool,
        case_overview_path: Optional[str],
        evidence_path: Optional[Path],
        evidence_folders: List,
        total_files: int = 0
    ) -> Dict:
        """Build validation response dictionary"""
        return {
            "valid": valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "case_overview_path": case_overview_path,
            "evidence_path": str(evidence_path) if evidence_path else None,
            "evidence_folders": evidence_folders,
            "total_files": total_files,
            "has_case_overview": case_overview_path is not None,
            "has_evidence": evidence_path is not None,
            "num_criteria": len(evidence_folders)
        }

    def copy_to_workspace(
        self,
        source_folder: str,
        destination_folder: str,
        case_id: str
    ) -> Tuple[bool, str]:
        """
        Copy case folder to processing workspace

        Args:
            source_folder: Original uploaded folder
            destination_folder: Base workspace directory
            case_id: Unique case identifier

        Returns:
            Tuple of (success: bool, case_path: str)
        """
        try:
            dest_path = Path(destination_folder) / case_id
            dest_path.mkdir(parents=True, exist_ok=True)

            # Copy entire folder
            shutil.copytree(
                source_folder,
                dest_path / "uploaded",
                dirs_exist_ok=True
            )

            return True, str(dest_path)

        except Exception as e:
            return False, f"Error copying folder: {str(e)}"

    def get_folder_summary(self, folder_path: str) -> Dict:
        """
        Get a summary of the folder contents

        Args:
            folder_path: Path to case folder

        Returns:
            Summary dictionary with file counts by type
        """
        path = Path(folder_path)

        if not path.exists():
            return {"error": "Folder not found"}

        file_types = {}
        total_size = 0

        for file in path.rglob('*'):
            if file.is_file():
                ext = file.suffix.lower()
                size = file.stat().st_size

                if ext not in file_types:
                    file_types[ext] = {"count": 0, "total_size": 0}

                file_types[ext]["count"] += 1
                file_types[ext]["total_size"] += size
                total_size += size

        return {
            "total_files": sum(ft["count"] for ft in file_types.values()),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types
        }
