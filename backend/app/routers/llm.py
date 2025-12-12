from fastapi import APIRouter, Depends, HTTPException
from ..schemas import ChatRequest, ChatResponse
from ..llm import LLMFactory, LLMRequest, Message
from ..auth import get_current_active_user
from ..models import User
from ..config import get_settings

router = APIRouter(prefix="/llm", tags=["llm"])
settings = get_settings()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Send a chat request to the LLM"""

    try:
        # Create LLM provider
        llm = LLMFactory.create_from_config(settings)

        # Convert request to LLM format
        llm_request = LLMRequest(
            messages=[Message(**msg.model_dump()) for msg in request.messages],
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        # Get response
        response = await llm.chat(llm_request)

        return ChatResponse(
            content=response.content,
            model=response.model,
            usage=response.usage
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-letter-intro")
async def generate_letter_intro(
    full_name: str,
    field: str,
    current_user: User = Depends(get_current_active_user)
):
    """Generate introduction paragraph for EB-1A letter"""

    try:
        llm = LLMFactory.create_from_config(settings)

        prompt = f"""You are an expert immigration attorney assistant. Write a professional introduction paragraph for an EB-1A (Extraordinary Ability) petition letter of support for {full_name}, who works in the field of {field}.

The introduction should:
- Establish the petitioner's extraordinary ability
- Mention their field of expertise
- Set a professional tone
- Be 3-4 sentences long

Write only the introduction paragraph, nothing else."""

        llm_request = LLMRequest(
            messages=[Message(role="user", content=prompt)],
            temperature=0.8,
            max_tokens=300
        )

        response = await llm.chat(llm_request)

        return {
            "introduction": response.content,
            "usage": response.usage
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
