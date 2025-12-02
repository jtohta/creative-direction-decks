"""
Creative Direction Questionnaire - Streamlit Application

TypeForm-style questionnaire with step-by-step validation.
Per spec.md requirements.
"""

import streamlit as st
from datetime import datetime, UTC
from src.models import FormSession, Response, FileReference
from src.config import QUESTIONS, get_r2_config, get_sendgrid_config, get_smtp_config
from src.services import validate_response, R2StorageService, EmailDeliveryService
from src.services.validation import validate_email
from src.utils import export_to_json


# Page configuration
st.set_page_config(
    page_title="Creative Direction Questionnaire",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def initialize_session():
    """Initialize session state with FormSession if not exists."""
    if "form_session" not in st.session_state:
        st.session_state.form_session = FormSession()
    
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    
    if "validation_error" not in st.session_state:
        st.session_state.validation_error = None


def render_progress_bar():
    """Render progress indicator showing completion percentage."""
    total_questions = len(QUESTIONS) + 1  # +1 for email step
    current_step = st.session_state.current_question_index + 1
    progress = current_step / total_questions
    
    st.progress(progress)
    st.caption(f"Question {current_step} of {total_questions}")


def render_question(question):
    """
    Render a question with appropriate input widget.
    
    Returns the user's input value.
    """
    st.markdown(f"### {question.text}")
    
    if question.description:
        st.markdown(f"*{question.description}*")
    
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
        return False, [], f"R2 configuration error: {e}"
    
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
        return False, [], "\n".join(errors)
    
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
        sendgrid_config = get_sendgrid_config()
        smtp_config = get_smtp_config()
        
        email_service = EmailDeliveryService(
            sendgrid_api_key=sendgrid_config["api_key"],
            sendgrid_from_email=sendgrid_config["from_email"],
            sendgrid_from_name=sendgrid_config["from_name"],
            smtp_server=smtp_config["server"],
            smtp_port=smtp_config["port"],
            smtp_user=smtp_config["user"],
            smtp_password=smtp_config["password"],
            smtp_from_email=smtp_config["from_email"],
        )
        
        user_name = email.split("@")[0].title()  # Extract name from email
        success, email_error = email_service.send_questionnaire_completion_email(
            to_email=email,
            user_name=user_name,
            questionnaire_data=data_dict,
        )
        
        if not success:
            st.warning(f"Email delivery failed: {email_error}")
        
    except KeyError:
        st.warning("Email configuration not found. Download JSON manually below.")
    
    # Store JSON and email in session for completion page
    st.session_state.completion_json = json_data
    st.session_state.completion_email = email
    st.session_state.validation_error = None
    st.session_state.current_question_index += 1


def render_email_step():
    """Render final email collection step."""
    st.markdown("### 📧 Almost done!")
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
    
    # Header
    st.title("🎨 Creative Direction Questionnaire")
    st.markdown("*Answer one question at a time to define your brand's creative direction*")
    st.markdown("---")
    
    current_index = st.session_state.current_question_index
    
    # Check if we're at completion page
    if current_index > len(QUESTIONS):
        render_completion_page()
        return
    
    # Render progress bar
    render_progress_bar()
    st.markdown("")
    
    # Check if we're at email step
    if current_index == len(QUESTIONS):
        render_email_step()
        return
    
    # Render current question
    question = QUESTIONS[current_index]
    answer = render_question(question)
    
    # Display validation error if exists
    if st.session_state.validation_error:
        st.error(st.session_state.validation_error)
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if current_index > 0:
            st.button("← Back", on_click=go_back_to_previous_question, use_container_width=True)
    
    with col2:
        st.button("Next →", on_click=advance_to_next_question, type="primary", use_container_width=True)


if __name__ == "__main__":
    main()

