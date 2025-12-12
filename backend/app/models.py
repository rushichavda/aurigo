from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    cases = relationship("Case", back_populates="owner")


class Case(Base):
    """EB-1A Case - main entity for case processing"""
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Case identification
    case_name = Column(String, nullable=False)  # Beneficiary name
    field = Column(String)  # Field of expertise (Cloud Engineering, etc.)

    # Processing status
    status = Column(String, default="uploaded")  # uploaded, processing, completed, failed
    current_step = Column(String)  # parsing, extracting, generating, etc.
    progress = Column(Integer, default=0)  # 0-100

    # Folder paths
    upload_path = Column(String)  # Original upload location
    workspace_path = Column(String)  # Processing workspace
    case_overview_path = Column(String)  # Path to case overview document

    # Criteria matched
    criteria_matched = Column(JSON)  # List of matched criteria
    num_criteria = Column(Integer, default=0)

    # Metadata
    total_documents = Column(Integer, default=0)
    total_exhibits = Column(Integer, default=0)

    # Output paths
    letter_path = Column(String)  # Generated letter DOCX path
    exhibit_index_path = Column(String)  # Exhibit index DOCX path
    metadata_path = Column(String)  # JSON metadata path

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    owner = relationship("User", back_populates="cases")
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    exhibits = relationship("CaseExhibit", back_populates="case", cascade="all, delete-orphan")
    letters = relationship("GeneratedLetter", back_populates="case", cascade="all, delete-orphan")


class Document(Base):
    """Individual document within a case"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)

    # Document identification
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String)  # pdf, docx, jpg, etc.
    file_size = Column(Integer)  # bytes

    # Categorization
    criterion = Column(String)  # Which EB-1A criterion this supports
    document_type = Column(String)  # certificate, letter, patent, etc.

    # Parsed content
    parsed_text = Column(Text)  # Full extracted text
    parsed_tables = Column(JSON)  # Extracted tables
    parsed_metadata = Column(JSON)  # Metadata from Docling

    # Extracted information
    extracted_info = Column(JSON)  # Structured data from Gemini
    key_facts = Column(JSON)  # List of key facts
    entities = Column(JSON)  # Named entities
    summary = Column(Text)  # Document summary

    # Exhibit assignment
    exhibit_id = Column(String)  # e.g., "C-1", "D-2"

    # Processing status
    parsed = Column(Boolean, default=False)
    extracted = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    case = relationship("Case", back_populates="documents")


class CaseExhibit(Base):
    """Exhibit assignments for a case"""
    __tablename__ = "case_exhibits"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)

    # Exhibit identification
    exhibit_id = Column(String, nullable=False)  # e.g., "A-1", "B-2"
    group_letter = Column(String, nullable=False)  # e.g., "A", "B"
    group_title = Column(String, nullable=False)  # Group description
    number = Column(Integer, nullable=False)  # Number within group

    # Exhibit details
    title = Column(String, nullable=False)
    description = Column(Text)

    # Associated document
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    criterion = Column(String)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    case = relationship("Case", back_populates="exhibits")


class GeneratedLetter(Base):
    """Generated attorney letters for a case"""
    __tablename__ = "generated_letters"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)

    # Letter content
    content = Column(Text, nullable=False)  # Full letter text
    sections = Column(JSON)  # Breakdown by section

    # Version tracking
    version = Column(Integer, default=1)
    is_polished = Column(Boolean, default=False)  # Whether Claude polished

    # Output
    docx_path = Column(String)  # Path to DOCX file

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    case = relationship("Case", back_populates="letters")


class EB1ACriteria(Base):
    """Reference table for EB-1A criteria"""
    __tablename__ = "eb1a_criteria"

    id = Column(Integer, primary_key=True, index=True)
    criteria_number = Column(Integer, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    regulation = Column(String)  # CFR citation
    examples = Column(Text)  # JSON or comma-separated examples
