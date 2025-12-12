"""
Exhibit Manager Agent
Centralized management of all exhibits across criterion agents
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Exhibit:
    """Exhibit data structure"""
    exhibit_id: str  # e.g., "C-3"
    group_letter: str  # e.g., "C"
    group_title: str  # e.g., "Critical Role"
    number: int  # Sequential number within group
    title: str  # Descriptive title
    description: str  # Detailed description
    file_path: str  # Path to original file
    criterion: str  # EB-1A criterion name
    key_points: List[str] = field(default_factory=list)
    document_type: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    def __str__(self) -> str:
        """String representation for citations"""
        return f"Exhibit {self.exhibit_id}"


class ExhibitManagerAgent:
    """
    Manages exhibit assignments and tracking across all agents

    Exhibit Grouping System:
    - Group A: Background exhibits (Case Overview, Personal docs)
    - Group B: Field exhibits (Statement of Intent, field descriptions)
    - Groups C-L: One group per criterion (if evidence present)
      - C: Critical Role
      - D: Original Contribution
      - E: High Salary
      - F: Judging
      - G: Membership
      - H: Awards
      - I: Authorship
      - J: Press
      - K: Final Merits
      - L: Performing Arts
    """

    # Mapping from criterion to group letter
    CRITERION_TO_GROUP = {
        "Leading or Critical Role": "C",
        "Original Contributions of Major Significance": "D",
        "High Salary or Remuneration": "E",
        "Judging the Work of Others": "F",
        "Membership in Associations": "G",
        "Awards and Prizes": "H",
        "Scholarly Authorship": "I",
        "Published Material About You": "J",
        "Final Merits Determination": "K",
        "Commercial Success in Performing Arts": "L",
        "Background Information": "A"
    }

    # Group titles
    GROUP_TITLES = {
        "A": "Background and Personal Information",
        "B": "Field Description",
        "C": "Critical Role in Distinguished Organizations",
        "D": "Original Contributions of Major Significance",
        "E": "High Salary or Remuneration",
        "F": "Judging the Work of Others",
        "G": "Membership in Selective Associations",
        "H": "Awards and Prizes",
        "I": "Scholarly Authorship",
        "J": "Published Material About the Beneficiary",
        "K": "Final Merits Determination",
        "L": "Commercial Success in Performing Arts"
    }

    def __init__(self):
        """Initialize exhibit manager"""
        self.exhibits: List[Exhibit] = []
        self.group_counters: Dict[str, int] = {}  # Track numbers per group
        self.exhibits_by_group: Dict[str, List[Exhibit]] = {}
        self.exhibits_by_criterion: Dict[str, List[Exhibit]] = {}

    async def create_exhibit(
        self,
        criterion: str,
        file_path: str,
        title: str,
        description: str,
        key_points: List[str] = None,
        document_type: str = None,
        metadata: Dict = None
    ) -> Exhibit:
        """
        Create a new exhibit with assigned ID

        Args:
            criterion: EB-1A criterion name
            file_path: Path to document
            title: Exhibit title
            description: Exhibit description
            key_points: Key points from document
            document_type: Type of document (certificate, letter, etc.)
            metadata: Additional metadata

        Returns:
            Created Exhibit object
        """
        # Get group letter for criterion
        group_letter = self.CRITERION_TO_GROUP.get(criterion)

        if not group_letter:
            logger.warning(f"Unknown criterion: {criterion}, using default group 'X'")
            group_letter = "X"

        # Get group title
        group_title = self.GROUP_TITLES.get(group_letter, criterion)

        # Get next number for this group
        if group_letter not in self.group_counters:
            self.group_counters[group_letter] = 0

        self.group_counters[group_letter] += 1
        number = self.group_counters[group_letter]

        # Create exhibit ID
        exhibit_id = f"{group_letter}-{number}"

        # Create exhibit
        exhibit = Exhibit(
            exhibit_id=exhibit_id,
            group_letter=group_letter,
            group_title=group_title,
            number=number,
            title=title,
            description=description,
            file_path=file_path,
            criterion=criterion,
            key_points=key_points or [],
            document_type=document_type,
            metadata=metadata or {}
        )

        # Store exhibit
        self.exhibits.append(exhibit)

        # Index by group
        if group_letter not in self.exhibits_by_group:
            self.exhibits_by_group[group_letter] = []
        self.exhibits_by_group[group_letter].append(exhibit)

        # Index by criterion
        if criterion not in self.exhibits_by_criterion:
            self.exhibits_by_criterion[criterion] = []
        self.exhibits_by_criterion[criterion].append(exhibit)

        logger.info(f"Created exhibit {exhibit_id}: {title}")

        return exhibit

    def get_exhibits_by_criterion(self, criterion: str) -> List[Exhibit]:
        """Get all exhibits for a specific criterion"""
        return self.exhibits_by_criterion.get(criterion, [])

    def get_exhibits_by_group(self, group_letter: str) -> List[Exhibit]:
        """Get all exhibits in a group"""
        return self.exhibits_by_group.get(group_letter, [])

    def get_all_exhibits(self) -> List[Exhibit]:
        """Get all exhibits sorted by group and number"""
        return sorted(self.exhibits, key=lambda e: (e.group_letter, e.number))

    def get_exhibit_by_id(self, exhibit_id: str) -> Optional[Exhibit]:
        """Get exhibit by ID"""
        for exhibit in self.exhibits:
            if exhibit.exhibit_id == exhibit_id:
                return exhibit
        return None

    def get_exhibit_index(self) -> List[Dict]:
        """
        Generate complete exhibit index for document

        Returns:
            List of exhibit dictionaries sorted by group
        """
        return [exhibit.to_dict() for exhibit in self.get_all_exhibits()]

    def get_exhibit_index_by_group(self) -> Dict[str, List[Dict]]:
        """
        Get exhibit index organized by groups

        Returns:
            Dictionary mapping group letters to exhibit lists
        """
        index = {}
        for group_letter in sorted(self.exhibits_by_group.keys()):
            index[group_letter] = [
                exhibit.to_dict()
                for exhibit in self.exhibits_by_group[group_letter]
            ]
        return index

    def generate_exhibit_citation(self, exhibit_id: str, inline: bool = True) -> str:
        """
        Generate properly formatted exhibit citation

        Args:
            exhibit_id: Exhibit ID (e.g., "C-3")
            inline: If True, format for inline citation; else for reference list

        Returns:
            Formatted citation string
        """
        exhibit = self.get_exhibit_by_id(exhibit_id)

        if not exhibit:
            return f"Exhibit {exhibit_id}"

        if inline:
            # Inline citation: "See Exhibit C-3"
            return f"See Exhibit {exhibit.exhibit_id}"
        else:
            # Reference list format: "Exhibit C-3: Title - Description"
            return f"Exhibit {exhibit.exhibit_id}: {exhibit.title}"

    def generate_citations_for_criterion(
        self,
        criterion: str,
        inline: bool = False
    ) -> List[str]:
        """
        Generate all citations for a criterion

        Args:
            criterion: Criterion name
            inline: If True, format for inline; else for reference list

        Returns:
            List of formatted citations
        """
        exhibits = self.get_exhibits_by_criterion(criterion)
        return [
            self.generate_exhibit_citation(exhibit.exhibit_id, inline)
            for exhibit in exhibits
        ]

    def get_summary(self) -> Dict:
        """
        Get summary statistics

        Returns:
            Summary dictionary with counts and groups
        """
        return {
            "total_exhibits": len(self.exhibits),
            "groups_used": sorted(list(self.group_counters.keys())),
            "exhibits_by_group": {
                group: len(exhibits)
                for group, exhibits in self.exhibits_by_group.items()
            },
            "criteria_covered": sorted(list(self.exhibits_by_criterion.keys()))
        }

    def validate_all_citations(self, letter_text: str) -> Dict:
        """
        Validate that all exhibit citations in letter exist

        Args:
            letter_text: Complete letter text

        Returns:
            Validation report with missing citations
        """
        import re

        # Find all exhibit citations in text (e.g., "Exhibit C-3")
        citation_pattern = r'Exhibit ([A-L]-\d+)'
        found_citations = set(re.findall(citation_pattern, letter_text))

        # Check which citations exist
        existing_ids = {exhibit.exhibit_id for exhibit in self.exhibits}

        missing = found_citations - existing_ids
        valid = found_citations & existing_ids

        return {
            "total_citations": len(found_citations),
            "valid_citations": len(valid),
            "missing_citations": sorted(list(missing)),
            "all_valid": len(missing) == 0
        }

    def clear(self):
        """Clear all exhibits (useful for testing)"""
        self.exhibits = []
        self.group_counters = {}
        self.exhibits_by_group = {}
        self.exhibits_by_criterion = {}
        logger.info("Cleared all exhibits")
