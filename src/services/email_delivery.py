"""
Email delivery service with Yagmail primary and SMTP fallback.

Per contracts/yagmail-delivery.md specification.
"""

import smtplib
import json
from io import BytesIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Optional
import yagmail


class EmailDeliveryService:
    """
    Service for sending emails via Yagmail (primary) with SMTP fallback.
    
    Supports plain text and HTML emails with JSON attachments.
    """
    
    def __init__(
        self,
        yagmail_user: Optional[str] = None,
        yagmail_password: Optional[str] = None,
        yagmail_from_email: Optional[str] = None,
        yagmail_from_name: Optional[str] = None,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        smtp_from_email: Optional[str] = None,
    ):
        """
        Initialize email service with Yagmail and SMTP credentials.
        
        Args:
            yagmail_user: Gmail address for Yagmail authentication (primary service)
            yagmail_password: Gmail App Password for Yagmail (primary service)
            yagmail_from_email: Sender email for Yagmail (optional, defaults to user)
            yagmail_from_name: Sender display name for Yagmail (optional)
            smtp_server: SMTP server address (fallback service)
            smtp_port: SMTP server port (fallback service)
            smtp_user: SMTP username (fallback service)
            smtp_password: SMTP password (fallback service)
            smtp_from_email: Sender email for SMTP (fallback service)
        """
        self.yagmail_user = yagmail_user
        self.yagmail_password = yagmail_password
        self.yagmail_from_email = yagmail_from_email or yagmail_user
        self.yagmail_from_name = yagmail_from_name
        
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.smtp_from_email = smtp_from_email
    
    def send_questionnaire_completion_email(
        self,
        to_email: str,
        user_name: str,
        questionnaire_data: dict,
    ) -> tuple[bool, Optional[str]]:
        """
        Send questionnaire completion email with JSON attachment.
        
        Args:
            to_email: Recipient email address
            user_name: User's name (extracted from email or provided)
            questionnaire_data: Complete questionnaire data as dictionary
        
        Returns:
            Tuple of (success, error_message)
            - success: True if email sent successfully, False otherwise
            - error_message: None if success, error description if failed
        """
        # Prepare email content
        subject = "Your Creative Direction Questionnaire Submission"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>Thank you for completing the Creative Direction Questionnaire! 🎨</h2>
            
            <p>Hi {user_name},</p>
            
            <p>We've received your questionnaire responses. Your creative direction data is attached as a JSON file.</p>
            
            <h3>What's Next?</h3>
            <ul>
                <li>Review your responses in the attached JSON file</li>
                <li>We'll use this to create your custom creative direction deck</li>
                <li>Expect to hear from us within 2-3 business days</li>
            </ul>
            
            <p>If you have any questions, feel free to reply to this email.</p>
            
            <p>Best regards,<br>
            <strong>Creative Direction Team</strong></p>
        </body>
        </html>
        """
        
        text_body = f"""
Thank you for completing the Creative Direction Questionnaire!

Hi {user_name},

We've received your questionnaire responses. Your creative direction data is attached as a JSON file.

What's Next?
- Review your responses in the attached JSON file
- We'll use this to create your custom creative direction deck
- Expect to hear from us within 2-3 business days

If you have any questions, feel free to reply to this email.

Best regards,
Creative Direction Team
        """
        
        # Convert questionnaire data to JSON
        json_content = json.dumps(questionnaire_data, indent=2)
        json_filename = f"questionnaire_submission_{questionnaire_data.get('submission_metadata', {}).get('session_id', 'unknown')}.json"
        
        # Try Yagmail first (primary)
        if self.yagmail_user and self.yagmail_password:
            success, error = self._send_via_yagmail(
                to_email=to_email,
                subject=subject,
                html_content=html_body,
                text_content=text_body,
                attachment_content=json_content,
                attachment_filename=json_filename,
            )
            if success:
                return True, None
            else:
                # Log Yagmail failure, will try SMTP fallback
                print(f"Yagmail failed: {error}. Trying SMTP fallback...")
        
        # Fallback to SMTP
        if self.smtp_server:
            success, error = self._send_via_smtp(
                to_email=to_email,
                subject=subject,
                html_content=html_body,
                text_content=text_body,
                attachment_content=json_content,
                attachment_filename=json_filename,
            )
            if success:
                return True, None
            else:
                return False, f"Both Yagmail and SMTP failed. Last error: {error}"
        
        return False, "No email service configured. Please configure Yagmail or SMTP."
    
    def _send_via_yagmail(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        attachment_content: str,
        attachment_filename: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Send email via Yagmail (primary method).
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Initialize Yagmail SMTP client
            yag = yagmail.SMTP(
                user=self.yagmail_user,
                password=self.yagmail_password,
            )
            
            # Yagmail's attachments parameter expects a LIST, not a dictionary
            # Option 1: Use BytesIO with .name attribute (in-memory, no temp file)
            attachment_file = BytesIO(attachment_content.encode('utf-8'))
            attachment_file.name = attachment_filename  # Required for Yagmail to determine MIME type
            
            # Send email with HTML, text, and attachment
            # Yagmail automatically handles text/HTML content ordering
            # attachments must be a list, not a dict
            yag.send(
                to=to_email,
                subject=subject,
                contents=[text_content, html_content],  # Yagmail handles text/HTML automatically
                attachments=[attachment_file],  # LIST, not dict!
            )
            
            return True, None
        
        except Exception as e:
            return False, f"Yagmail error: {str(e)}"
    
    def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        attachment_content: str,
        attachment_filename: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Send email via SMTP (fallback method).
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Create MIME message
            msg = MIMEMultipart("alternative")
            msg["From"] = self.smtp_from_email
            msg["To"] = to_email
            msg["Subject"] = subject
            
            # Add text and HTML versions
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            msg.attach(part1)
            msg.attach(part2)
            
            # Add JSON attachment
            attachment = MIMEApplication(attachment_content.encode(), _subtype="json")
            attachment.add_header("Content-Disposition", "attachment", filename=attachment_filename)
            msg.attach(attachment)
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enable TLS
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True, None
        
        except Exception as e:
            return False, f"SMTP error: {str(e)}"

