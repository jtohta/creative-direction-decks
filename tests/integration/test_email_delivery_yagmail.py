"""
Integration tests for Yagmail email delivery.

Tests email delivery via Yagmail with HTML, text, and JSON attachments.
Tests error handling and SMTP fallback behavior.

NOTE: These tests use mocks by default to avoid sending real emails and depending on external services.
This is appropriate for CI/CD and fast feedback.

For more realistic integration testing without sending real emails, you can use a local test SMTP server:
- Python's built-in `smtpd` module (see test_yagmail_with_local_smtp below)
- MailHog (https://github.com/mailhog/MailHog) - web UI to view captured emails
- MailCatcher (https://mailcatcher.me/) - similar to MailHog

Unlike HTTP (where VCR.py records/replays), SMTP requires either:
1. Mocking (what we do here - fast, deterministic)
2. Local test SMTP server (more realistic, still no real emails)
3. Real SMTP server (sends actual emails - use with caution)

Per contracts/yagmail-delivery.md specification.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.services.email_delivery import EmailDeliveryService


@pytest.fixture
def yagmail_config():
    """Provide Yagmail configuration for tests."""
    return {
        "user": "test@gmail.com",
        "password": "test-app-password",
        "from_email": "test@gmail.com",
        "from_name": "Test Service",
    }


@pytest.fixture
def smtp_config():
    """Provide SMTP configuration for fallback tests."""
    return {
        "server": "smtp.gmail.com",
        "port": 587,
        "user": "test@gmail.com",
        "password": "test-app-password",
        "from_email": "test@gmail.com",
    }


@pytest.fixture
def email_service_yagmail_only(yagmail_config):
    """EmailDeliveryService with Yagmail only (no SMTP fallback)."""
    return EmailDeliveryService(
        yagmail_user=yagmail_config["user"],
        yagmail_password=yagmail_config["password"],
        yagmail_from_email=yagmail_config["from_email"],
        yagmail_from_name=yagmail_config["from_name"],
    )


@pytest.fixture
def email_service_with_fallback(yagmail_config, smtp_config):
    """EmailDeliveryService with Yagmail primary and SMTP fallback."""
    return EmailDeliveryService(
        yagmail_user=yagmail_config["user"],
        yagmail_password=yagmail_config["password"],
        yagmail_from_email=yagmail_config["from_email"],
        yagmail_from_name=yagmail_config["from_name"],
        smtp_server=smtp_config["server"],
        smtp_port=smtp_config["port"],
        smtp_user=smtp_config["user"],
        smtp_password=smtp_config["password"],
        smtp_from_email=smtp_config["from_email"],
    )


@pytest.fixture
def sample_questionnaire_data():
    """Provide sample questionnaire data for testing."""
    return {
        "submission_metadata": {
            "session_id": "test-session-123",
            "submitted_at": "2025-01-27T12:00:00Z",
        },
        "responses": {
            "question_1": "Sample answer",
            "question_2": ["option_a", "option_b"],
        },
        "file_references": {
            "image_1": "https://r2.example.com/image1.jpg",
        },
    }


@pytest.mark.integration
def test_yagmail_successful_email_delivery(
    email_service_yagmail_only, sample_questionnaire_data, yagmail_config
):
    """
    Test successful email delivery via Yagmail.
    
    Arrange: EmailDeliveryService with Yagmail configured, valid questionnaire data
    Act: Send questionnaire completion email
    Assert: Email sent successfully via Yagmail, no errors
    """
    # Arrange
    to_email = "recipient@example.com"
    user_name = "Test User"
    
    # Mock Yagmail SMTP client
    with patch("src.services.email_delivery.yagmail.SMTP") as mock_yagmail_class:
        mock_yag = MagicMock()
        mock_yagmail_class.return_value = mock_yag
        
        # Act
        success, error = email_service_yagmail_only.send_questionnaire_completion_email(
            to_email=to_email,
            user_name=user_name,
            questionnaire_data=sample_questionnaire_data,
        )
        
        # Assert
        assert success is True
        assert error is None
        # Yagmail.SMTP is called with keyword arguments
        mock_yagmail_class.assert_called_once_with(
            user=yagmail_config["user"],
            password=yagmail_config["password"],
        )
        mock_yag.send.assert_called_once()
        call_args = mock_yag.send.call_args
        assert call_args[1]["to"] == to_email
        
        # Verify attachments structure
        attachments = call_args[1]["attachments"]
        assert isinstance(attachments, dict)
        assert len(attachments) == 1
        
        # Verify filename pattern
        attachment_filename = list(attachments.keys())[0]
        assert attachment_filename.startswith("questionnaire_submission_")
        assert attachment_filename.endswith(".json")
        
        # Verify JSON content structure
        attachment_content = attachments[attachment_filename]
        parsed_json = json.loads(attachment_content)
        assert parsed_json["submission_metadata"]["session_id"] == sample_questionnaire_data["submission_metadata"]["session_id"]
        assert parsed_json["responses"] == sample_questionnaire_data["responses"]


@pytest.mark.integration
def test_yagmail_with_json_attachment(
    email_service_yagmail_only, sample_questionnaire_data
):
    """
    Test Yagmail email delivery with JSON attachment.
    
    Arrange: EmailDeliveryService with Yagmail, questionnaire data
    Act: Send email with JSON attachment
    Assert: Email sent with correct JSON attachment content and filename
    """
    # Arrange
    to_email = "recipient@example.com"
    user_name = "Test User"
    
    # Mock Yagmail
    with patch("src.services.email_delivery.yagmail.SMTP") as mock_yagmail_class:
        mock_yag = MagicMock()
        mock_yagmail_class.return_value = mock_yag
        
        # Act
        success, error = email_service_yagmail_only.send_questionnaire_completion_email(
            to_email=to_email,
            user_name=user_name,
            questionnaire_data=sample_questionnaire_data,
        )
        
        # Assert
        assert success is True
        call_args = mock_yag.send.call_args
        attachments = call_args[1]["attachments"]
        
        # Verify attachment exists
        assert len(attachments) == 1
        attachment_filename = list(attachments.keys())[0]
        attachment_content = attachments[attachment_filename]
        
        # Verify filename format
        assert attachment_filename.startswith("questionnaire_submission_")
        assert attachment_filename.endswith(".json")
        assert "test-session-123" in attachment_filename
        
        # Verify JSON content is valid
        parsed_json = json.loads(attachment_content)
        assert parsed_json["submission_metadata"]["session_id"] == "test-session-123"


@pytest.mark.integration
def test_yagmail_authentication_failure(
    email_service_with_fallback, sample_questionnaire_data
):
    """
    Test Yagmail authentication failure triggers SMTP fallback.
    
    Arrange: EmailDeliveryService with Yagmail and SMTP, Yagmail will fail
    Act: Send email, Yagmail raises authentication error
    Assert: System falls back to SMTP, email sent successfully
    """
    # Arrange
    to_email = "recipient@example.com"
    user_name = "Test User"
    
    # Mock Yagmail to raise authentication error
    with patch("src.services.email_delivery.yagmail.SMTP") as mock_yagmail_class:
        import smtplib
        mock_yagmail_class.side_effect = smtplib.SMTPAuthenticationError(
            535, "Invalid credentials"
        )
        
        # Mock SMTP fallback
        with patch.object(
            email_service_with_fallback, "_send_via_smtp"
        ) as mock_smtp:
            mock_smtp.return_value = (True, None)
            
            # Act
            success, error = email_service_with_fallback.send_questionnaire_completion_email(
                to_email=to_email,
                user_name=user_name,
                questionnaire_data=sample_questionnaire_data,
            )
            
            # Assert
            assert success is True
            assert error is None
            mock_smtp.assert_called_once()


@pytest.mark.integration
def test_yagmail_fallback_to_smtp(
    email_service_with_fallback, sample_questionnaire_data
):
    """
    Test Yagmail failure triggers SMTP fallback.
    
    Arrange: EmailDeliveryService with Yagmail and SMTP, Yagmail fails
    Act: Send email, Yagmail raises exception
    Assert: System falls back to SMTP, email sent successfully
    """
    # Arrange
    to_email = "recipient@example.com"
    user_name = "Test User"
    
    # Mock Yagmail to raise generic exception
    with patch("src.services.email_delivery.yagmail.SMTP") as mock_yagmail_class:
        mock_yagmail_class.side_effect = Exception("Network error")
        
        # Mock SMTP fallback
        with patch.object(
            email_service_with_fallback, "_send_via_smtp"
        ) as mock_smtp:
            mock_smtp.return_value = (True, None)
            
            # Act
            success, error = email_service_with_fallback.send_questionnaire_completion_email(
                to_email=to_email,
                user_name=user_name,
                questionnaire_data=sample_questionnaire_data,
            )
            
            # Assert
            assert success is True
            assert error is None
            mock_smtp.assert_called_once()


@pytest.mark.integration
def test_yagmail_attachment_size_limit(
    email_service_yagmail_only, sample_questionnaire_data
):
    """
    Test Yagmail handles attachment size limits correctly.
    
    Arrange: EmailDeliveryService with Yagmail, large attachment (within 25MB limit)
    Act: Send email with large JSON attachment
    Assert: Email sent successfully (Gmail 25MB limit is sufficient for JSON)
    """
    # Arrange
    to_email = "recipient@example.com"
    user_name = "Test User"
    
    # Create large but valid questionnaire data (still under 25MB)
    large_data = sample_questionnaire_data.copy()
    large_data["large_field"] = "x" * (10 * 1024 * 1024)  # 10MB string
    
    # Mock Yagmail
    with patch("src.services.email_delivery.yagmail.SMTP") as mock_yagmail_class:
        mock_yag = MagicMock()
        mock_yagmail_class.return_value = mock_yag
        
        # Act
        success, error = email_service_yagmail_only.send_questionnaire_completion_email(
            to_email=to_email,
            user_name=user_name,
            questionnaire_data=large_data,
        )
        
        # Assert
        assert success is True
        assert error is None
        mock_yag.send.assert_called_once()
        
        # Verify attachment was included
        call_args = mock_yag.send.call_args
        attachments = call_args[1]["attachments"]
        assert len(attachments) > 0

