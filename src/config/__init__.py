"""
Configuration module for Creative Direction Questionnaire application.

Exports:
- get_r2_config, get_yagmail_config, get_smtp_config
- QUESTIONS (list of all 20 question definitions)
"""

from .secrets import get_r2_config, get_yagmail_config, get_smtp_config
from .questions import QUESTIONS

__all__ = [
    "get_r2_config",
    "get_yagmail_config",
    "get_smtp_config",
    "QUESTIONS",
]

