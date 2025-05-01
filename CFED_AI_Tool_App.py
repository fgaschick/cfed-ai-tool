import streamlit as st
import openai
import os
import base64
import pandas as pd
from fpdf import FPDF

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Page configuration
st.set_page_config(page_title="CFED AI Diagnostic Tool", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    .custom-footer { 
        position: fixed; 
        left: 0; 
        bottom: 0; 
        width: 100%; 
        background-color: #005670; 
        color: white; 
        text-align: center; 
        padding: 10px; 
        font-size: 13px; 
    }
    .header-bar {
        position: fixed;
        top: 0;
        width: 100%;
        background-color: #005670;
        padding: 1em;
        text-align: center;
        z-index: 999;
    }
    .header-bar img {
        width: 200px;
    }
    </style>
    <div class='custom-footer'>
        © 2025 Chemonics International Inc. | Contact: Climate Finance Team
    </div>
    <div class='header-bar'>
        <img src='https://raw.githubusercontent.com/fgaschick/cfed-ai-tool/main/Chemonics_RGB_Horizontal_BLUE-WHITE.png' alt='Chemonics Logo'/>
    </div>
    <br><br><br><br>
""", unsafe_allow_html=True)

st.title("Climate Finance Ecosystem Diagnostic (CFED)")
st.subheader("AI-Assisted Maturity Scoring Tool – Full Prototype")
with st.expander("📘 Walkthrough Guide – How to Use This Tool"):
    st.markdown("""
    1. Start with **Enabling Environment**.
       - Use **AI Scoring** to type a short description, or **Manual Scoring** to answer yes/no questions.

    2. Move to **Ecosystem Infrastructure**, **Finance Providers**, and **Finance Seekers** the same way.

    3. Scroll down to **Results Summary** to view your scores and the average maturity level.

    4. Click the download links to **export results** as a PDF or CSV.

    You can go back and edit your responses at any time.
    """)

st.markdown("""
    This tool is designed by Chemonics International to help governments, donors, and implementing partners rapidly assess the maturity of a country's climate finance ecosystem.
    
    Users can choose either AI-generated scoring or manual scoring for four key areas:
    - Enabling Environment
    - Ecosystem Infrastructure
    - Finance Providers
    - Finance Seekers
    The tool helps identify maturity gaps, prioritize investments, and track progress over time. Results can be exported in PDF and CSV formats.
    """)

st.markdown("""
This interactive tool estimates the maturity of a country’s climate finance ecosystem across all four CFED dimensions. You can either use AI-generated scoring (by describing the situation) or answer simple questions.
""")

st.markdown("---")

# --- Helper: AI scoring function ---
def get_ai_score(prompt, user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices.message.content
    except openai.error.OpenAIError as e:
        if hasattr(e, 'http_status') and e.http_status == 429:
            return "⚠️ Your OpenAI quota has been exceeded. Please use manual scoring."
        return f"Error from OpenAI: {e}"
    except Exception as e:
        return f"Error from OpenAI: {e}"

# --- Scoring Data ---
scores_data = []

#
