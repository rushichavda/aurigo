"""
Claude API Integration for EB-1A Letter Polishing
"""
import anthropic
from typing import Optional, Dict, Any
from .base import BaseLLM
from ..config import get_settings


class ClaudeLLM(BaseLLM):
    """Claude Sonnet 4 integration for final letter polishing"""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.claude_api_key
        self.model_name = settings.claude_model

        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY not configured")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 4096,
        **kwargs
    ) -> str:
        """
        Generate text using Claude

        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Claude-specific parameters

        Returns:
            Generated text
        """
        try:
            message_params = {
                "model": self.model_name,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            if system_prompt:
                message_params["system"] = system_prompt

            response = self.client.messages.create(**message_params)

            return response.content[0].text

        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    async def polish_letter(
        self,
        draft_letter: str,
        focus_areas: Optional[str] = None
    ) -> str:
        """
        Polish a draft EB-1A attorney letter for final submission

        Args:
            draft_letter: The draft letter to polish
            focus_areas: Specific areas to improve (optional)

        Returns:
            Polished letter text
        """
        system_prompt = """You are an expert immigration attorney specializing in EB-1A petitions.
Your role is to polish and refine attorney letters to maximize persuasiveness while maintaining accuracy.

Focus on:
- Legal tone and formal language
- Persuasive argumentation
- Clear, compelling narratives
- Proper citation of regulations
- Professional structure and flow"""

        focus_hint = f"\n\nPay special attention to: {focus_areas}" if focus_areas else ""

        prompt = f"""Polish this EB-1A attorney support letter for final submission.

Improve:
- Legal language and tone
- Persuasive strength of arguments
- Clarity and professional flow
- Sentence structure and transitions
- Formal attorney-style writing

Maintain:
- All factual information and exhibit references
- Original structure (sections, subsections)
- All names, dates, numbers, and citations
- Exhibit numbering (A-1, B-2, etc.)
{focus_hint}

DRAFT LETTER:

{draft_letter}

Return ONLY the polished letter. Do not add explanations or comments."""

        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=8000
        )

    async def refine_section(
        self,
        section_text: str,
        section_type: str,
        instructions: Optional[str] = None
    ) -> str:
        """
        Refine a specific section of the letter

        Args:
            section_text: The section content
            section_type: Type of section (field_description, beneficiary_background, criterion, final_merits)
            instructions: Specific refinement instructions

        Returns:
            Refined section text
        """
        system_prompt = f"""You are refining the {section_type} section of an EB-1A attorney letter.
Maintain legal professionalism and persuasive strength."""

        instruct_hint = f"\n\nSpecific instructions: {instructions}" if instructions else ""

        prompt = f"""Refine this {section_type} section:

{section_text}

Improve clarity, persuasiveness, and legal tone while maintaining all facts.{instruct_hint}

Return ONLY the refined section text."""

        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=2000
        )
