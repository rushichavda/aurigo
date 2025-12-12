"""
Information Extractor Service
Extracts structured information from parsed documents using Gemini
"""
from typing import Dict, List, Optional, Any
from .document_parser import DocumentParser
from ..llm.gemini import GeminiLLM


class InformationExtractor:
    """
    Extracts and structures information from evidence documents
    Uses Gemini for intelligent document understanding
    """

    def __init__(self):
        self.parser = DocumentParser()
        self.llm = GeminiLLM()

    async def extract_from_document(
        self,
        file_path: str,
        criterion: Optional[str] = None,
        document_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured information from a single document

        Args:
            file_path: Path to the document
            criterion: EB-1A criterion this document supports
            document_hint: Hint about document type (from filename)

        Returns:
            Extracted information dictionary
        """
        # First, parse the document
        parsed = self.parser.parse_document(file_path)

        if not parsed["success"]:
            return {
                "success": False,
                "error": parsed["error"],
                "file_path": file_path
            }

        # Prepare extraction instructions based on criterion
        extraction_instructions = self._get_extraction_instructions(criterion)

        # Use LLM to analyze the document
        try:
            # Handle images separately
            if parsed["format"] == "IMAGE":
                analysis = await self.llm.analyze_image_document(
                    file_path,
                    extraction_instructions
                )
            else:
                # Analyze text document
                analysis = await self.llm.analyze_document(
                    document_text=parsed["text"],
                    document_type=document_hint,
                    extraction_instructions=extraction_instructions
                )

            # Combine parsed data with LLM analysis
            result = {
                "success": True,
                "file_path": file_path,
                "criterion": criterion,
                "parsed_content": {
                    "text": parsed["text"],
                    "tables": parsed["tables"],
                    "metadata": parsed["metadata"]
                },
                "extracted_info": analysis,
                "document_type": analysis.get("document_type", "unknown"),
                "key_facts": analysis.get("main_facts", []),
                "entities": analysis.get("key_entities", {}),
                "summary": analysis.get("summary", "")
            }

            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"Extraction failed: {str(e)}",
                "file_path": file_path,
                "parsed_content": parsed
            }

    async def extract_from_folder(
        self,
        folder_path: str,
        criterion: str
    ) -> List[Dict[str, Any]]:
        """
        Extract information from all documents in a criterion folder

        Args:
            folder_path: Path to the criterion folder
            criterion: The EB-1A criterion name

        Returns:
            List of extraction results
        """
        # Parse all documents in folder
        parsed_docs = self.parser.extract_from_folder(
            folder_path,
            recursive=False
        )

        results = []

        for doc in parsed_docs:
            if not doc["success"]:
                results.append(doc)
                continue

            # Extract document type hint from filename
            filename = doc["metadata"]["filename"]
            document_hint = self._infer_document_type(filename)

            # Extract information
            extracted = await self.extract_from_document(
                file_path=doc["file_path"],
                criterion=criterion,
                document_hint=document_hint
            )

            results.append(extracted)

        return results

    async def extract_case_overview(self, file_path: str) -> Dict[str, Any]:
        """
        Extract beneficiary information from case overview document

        Args:
            file_path: Path to case overview document

        Returns:
            Extracted beneficiary information
        """
        parsed = self.parser.parse_document(file_path)

        if not parsed["success"]:
            return {"success": False, "error": parsed["error"]}

        # Specific instructions for case overview
        instructions = """
Extract the following information about the beneficiary:
- Full name
- Current position/title
- Current company/organization
- Field of expertise
- Education (degrees, universities, years)
- Career history (positions, companies, dates)
- Key achievements
- Nationality/country of origin
- Any other relevant background information
"""

        try:
            analysis = await self.llm.analyze_document(
                document_text=parsed["text"],
                document_type="case_overview",
                extraction_instructions=instructions
            )

            return {
                "success": True,
                "beneficiary_info": analysis,
                "full_text": parsed["text"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "full_text": parsed["text"]
            }

    def _get_extraction_instructions(self, criterion: Optional[str]) -> str:
        """
        Get criterion-specific extraction instructions

        Args:
            criterion: EB-1A criterion

        Returns:
            Extraction instructions for the LLM
        """
        instructions = {
            "Awards / Prizes": """
Extract:
- Award/prize name
- Awarding organization
- Date received
- Level (national/international)
- Criteria for selection
- Number of recipients/selectivity
- Significance/prestige indicators
""",
            "Membership in Outstanding Associations": """
Extract:
- Association/organization name
- Membership type/level (Fellow, Member, etc.)
- Date joined
- Selection criteria
- Membership requirements
- Prestige indicators
- Number of members/selectivity
""",
            "Published Material About You": """
Extract:
- Publication name
- Article title
- Author(s)
- Publication date
- Circulation/reach
- Topics covered about the beneficiary
- Achievements highlighted
""",
            "Judging the Work of Others": """
Extract:
- Conference/journal/organization name
- Role (reviewer, judge, session chair, etc.)
- Number of papers/works reviewed
- Date(s)
- Selection process
- Scope (national/international)
""",
            "Original Contributions": """
Extract:
- Contribution/innovation description
- Impact metrics (revenue, users, efficiency gains)
- Organizations/companies affected
- Dates
- Recognition received
- Testimonials/statements from others
""",
            "Authorship of Scholarly Articles": """
Extract:
- Article/paper title
- Publication name (journal/conference)
- Publication date
- Co-authors
- Citations (if mentioned)
- Impact factor/ranking
- Topics/field
""",
            "Leading or Critical Role": """
Extract:
- Position/title
- Company/organization name
- Dates (start-end)
- Team size/reporting structure
- Key responsibilities
- Achievements/impact
- Promotion history
""",
            "High Salary / Remuneration": """
Extract:
- Salary/compensation amount
- Currency
- Time period (annual, monthly)
- Bonuses/stock options
- Total compensation
- Company/employer
- Position/title
""",
            "Final Merits": """
Extract:
- Supporting evidence type
- Organizations/activities involved
- Additional achievements
- Industry recognition
- Community impact
- Future work plans
"""
        }

        return instructions.get(criterion, "Extract all relevant information from this document.")

    def _infer_document_type(self, filename: str) -> str:
        """
        Infer document type from filename

        Args:
            filename: Name of the file

        Returns:
            Document type hint
        """
        filename_lower = filename.lower()

        type_keywords = {
            "certificate": "certificate",
            "award": "award",
            "letter": "letter",
            "recommendation": "letter_of_recommendation",
            "lor": "letter_of_recommendation",
            "patent": "patent",
            "publication": "publication",
            "paper": "research_paper",
            "salary": "salary_slip",
            "compensation": "compensation",
            "pay": "salary_slip",
            "w2": "tax_document",
            "w-2": "tax_document",
            "promotion": "promotion_announcement",
            "membership": "membership_certificate",
            "review": "review_documentation",
            "article": "article",
            "press": "press_coverage"
        }

        for keyword, doc_type in type_keywords.items():
            if keyword in filename_lower:
                return doc_type

        return "unknown"

    async def aggregate_criterion_data(
        self,
        extracted_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate extracted information for a criterion into a summary

        Args:
            extracted_documents: List of extracted document data

        Returns:
            Aggregated summary for the criterion
        """
        # Collect all key facts
        all_facts = []
        all_entities = {}
        all_summaries = []

        for doc in extracted_documents:
            if doc.get("success"):
                all_facts.extend(doc.get("key_facts", []))

                # Merge entities
                entities = doc.get("entities", {})
                for key, value in entities.items():
                    if key not in all_entities:
                        all_entities[key] = []
                    if isinstance(value, list):
                        all_entities[key].extend(value)
                    else:
                        all_entities[key].append(value)

                summary = doc.get("summary", "")
                if summary:
                    all_summaries.append(summary)

        # Use LLM to create cohesive summary
        try:
            prompt = f"""
Based on the following document summaries and facts, create a cohesive narrative summary:

Document Summaries:
{chr(10).join(f'- {s}' for s in all_summaries)}

Key Facts:
{chr(10).join(f'- {f}' for f in all_facts if isinstance(f, str))}

Create a comprehensive 2-3 paragraph summary highlighting the most important achievements and evidence.
"""

            cohesive_summary = await self.llm.generate(
                prompt=prompt,
                system_prompt="You are summarizing evidence for an EB-1A visa petition.",
                temperature=0.5
            )

            return {
                "summary": cohesive_summary,
                "key_facts": all_facts,
                "entities": all_entities,
                "document_count": len(extracted_documents)
            }

        except Exception as e:
            return {
                "summary": " ".join(all_summaries),
                "key_facts": all_facts,
                "entities": all_entities,
                "document_count": len(extracted_documents),
                "error": str(e)
            }
