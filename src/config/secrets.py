"""
Secrets management helper functions.

Provides easy access to Streamlit secrets for R2, SendGrid, and SMTP configuration.
"""

import streamlit as st
from typing import Dict, Any


def get_r2_config() -> Dict[str, Any]:
    """
    Get Cloudflare R2 configuration from Streamlit secrets.
    
    Returns:
        Dictionary with R2 connection parameters:
        - endpoint_url: R2 endpoint URL
        - access_key_id: R2 access key ID
        - secret_access_key: R2 secret access key
        - bucket_name: Target bucket name
        - bucket_id: Public bucket ID for URL construction
    
    Raises:
        KeyError: If required secrets are missing
    """
    try:
        return {
            "endpoint_url": st.secrets["r2"]["endpoint_url"],
            "access_key_id": st.secrets["r2"]["access_key_id"],
            "secret_access_key": st.secrets["r2"]["secret_access_key"],
            "bucket_name": st.secrets["r2"]["bucket_name"],
            "bucket_id": st.secrets["r2"]["bucket_id"],
        }
    except KeyError as e:
        raise KeyError(
            f"Missing R2 configuration in secrets: {e}. "
            "Please configure .streamlit/secrets.toml with [r2] section."
        )


def get_sendgrid_config() -> Dict[str, str]:
    """
    Get SendGrid configuration from Streamlit secrets.
    
    Returns:
        Dictionary with SendGrid parameters:
        - api_key: SendGrid API key
        - from_email: Sender email address
        - from_name: Sender display name
    
    Raises:
        KeyError: If required secrets are missing
    """
    try:
        return {
            "api_key": st.secrets["sendgrid"]["api_key"],
            "from_email": st.secrets["sendgrid"]["from_email"],
            "from_name": st.secrets["sendgrid"]["from_name"],
        }
    except KeyError as e:
        raise KeyError(
            f"Missing SendGrid configuration in secrets: {e}. "
            "Please configure .streamlit/secrets.toml with [sendgrid] section."
        )


def get_smtp_config() -> Dict[str, Any]:
    """
    Get SMTP configuration from Streamlit secrets (fallback email service).
    
    Returns:
        Dictionary with SMTP parameters:
        - server: SMTP server address
        - port: SMTP server port
        - user: SMTP username
        - password: SMTP password
        - from_email: Sender email address
    
    Raises:
        KeyError: If required secrets are missing
    """
    try:
        return {
            "server": st.secrets["smtp"]["server"],
            "port": st.secrets["smtp"]["port"],
            "user": st.secrets["smtp"]["user"],
            "password": st.secrets["smtp"]["password"],
            "from_email": st.secrets["smtp"]["from_email"],
        }
    except KeyError as e:
        raise KeyError(
            f"Missing SMTP configuration in secrets: {e}. "
            "Please configure .streamlit/secrets.toml with [smtp] section."
        )

