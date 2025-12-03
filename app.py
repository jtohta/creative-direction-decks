"""
Creative Direction Questionnaire - Streamlit Application

TypeForm-style questionnaire with step-by-step validation.
Per spec.md requirements.
"""

import streamlit as st
import logging
from datetime import datetime, UTC
from src.models import FormSession, Response, FileReference
from src.config import QUESTIONS, get_r2_config, get_yagmail_config, get_smtp_config
from src.services import validate_response, R2StorageService, EmailDeliveryService
from src.services.validation import validate_email
from src.utils import export_to_json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Page configuration
st.set_page_config(
    page_title="Creative Direction Questionnaire",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS - Phase 1: Base layout & typography
st.html("""
<style>
    /* Hide Streamlit chrome */
    #MainMenu, footer { visibility: hidden; }
    
    /* Global layout */
    .stApp {
        background-color: #ffffff;
    }
    
    .block-container {
        max-width: 640px;
        margin-left: auto;
        margin-right: auto;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Vertical centering */
    div[data-testid="stMain"] > div[data-testid="stMainBlockContainer"] {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] {
        flex-grow: 0;
    }
    
    /* Card containers (st.container with border) */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
        border: none;
    }
    
    /* Question titles (using st.subheader) */
    div[data-testid="stSubheader"] p {
        font-size: 1.5rem;
        line-height: 1.4;
        font-weight: 600;
        color: #1f2933;
    }
    
    /* Progress bar spacing */
    div[data-testid="stProgress"] {
        margin-bottom: 0.5rem;
    }
    
    /* Form controls - visible borders */
    .stTextArea textarea,
    .stTextInput input {
        border: 1px solid #CBD5E0;
        border-radius: 6px;
    }
    
    /* Radio/checkbox base spacing */
    .stRadio > div { gap: 0.5rem; }
    div[data-testid="stCheckbox"] { margin-bottom: -0.75rem; }
</style>
""")


def initialize_session():
    """Initialize session state with FormSession if not exists."""
    if "form_session" not in st.session_state:
        st.session_state.form_session = FormSession()
    
    if "current_step" not in st.session_state:
        st.session_state.current_step = "welcome"  # welcome, questions, email, complete
    
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    
    if "validation_error" not in st.session_state:
        st.session_state.validation_error = None


def start_questionnaire():
    """Transition from welcome screen to first question."""
    st.session_state.current_step = "questions"


def render_welcome_screen():
    """Render Typeform-style welcome screen."""
    # Add vertical spacing for welcome page only
    st.container(height=80, border=False)
    
    with st.container(border=True):
        st.title("🎨 Creative Direction Questionnaire")
        st.markdown("Answer a few questions to help us understand your brand's creative direction.")
        st.markdown("*This takes about 5-10 minutes.*")
        st.markdown("")
        st.button("Start →", on_click=start_questionnaire, type="primary", use_container_width=True)


def render_progress_bar():
    """Render minimal progress indicator."""
    total_questions = len(QUESTIONS) + 1  # +1 for email step
    current_step = st.session_state.current_question_index + 1
    progress = current_step / total_questions
    
    st.progress(progress)
    st.caption(f"{current_step} of {total_questions}")


def render_question(question):
    """
    Render a question with appropriate input widget.
    
    Returns the user's input value.
    """
    with st.container(border=True):
        st.subheader(question.text)
        
        if question.description:
            st.caption(question.description)
        
        # Get previous response if exists
        previous_response = st.session_state.form_session.get_response(question.id)
        default_value = previous_response.answer_value if previous_response else None
        
        # Render appropriate input widget based on question type
        if question.type.value == "multiple_choice":
            answer = st.radio(
                "Select one:",
                options=question.options,
                index=question.options.index(default_value) if default_value in question.options else 0,
                key=f"input_{question.id}",
            )
        
        elif question.type.value == "checkboxes":
            st.write("Select 1-2 options:")
            # Store checkbox selections in session state
            if f"checkbox_selections_{question.id}" not in st.session_state:
                st.session_state[f"checkbox_selections_{question.id}"] = default_value or []
            
            selected = []
            for option in question.options:
                is_checked = option in st.session_state[f"checkbox_selections_{question.id}"]
                if st.checkbox(option, value=is_checked, key=f"checkbox_{question.id}_{option}"):
                    selected.append(option)
            
            # Update session state with current selections
            st.session_state[f"checkbox_selections_{question.id}"] = selected
            answer = selected
        
        elif question.type.value == "short_answer":
            answer = st.text_input(
                "Your answer:",
                value=default_value or "",
                key=f"input_{question.id}",
            )
        
        elif question.type.value == "paragraph":
            answer = st.text_area(
                "Your answer:",
                value=default_value or "",
                height=150,
                key=f"input_{question.id}",
            )
        
        elif question.type.value == "file_upload":
            st.info("📸 Upload 5-15 reference images (JPEG, PNG, or WebP)")
            st.caption("Max 20MB per file, 200MB total")
            
            uploaded_files = st.file_uploader(
                "Choose images:",
                type=["jpg", "jpeg", "png", "webp"],
                accept_multiple_files=True,
                key=f"input_{question.id}",
            )
            answer = uploaded_files
        
        else:
            st.error(f"Unknown question type: {question.type}")
            answer = None
        
        return answer


def handle_file_upload(uploaded_files, question_id):
    """
    Upload files to R2 and return FileReference objects.
    
    Returns:
        tuple: (success: bool, file_references: list, error: str)
    """
    if not uploaded_files:
        return False, [], "No files provided"
    
    # Get R2 config
    try:
        r2_config = get_r2_config()
    except KeyError as e:
        logger.error(f"R2 configuration error: {e}")
        return False, [], "File storage is not configured. Please contact support."
    
    try:
        # Initialize R2 service
        r2_service = R2StorageService(**r2_config)
        
        # Prepare files for batch upload
        files_to_upload = []
        for uploaded_file in uploaded_files:
            uploaded_file.seek(0)  # Reset file pointer
            files_to_upload.append((uploaded_file, uploaded_file.name))
        
        # Validation rules from question
        question = next(q for q in QUESTIONS if q.id == question_id)
        validation_rules = {
            "allowed_types": question.validation.allowed_file_types,
            "max_file_size_mb": question.validation.max_file_size_mb,
            "max_total_size_mb": question.validation.max_total_size_mb,
            "min_files": question.validation.min_files,
            "max_files": question.validation.max_files,
        }
        
        # Upload files
        session_folder = st.session_state.form_session.r2_folder_path
        uploaded_file_info, errors = r2_service.batch_upload_files(
            files_to_upload, session_folder, validation_rules
        )
        
        if errors:
            # Known validation error prefixes (user-actionable errors)
            validation_error_prefixes = [
                "Please upload at least",
                "Please upload at most",
                "Total upload size exceeds",
                "File '",
                "Could not determine file type",
                "File type '",
            ]
            
            validation_errors = []
            system_errors = []
            
            for error in errors:
                # Check if this is a known validation error
                is_validation_error = any(error.startswith(prefix) for prefix in validation_error_prefixes)
                
                if is_validation_error:
                    validation_errors.append(error)
                else:
                    # Everything else is a system error
                    system_errors.append(error)
            
            # Log system errors but don't show them to users
            if system_errors:
                logger.error(
                    f"File upload system errors for session {st.session_state.form_session.session_id}: {system_errors}",
                    exc_info=False
                )
                return False, [], "Unable to upload files at this time. Please try again later or contact support if the problem persists."
            
            # Show validation errors to users (these are actionable)
            if validation_errors:
                logger.info(f"File validation errors for session {st.session_state.form_session.session_id}: {validation_errors}")
                return False, [], "\n".join(validation_errors)
    
    except Exception as e:
        # Log the actual backend error
        logger.error(
            f"File upload failed for session {st.session_state.form_session.session_id}: {type(e).__name__}: {str(e)}",
            exc_info=True
        )
        # Return user-friendly message
        return False, [], "Unable to upload files at this time. Please try again later or contact support if the problem persists."
    
    # Convert to FileReference objects
    file_references = [
        FileReference(
            original_filename=file_info["file_name"],
            r2_key=file_info["r2_key"],
            r2_url=file_info["r2_url"],
            file_size_bytes=file_info["file_size_bytes"],
            mime_type=file_info["mime_type"],
            upload_timestamp=datetime.now(UTC),
        )
        for file_info in uploaded_file_info
    ]
    
    return True, file_references, None


def advance_to_next_question():
    """Validate current answer and advance to next question."""
    current_index = st.session_state.current_question_index
    
    # Check if we're at email step
    if current_index >= len(QUESTIONS):
        return
    
    question = QUESTIONS[current_index]
    
    # Get answer based on question type
    if question.type.value == "checkboxes":
        # For checkboxes, collect from checkbox selections stored in session state
        answer = st.session_state.get(f"checkbox_selections_{question.id}", [])
    else:
        answer = st.session_state.get(f"input_{question.id}")
    
    # Special handling for file uploads
    if question.type.value == "file_upload":
        if not answer:
            st.session_state.validation_error = "Please upload at least 5 images."
            return
        
        # Validate file count and upload
        is_valid, file_refs, error = handle_file_upload(answer, question.id)
        
        if not is_valid:
            st.session_state.validation_error = error
            return
        
        # Create response with file references
        response = Response(
            question_id=question.id,
            answer_value=f"{len(file_refs)} files uploaded",
            timestamp=datetime.now(UTC),
            validation_status=True,
            file_references=file_refs,
        )
    else:
        # Standard validation
        is_valid, error = validate_response(question, answer)
        
        if not is_valid:
            st.session_state.validation_error = error
            return
        
        # Create response
        response = Response(
            question_id=question.id,
            answer_value=answer,
            timestamp=datetime.now(UTC),
            validation_status=True,
        )
    
    # Save response
    st.session_state.form_session.add_response(question.id, response)
    
    # Clear error and advance
    st.session_state.validation_error = None
    st.session_state.current_question_index += 1


def go_back_to_previous_question():
    """Navigate back to previous question."""
    if st.session_state.current_question_index > 0:
        st.session_state.current_question_index -= 1
        st.session_state.validation_error = None


def submit_questionnaire():
    """Submit final email and complete questionnaire."""
    email = st.session_state.get("email_input", "")
    
    # Validate email
    is_valid, error = validate_email(email)
    
    if not is_valid:
        st.session_state.validation_error = error
        return
    
    # Mark session as complete
    st.session_state.form_session.mark_complete(email)
    
    # Export to JSON
    questions_map = {q.id: q for q in QUESTIONS}
    json_data = export_to_json(st.session_state.form_session, questions_map)
    
    # Parse JSON for email
    import json
    data_dict = json.loads(json_data)
    
    # Send email
    try:
        # Try Yagmail first (primary)
        try:
            yagmail_config = get_yagmail_config()
            yagmail_params = {
                "yagmail_user": yagmail_config["user"],
                "yagmail_password": yagmail_config["password"],
                "yagmail_from_email": yagmail_config.get("from_email"),
                "yagmail_from_name": yagmail_config.get("from_name"),
            }
        except KeyError:
            # Yagmail not configured, use empty params
            yagmail_params = {}
        
        # Get SMTP config for fallback
        try:
            smtp_config = get_smtp_config()
            smtp_params = {
                "smtp_server": smtp_config["server"],
                "smtp_port": smtp_config["port"],
                "smtp_user": smtp_config["user"],
                "smtp_password": smtp_config["password"],
                "smtp_from_email": smtp_config["from_email"],
            }
        except KeyError:
            # SMTP not configured, use empty params
            smtp_params = {}
        
        email_service = EmailDeliveryService(**yagmail_params, **smtp_params)
        
        user_name = email.split("@")[0].title()  # Extract name from email
        success, email_error = email_service.send_questionnaire_completion_email(
            to_email=email,
            user_name=user_name,
            questionnaire_data=data_dict,
        )
        
        if not success:
            logger.error(f"Email delivery failed for {email}: {email_error}")
            st.info("📧 Email delivery is temporarily unavailable. You can download your responses below.")
        
    except KeyError as e:
        logger.warning(f"Email configuration missing: {e}")
        st.info("📧 Email is not configured. You can download your responses below.")
    except Exception as e:
        logger.error(f"Unexpected error sending email: {type(e).__name__}: {str(e)}", exc_info=True)
        st.info("📧 Unable to send email at this time. You can download your responses below.")
    
    # Store JSON and email in session for completion page
    st.session_state.completion_json = json_data
    st.session_state.completion_email = email
    st.session_state.validation_error = None
    st.session_state.current_question_index += 1


def render_email_step():
    """Render final email collection step."""
    with st.container(border=True):
        st.subheader("📧 Almost done!")
        st.markdown("Enter your email to receive your questionnaire responses:")
        
        email = st.text_input(
            "Email address:",
            value=st.session_state.get("email_input", ""),
            key="email_input",
        )
        
        # Display validation error if exists
        if st.session_state.validation_error:
            st.error(st.session_state.validation_error)
        
        # Navigation buttons
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.button("← Back", on_click=go_back_to_previous_question, use_container_width=True)
        
        with col2:
            st.button("Submit ✓", on_click=submit_questionnaire, type="primary", use_container_width=True)


def render_completion_page():
    """Render completion confirmation page."""
    st.balloons()
    
    with st.container(border=True):
        st.success("✅ Thank you for completing the Creative Direction Questionnaire!")
        
        st.markdown(f"""
### Your submission has been received

**Email:** {st.session_state.completion_email}

Your responses have been emailed to you as a JSON file. You can also download them below.
        """)
        
        # Download button for JSON
        st.download_button(
            label="📥 Download Responses (JSON)",
            data=st.session_state.completion_json,
            file_name=f"questionnaire_{st.session_state.form_session.session_id}.json",
            mime="application/json",
            use_container_width=True,
        )
        
        st.markdown("---")
        st.caption("We'll be in touch within 2-3 business days to discuss your creative direction.")
        
        # Option to start over
        if st.button("Start New Questionnaire"):
            # Clear session
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            # Streamlit automatically reruns after button click


def main():
    """Main application entry point."""
    initialize_session()
    
    current_step = st.session_state.current_step
    current_index = st.session_state.current_question_index
    
    # Welcome screen
    if current_step == "welcome":
        render_welcome_screen()
        return
    
    # Completion page
    if current_index > len(QUESTIONS):
        render_completion_page()
        return
    
    # Email step
    if current_index == len(QUESTIONS):
        render_progress_bar()
        render_email_step()
        return
    
    # Question screens
    render_progress_bar()
    
    question = QUESTIONS[current_index]
    render_question(question)
    
    # Display validation error if exists
    if st.session_state.validation_error:
        st.error(st.session_state.validation_error)
    
    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if current_index > 0:
            st.button("← Back", on_click=go_back_to_previous_question, use_container_width=True)
    
    with col2:
        st.button("Next →", on_click=advance_to_next_question, type="primary", use_container_width=True)


if __name__ == "__main__":
    main()

