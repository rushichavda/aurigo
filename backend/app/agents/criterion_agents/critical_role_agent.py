"""
Critical Role Agent
Analyzes evidence for "Leading or Critical Role in Distinguished Organizations"
"""
from typing import Dict, List
import json
import logging
from pathlib import Path

from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CriticalRoleAgent(BaseAgent):
    """
    Specialized agent for Critical Role criterion

    Focus Areas:
    - Job titles and seniority level
    - Organization reputation/prestige
    - Scope of responsibility
    - Impact on organization
    - Leadership evidence
    - Organizational charts
    - Recommendation letters from executives

    Expected Documents:
    - Offer letters
    - Employment letters
    - Organizational charts
    - Job descriptions
    - Performance reviews
    - Recommendation letters
    """

    def __init__(self, llm_provider: str = "gemini", api_key: str = None):
        super().__init__(
            agent_id="critical_role_agent",
            criterion="Leading or Critical Role",
            llm_provider=llm_provider,
            api_key=api_key
        )

    async def _analyze_documents(self):
        """Analyze documents for critical role evidence"""
        logger.info(f"[{self.agent_id}] Analyzing {len(self.documents)} documents")

        for i, doc in enumerate(self.documents):
            try:
                # Prepare document context
                doc_context = self._prepare_document_context(doc)

                # Analyze with LLM
                analysis_prompt = self._create_analysis_prompt(doc_context)
                analysis_result = await self.invoke_llm(
                    prompt=analysis_prompt,
                    system_prompt="You are an expert immigration attorney analyzing EB-1A evidence for the Critical Role criterion."
                )

                # Parse and store analysis
                doc["analysis"] = self._parse_analysis(analysis_result)

                # Update progress
                progress = 30 + int((i + 1) / len(self.documents) * 20)
                self.state.update_progress(progress, f"Analyzing documents ({i+1}/{len(self.documents)})")

            except Exception as e:
                logger.error(f"[{self.agent_id}] Error analyzing {doc['file_name']}: {e}")

    def _prepare_document_context(self, doc: Dict) -> str:
        """Prepare document context for LLM analysis"""
        text = doc.get("text", "")[:5000]  # Limit to first 5000 chars
        tables = doc.get("tables", [])

        context = f"Document: {doc['file_name']}\n\n"
        context += f"Content:\n{text}\n\n"

        if tables:
            context += f"Tables: {len(tables)} table(s) found\n"
            for table in tables[:3]:  # Include first 3 tables
                context += f"{table}\n"

        return context

    def _create_analysis_prompt(self, doc_context: str) -> str:
        """Create analysis prompt for LLM"""
        return f"""Analyze this document for evidence of a LEADING OR CRITICAL ROLE in a distinguished organization.

{doc_context}

Please identify and extract:

1. **Document Type**: What type of document is this?
   (e.g., employment letter, offer letter, org chart, recommendation letter, job description)

2. **Organization Information**:
   - Organization name
   - Organization reputation/prestige indicators
   - Organization size and reach
   - Industry standing

3. **Position Details**:
   - Job title
   - Seniority level
   - Department/division
   - Direct reports (if any)
   - Reporting line (reports to whom)

4. **Scope of Responsibility**:
   - Key responsibilities
   - Budget authority
   - Team size
   - Geographic scope
   - Products/services impacted

5. **Impact Evidence**:
   - Measurable impacts
   - Strategic contributions
   - Revenue/user impact
   - Innovation/transformation led

6. **Leadership Indicators**:
   - Decision-making authority
   - Strategic planning involvement
   - Cross-functional leadership
   - External representation

7. **Key Facts**: List 3-5 most important facts that demonstrate critical role

8. **Strength Assessment**: Rate the strength of this evidence (Strong/Moderate/Weak) and explain why

Provide your analysis in JSON format:
{{
    "document_type": "...",
    "organization": {{...}},
    "position": {{...}},
    "scope": {{...}},
    "impact": {{...}},
    "leadership": {{...}},
    "key_facts": [...],
    "strength": "...",
    "explanation": "..."
}}"""

    def _parse_analysis(self, analysis_text: str) -> Dict:
        """Parse LLM analysis response"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"raw_analysis": analysis_text}
        except Exception as e:
            logger.error(f"Error parsing analysis: {e}")
            return {"raw_analysis": analysis_text}

    async def _extract_facts(self):
        """Extract key facts from analyzed documents"""
        logger.info(f"[{self.agent_id}] Extracting key facts")

        all_facts = []

        for doc in self.documents:
            analysis = doc.get("analysis", {})

            # Extract key facts from analysis
            key_facts = analysis.get("key_facts", [])
            all_facts.extend(key_facts)

            # Extract position details
            position = analysis.get("position", {})
            if position:
                job_title = position.get("job_title")
                if job_title:
                    all_facts.append(f"Served as {job_title}")

            # Extract impact evidence
            impact = analysis.get("impact", {})
            if impact:
                measurable = impact.get("measurable_impacts", [])
                all_facts.extend(measurable)

        # Deduplicate and store
        self.extracted_facts = list(set(all_facts))
        logger.info(f"[{self.agent_id}] Extracted {len(self.extracted_facts)} key facts")

    def _generate_exhibit_title(self, document: Dict) -> str:
        """Generate descriptive title for exhibit"""
        analysis = document.get("analysis", {})
        doc_type = analysis.get("document_type", "Document")
        organization = analysis.get("organization", {}).get("organization_name", "")

        file_name = Path(document["file_name"]).stem

        if organization:
            return f"{doc_type} - {organization}"
        else:
            return f"{doc_type} - {file_name}"

    def _generate_exhibit_description(self, document: Dict) -> str:
        """Generate detailed description for exhibit"""
        analysis = document.get("analysis", {})

        desc_parts = []

        # Document type
        doc_type = analysis.get("document_type", "Document")
        desc_parts.append(f"{doc_type}")

        # Organization
        org_name = analysis.get("organization", {}).get("organization_name")
        if org_name:
            desc_parts.append(f"from {org_name}")

        # Position
        job_title = analysis.get("position", {}).get("job_title")
        if job_title:
            desc_parts.append(f"confirming role as {job_title}")

        # Key responsibility
        responsibilities = analysis.get("scope", {}).get("key_responsibilities", [])
        if responsibilities:
            desc_parts.append(f"with responsibilities including {responsibilities[0]}")

        return " ".join(desc_parts)

    def _extract_document_key_points(self, document: Dict) -> List[str]:
        """Extract key points from document"""
        analysis = document.get("analysis", {})
        return analysis.get("key_facts", [])

    async def _generate_letter_section(self):
        """Generate attorney letter section for Critical Role criterion"""
        logger.info(f"[{self.agent_id}] Generating letter section")

        # Prepare context for letter generation
        context = self._prepare_letter_context()

        # Generate letter section with LLM
        letter_prompt = self._create_letter_prompt(context)
        self.letter_section = await self.invoke_llm(
            prompt=letter_prompt,
            system_prompt="You are an experienced immigration attorney writing an EB-1A petition letter. Write in a professional, persuasive legal tone."
        )

        logger.info(f"[{self.agent_id}] Generated letter section ({len(self.letter_section)} chars)")

    def _prepare_letter_context(self) -> Dict:
        """Prepare context for letter generation"""
        context = {
            "criterion": self.criterion,
            "total_documents": len(self.documents),
            "key_facts": self.extracted_facts,
            "exhibits": []
        }

        # Add exhibit information
        for exhibit in self.exhibits:
            context["exhibits"].append({
                "id": exhibit.exhibit_id,
                "title": exhibit.title,
                "description": exhibit.description,
                "key_points": exhibit.key_points
            })

        # Extract aggregated information
        organizations = []
        positions = []
        impacts = []

        for doc in self.documents:
            analysis = doc.get("analysis", {})

            org_name = analysis.get("organization", {}).get("organization_name")
            if org_name:
                organizations.append(org_name)

            position = analysis.get("position", {})
            if position:
                positions.append(position)

            impact = analysis.get("impact", {})
            if impact:
                impacts.append(impact)

        context["organizations"] = list(set(organizations))
        context["positions"] = positions
        context["impacts"] = impacts

        return context

    def _create_letter_prompt(self, context: Dict) -> str:
        """Create prompt for letter generation"""
        exhibits_text = "\n".join([
            f"- Exhibit {ex['id']}: {ex['title']}"
            for ex in context["exhibits"]
        ])

        return f"""Write a professional attorney letter section for the EB-1A criterion: "Leading or Critical Role in Distinguished Organizations".

Context:
- Criterion: {context['criterion']}
- Number of supporting documents: {context['total_documents']}
- Organizations: {', '.join(context['organizations'])}

Key Facts to Address:
{chr(10).join([f"- {fact}" for fact in context['key_facts'][:10]])}

Available Exhibits:
{exhibits_text}

Requirements:
1. Write in professional legal tone appropriate for USCIS petition
2. Start with a strong introduction explaining this criterion
3. Reference exhibits using inline citations (e.g., "As evidenced in Exhibit C-3...")
4. Provide specific examples with measurable impacts
5. Emphasize the critical nature of the roles and organizational prestige
6. Connect evidence to "extraordinary ability" standard
7. Use persuasive language that demonstrates why this criterion is met
8. Structure with clear paragraphs and logical flow

Length: 2-3 paragraphs (approximately 300-500 words)

Write the letter section now:"""

    async def _calculate_confidence(self) -> float:
        """Calculate confidence score for critical role evidence"""
        if not self.documents:
            return 0.0

        # Factors for confidence
        scores = []

        # 1. Number of documents (more is better)
        doc_count_score = min(len(self.documents) / 8, 1.0)
        scores.append(doc_count_score * 0.3)

        # 2. Document types (variety is good)
        doc_types = set()
        for doc in self.documents:
            doc_type = doc.get("analysis", {}).get("document_type", "")
            if doc_type:
                doc_types.add(doc_type)

        doc_variety_score = min(len(doc_types) / 4, 1.0)
        scores.append(doc_variety_score * 0.2)

        # 3. Evidence strength
        strong_count = sum(
            1 for doc in self.documents
            if doc.get("analysis", {}).get("strength") == "Strong"
        )
        strength_score = min(strong_count / len(self.documents), 1.0) if self.documents else 0
        scores.append(strength_score * 0.3)

        # 4. Key facts extracted
        facts_score = min(len(self.extracted_facts) / 10, 1.0)
        scores.append(facts_score * 0.2)

        return sum(scores)
