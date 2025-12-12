"""
Strict Folder Structure Validator
Validates case folders against hardcoded EB-1A criterion folder names
"""
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


# Hardcoded required folder names (exact match required)
REQUIRED_CRITERION_FOLDERS = [
    "1_Critical_role",
    "2_Original_contribution",
    "3_High_salary",
    "4_Judging",
    "5_Membership",
    "6_Awards",
    "7_Authorship",
    "8_Press",
    "9_Final_merits",
    "10_Performing_Arts",
    "Personal"
]

# Mapping folder names to official EB-1A criteria
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

# Supported file formats
SUPPORTED_FORMATS = [
    '.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png',
    '.tiff', '.tif', '.ppt', '.pptx', '.html', '.htm', '.md'
]


class StrictFolderValidator:
    """Validates case folder structure against strict requirements"""

    def __init__(self):
        self.required_folders = REQUIRED_CRITERION_FOLDERS
        self.folder_to_criterion = FOLDER_TO_CRITERION
        self.supported_formats = SUPPORTED_FORMATS

    def validate_structure(self, case_folder_path: str) -> Dict:
        """
        Validate folder structure with strict requirements

        Args:
            case_folder_path: Path to the case folder

        Returns:
            Validation result dictionary with:
            - valid: bool
            - errors: List[str]
            - warnings: List[str]
            - evidence_path: str
            - case_overview_path: Optional[str]
            - folders_found: Dict[str, Dict]
        """
        case_path = Path(case_folder_path)

        errors = []
        warnings = []
        folders_found = {}
        evidence_path = None
        case_overview_path = None

        # Check if case folder exists
        if not case_path.exists():
            errors.append(f"Case folder not found: {case_folder_path}")
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "evidence_path": None,
                "case_overview_path": None,
                "folders_found": {}
            }

        # Look for Evidence folder
        evidence_folder = case_path / "Evidence"
        if not evidence_folder.exists():
            errors.append("'Evidence' folder not found in case folder")
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "evidence_path": None,
                "case_overview_path": None,
                "folders_found": {}
            }

        evidence_path = str(evidence_folder)

        # Look for Case_Overview file
        for overview_file in ["Case_Overview.docx", "Case_Overview.pdf", "Case_Overview.doc"]:
            overview_path = case_path / overview_file
            if overview_path.exists():
                case_overview_path = str(overview_path)
                break

        if not case_overview_path:
            warnings.append("Case_Overview file not found (optional)")

        # Validate Evidence subfolder structure
        available_folders = [f.name for f in evidence_folder.iterdir() if f.is_dir()]

        # Check for exact folder name matches
        for folder_name in self.required_folders:
            folder_path = evidence_folder / folder_name

            if folder_path.exists():
                # Check if folder contains files
                files = self._get_supported_files(folder_path)

                if len(files) > 0:
                    folders_found[folder_name] = {
                        "path": str(folder_path),
                        "criterion": self.folder_to_criterion[folder_name],
                        "file_count": len(files),
                        "files": [str(f) for f in files]
                    }
                else:
                    warnings.append(f"Folder '{folder_name}' exists but contains no supported files")
            else:
                # Folder not found - this is acceptable, just log it
                logger.debug(f"Optional criterion folder not present: {folder_name}")

        # Check for unexpected folders
        unexpected_folders = set(available_folders) - set(self.required_folders)
        if unexpected_folders:
            warnings.append(
                f"Unexpected folders found (will be ignored): {', '.join(unexpected_folders)}"
            )

        # Validate minimum criterion requirement (at least 3 folders with files)
        criterion_folders_with_files = [
            f for f in folders_found.keys()
            if f != "Personal" and folders_found[f]["file_count"] > 0
        ]

        if len(criterion_folders_with_files) < 3:
            errors.append(
                f"At least 3 criterion folders with files required for EB-1A. "
                f"Found: {len(criterion_folders_with_files)}"
            )

        # Final validation
        valid = len(errors) == 0

        result = {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "evidence_path": evidence_path,
            "case_overview_path": case_overview_path,
            "folders_found": folders_found,
            "criterion_folders_count": len(criterion_folders_with_files)
        }

        logger.info(f"Validation result: {valid}, Folders found: {len(folders_found)}")
        return result

    def _get_supported_files(self, folder_path: Path) -> List[Path]:
        """Get all supported files in a folder"""
        files = []
        for file_path in folder_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                files.append(file_path)
        return files

    def get_folder_names(self) -> List[str]:
        """Get list of all required folder names"""
        return self.required_folders.copy()

    def get_criterion_name(self, folder_name: str) -> Optional[str]:
        """Get official criterion name for a folder"""
        return self.folder_to_criterion.get(folder_name)

    def is_valid_folder_name(self, folder_name: str) -> bool:
        """Check if folder name is valid"""
        return folder_name in self.required_folders
