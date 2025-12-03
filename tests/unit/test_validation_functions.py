"""
Unit tests for pure validation functions.

Per TDD workflow: These tests verify pure validation logic.
Focus: validate_email, validate_response for text/choice questions.
"""

import pytest
from src.services.validation import validate_email, validate_response
from src.models import Question, QuestionType, ValidationRule


class TestEmailValidation:
    """Test email validation per FR-009."""
    
    def test_valid_email_formats(self):
        """Test that valid email addresses pass validation."""
        valid_emails = [
            "user@example.com",
            "test.user@domain.co.uk",
            "name+tag@company.org",
            "user123@test-domain.com",
            "a@b.co",
        ]
        for email in valid_emails:
            is_valid, error = validate_email(email)
            assert is_valid is True, f"Email '{email}' should be valid"
            assert error is None, f"No error expected for valid email '{email}'"
    
    def test_invalid_email_formats(self):
        """Test that invalid email addresses fail validation."""
        invalid_emails = [
            "no-at-sign",  # Missing @
            "@no-username.com",  # Missing username
            "no-domain@",  # Missing domain
            "no-tld@domain",  # Missing TLD
            "user @example.com",  # Space in username
            "user@domain .com",  # Space in domain
            "user@@example.com",  # Double @
            "user@domain@example.com",  # Multiple @
        ]
        for email in invalid_emails:
            is_valid, error = validate_email(email)
            assert is_valid is False, f"Email '{email}' should be invalid"
            assert error is not None, f"Error message expected for invalid email '{email}'"
            assert "email" in error.lower(), "Error should mention email"
    
    def test_empty_email(self):
        """Test that empty email fails validation."""
        is_valid, error = validate_email("")
        assert is_valid is False
        assert "provide an email" in error.lower()
    
    def test_none_email(self):
        """Test that None email fails validation."""
        is_valid, error = validate_email(None)
        assert is_valid is False
        assert "provide an email" in error.lower()


class TestParagraphValidation:
    """Test paragraph response validation per FR-012."""
    
    def test_paragraph_above_minimum_length(self):
        """Test that paragraph with 100+ characters passes validation."""
        question = Question(
            id="Q3",
            text="Test paragraph question",
            type=QuestionType.PARAGRAPH,
            validation=ValidationRule(required=True, min_length=100),
        )
        
        # 105 characters
        valid_text = "This is a sufficiently long paragraph that exceeds the minimum requirement of one hundred characters."
        is_valid, error = validate_response(question, valid_text)
        assert is_valid is True
        assert error is None
    
    def test_paragraph_below_minimum_length(self):
        """Test that paragraph with <100 characters fails validation."""
        question = Question(
            id="Q3",
            text="Test paragraph question",
            type=QuestionType.PARAGRAPH,
            validation=ValidationRule(required=True, min_length=100),
        )
        
        # 44 characters
        short_text = "This text is too short for the requirement."
        is_valid, error = validate_response(question, short_text)
        assert is_valid is False
        assert error is not None
        assert "100 characters" in error
        assert "44 characters" in error or "43 characters" in error  # Should show current length (44 with period, 43 without)
    
    def test_paragraph_exactly_minimum_length(self):
        """Test that paragraph with exactly 100 characters passes."""
        question = Question(
            id="Q3",
            text="Test paragraph question",
            type=QuestionType.PARAGRAPH,
            validation=ValidationRule(required=True, min_length=100),
        )
        
        # Exactly 100 characters
        exact_text = "a" * 100
        is_valid, error = validate_response(question, exact_text)
        assert is_valid is True
        assert error is None
    
    def test_paragraph_empty_when_required(self):
        """Test that empty paragraph fails when required."""
        question = Question(
            id="Q3",
            text="Test paragraph question",
            type=QuestionType.PARAGRAPH,
            validation=ValidationRule(required=True, min_length=100),
        )
        
        is_valid, error = validate_response(question, "")
        assert is_valid is False
        assert "required" in error.lower()


class TestMultipleChoiceValidation:
    """Test multiple choice validation per FR-010."""
    
    def test_multiple_choice_with_valid_selection(self):
        """Test that selecting a valid option passes validation."""
        question = Question(
            id="Q1",
            text="Choose one",
            type=QuestionType.MULTIPLE_CHOICE,
            options=["Option A", "Option B", "Option C"],
            validation=ValidationRule(required=True),
        )
        
        is_valid, error = validate_response(question, "Option A")
        assert is_valid is True
        assert error is None
    
    def test_multiple_choice_without_selection(self):
        """Test that empty selection fails validation."""
        question = Question(
            id="Q1",
            text="Choose one",
            type=QuestionType.MULTIPLE_CHOICE,
            options=["Option A", "Option B", "Option C"],
            validation=ValidationRule(required=True),
        )
        
        is_valid, error = validate_response(question, "")
        assert is_valid is False
        assert "required" in error.lower()
    
    def test_multiple_choice_invalid_option(self):
        """Test that selecting an invalid option fails validation."""
        question = Question(
            id="Q1",
            text="Choose one",
            type=QuestionType.MULTIPLE_CHOICE,
            options=["Option A", "Option B", "Option C"],
            validation=ValidationRule(required=True),
        )
        
        is_valid, error = validate_response(question, "Option D")
        assert is_valid is False
        assert "invalid" in error.lower() or "choose from" in error.lower()


class TestCheckboxValidation:
    """Test checkbox validation per FR-011 and FR-014."""
    
    def test_checkboxes_within_selection_limits(self):
        """Test that selecting 1-2 options passes validation when min=1, max=2."""
        question = Question(
            id="Q2",
            text="Choose 1-2",
            type=QuestionType.CHECKBOXES,
            options=["Option A", "Option B", "Option C"],
            validation=ValidationRule(required=True, min_selections=1, max_selections=2),
        )
        
        # Test with 1 selection
        is_valid, error = validate_response(question, ["Option A"])
        assert is_valid is True
        assert error is None
        
        # Test with 2 selections
        is_valid, error = validate_response(question, ["Option A", "Option B"])
        assert is_valid is True
        assert error is None
    
    def test_checkboxes_too_few_selections(self):
        """Test that selecting fewer than minimum fails validation."""
        question = Question(
            id="Q2",
            text="Choose 1-2",
            type=QuestionType.CHECKBOXES,
            options=["Option A", "Option B", "Option C"],
            validation=ValidationRule(required=True, min_selections=1, max_selections=2),
        )
        
        # Empty list triggers "required" check first
        is_valid, error = validate_response(question, [])
        assert is_valid is False
        assert "required" in error.lower() or "at least 1" in error.lower()
    
    def test_checkboxes_too_many_selections(self):
        """Test that selecting more than maximum fails validation."""
        question = Question(
            id="Q2",
            text="Choose 1-2",
            type=QuestionType.CHECKBOXES,
            options=["Option A", "Option B", "Option C", "Option D"],
            validation=ValidationRule(required=True, min_selections=1, max_selections=2),
        )
        
        is_valid, error = validate_response(question, ["Option A", "Option B", "Option C"])
        assert is_valid is False
        assert "at most 2" in error.lower()
    
    def test_checkboxes_invalid_option(self):
        """Test that selecting an option not in the list fails validation."""
        question = Question(
            id="Q2",
            text="Choose 1-2",
            type=QuestionType.CHECKBOXES,
            options=["Option A", "Option B", "Option C"],
            validation=ValidationRule(required=True, min_selections=1, max_selections=2),
        )
        
        is_valid, error = validate_response(question, ["Option A", "Option Z"])
        assert is_valid is False
        assert "invalid" in error.lower()


class TestShortAnswerValidation:
    """Test short answer validation."""
    
    def test_short_answer_with_valid_text(self):
        """Test that short answer with sufficient text passes."""
        question = Question(
            id="Q13",
            text="Short answer",
            type=QuestionType.SHORT_ANSWER,
            validation=ValidationRule(required=True, min_length=10),
        )
        
        is_valid, error = validate_response(question, "This is a valid short answer.")
        assert is_valid is True
        assert error is None
    
    def test_short_answer_too_short(self):
        """Test that short answer below minimum fails."""
        question = Question(
            id="Q13",
            text="Short answer",
            type=QuestionType.SHORT_ANSWER,
            validation=ValidationRule(required=True, min_length=10),
        )
        
        is_valid, error = validate_response(question, "Short")
        assert is_valid is False
        assert "10 characters" in error
    
    def test_short_answer_empty_when_required(self):
        """Test that empty short answer fails when required."""
        question = Question(
            id="Q13",
            text="Short answer",
            type=QuestionType.SHORT_ANSWER,
            validation=ValidationRule(required=True, min_length=10),
        )
        
        is_valid, error = validate_response(question, "")
        assert is_valid is False
        assert "required" in error.lower()

