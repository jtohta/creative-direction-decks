"""
Response data model for user answers.

Per data-model.md specification.
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, Optional


@dataclass
class FileReference:
    """
    Reference to an uploaded file in Cloudflare R2.
    
    Attributes:
        original_filename: Original filename from user's upload
        r2_key: Path in R2 bucket (e.g., "session_id/timestamp_filename.jpg")
        r2_url: Full URL to access file from R2
        file_size_bytes: Size of file in bytes
        mime_type: MIME type (e.g., "image/jpeg")
        upload_timestamp: When the file was uploaded to R2
    """
    
    original_filename: str
    r2_key: str
    r2_url: str
    file_size_bytes: int
    mime_type: str
    upload_timestamp: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "original_filename": self.original_filename,
            "r2_key": self.r2_key,
            "r2_url": self.r2_url,
            "file_size_bytes": self.file_size_bytes,
            "mime_type": self.mime_type,
            "upload_timestamp": self.upload_timestamp.isoformat(),
        }


@dataclass
class Response:
    """
    User's answer to a specific question.
    
    Attributes:
        question_id: ID of the question this response answers
        answer_value: The actual answer (type varies by question type)
        timestamp: When the answer was recorded
        validation_status: Whether the response passed validation
        file_references: List of FileReference objects for file upload questions
    
    Answer value types by question type:
        - multiple_choice: str (single selection)
        - checkboxes: list[str] (multiple selections)
        - short_answer: str (single line text)
        - paragraph: str (multi-line text)
        - file_upload: str (descriptive text like "15 files uploaded")
    """
    
    question_id: str
    answer_value: Any
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    validation_status: bool = False
    file_references: list[FileReference] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "question_id": self.question_id,
            "answer_value": self.answer_value,
            "timestamp": self.timestamp.isoformat(),
            "validation_status": self.validation_status,
            "file_references": [f.to_dict() for f in self.file_references],
        }

