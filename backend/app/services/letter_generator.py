"""
EB-1A Attorney Letter Generator
Generates complete attorney support letters using extracted evidence and Gemini
"""
from typing import Dict, List, Optional
from datetime import datetime
from ..llm.gemini import GeminiLLM
from ..llm.claude import ClaudeLLM
from ..config import get_settings


class LetterGenerator:
    """
    Generates professional EB-1A attorney support letters
    Based on the Amit Kumar template structure
    """

    def __init__(self):
        self.gemini = GeminiLLM()
        settings = get_settings()

        # Optional Claude for polishing
        self.use_claude = settings.use_claude_polish
        if self.use_claude:
            try:
                self.claude = ClaudeLLM()
            except:
                self.use_claude = False

    async def generate_complete_letter(
        self,
        beneficiary_info: Dict,
        field: str,
        criteria_data: Dict[str, Dict],
        exhibit_manager,
        attorney_info: Optional[Dict] = None
    ) -> str:
        """
        Generate complete EB-1A attorney letter

        Args:
            beneficiary_info: Extracted beneficiary information
            field: Field of expertise (e.g., "Cloud Engineering")
            criteria_data: Dictionary mapping criterion -> extracted evidence data
            exhibit_manager: ExhibitManager instance with all exhibits
            attorney_info: Optional attorney/law firm information

        Returns:
            Complete letter text
        """
        sections = []

        # Header
        header = self._generate_header(beneficiary_info, attorney_info)
        sections.append(header)

        # Opening
        opening = self._generate_opening(beneficiary_info, field, len(criteria_data))
        sections.append(opening)

        # Section I: The Field
        field_section = await self.generate_field_section(field, beneficiary_info)
        sections.append(field_section)

        # Section II: The Beneficiary
        beneficiary_section = await self.generate_beneficiary_section(beneficiary_info, field)
        sections.append(beneficiary_section)

        # Section III: EB-1A Eligibility Criteria
        criteria_section = await self.generate_criteria_sections(
            criteria_data,
            exhibit_manager
        )
        sections.append(criteria_section)

        # Section IV: Final Merits Analysis
        final_merits = await self.generate_final_merits(
            beneficiary_info,
            field,
            criteria_data,
            exhibit_manager
        )
        sections.append(final_merits)

        # Section V: Conclusion
        conclusion = self._generate_conclusion(beneficiary_info)
        sections.append(conclusion)

        # Combine all sections
        complete_letter = "\n\n".join(sections)

        # Optional Claude polishing
        if self.use_claude:
            try:
                complete_letter = await self.claude.polish_letter(complete_letter)
            except Exception as e:
                # If polishing fails, return unpolished version
                pass

        return complete_letter

    def _generate_header(self, beneficiary_info: Dict, attorney_info: Optional[Dict]) -> str:
        """Generate letter header with law firm info"""

        # Default law firm info (can be customized)
        if not attorney_info:
            attorney_info = {
                "firm_name": "[LAW FIRM NAME]",
                "address": "[ADDRESS]",
                "phone": "[PHONE]",
                "email": "[EMAIL]",
                "attorney_name": "[ATTORNEY NAME]"
            }

        date = datetime.now().strftime("%B %d, %Y")
        beneficiary_name = beneficiary_info.get("name", "[Beneficiary Name]")

        header = f"""{attorney_info['firm_name']}
{attorney_info['address']}
{attorney_info['phone']}
{attorney_info['email']}

{date}

Subject: I-140 Petition for EB-1A (Business) by {beneficiary_name}

Dear USCIS Officer:"""

        return header

    def _generate_opening(self, beneficiary_info: Dict, field: str, num_criteria: int) -> str:
        """Generate opening paragraph"""

        beneficiary_name = beneficiary_info.get("name", "[Beneficiary Name]")

        opening = f"""This letter is submitted in support of {beneficiary_name} ("Beneficiary") as an Alien of Extraordinary Ability in business.

In this petition, we submit probative evidence to demonstrate by a preponderance of the evidence that the Beneficiary is an expert in the field of {field}. The evidence demonstrates that the Beneficiary has established a proven record as a leader in this field, and clearly meets at least three (3) regulatory criteria to qualify for EB-1A classification. Specifically, the Beneficiary meets {num_criteria} criteria."""

        return opening

    async def generate_field_section(self, field: str, beneficiary_info: Dict) -> str:
        """
        Generate Section I: THE FIELD

        Args:
            field: Field of expertise
            beneficiary_info: Beneficiary information for context

        Returns:
            Field section text
        """
        system_prompt = """You are writing the field description section for an EB-1A attorney letter.
This section should:
1. Define the field comprehensively
2. Explain its technical aspects and scope
3. Demonstrate its importance to the United States
4. Connect to national priorities (economy, security, innovation)
5. Use professional legal language
6. Be 3-4 detailed paragraphs"""

        prompt = f"""Write the "THE FIELD: {field}" section for an EB-1A attorney letter.

The beneficiary works in: {field}

Current position: {beneficiary_info.get('position', 'Not specified')}
Company: {beneficiary_info.get('company', 'Not specified')}

Structure the section as follows:
- Paragraph 1: Define {field} and its core concepts
- Paragraph 2: Technical depth and modern practices in the field
- Paragraph 3: Importance to U.S. national interests, economy, and innovation
- Paragraph 4: Strategic significance and future outlook

Use the format:
## I. THE FIELD: {field}

[Your detailed content here...]"""

        field_content = await self.gemini.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.6,
            max_tokens=2000
        )

        return field_content

    async def generate_beneficiary_section(self, beneficiary_info: Dict, field: str) -> str:
        """
        Generate Section II: THE BENEFICIARY

        Args:
            beneficiary_info: Extracted beneficiary information
            field: Field of expertise

        Returns:
            Beneficiary section text
        """
        system_prompt = """You are writing the beneficiary background section for an EB-1A attorney letter.
This section should:
1. Present career trajectory chronologically
2. Highlight education and credentials
3. Emphasize progression and achievements
4. Use professional legal language
5. Be 2-3 paragraphs"""

        # Extract key info
        name = beneficiary_info.get("name", "[Name]")
        education = beneficiary_info.get("education", [])
        career = beneficiary_info.get("career_history", [])
        current_position = beneficiary_info.get("position", "")
        current_company = beneficiary_info.get("company", "")

        prompt = f"""Write the "THE BENEFICIARY: {name}" section for an EB-1A attorney letter.

Beneficiary Information:
- Name: {name}
- Field: {field}
- Current Position: {current_position}
- Current Company: {current_company}
- Education: {education}
- Career History: {career}

Structure:
- Paragraph 1: Education and early career
- Paragraph 2: Career progression and current role
- Paragraph 3: Specialized expertise and achievements

Use the format:
## II. THE BENEFICIARY: {name}

[Your detailed content here...]"""

        beneficiary_content = await self.gemini.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.6,
            max_tokens=1500
        )

        return beneficiary_content

    async def generate_criteria_sections(
        self,
        criteria_data: Dict[str, Dict],
        exhibit_manager
    ) -> str:
        """
        Generate Section III: EB-1A ELIGIBILITY CRITERIA

        Args:
            criteria_data: Dictionary of criterion -> extracted evidence
            exhibit_manager: ExhibitManager instance

        Returns:
            Complete criteria section text
        """
        sections = ["## III. EB-1A ELIGIBILITY CRITERIA\n"]

        criterion_number = 1

        for criterion, data in criteria_data.items():
            if criterion == "Final Merits":
                continue  # Handle separately

            # Generate subsection for this criterion
            subsection = await self._generate_criterion_subsection(
                criterion_number,
                criterion,
                data,
                exhibit_manager
            )

            sections.append(subsection)
            criterion_number += 1

        return "\n\n".join(sections)

    async def _generate_criterion_subsection(
        self,
        number: int,
        criterion: str,
        evidence_data: Dict,
        exhibit_manager
    ) -> str:
        """Generate a single criterion subsection"""

        # Get regulation citation
        regulation = self._get_regulation_citation(criterion)

        # Get exhibit references
        exhibit_refs = exhibit_manager.get_exhibit_references(criterion)
        exhibit_list = ", ".join(exhibit_refs)

        system_prompt = """You are writing a criterion section for an EB-1A attorney letter.
This section should:
1. Present detailed evidence narratives
2. Explain significance and impact
3. Use specific facts, numbers, and achievements
4. Reference exhibits appropriately
5. Conclude with regulation citation
6. Be 3-5 paragraphs of detailed analysis"""

        prompt = f"""Write the criterion subsection for an EB-1A letter:

Criterion: {criterion}
Evidence Summary: {evidence_data.get('summary', '')}
Key Facts: {evidence_data.get('key_facts', [])}
Entities: {evidence_data.get('entities', {})}

Available Exhibits: {exhibit_list}

Structure:
1. Introduction paragraph explaining how beneficiary meets this criterion
2. 2-3 paragraphs with specific evidence, achievements, and impact
3. Exhibit reference paragraph: "For documentation of [beneficiary]'s {criterion}, please see:"
4. Concluding paragraph citing regulation

Use the format:
### {number}. Evidence of {criterion}

[Your detailed content here...]

For documentation... please see:
{exhibit_list}

Based on the evidence... {regulation}."""

        content = await self.gemini.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2000
        )

        return content

    async def generate_final_merits(
        self,
        beneficiary_info: Dict,
        field: str,
        criteria_data: Dict,
        exhibit_manager
    ) -> str:
        """Generate Section IV: FINAL MERITS ANALYSIS"""

        name = beneficiary_info.get("name", "[Name]")
        num_criteria = len([c for c in criteria_data.keys() if c != "Final Merits"])

        system_prompt = """You are writing the final merits analysis for an EB-1A attorney letter.
This section should:
1. Synthesize all evidence
2. Demonstrate sustained national/international acclaim
3. Show beneficiary is in top percentile of field
4. Explain benefits to United States
5. Use persuasive legal argumentation"""

        # Get final merits evidence if provided
        final_merits_data = criteria_data.get("Final Merits", {})

        prompt = f"""Write the "FINAL MERITS ANALYSIS" section for an EB-1A attorney letter.

Beneficiary: {name}
Field: {field}
Criteria Met: {num_criteria}

Evidence Summary:
{chr(10).join(f"- {c}: {d.get('summary', '')[:200]}" for c, d in criteria_data.items() if c != "Final Merits")}

Additional Final Merits Evidence: {final_merits_data.get('summary', 'None provided')}

Structure:
- Paragraph 1: Summarize sustained acclaim and recognition
- Paragraph 2: Demonstrate top-tier status in field
- Paragraph 3: Benefits to United States
- Paragraph 4: Conclusion affirming EB-1A eligibility

Use the format:
## IV. FINAL MERITS ANALYSIS

[Your detailed content here...]"""

        content = await self.gemini.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2000
        )

        return content

    def _generate_conclusion(self, beneficiary_info: Dict) -> str:
        """Generate Section V: CONCLUSION"""

        name = beneficiary_info.get("name", "[Name]")
        field = beneficiary_info.get("field", "[field]")

        conclusion = f"""## V. CONCLUSION

The submitted evidence shows, by a preponderance of the evidence, that {name} is an alien of extraordinary ability in the field of {field}. {name} intends to continue their work in {field} in the United States. For all the reasons set forth herein, we respectfully request the approval of this petition.

Thank you for your time and for your consideration of this petition. Please do not hesitate to contact us if you require any further documentation.

Respectfully submitted,

[Attorney Signature]
[Attorney Name]
[Law Firm Name]"""

        return conclusion

    def _get_regulation_citation(self, criterion: str) -> str:
        """Get the appropriate CFR regulation citation"""

        citations = {
            "Membership in Outstanding Associations": "8 C.F.R. § 204.5(h)(3)(ii)",
            "Judging the Work of Others": "8 C.F.R. § 204.5(h)(3)(iv)",
            "Authorship of Scholarly Articles": "8 C.F.R. § 204.5(h)(3)(vi)",
            "Leading or Critical Role": "8 C.F.R. § 204.5(h)(3)(viii)",
            "High Salary / Remuneration": "8 C.F.R. § 204.5(h)(3)(ix)",
            "Original Contributions": "8 C.F.R. § 204.5(h)(3)(v)",
            "Awards / Prizes": "8 C.F.R. § 204.5(h)(3)(i)",
            "Published Material About You": "8 C.F.R. § 204.5(h)(3)(iii)",
            "Artistic Exhibitions / Showcases": "8 C.F.R. § 204.5(h)(3)(vii)",
            "Commercial Success in Performing Arts": "8 C.F.R. § 204.5(h)(3)(x)"
        }

        return citations.get(criterion, "8 C.F.R. § 204.5(h)(3)")
