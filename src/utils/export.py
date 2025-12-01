"""
Data export utilities for questionnaire responses.

Handles JSON export format per data-model.md specification.
"""

import json
from typing import Dict
from src.models import FormSession


def export_to_json(
    form_session: FormSession,
    questions_map: Dict,
    pretty: bool = True,
) -> str:
    """
    Export form session to JSON string.
    
    Args:
        form_session: Complete form session with all responses
        questions_map: Dictionary mapping question_id to Question objects
        pretty: Whether to format JSON with indentation (default: True)
    
    Returns:
        JSON string in format specified by data-model.md
    
    JSON Structure:
        {
            "questionnaire_version": "1.0.0",
            "submission_metadata": {
                "session_id": "uuid4",
                "submitted_at": "ISO8601 timestamp",
                "user_email": "email@example.com",
                "completion_time_minutes": 15.5,
                "started_at": "ISO8601 timestamp"
            },
            "responses": [
                {
                    "question_id": "Q1",
                    "question_text": "Who are you?",
                    "question_type": "multiple_choice",
                    "answer_value": "Creator (innovative, artistic, original)",
                    "timestamp": "ISO8601 timestamp",
                    "validation_status": true,
                    "file_references": []
                },
                ...
            ],
            "r2_storage": {
                "bucket_name": "creative-direction-decks",
                "session_folder": "session_id/timestamp"
            }
        }
    
    Example:
        >>> session = FormSession(...)
        >>> questions = {q.id: q for q in QUESTIONS}
        >>> json_str = export_to_json(session, questions)
    """
    data = form_session.to_dict(questions_map)
    
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    else:
        return json.dumps(data, ensure_ascii=False)


def save_json_to_file(
    form_session: FormSession,
    questions_map: Dict,
    file_path: str,
) -> bool:
    """
    Export form session to JSON file.
    
    Args:
        form_session: Complete form session with all responses
        questions_map: Dictionary mapping question_id to Question objects
        file_path: Path where JSON file should be saved
    
    Returns:
        True if save succeeded, False otherwise
    
    Example:
        >>> session = FormSession(...)
        >>> questions = {q.id: q for q in QUESTIONS}
        >>> success = save_json_to_file(session, questions, "submission.json")
    """
    try:
        json_str = export_to_json(form_session, questions_map, pretty=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json_str)
        return True
    except Exception as e:
        print(f"Error saving JSON to file: {e}")
        return False

