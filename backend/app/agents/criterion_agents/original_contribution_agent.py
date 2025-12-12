"""
Original Contribution Agent
Analyzes evidence for "Original Contributions of Major Significance"
"""
from typing import Dict, List
import json
import logging
from pathlib import Path

from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)


class OriginalContributionAgent(BaseAgent):
    """
    Specialized agent for Original Contributions criterion

    Focus Areas:
    - Research publications and citations
    - Patents and inventions
    - Novel methodologies/techniques
    - Industry adoption of contributions
    - Expert testimonials about impact
    - Awards for contributions
    - Adoption by other researchers/companies

    Expected Documents:
    - Research papers
    - Patents
    - Citation reports
    - Impact letters
    - Adoption evidence
    - Technology transfer agreements
    """

    def __init__(self, llm_provider: str = "gemini", api_key: str = None):
        super().__init__(
            agent_id="original_contribution_agent",
            criterion="Original Contributions of Major Significance",
            llm_provider=llm_provider,
            api_key=api_key
        )

    async def _analyze_documents(self):
        """Analyze documents for original contribution evidence"""
        logger.info(f"[{self.agent_id}] Analyzing {len(self.documents)} documents")

        for i, doc in enumerate(self.documents):
            try:
                # Prepare document context
                doc_context = self._prepare_document_context(doc)

                # Analyze with LLM
                analysis_prompt = self._create_analysis_prompt(doc_context)
                analysis_result = await self.invoke_llm(
                    prompt=analysis_prompt,
                    system_prompt="You are an expert immigration attorney analyzing EB-1A evidence for the Original Contributions criterion."
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
            for table in tables[:3]:
                context += f"{table}\n"

        return context

    def _create_analysis_prompt(self, doc_context: str) -> str:
        """Create analysis prompt for LLM"""
        return f"""Analyze this document for evidence of ORIGINAL CONTRIBUTIONS OF MAJOR SIGNIFICANCE to the field.

{doc_context}

Please identify and extract:

1. **Document Type**: What type of document is this?
   (e.g., research paper, patent, citation report, impact letter, adoption evidence)

2. **Contribution Description**:
   - What is the original contribution?
   - Field/domain of contribution
   - Innovation or novelty aspect
   - Technical/scientific advancement

3. **Publication/Patent Details** (if applicable):
   - Title
   - Authors/inventors
   - Publication venue/patent office
   - Publication date
   - Journal impact factor or patent classification

4. **Impact Evidence**:
   - Citation count
   - Download statistics
   - Adoption by others
   - Commercial implementation
   - Industry standards influenced
   - Awards received for contribution

5. **Significance Indicators**:
   - Testimonials from experts
   - Comparative advantage over prior work
   - Problems solved
   - Scale of impact (number of users, companies, researchers)
   - Geographic reach

6. **Quantitative Metrics**:
   - Citations
   - Downloads
   - Users
   - Revenue generated
   - Patents citing this work
   - Follow-on research

7. **Key Facts**: List 3-5 most important facts that demonstrate major significance

8. **Strength Assessment**: Rate the strength of this evidence (Strong/Moderate/Weak) and explain why

Provide your analysis in JSON format:
{{
    "document_type": "...",
    "contribution": {{...}},
    "publication_details": {{...}},
    "impact": {{...}},
    "significance": {{...}},
    "metrics": {{...}},
    "key_facts": [...],
    "strength": "...",
    "explanation": "..."
}}"""

    def _parse_analysis(self, analysis_text: str) -> Dict:
        """Parse LLM analysis response"""
        try:
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

            # Extract contribution description
            contribution = analysis.get("contribution", {})
            if contribution:
                contrib_desc = contribution.get("what_is_contribution")
                if contrib_desc:
                    all_facts.append(f"Contribution: {contrib_desc}")

            # Extract impact metrics
            metrics = analysis.get("metrics", {})
            if metrics:
                for key, value in metrics.items():
                    if value and str(value).strip():
                        all_facts.append(f"{key}: {value}")

        # Deduplicate and store
        self.extracted_facts = list(set(all_facts))
        logger.info(f"[{self.agent_id}] Extracted {len(self.extracted_facts)} key facts")

    def _generate_exhibit_title(self, document: Dict) -> str:
        """Generate descriptive title for exhibit"""
        analysis = document.get("analysis", {})
        doc_type = analysis.get("document_type", "Document")

        # Try to get publication/patent title
        pub_details = analysis.get("publication_details", {})
        title = pub_details.get("title")

        if title:
            # Truncate long titles
            if len(title) > 80:
                title = title[:77] + "..."
            return f"{doc_type}: {title}"
        else:
            file_name = Path(document["file_name"]).stem
            return f"{doc_type} - {file_name}"

    def _generate_exhibit_description(self, document: Dict) -> str:
        """Generate detailed description for exhibit"""
        analysis = document.get("analysis", {})

        desc_parts = []

        # Document type
        doc_type = analysis.get("document_type", "Document")

        # Contribution description
        contribution = analysis.get("contribution", {})
        contrib_desc = contribution.get("what_is_contribution")
        if contrib_desc:
            desc_parts.append(f"{doc_type} describing {contrib_desc}")
        else:
            desc_parts.append(doc_type)

        # Add impact metrics
        metrics = analysis.get("metrics", {})
        if metrics:
            citations = metrics.get("citations")
            if citations:
                desc_parts.append(f"with {citations} citations")

        # Add significance
        significance = analysis.get("significance", {})
        scale = significance.get("scale_of_impact")
        if scale:
            desc_parts.append(f"impacting {scale}")

        return " ".join(desc_parts)

    def _extract_document_key_points(self, document: Dict) -> List[str]:
        """Extract key points from document"""
        analysis = document.get("analysis", {})
        return analysis.get("key_facts", [])

    async def _generate_letter_section(self):
        """Generate attorney letter section for Original Contributions criterion"""
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

        # Extract aggregated metrics
        total_citations = 0
        contributions = []
        impacts = []

        for doc in self.documents:
            analysis = doc.get("analysis", {})

            # Contribution
            contribution = analysis.get("contribution", {})
            if contribution:
                contributions.append(contribution)

            # Metrics
            metrics = analysis.get("metrics", {})
            if metrics:
                citations = metrics.get("citations")
                if citations and str(citations).isdigit():
                    total_citations += int(citations)

            # Impact
            impact = analysis.get("impact", {})
            if impact:
                impacts.append(impact)

        context["total_citations"] = total_citations
        context["contributions"] = contributions
        context["impacts"] = impacts

        return context

    def _create_letter_prompt(self, context: Dict) -> str:
        """Create prompt for letter generation"""
        exhibits_text = "\n".join([
            f"- Exhibit {ex['id']}: {ex['title']}"
            for ex in context["exhibits"]
        ])

        return f"""Write a professional attorney letter section for the EB-1A criterion: "Original Contributions of Major Significance to the Field".

Context:
- Criterion: {context['criterion']}
- Number of supporting documents: {context['total_documents']}
- Total citations (aggregate): {context.get('total_citations', 'N/A')}

Key Facts to Address:
{chr(10).join([f"- {fact}" for fact in context['key_facts'][:10]])}

Available Exhibits:
{exhibits_text}

Requirements:
1. Write in professional legal tone appropriate for USCIS petition
2. Start with a strong introduction explaining this criterion
3. Reference exhibits using inline citations (e.g., "As demonstrated in Exhibit D-5...")
4. Emphasize the ORIGINAL and NOVEL nature of contributions
5. Provide specific evidence of MAJOR SIGNIFICANCE (citations, adoption, impact)
6. Use quantitative metrics where available
7. Connect evidence to "extraordinary ability" standard
8. Explain how contributions advanced the field
9. Structure with clear paragraphs and logical flow

Length: 2-3 paragraphs (approximately 300-500 words)

Write the letter section now:"""

    async def _calculate_confidence(self) -> float:
        """Calculate confidence score for original contribution evidence"""
        if not self.documents:
            return 0.0

        scores = []

        # 1. Number of documents
        doc_count_score = min(len(self.documents) / 6, 1.0)
        scores.append(doc_count_score * 0.3)

        # 2. Citation evidence
        has_citations = any(
            doc.get("analysis", {}).get("metrics", {}).get("citations")
            for doc in self.documents
        )
        scores.append(0.25 if has_citations else 0.0)

        # 3. Evidence strength
        strong_count = sum(
            1 for doc in self.documents
            if doc.get("analysis", {}).get("strength") == "Strong"
        )
        strength_score = min(strong_count / len(self.documents), 1.0) if self.documents else 0
        scores.append(strength_score * 0.25)

        # 4. Key facts extracted
        facts_score = min(len(self.extracted_facts) / 8, 1.0)
        scores.append(facts_score * 0.2)

        return sum(scores)
