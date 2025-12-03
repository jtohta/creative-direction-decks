"""
Question data model and validation rules.

Per data-model.md specification.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class QuestionType(Enum):
    """Types of questions supported in the questionnaire."""
    
    MULTIPLE_CHOICE = "multiple_choice"
    CHECKBOXES = "checkboxes"
    SHORT_ANSWER = "short_answer"
    PARAGRAPH = "paragraph"
    FILE_UPLOAD = "file_upload"


@dataclass
class ValidationRule:
    """
    Validation configuration for a question.
    
    Attributes:
        required: Whether the question must be answered
        min_length: Minimum character length for text responses
        max_length: Maximum character length for text responses
        min_selections: Minimum selections for checkbox questions
        max_selections: Maximum selections for checkbox questions
        allowed_file_types: List of allowed MIME types for file uploads
        max_file_size_mb: Maximum size per file in MB
        max_total_size_mb: Maximum total size for all files in MB
        min_files: Minimum number of files for file upload questions
        max_files: Maximum number of files for file upload questions
    """
    
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_selections: Optional[int] = None
    max_selections: Optional[int] = None
    allowed_file_types: Optional[list[str]] = None
    max_file_size_mb: Optional[int] = None
    max_total_size_mb: Optional[int] = None
    min_files: Optional[int] = None
    max_files: Optional[int] = None


@dataclass
class Question:
    """
    Question definition for the questionnaire.
    
    Attributes:
        id: Unique identifier (e.g., "Q1", "Q2")
        text: Question text displayed to user
        type: Type of question (determines input widget)
        description: Optional helper text/context for the question
        options: List of options for multiple_choice/checkboxes questions
        validation: Validation rules for this question
    """
    
    id: str
    text: str
    type: QuestionType
    description: Optional[str] = None
    options: Optional[list[str]] = None
    validation: Optional[ValidationRule] = None
    
    def __post_init__(self):
        """Initialize validation rule if not provided."""
        if self.validation is None:
            self.validation = ValidationRule()

