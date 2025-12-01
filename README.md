# Creative Direction Questionnaire Application

A TypeForm-style Streamlit application for collecting creative direction brand questionnaire responses.

## Features

- **Step-by-step form flow**: One question at a time for focused user experience
- **Real-time validation**: Prevents advancement without valid inputs
- **20 essential questions**: Comprehensive brand direction questionnaire
- **File uploads**: 5-15 reference images with validation
- **Cloudflare R2 storage**: Persistent file storage
- **Email delivery**: Results sent via email with JSON attachment
- **Progress tracking**: Visual progress indicator throughout questionnaire
- **Navigation**: Back/forward navigation with answer preservation

## Quick Start

See [specs/001-streamlit-typeform-app/quickstart.md](specs/001-streamlit-typeform-app/quickstart.md) for detailed setup instructions.

### Prerequisites

- Python 3.13+
- Cloudflare R2 account (free tier)
- SendGrid account (free tier) OR Gmail with App Password

### Installation

```bash
# Clone and navigate
git clone <repository-url>
cd creative-direction-decks
git checkout 001-streamlit-typeform-app

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Configure secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your credentials

# Run application
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Development

### Testing (TDD Required)

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/           # Unit tests (pure functions)
pytest tests/integration/    # Integration tests (main focus)
pytest tests/e2e/            # End-to-end tests

# Run with coverage
pytest --cov=src --cov-report=html
```

### Project Structure

```
creative-direction-decks/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── src/
│   ├── models/            # Data models (Question, Response, FormSession)
│   ├── services/          # Business logic (validation, R2, email)
│   ├── config/            # Configuration (questions, secrets)
│   └── utils/             # Utilities (JSON export, file utils)
├── tests/
│   ├── unit/              # Pure function tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
└── .streamlit/
    ├── config.toml        # Streamlit settings
    └── secrets.toml       # Credentials (not committed)
```

## Documentation

- **Feature Specification**: [specs/001-streamlit-typeform-app/spec.md](specs/001-streamlit-typeform-app/spec.md)
- **Implementation Plan**: [specs/001-streamlit-typeform-app/plan.md](specs/001-streamlit-typeform-app/plan.md)
- **Task Breakdown**: [specs/001-streamlit-typeform-app/tasks.md](specs/001-streamlit-typeform-app/tasks.md)
- **Data Model**: [specs/001-streamlit-typeform-app/data-model.md](specs/001-streamlit-typeform-app/data-model.md)
- **API Contracts**: [specs/001-streamlit-typeform-app/contracts/](specs/001-streamlit-typeform-app/contracts/)

## Deployment

Deploy to Streamlit Community Cloud:

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Deploy from repository
4. Configure secrets in App Settings → Secrets
5. Test live application

See [quickstart.md](specs/001-streamlit-typeform-app/quickstart.md) for detailed deployment instructions.

## License

[Add license information]

## Contributing

Follow TDD workflow per project constitution:
1. Write tests first (RED phase)
2. Implement to pass tests (GREEN phase)
3. Refactor while keeping tests green (REFACTOR phase)
4. Write E2E tests after implementation (ACCEPTANCE VALIDATION phase)

