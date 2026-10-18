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

        .card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1.2rem 1.35rem;
            box-shadow: 0 5px 18px rgba(16, 42, 67, 0.055);
        }

        .feature-card {
            background: white;
            border: 1px solid #e2e8f0;
