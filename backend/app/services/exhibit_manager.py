"""
Exhibit Management System
Auto-assigns exhibit IDs and tracks document-to-exhibit mapping
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json


@dataclass
class Exhibit:
    """Represents a single exhibit"""
    exhibit_id: str  # e.g., "A-1", "B-2"
    group_letter: str  # e.g., "A", "B"
    group_title: str  # e.g., "BACKGROUND INFORMATION"
    number: int  # Sequential number within group
    title: str  # Descriptive title
    description: str  # Detailed description
    file_path: str  # Path to original document
    criterion: Optional[str] = None  # EB-1A criterion
    document_type: Optional[str] = None  # certificate, letter, etc.


class ExhibitManager:
    """
    Manages exhibit numbering and organization for EB-1A petitions
    """

    # Standard exhibit group structure
    STANDARD_GROUPS = {
        "A": "THE PETITIONER'S BACKGROUND INFORMATION",
        "B": "ABOUT THE FIELD AND THE PETITIONER'S PROPOSED WORK",
        "C": "ORIGINAL CONTRIBUTIONS OF MAJOR SIGNIFICANCE",
        "D": "LEADING OR CRITICAL ROLE",
        "E": "HIGH SALARY OR OTHER REMUNERATION",
        "F": "JUDGING THE WORK OF OTHERS",
        "G": "AUTHORSHIP OF SCHOLARLY ARTICLES",
        "H": "MEMBERSHIP IN OUTSTANDING ASSOCIATIONS",
        "I": "FINAL MERITS",
        "J": "AWARDS / PRIZES",
        "K": "PUBLISHED MATERIAL ABOUT YOU",
        "L": "ARTISTIC EXHIBITIONS / SHOWCASES",
        "M": "COMMERCIAL SUCCESS IN PERFORMING ARTS"
    }

    # Map criteria to exhibit groups
    CRITERION_TO_GROUP = {
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

    def __init__(self):
        self.exhibits: List[Exhibit] = []
        self.group_counters: Dict[str, int] = {}
        self.used_groups: set = set()

    def create_background_exhibits(
        self,
        resume_path: Optional[str] = None,
        passport_path: Optional[str] = None,
        case_overview_path: Optional[str] = None
    ) -> List[Exhibit]:
        """
        Create standard background exhibits (Group A)

        Args:
            resume_path: Path to resume/CV
            passport_path: Path to passport copy
            case_overview_path: Path to case overview document

        Returns:
            List of created exhibits
        """
        background_exhibits = []

        if resume_path or case_overview_path:
            exhibit = self._create_exhibit(
                group_letter="A",
                group_title=self.STANDARD_GROUPS["A"],
                title="Resume and Academic Records" if resume_path else "Case Overview and Background",
                description="Documentation of the Petitioner's educational background and professional experience.",
                file_path=resume_path or case_overview_path,
                criterion="Background"
            )
            background_exhibits.append(exhibit)

        if passport_path:
            exhibit = self._create_exhibit(
                group_letter="A",
                group_title=self.STANDARD_GROUPS["A"],
                title="Copy of Passport and Evidence of Nonimmigrant Status",
                description="Passport copy and current immigration status documentation.",
                file_path=passport_path,
                criterion="Background"
            )
            background_exhibits.append(exhibit)

        return background_exhibits

    def create_field_exhibits(
        self,
        field_name: str,
        statement_of_intent_path: Optional[str] = None
    ) -> List[Exhibit]:
        """
        Create field information exhibits (Group B)

        Args:
            field_name: The beneficiary's field of expertise
            statement_of_intent_path: Path to statement of intent document

        Returns:
            List of created exhibits
        """
        field_exhibits = []

        # Field information exhibit (can be auto-generated)
        exhibit = self._create_exhibit(
            group_letter="B",
            group_title=self.STANDARD_GROUPS["B"],
            title=f"Information about the field of {field_name}",
            description=f"Detailed information about the {field_name} field and its significance to the United States.",
            file_path="[auto-generated]",
            criterion="Field Information"
        )
        field_exhibits.append(exhibit)

        if statement_of_intent_path:
            exhibit = self._create_exhibit(
                group_letter="B",
                group_title=self.STANDARD_GROUPS["B"],
                title="Statement of intent detailing proposed work in the U.S.",
                description="Documentation of how the Petitioner intends to continue their work in the United States.",
                file_path=statement_of_intent_path,
                criterion="Field Information"
            )
            field_exhibits.append(exhibit)

        return field_exhibits

    def create_criterion_exhibits(
        self,
        criterion: str,
        documents: List[Dict],
        extracted_info: List[Dict]
    ) -> List[Exhibit]:
        """
        Create exhibits for a specific EB-1A criterion

        Args:
            criterion: The EB-1A criterion name
            documents: List of document dictionaries with file paths
            extracted_info: List of extracted information for each document

        Returns:
            List of created exhibits
        """
        # Get group letter for this criterion
        group_letter = self.CRITERION_TO_GROUP.get(criterion, "Z")
        group_title = self.STANDARD_GROUPS.get(group_letter, criterion.upper())

        exhibits = []

        for doc, info in zip(documents, extracted_info):
            # Generate exhibit title from extracted info
            title = self._generate_exhibit_title(criterion, info)

            # Generate description
            description = self._generate_exhibit_description(criterion, info)

            exhibit = self._create_exhibit(
                group_letter=group_letter,
                group_title=group_title,
                title=title,
                description=description,
                file_path=doc.get("file_path", ""),
                criterion=criterion,
                document_type=info.get("document_type")
            )

            exhibits.append(exhibit)

        return exhibits

    def _create_exhibit(
        self,
        group_letter: str,
        group_title: str,
        title: str,
        description: str,
        file_path: str,
        criterion: Optional[str] = None,
        document_type: Optional[str] = None
    ) -> Exhibit:
        """
        Create a new exhibit with auto-incremented numbering

        Args:
            group_letter: Exhibit group letter (A, B, C, etc.)
            group_title: Title of the exhibit group
            title: Exhibit title
            description: Exhibit description
            file_path: Path to the document
            criterion: EB-1A criterion
            document_type: Type of document

        Returns:
            Created Exhibit object
        """
        # Initialize counter for this group if needed
        if group_letter not in self.group_counters:
            self.group_counters[group_letter] = 0

        # Increment counter
        self.group_counters[group_letter] += 1
        number = self.group_counters[group_letter]

        # Create exhibit ID
        exhibit_id = f"{group_letter}-{number}"

        # Mark group as used
        self.used_groups.add(group_letter)

        exhibit = Exhibit(
            exhibit_id=exhibit_id,
            group_letter=group_letter,
            group_title=group_title,
            number=number,
            title=title,
            description=description,
            file_path=file_path,
            criterion=criterion,
            document_type=document_type
        )

        self.exhibits.append(exhibit)
        return exhibit

    def _generate_exhibit_title(self, criterion: str, info: Dict) -> str:
        """Generate a descriptive exhibit title from extracted info"""

        # Try to extract key information for title
        document_type = info.get("document_type", "").replace("_", " ").title()
        entities = info.get("entities", {})

        # Criterion-specific title generation
        if criterion == "Membership in Outstanding Associations":
            org_name = entities.get("organizations", [""])[0] if "organizations" in entities else "Association"
            return f"Evidence of membership in {org_name}"

        elif criterion == "Judging the Work of Others":
            conf_name = entities.get("conference", "") or entities.get("organization", [""])[0] if "organization" in entities else "Conference"
            return f"Evidence of peer review service for {conf_name}"

        elif criterion == "Authorship of Scholarly Articles":
            title = entities.get("title", "") or "Scholarly Article"
            return f"Copy of scholarly article: {title}"

        elif criterion == "Leading or Critical Role":
            company = entities.get("company", "") or entities.get("organizations", [""])[0] if "organizations" in entities else "Organization"
            role = entities.get("position", "") or "Leadership Role"
            return f"Evidence of {role} at {company}"

        elif criterion == "High Salary / Remuneration":
            return f"Evidence of high compensation ({document_type})"

        elif criterion == "Awards / Prizes":
            award = entities.get("award_name", "") or "Award"
            return f"Evidence of {award}"

        elif criterion == "Original Contributions":
            return f"Documentation of original contributions ({document_type})"

        else:
            return f"Evidence for {criterion} ({document_type})"

    def _generate_exhibit_description(self, criterion: str, info: Dict) -> str:
        """Generate exhibit description from extracted info"""

        summary = info.get("summary", "")
        if summary:
            # Limit to reasonable length
            if len(summary) > 200:
                summary = summary[:197] + "..."
            return summary

        # Fallback generic description
        return f"Supporting documentation for {criterion} criterion."

    def get_exhibits_by_group(self) -> Dict[str, List[Exhibit]]:
        """
        Get exhibits organized by group letter

        Returns:
            Dictionary mapping group_letter -> list of exhibits
        """
        grouped = {}

        for exhibit in self.exhibits:
            group = exhibit.group_letter
            if group not in grouped:
                grouped[group] = []
            grouped[group].append(exhibit)

        # Sort groups alphabetically
        return dict(sorted(grouped.items()))

    def get_exhibit_index(self) -> List[Dict]:
        """
        Generate exhibit index structure for document

        Returns:
            List of exhibit groups with their exhibits
        """
        grouped = self.get_exhibits_by_group()

        index = []

        for group_letter in sorted(grouped.keys()):
            exhibits = grouped[group_letter]

            # Get group title
            group_title = exhibits[0].group_title if exhibits else ""

            group_data = {
                "group_letter": group_letter,
                "group_title": group_title,
                "exhibits": [
                    {
                        "exhibit_id": ex.exhibit_id,
                        "title": ex.title,
                        "description": ex.description
                    }
                    for ex in exhibits
                ]
            }

            index.append(group_data)

        return index

    def get_exhibit_references(self, criterion: str) -> List[str]:
        """
        Get list of exhibit IDs for a criterion (for letter generation)

        Args:
            criterion: The EB-1A criterion

        Returns:
            List of exhibit IDs (e.g., ["C-1", "C-2", "C-3"])
        """
        refs = []

        for exhibit in self.exhibits:
            if exhibit.criterion == criterion:
                refs.append(exhibit.exhibit_id)

        return refs

    def export_metadata(self, output_path: str):
        """
        Export exhibit metadata to JSON file

        Args:
            output_path: Path to output JSON file
        """
        metadata = {
            "total_exhibits": len(self.exhibits),
            "groups_used": sorted(list(self.used_groups)),
            "exhibits": [asdict(ex) for ex in self.exhibits]
        }

        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def get_exhibit_by_id(self, exhibit_id: str) -> Optional[Exhibit]:
        """
        Get exhibit by its ID

        Args:
            exhibit_id: Exhibit ID (e.g., "A-1")

        Returns:
            Exhibit object or None
        """
        for exhibit in self.exhibits:
            if exhibit.exhibit_id == exhibit_id:
                return exhibit
        return None

    def get_total_count(self) -> int:
        """Get total number of exhibits"""
        return len(self.exhibits)

    def get_summary(self) -> Dict:
        """
        Get summary statistics

        Returns:
            Summary dictionary
        """
        grouped = self.get_exhibits_by_group()

        return {
            "total_exhibits": len(self.exhibits),
            "num_groups": len(grouped),
            "groups": {
                letter: len(exhibits)
                for letter, exhibits in grouped.items()
            },
            "criteria_covered": list(set(
                ex.criterion for ex in self.exhibits if ex.criterion
            ))
        }
