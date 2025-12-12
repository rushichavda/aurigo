from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Letter Schemas
class LetterBase(BaseModel):
    title: str
    content: Optional[str] = None


class LetterCreate(LetterBase):
    pass


class LetterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None


class LetterResponse(LetterBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Exhibit Schemas
class ExhibitBase(BaseModel):
    criteria_number: int
    title: str
    description: Optional[str] = None


class ExhibitCreate(ExhibitBase):
    letter_id: Optional[int] = None


class ExhibitResponse(ExhibitBase):
    id: int
    user_id: int
    letter_id: Optional[int]
    document_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# LLM Schemas
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None


class ChatResponse(BaseModel):
    content: str
    model: str
    usage: Optional[dict] = None
