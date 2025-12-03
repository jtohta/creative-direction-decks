"""
Form session model for managing overall questionnaire state.

Per data-model.md specification.
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Optional
import uuid

from .response import Response


@dataclass
class FormSession:
    """
    Overall questionnaire session state.
    
    Attributes:
        session_id: Unique identifier for this session (UUID4)
        current_question_index: Index of current question (0-based)
        all_responses: Dictionary mapping question_id to Response objects
        completion_status: Whether the questionnaire has been completed
        user_email: Email address submitted by user (set on completion)
        started_at: When the session was initiated
        completed_at: When the session was completed (None if in progress)
        r2_folder_path: Path in R2 bucket for this session's files
    
    State transitions:
        1. Initial: completion_status=False, current_question_index=0
        2. In Progress: User advances through questions, responses accumulated
        3. Complete: completion_status=True, user_email set, completed_at recorded
    """
    
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    current_question_index: int = 0
    all_responses: dict[str, Response] = field(default_factory=dict)
    completion_status: bool = False
    user_email: Optional[str] = None
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None
    r2_folder_path: Optional[str] = None
    
    def __post_init__(self):
        """Initialize R2 folder path if not provided."""
        if self.r2_folder_path is None:
            timestamp = self.started_at.strftime('%Y%m%d_%H%M%S')
            self.r2_folder_path = f"{self.session_id}/{timestamp}"
    
    def add_response(self, question_id: str, response: Response) -> None:
        """
        Add or update a response for a question.
        
        Args:
            question_id: ID of the question
            response: Response object containing the answer
        """
        self.all_responses[question_id] = response
    
    def get_response(self, question_id: str) -> Optional[Response]:
        """
        Retrieve response for a specific question.
        
        Args:
            question_id: ID of the question
        
        Returns:
            Response object if exists, None otherwise
        """
        return self.all_responses.get(question_id)
    
    def mark_complete(self, email: str) -> None:
        """
        Mark session as complete.
        
        Args:
            email: User's email address
        """
        self.completion_status = True
        self.user_email = email
        self.completed_at = datetime.now(UTC)
    
    def completion_time_minutes(self) -> Optional[float]:
        """
        Calculate completion time in minutes.
        
        Returns:
            Time taken to complete in minutes, or None if not completed
        """
        if self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds() / 60
        return None
    
    def to_dict(self, questions_map: dict) -> dict:
        """
        Convert to dictionary for JSON export.
        
        Args:
            questions_map: Dictionary mapping question_id to Question objects
                           (needed to include question text in export)
        
        Returns:
            Dictionary matching the JSON export schema from data-model.md
        """
        return {
            "questionnaire_version": "1.0.0",
            "submission_metadata": {
                "session_id": self.session_id,
                "submitted_at": self.completed_at.isoformat() if self.completed_at else None,
                "user_email": self.user_email,
                "completion_time_minutes": self.completion_time_minutes(),
                "started_at": self.started_at.isoformat(),
            },
            "responses": [
                {
                    **response.to_dict(),
                    "question_text": questions_map[qid].text,
                    "question_type": questions_map[qid].type.value,
                }
                for qid, response in self.all_responses.items()
            ],
            "r2_storage": {
                "bucket_name": "creative-direction-decks",
                "session_folder": self.r2_folder_path,
            },
        }

