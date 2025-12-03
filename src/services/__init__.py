"""
Service layer for Creative Direction Questionnaire application.

Exports:
- validate_response: Input validation logic
- R2StorageService: Cloudflare R2 file storage operations
- EmailDeliveryService: Email sending (Yagmail + SMTP fallback)
"""

from .validation import validate_response
from .r2_storage import R2StorageService
from .email_delivery import EmailDeliveryService

__all__ = [
    "validate_response",
    "R2StorageService",
    "EmailDeliveryService",
]

