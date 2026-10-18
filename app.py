import base64
import os

import streamlit as st
from groq import Groq


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Student Helper",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Professional study-themed styling
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:wght@500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: #f5f7fb;
        }

        .main .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .hero {
            background: linear-gradient(135deg, #102a43 0%, #173f5f 58%, #1f5f7a 100%);
            padding: 2.4rem 2.5rem;
            border-radius: 22px;
            color: white;
            margin-bottom: 1.6rem;
            box-shadow: 0 14px 35px rgba(16, 42, 67, 0.15);
        }

        .hero h1 {
            font-family: 'Source Serif 4', serif;
            font-size: 2.55rem;
            margin: 0 0 .35rem 0;
            color: white;
        }

        .hero p {
            color: #dceaf4;
            font-size: 1.02rem;
            margin: 0;
            max-width: 760px;
            line-height: 1.65;
        }

        .eyebrow {
            color: #b9d9ea;
            font-size: .78rem;
            font-weight: 700;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin-bottom: .7rem;
        }

        .section-title {
            font-family: 'Source Serif 4', serif;
            color: #102a43;
            font-size: 1.55rem;
            font-weight: 700;
            margin: 1.2rem 0 .35rem;
        }

        .section-subtitle {
            color: #627d98;
            margin-bottom: 1rem;
        }

        .feature-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1rem;
            min-height: 125px;
        }

        .feature-icon {
            font-size: 1.45rem;
        }

        .feature-title {
            color: #102a43;
            font-weight: 700;
            margin-top: .45rem;
        }

        .feature-text {
            color: #627d98;
            font-size: .88rem;
            line-height: 1.45;
            margin-top: .25rem;
        }

        .answer-label {
            color: #1f5f7a;
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .1em;
            text-transform: uppercase;
            margin: 1.2rem 0 .5rem;
        }

        .footer {
            text-align: center;
            color: #829ab1;
            font-size: .78rem;
            margin-top: 2.5rem;
            padding-top: 1.2rem;
            border-top: 1px solid #dfe7ee;
        }

        [data-testid="stSidebar"] {
            background: #102a43;
        }

        [data-testid="stSidebar"] * {
            color: #e7f0f6;
        }

        [data-testid="stSidebar"] .stCaption {
            color: #b9cddd;
        }

        div.stButton > button {
            border-radius: 10px;
            font-weight: 700;
            min-height: 2.75rem;
        }

        .stTextArea textarea, .stTextInput input {
            border-radius: 11px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
# Image questions need a vision-capable model. Change these names if
# Groq retires them (see https://console.groq.com/docs/models).
TEXT_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

MAX_IMAGE_BYTES = 3 * 1024 * 1024  # Groq limits base64 images to ~4 MB

SYSTEM_PROMPT = """You are AI Student Helper, an expert secondary-school teacher and academic tutor.

Your main audience is Grade 10 / Class 10 students. Answer according to a
Class 10 learning level: accurate, clear, structured, and educational.

Important rules:
1. Read the student's question or image carefully.
2. If an image contains a textbook question, worksheet, handwritten question,
   diagram, project prompt, or mathematical/scientific problem, identify the
   actual task before answering.
3. Give the correct answer, but also teach the student how and why it works.
4. Never invent information when the image is unclear. If a key part cannot
   be read, explicitly say what is unclear and ask for a clearer image.
5. Use simple language without becoming childish.
6. Use equations, bullet points, numbered steps, and examples where useful.
7. For a normal conceptual topic, use this structure:
   - Definition
   - Explanation
   - Key Points
   - Example(s)
   - Conclusion
8. For a numerical/problem-solving question, use:
   - Given
   - Required
   - Formula/Rule
   - Step-by-step solution
   - Final Answer
   - Quick check (when useful)
9. For a project/report request, use:
   - Title
   - Introduction
   - Definition / Background
   - Main Explanation
   - Examples / Applications
   - Conclusion
   - Short list of important points
10. Keep the answer aligned with a school student's curriculum and avoid
    unnecessary university-level detail.
11. Do not claim certainty when the source image is ambiguous.
12. Encourage understanding rather than simply copying an answer.
"""


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def get_api_key():
    """Read the key from Streamlit secrets, falling back to env variables."""
    try:
        key = st.secrets.get("GROQ_API_KEY")
        if key:
            return key
    except Exception:
        pass  # no secrets.toml present
    return os.getenv("GROQ_API_KEY")


def get_client():
    api_key = get_api_key()
    if not api_key:
        return None
    return Groq(api_key=api_key)


def image_to_data_url(uploaded_file):
    raw = uploaded_file.getvalue()
    if len(raw) > MAX_IMAGE_BYTES:
        raise ValueError(
            "The image is too large. Please use a photo under 3 MB "
            "(lower the camera resolution or crop the image)."
        )
    encoded = base64.b64encode(raw).decode("utf-8")
    mime = uploaded_file.type or "image/jpeg"
    return f"data:{mime};base64,{encoded}"


def ask_groq(question, image_file=None):
    client = get_client()
    if client is None:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Add it to Streamlit secrets "
            "or your environment variables."
        )

    if image_file is not None:
        prompt = (
            "Analyze the attached school-work image. First identify "
            "the question/topic, then provide the most accurate "
            "Class 10 educational answer. Explain every important "
            "step and use the required structure from your instructions."
        )
        if question:
            prompt += f"\n\nStudent's additional instruction:\n{question}"

        user_content = [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": image_to_data_url(image_file)},
            },
        ]
        model = VISION_MODEL
    else:
        user_content = question
        model = TEXT_MODEL

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.25,
        max_completion_tokens=2500,
    )
    return response.choices[0].message.content


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="padding: .5rem 0 1.3rem;">
            <div style="font-size:2rem;">📘</div>
            <div style="font-family:'Source Serif 4',serif;font-size:1.35rem;font-weight:700;">
                AI Student Helper
            </div>
            <div style="color:#b9cddd;font-size:.82rem;margin-top:.25rem;">
                A focused learning companion for Class 10
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### How to use")
    st.caption("1. Type a topic or question.")
    st.caption("2. Or upload/take a photo of the work.")
    st.caption("3. Add an optional instruction.")
    st.caption("4. Select **Generate Explanation**.")

    st.markdown("---")
    st.markdown("### Supported input")
    st.caption("• Text questions")
    st.caption("• Textbook pages")
    st.caption("• Homework")
    st.caption("• Project prompts")
    st.caption("• Handwritten questions")
    st.caption("• Diagrams and worksheets")

    st.markdown("---")
    st.caption("Powered by Groq • Designed for learning")

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">CLASS 10 • LEARNING ASSISTANT</div>
        <h1>Learn the concept. Understand the answer.</h1>
        <p>
            Ask about any school topic or scan your project/question.
            AI Student Helper turns it into a clear, structured explanation
            with definitions, reasoning, examples and a conclusion.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Feature row
# ---------------------------------------------------------
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <div class="feature-title">Curriculum-Friendly</div>
            <div class="feature-text">Explanations are written for a Class 10 level.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📷</div>
            <div class="feature-title">Ask from a Photo</div>
            <div class="feature-text">Upload or capture a textbook, worksheet or project.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <div class="feature-title">Structured Answers</div>
            <div class="feature-text">Definitions, explanations, examples and conclusions.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# Input area
# ---------------------------------------------------------
st.markdown(
    '<div class="section-title">What are you studying?</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">Type your question, upload a photo, or use both.</div>',
    unsafe_allow_html=True,
)

question = st.text_area(
    "Question or topic",
    placeholder=(
        "Example: Explain photosynthesis and write its importance.\n"
        "Or: Solve this quadratic equation step by step."
    ),
    height=145,
    label_visibility="collapsed",
)

col_a, col_b = st.columns(2)

with col_a:
    uploaded = st.file_uploader(
        "Upload a project or question photo",
        type=["jpg", "jpeg", "png", "webp"],
        help="Use a clear, well-lit photo. Keep the complete question visible.",
    )

with col_b:
    camera = st.camera_input(
        "Take a photo directly",
        help="Capture a clear photo of the question or project.",
    )

image_file = camera if camera is not None else uploaded

if image_file:
    st.image(
        image_file,
        caption="Selected study material",
        use_container_width=True,
    )

st.markdown("")
generate = st.button(
    "✨  Generate Explanation",
    type="primary",
    use_container_width=True,
)

# ---------------------------------------------------------
# Generate answer
# ---------------------------------------------------------
if generate:
    if not question.strip() and image_file is None:
        st.warning("Please enter a topic/question or provide a photo first.")
    else:
        with st.spinner("Preparing a teacher-style explanation..."):
            try:
                answer = ask_groq(question.strip(), image_file)
            except Exception as exc:
                st.error(f"Unable to generate the answer: {exc}")
                st.info(
                    "Check that your GROQ_API_KEY is correctly configured and "
                    "that the selected Groq model is available to your account."
                )
                answer = None

        if answer:
            st.markdown(
                '<div class="answer-label">Teacher\'s Explanation</div>',
                unsafe_allow_html=True,
            )
            with st.container(border=True):
                st.markdown(answer)

            st.download_button(
                "Download this explanation",
                data=answer,
                file_name="ai_student_helper_answer.txt",
                mime="text/plain",
                use_container_width=True,
            )

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown(
    """
    <div class="footer">
        AI Student Helper • Built to support understanding, not just copying answers.
        Always review important schoolwork with your teacher or textbook.
    </div>
    """,
    unsafe_allow_html=True,
)
