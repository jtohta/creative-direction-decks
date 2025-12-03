"""
Input validation service for questionnaire responses.

Per contracts and data-model requirements.
"""

import re
from typing import Any, Optional
from src.models import Question, QuestionType, ValidationRule


def validate_response(question: Question, answer_value: Any) -> tuple[bool, Optional[str]]:
    """
    Validate a user's response to a question.
    
    Args:
        question: Question definition with validation rules
        answer_value: User's answer (type varies by question type)
    
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if validation passed, False otherwise
        - error_message: None if valid, descriptive error string if invalid
    
    Validation rules by question type:
        - multiple_choice: Must have exactly one selection (string)
        - checkboxes: Must meet min/max selection limits (list of strings)
        - short_answer: Must meet min_length requirement (string)
        - paragraph: Must meet min_length requirement (string)
        - file_upload: Validated separately by R2 service (not here)
    """
    validation = question.validation
    
    # Check if required and empty
    if validation.required and answer_value in (None, "", []):
        return False, f"This question is required. Please provide an answer."
    
    # If not required and empty, allow it
    if not answer_value and not validation.required:
        return True, None
    
    # Validate by question type
    if question.type == QuestionType.MULTIPLE_CHOICE:
        return _validate_multiple_choice(question, answer_value, validation)
    
    elif question.type == QuestionType.CHECKBOXES:
        return _validate_checkboxes(question, answer_value, validation)
    
    elif question.type == QuestionType.SHORT_ANSWER:
        return _validate_text(answer_value, validation, "short answer")
    
    elif question.type == QuestionType.PARAGRAPH:
        return _validate_text(answer_value, validation, "paragraph")
    
    elif question.type == QuestionType.FILE_UPLOAD:
        # File upload validation handled by R2StorageService
        # Just check if files were provided
        if validation.required and not answer_value:
            return False, "Please upload at least one file."
        return True, None
    
    return True, None


def _validate_multiple_choice(
    question: Question, answer_value: Any, validation: ValidationRule
) -> tuple[bool, Optional[str]]:
    """Validate multiple choice question (single selection)."""
    if not isinstance(answer_value, str):
        return False, "Please select one option."
    
    if answer_value not in question.options:
        return False, "Invalid selection. Please choose from the available options."
    
    return True, None


def _validate_checkboxes(
    question: Question, answer_value: Any, validation: ValidationRule
) -> tuple[bool, Optional[str]]:
    """Validate checkbox question (multi-select with limits)."""
    if not isinstance(answer_value, list):
        return False, "Please select at least one option."
    
    # Check min selections
    if validation.min_selections is not None and len(answer_value) < validation.min_selections:
        return False, f"Please select at least {validation.min_selections} option(s)."
    
    # Check max selections
    if validation.max_selections is not None and len(answer_value) > validation.max_selections:
        return False, f"Please select at most {validation.max_selections} option(s)."
    
    # Verify all selections are valid options
    for selection in answer_value:
        if selection not in question.options:
            return False, f"Invalid selection: '{selection}'"
    
    return True, None


def _validate_text(
    answer_value: Any, validation: ValidationRule, field_name: str
) -> tuple[bool, Optional[str]]:
    """Validate text input (short answer or paragraph)."""
    if not isinstance(answer_value, str):
        return False, f"Please provide text for this {field_name}."
    
    # Strip whitespace for length check
    text = answer_value.strip()
    
    # Check minimum length
    if validation.min_length is not None and len(text) < validation.min_length:
        return (
            False,
            f"Please provide at least {validation.min_length} characters. "
            f"Current length: {len(text)} characters.",
        )
    
    # Check maximum length
    if validation.max_length is not None and len(text) > validation.max_length:
        return (
            False,
            f"Please keep your answer under {validation.max_length} characters. "
            f"Current length: {len(text)} characters.",
        )
    
    return True, None


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Validate email address format.
    
    Args:
        email: Email address string to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Validation rules:
        - Must contain exactly one @ symbol
        - Must have text before and after @
        - Domain must have at least one dot
        - No whitespace allowed
    """
    if not email or not isinstance(email, str):
        return False, "Please provide an email address."
    
    email = email.strip()
    
    # Basic regex for email validation
    # Pattern: username@domain.tld
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Please provide a valid email address (e.g., name@example.com)."
    
    return True, None

