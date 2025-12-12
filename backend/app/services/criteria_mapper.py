"""
EB-1A Criteria Mapper Service
Maps folder names to official EB-1A criteria using LLM-first approach
"""
from typing import Dict, List, Any
from pathlib import Path
from ..llm.gemini import GeminiLLM


class CriteriaMapper:
    """
    Maps evidence folder names to official EB-1A criteria using intelligent LLM analysis

    Strategy: LLM-first approach with confidence scoring
    - Analyzes folder names and sample file names for context
    - Returns criterion, confidence score, and reasoning
    - No rigid pattern matching - fully flexible
    """

    # Official EB-1A Criteria (for reference)
    OFFICIAL_CRITERIA = [
        "Awards / Prizes",
        "Membership in Outstanding Associations",
        "Published Material About You",
        "Judging the Work of Others",
        "Original Contributions",
        "Authorship of Scholarly Articles",
        "Artistic Exhibitions / Showcases",
        "Leading or Critical Role",
        "High Salary / Remuneration",
        "Commercial Success in Performing Arts",
        "Final Merits"  # Supporting analysis section
    ]

    # Confidence threshold for accepting mappings
    CONFIDENCE_THRESHOLD = 0.5

    def __init__(self):
        self.llm = GeminiLLM()

    async def map_folders(
        self,
        evidence_path: Path
    ) -> Dict[str, Dict[str, Any]]:
        """
        Map all evidence folders to EB-1A criteria using LLM intelligence

        Args:
            evidence_path: Path to the Evidence directory

        Returns:
            Dictionary mapping folder_name -> {
                'criterion': str,
                'confidence': float,
                'reasoning': str
            }
        """
        # Get all criterion folders with sample files
        folders_with_files = {}

        for folder in evidence_path.iterdir():
            if folder.is_dir():
                # Get sample file names for context
                files = [f.name for f in folder.iterdir() if f.is_file()]
                folders_with_files[folder.name] = files[:10]  # First 10 files as context

        if not folders_with_files:
            return {}

        # Use batch LLM mapping (more efficient)
        try:
            print(f"[Criteria Mapping] Analyzing {len(folders_with_files)} folders with LLM...")
            mappings = await self.llm.batch_map_folders_to_criteria(folders_with_files)

            # Log results
            for folder_name, mapping_info in mappings.items():
                confidence = mapping_info.get('confidence', 0)
                criterion = mapping_info.get('criterion', 'Other')

                print(f"[Criteria Mapping] '{folder_name}' -> '{criterion}' (confidence: {confidence:.2f})")

                # Warn on low confidence
                if confidence < self.CONFIDENCE_THRESHOLD:
                    print(f"[Warning] Low confidence mapping for '{folder_name}'")

            return mappings

        except Exception as e:
            print(f"[LLM Error] Criteria mapping failed: {str(e)}")
            # Fallback: assign "Other" to all folders
            return {
                name: {
                    'criterion': 'Other',
                    'confidence': 0.0,
                    'reasoning': f'LLM mapping failed: {str(e)}'
                }
                for name in folders_with_files.keys()
            }

    async def map_single_folder(
        self,
        folder_name: str,
        folder_path: Path
    ) -> Dict[str, Any]:
        """
        Map a single folder to a criterion (useful for testing or incremental updates)

        Args:
            folder_name: Name of the folder
            folder_path: Path to the folder

        Returns:
            Dict with {criterion, confidence, reasoning}
        """
        # Get sample files
        sample_files = [f.name for f in folder_path.iterdir() if f.is_file()][:10]

        try:
            mapping = await self.llm.map_folder_to_criterion(
                folder_name=folder_name,
                sample_files=sample_files
            )

            print(f"[Single Mapping] '{folder_name}' -> '{mapping.get('criterion')}' (confidence: {mapping.get('confidence', 0):.2f})")

            return mapping

        except Exception as e:
            print(f"[LLM Error] Single folder mapping failed: {str(e)}")
            return {
                'criterion': 'Other',
                'confidence': 0.0,
                'reasoning': f'LLM mapping failed: {str(e)}'
            }

    def get_criterion_description(self, criterion: str) -> str:
        """
        Get a description of what the criterion means

        Args:
            criterion: The EB-1A criterion name

        Returns:
            Description text
        """
        descriptions = {
            "Awards / Prizes": "Evidence of receipt of lesser nationally or internationally recognized prizes or awards for excellence",
            "Membership in Outstanding Associations": "Evidence of membership in associations that demand outstanding achievement of their members",
            "Published Material About You": "Evidence of published material about you in professional or major trade publications or other major media",
            "Judging the Work of Others": "Evidence that you have been asked to judge the work of others, either individually or on a panel",
            "Original Contributions": "Evidence of your original scientific, scholarly, artistic, athletic, or business-related contributions of major significance",
            "Authorship of Scholarly Articles": "Evidence of your authorship of scholarly articles in professional or major trade publications or other major media",
            "Artistic Exhibitions / Showcases": "Evidence that your work has been displayed at artistic exhibitions or showcases",
            "Leading or Critical Role": "Evidence of your performance of a leading or critical role in distinguished organizations",
            "High Salary / Remuneration": "Evidence that you command a high salary or other significantly high remuneration in relation to others in the field",
            "Commercial Success in Performing Arts": "Evidence of your commercial successes in the performing arts",
            "Final Merits": "Supporting evidence for final merits determination demonstrating sustained national or international acclaim"
        }

        return descriptions.get(criterion, "No description available")

    def get_exhibit_group_letter(self, criterion: str, existing_groups: List[str] = None) -> str:
        """
        Get the exhibit group letter for a criterion

        Args:
            criterion: The EB-1A criterion
            existing_groups: List of already assigned group letters

        Returns:
            Exhibit group letter (A, B, C, etc.)
        """
        # Standard grouping
        criterion_to_letter = {
            "Background": "A",
            "Field Information": "B",
            "Original Contributions": "C",
            "Leading or Critical Role": "D",
            "High Salary / Remuneration": "E",
            "Judging the Work of Others": "F",
            "Authorship of Scholarly Articles": "G",
            "Membership in Outstanding Associations": "H",
            "Final Merits": "I",
            "Awards / Prizes": "J",
            "Published Material About You": "K",
            "Artistic Exhibitions / Showcases": "L",
            "Commercial Success in Performing Arts": "M"
        }

        if criterion in criterion_to_letter:
            return criterion_to_letter[criterion]

        # For unmapped, assign next available letter
        if existing_groups:
            used_letters = set(existing_groups)
            for letter in "NOPQRSTUVWXYZ":
                if letter not in used_letters:
                    return letter

        return "Z"  # Fallback

    def validate_criteria_match(self, folder_count: int) -> Dict:
        """
        Validate if client meets minimum EB-1A requirements

        Args:
            folder_count: Number of criterion folders found

        Returns:
            Validation result dictionary
        """
        MIN_CRITERIA = 3

        return {
            "meets_minimum": folder_count >= MIN_CRITERIA,
            "criteria_count": folder_count,
            "minimum_required": MIN_CRITERIA,
            "message": f"Found {folder_count} criteria. " +
                       (f"Meets minimum requirement ({MIN_CRITERIA})." if folder_count >= MIN_CRITERIA
                        else f"Does NOT meet minimum requirement ({MIN_CRITERIA}).")
        }
