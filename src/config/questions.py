"""
Question definitions for Creative Direction Questionnaire.

Based on phase_1a_strategic_foundation_prompt.md
Includes 14 essential questions covering:
- Core Identity (Q1-Q3, Q9-Q10, Q13)
- Brand Boundaries (Q15-Q16)
- Color Palette (Q28-Q30)
- Elevator Pitch (Q44)
- Visual References (Q45, Q47)
"""

from src.models import Question, QuestionType, ValidationRule


# Core Identity Questions
Q1 = Question(
    id="Q1",
    text="Who are you? (Select the archetype that best fits your brand)",
    type=QuestionType.MULTIPLE_CHOICE,
    options=[
        "Everyman (relatable, down-to-earth, authentic)",
        "Caregiver (nurturing, supportive, community-focused)",
        "Ruler (authoritative, leader, premium)",
        "Creator (innovative, artistic, original)",
        "Innocent (optimistic, pure, simple)",
        "Sage (wise, knowledgeable, expert)",
        "Explorer (adventurous, independent, pioneering)",
        "Outlaw (rebellious, revolutionary, disruptive)",
        "Magician (transformative, visionary, mystical)",
        "Hero (courageous, inspiring, triumphant)",
        "Lover (passionate, intimate, sensual)",
        "Jester (fun, entertaining, playful)",
    ],
    validation=ValidationRule(required=True),
)

Q2 = Question(
    id="Q2",
    text="What's your story arc?",
    description="Select 1-2 that best fit - you can mix plots, but one should be primary",
    type=QuestionType.CHECKBOXES,
    options=[
        "Rags to Riches (self-made success, rising from humble beginnings)",
        "Overcoming the Monster (defeating obstacles/competition/evil forces)",
        "The Quest (journey to obtain a goal, facing trials along the way)",
        "Voyage and Return (entering a strange new world, then returning changed)",
        "Comedy (entertaining through jokes, skits, characters, punchlines)",
        "Tragedy (exploring themes of self-destruction, struggle, mental health, darkness)",
        "Rebirth (trapped by something, then emerging transformed/reborn)",
    ],
    validation=ValidationRule(required=True, min_selections=1, max_selections=2),
)

Q3 = Question(
    id="Q3",
    text="What are the KEY PLOT POINTS in your story that you want the audience to know?",
    description=(
        "Depending on your plot structure, think about:\n"
        "• For Overcoming the Monster: What's your 'monster'? What are you fighting against?\n"
        "• For Rags to Riches: Where did you start? What's the mountain you're climbing?\n"
        "• For The Quest: What's your goal/destination? What trials are you facing?\n"
        "• For Voyage and Return: What new worlds are you exploring?\n"
        "• For Comedy: What recurring characters, jokes, or themes make your brand funny?\n"
        "• For Tragedy: What struggles, darkness, or emotional themes are you exploring?\n"
        "• For Rebirth: What trapped you? How were you freed/reborn?"
    ),
    type=QuestionType.PARAGRAPH,
    validation=ValidationRule(required=True, min_length=100),
)

Q9 = Question(
    id="Q9",
    text="What is your point of view?",
    description="What do you stand for? What's your unique perspective on music/culture/your scene?",
    type=QuestionType.PARAGRAPH,
    validation=ValidationRule(required=True, min_length=100),
)

Q10 = Question(
    id="Q10",
    text="What is your aesthetic?",
    description="Describe the overall visual vibe/world you want to create",
    type=QuestionType.PARAGRAPH,
    validation=ValidationRule(required=True, min_length=100),
)

Q13 = Question(
    id="Q13",
    text="In one sentence, what makes you different from other DJs in your genre?",
    type=QuestionType.SHORT_ANSWER,
    validation=ValidationRule(required=True, min_length=10),
)

# Brand Boundaries Questions
Q15 = Question(
    id="Q15",
    text="What will your brand ALWAYS be about?",
    description=(
        "What themes or elements will consistently appear in everything you do? "
        "These are your 'positive protective constraints' - the things that define your world"
    ),
    type=QuestionType.PARAGRAPH,
    validation=ValidationRule(required=True, min_length=100),
)

Q16 = Question(
    id="Q16",
    text="What should NEVER appear in your brand?",
    description="Colors, styles, vibes, themes, topics, or elements you want to avoid",
    type=QuestionType.SHORT_ANSWER,
    validation=ValidationRule(required=True, min_length=10),
)

# Color Palette Questions
Q28 = Question(
    id="Q28",
    text="Describe the color palette for your brand (in words, not hex codes)",
    description=(
        "Examples: 'neon pink and electric blue with black backgrounds', "
        "'earthy browns and forest greens', 'monochrome black and white with red accents', "
        "'pastel sunset colors', etc."
    ),
    type=QuestionType.PARAGRAPH,
    validation=ValidationRule(required=True, min_length=50),
)

Q29 = Question(
    id="Q29",
    text="What is the dominant/base color of your brand?",
    type=QuestionType.SHORT_ANSWER,
    validation=ValidationRule(required=True, min_length=5),
)

Q30 = Question(
    id="Q30",
    text="What is your accent/pop color?",
    description="The color that makes things stand out",
    type=QuestionType.SHORT_ANSWER,
    validation=ValidationRule(required=True, min_length=5),
)

# Elevator Pitch
Q44 = Question(
    id="Q44",
    text="Elevator Pitch: In 3 sentences or less, describe your brand story.",
    description=(
        "What's the show your fans are tuning in to watch?\n\n"
        "Examples:\n"
        "• 'Isoxo and Knock2: Two high-energy rebel brands that focus on freedom of expression. "
        "The brand celebrates outcasts and ignites a feeling of positive rebellion at every turn. "
        "The visual identity has an edge with undertones of nostalgia, rock, and metal influences.'\n"
        "• 'Two friends: An everyman brand about two lifelong best friends focused on relatability and fun. "
        "The two bring you into their normal, authentic world where extraordinary moments happen.'"
    ),
    type=QuestionType.PARAGRAPH,
    validation=ValidationRule(required=True, min_length=100),
)

# Visual References
Q45 = Question(
    id="Q45",
    text="Upload 5-15 images that capture your ideal aesthetic",
    description=(
        "These should NOT be other music artists. Look to films, fashion, art books, magazines, "
        "things you loved growing up, architecture, nature, etc. This is one of the most important "
        "parts - show us what visually inspires you from OUTSIDE the music world."
    ),
    type=QuestionType.FILE_UPLOAD,
    validation=ValidationRule(
        required=True,
        allowed_file_types=["image/jpeg", "image/jpg", "image/png", "image/webp"],
        max_file_size_mb=20,
        max_total_size_mb=200,
        min_files=5,
        max_files=15,
    ),
)

Q47 = Question(
    id="Q47",
    text="Briefly describe what you like about the reference images you uploaded",
    type=QuestionType.SHORT_ANSWER,
    validation=ValidationRule(required=True, min_length=50),
)

# Export all questions in order
QUESTIONS = [
    Q1,   # Archetype
    Q2,   # Story arc
    Q3,   # Key plot points
    Q9,   # Point of view
    Q10,  # Aesthetic
    Q13,  # Differentiator
    Q15,  # Always about
    Q16,  # Never about
    Q28,  # Color palette description
    Q29,  # Base color
    Q30,  # Accent color
    Q44,  # Elevator pitch
    Q45,  # Reference images (file upload)
    Q47,  # Reference image description
]

# Helper to get question by ID
def get_question_by_id(question_id: str) -> Question:
    """
    Retrieve a question by its ID.
    
    Args:
        question_id: Question identifier (e.g., "Q1", "Q45")
    
    Returns:
        Question object if found
    
    Raises:
        ValueError: If question_id not found
    """
    for question in QUESTIONS:
        if question.id == question_id:
            return question
    raise ValueError(f"Question with ID '{question_id}' not found")

