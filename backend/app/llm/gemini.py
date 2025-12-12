"""
Gemini API Integration for EB-1A Letter Generation
"""
import google.generativeai as genai
from typing import Optional, Dict, Any, List
from .base import BaseLLM, LLMRequest, LLMResponse, Message
from ..config import get_settings


class GeminiLLM(BaseLLM):
    """Gemini 2.5 Flash integration for document analysis and letter generation"""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.model_name = settings.gemini_model

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def get_provider_name(self) -> str:
        """Get the provider name"""
        return "gemini"

    def validate_config(self) -> bool:
        """Validate that API key is configured"""
        return bool(self.api_key and len(self.api_key) > 0)

    async def chat(self, request: LLMRequest) -> LLMResponse:
        """
        Send a chat request to Gemini

        Args:
            request: LLM request with messages

        Returns:
            LLM response
        """
        try:
            # Convert messages to Gemini format
            # Gemini uses a simple list of parts, we'll combine system and user messages
            prompt_parts = []

            for msg in request.messages:
                if msg.role == "system":
                    prompt_parts.append(f"System: {msg.content}")
                elif msg.role == "user":
                    prompt_parts.append(f"User: {msg.content}")
                elif msg.role == "assistant":
                    prompt_parts.append(f"Assistant: {msg.content}")

            combined_prompt = "\n\n".join(prompt_parts)

            generation_config = {
                "temperature": request.temperature,
                "top_p": 0.95,
                "top_k": 40,
            }

            if request.max_tokens:
                generation_config["max_output_tokens"] = request.max_tokens

            response = self.model.generate_content(
                combined_prompt,
                generation_config=generation_config
            )

            return LLMResponse(
                content=response.text,
                model=self.model_name,
                usage=None,  # Gemini doesn't provide detailed usage in free tier
                finish_reason="stop"
            )

        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text using Gemini

        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Gemini-specific parameters

        Returns:
            Generated text
        """
        try:
            generation_config = {
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
            }

            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            # Combine system and user prompts
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            return response.text

        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    async def generate_with_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate JSON response using Gemini

        Args:
            prompt: User prompt requesting JSON output
            system_prompt: System instructions
            temperature: Lower temperature for structured output
            **kwargs: Additional parameters

        Returns:
            Parsed JSON dictionary
        """
        import json

        json_prompt = f"{prompt}\n\nRespond ONLY with valid JSON. No additional text."

        response_text = await self.generate(
            prompt=json_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            **kwargs
        )

        # Clean markdown code blocks if present
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        return json.loads(cleaned.strip())

    async def analyze_document(
        self,
        document_text: str,
        document_type: Optional[str] = None,
        extraction_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a document and extract structured information

        Args:
            document_text: The document content
            document_type: Type hint (certificate, letter, patent, etc.)
            extraction_instructions: Specific fields to extract

        Returns:
            Structured document analysis
        """
        system_prompt = """You are an expert legal document analyst specializing in EB-1A visa petitions.
Analyze documents carefully and extract relevant information for immigration purposes."""

        type_hint = f" The document type is: {document_type}." if document_type else ""
        extract_hint = f"\n\nExtract the following information: {extraction_instructions}" if extraction_instructions else ""

        prompt = f"""Analyze this document{type_hint}:

{document_text}

Extract and return a JSON object with:
- document_type: (certificate, letter, patent, salary_slip, award, publication, etc.)
- key_entities: (names, organizations, dates, amounts)
- main_facts: (achievements, roles, metrics, impact)
- eb1a_relevance: (which EB-1A criterion this supports)
- summary: (brief 2-3 sentence summary)
{extract_hint}"""

        return await self.generate_with_json(prompt, system_prompt, temperature=0.3)

    async def analyze_image_document(
        self,
        image_path: str,
        extraction_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze an image document (screenshot, scanned certificate, etc.)

        Args:
            image_path: Path to the image file
            extraction_instructions: Specific information to extract

        Returns:
            Structured document analysis
        """
        import PIL.Image

        try:
            img = PIL.Image.open(image_path)

            system_prompt = """You are analyzing a document image for an EB-1A visa petition.
Extract all visible text and relevant information."""

            extract_hint = f"\n\nFocus on extracting: {extraction_instructions}" if extraction_instructions else ""

            prompt = f"""Analyze this document image and extract:
- All visible text
- Document type (certificate, promotion announcement, screenshot, etc.)
- Key information (names, dates, positions, companies, achievements)
- EB-1A relevance
{extract_hint}

Return a JSON object with this information."""

            # Use vision model for image analysis
            vision_model = genai.GenerativeModel(self.model_name)
            response = vision_model.generate_content([prompt, img])

            # Parse response as JSON
            import json
            cleaned = response.text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            return json.loads(cleaned.strip())

        except Exception as e:
            raise Exception(f"Image analysis error: {str(e)}")

    async def identify_evidence_folder(
        self,
        folder_names: List[str]
    ) -> Dict[str, Any]:
        """
        Intelligently identify which folder contains evidence/documents

        Args:
            folder_names: List of folder names in the case directory

        Returns:
            Dict with:
            - evidence_folder: Name of the evidence folder (or None)
            - confidence: Float 0-1
            - reasoning: Why this folder was selected
        """
        system_prompt = """You are analyzing folder structure for an EB-1A visa case upload.
Identify which folder likely contains the organized evidence documents."""

        prompt = f"""Given these folder names in a case upload:
{folder_names}

Which folder most likely contains the organized evidence documents (criterion-based folders with supporting documents)?

Common patterns:
- Evidence, Evidences, Documents, Proofs (direct)
- Supporting Documents, Case Evidence, Exhibits
- Organized materials, Case Materials, Documentation

Return JSON:
{{
    "evidence_folder": "folder_name" or null,
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

If none look like evidence containers, return null with low confidence."""

        return await self.generate_with_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2
        )

    async def identify_case_overview(
        self,
        file_names: List[str]
    ) -> Dict[str, Any]:
        """
        Intelligently identify which file is the case overview/background document

        Args:
            file_names: List of file names in the case root directory

        Returns:
            Dict with:
            - case_overview_file: Name of the case overview file (or None)
            - confidence: Float 0-1
            - reasoning: Why this file was selected
        """
        system_prompt = """You are analyzing files for an EB-1A visa case upload.
Identify which file contains the beneficiary's background information."""

        prompt = f"""Given these file names in a case upload:
{file_names}

Which file most likely contains the case overview, beneficiary background, or client information?

Common patterns:
- Case_Overview, Case Overview, Overview, Background
- Client_Info, Client Information, Beneficiary_Info
- Case Summary, Client Background, Profile
- May have beneficiary name in filename

Return JSON:
{{
    "case_overview_file": "filename" or null,
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

If none look like overview documents, return null with low confidence."""

        return await self.generate_with_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2
        )

    async def map_folder_to_criterion(
        self,
        folder_name: str,
        sample_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Map a single folder to an EB-1A criterion with confidence scoring

        Args:
            folder_name: Name of the evidence folder
            sample_files: Optional list of file names in the folder for context

        Returns:
            Dict with:
            - criterion: Matched EB-1A criterion
            - confidence: Float 0-1
            - reasoning: Why this mapping was chosen
        """
        criteria_list = """
1. Awards / Prizes
2. Membership in Outstanding Associations
3. Published Material About You
4. Judging the Work of Others
5. Original Contributions
6. Authorship of Scholarly Articles
7. Artistic Exhibitions / Showcases
8. Leading or Critical Role
9. High Salary / Remuneration
10. Commercial Success in Performing Arts
11. Final Merits (supporting analysis)
"""

        files_context = ""
        if sample_files:
            files_context = f"\n\nSample files in this folder:\n{sample_files[:10]}"

        prompt = f"""Map this folder name to the most appropriate EB-1A criterion:

Folder name: "{folder_name}"{files_context}

Official EB-1A criteria:
{criteria_list}

Analyze the folder name and any file context to determine the best matching criterion.

Return JSON:
{{
    "criterion": "Full criterion name from list above",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of why this mapping makes sense"
}}

Use confidence scores:
- 0.9-1.0: Very clear match (e.g., "Awards" -> "Awards / Prizes")
- 0.7-0.9: Strong match with clear intent
- 0.5-0.7: Reasonable match but some ambiguity
- 0.3-0.5: Best guess with uncertainty
- 0.0-0.3: No clear match, assigned "Other"

If no criterion matches well, use "Other" as the criterion."""

        return await self.generate_with_json(
            prompt=prompt,
            system_prompt="You are an expert in EB-1A visa criteria classification.",
            temperature=0.2
        )

    async def batch_map_folders_to_criteria(
        self,
        folders_with_files: Dict[str, List[str]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Map multiple folders to criteria in a single LLM call (more efficient)

        Args:
            folders_with_files: Dict of {folder_name: [sample_file_names]}

        Returns:
            Dict of {folder_name: {criterion, confidence, reasoning}}
        """
        criteria_list = """
1. Awards / Prizes
2. Membership in Outstanding Associations
3. Published Material About You
4. Judging the Work of Others
5. Original Contributions
6. Authorship of Scholarly Articles
7. Artistic Exhibitions / Showcases
8. Leading or Critical Role
9. High Salary / Remuneration
10. Commercial Success in Performing Arts
11. Final Merits (supporting analysis)
"""

        folders_info = []
        for folder, files in folders_with_files.items():
            sample = files[:5] if len(files) > 5 else files
            folders_info.append(f"- {folder}: {sample}")

        prompt = f"""Map these evidence folders to EB-1A criteria:

Folders with sample files:
{chr(10).join(folders_info)}

Official EB-1A criteria:
{criteria_list}

Analyze each folder name and its contents to determine the best criterion match.

Return JSON mapping each folder to its criterion with confidence:
{{
    "folder_name": {{
        "criterion": "Full criterion name",
        "confidence": 0.0-1.0,
        "reasoning": "brief explanation"
    }},
    ...
}}

Confidence scoring:
- 0.9-1.0: Very clear match
- 0.7-0.9: Strong match
- 0.5-0.7: Reasonable match
- 0.3-0.5: Uncertain match
- 0.0-0.3: No match, use "Other"

If a folder doesn't clearly match any criterion, assign "Other"."""

        return await self.generate_with_json(
            prompt=prompt,
            system_prompt="You are an expert in EB-1A visa criteria classification.",
            temperature=0.2
        )
