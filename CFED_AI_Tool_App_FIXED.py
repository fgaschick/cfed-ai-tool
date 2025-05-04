import streamlit as st
from openai import OpenAI
import os
from PyPDF2 import PdfReader
import docx

# Set OpenAI API key using environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY environment variable not set.")
    st.stop()

client = OpenAI(api_key=api_key)

def get_ai_score(prompt, user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI error: {str(e)}"

# Page configuration
st.set_page_config(page_title="Climate Finance Maturity Assessment Tool", layout="wide")

# Custom header and footer with logo
import streamlit.components.v1 as components

components.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    body {
        font-family: 'Roboto', sans-serif;
        background-color: #f5f5f5;
    }
    .custom-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100vw;
        background-color: #005670;
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 13px;
        z-index: 1000;
    }
    .header-bar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        background-color: #005670;
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 13px;
        z-index: 1001;
    }
    .header-bar img {
        max-height: 30px;
    }
    .bottom-box {
        position: fixed;
        bottom: 60px;
        right: 30px;
        padding: 10px 20px;
        border-radius: 8px;
        z-index: 1001;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
        font-weight: bold;
        color: white;
    }
    .score-low { background-color: #e57373; }
    .score-medium { background-color: #fdd835; }
    .score-high { background-color: #81c784; }
    </style>

    <div class='header-bar'>
        <img src='https://raw.githubusercontent.com/fgaschick/cfed-ai-tool/main/Chemonics_RGB_Horizontal_BLUE-WHITE.png' alt='Chemonics Logo'/>
    </div>
    <div style='height: 100px;'></div>
    
""", height=150, scrolling=False)

# Categories and scoring for Ecosystem Infrastructure
def manual_scoring_ui(dimension):
    st.markdown(f"### {dimension}")
    
    if dimension == "Ecosystem Infrastructure":
        # Add relevant questions for Ecosystem Infrastructure
        st.markdown("#### Monitoring, Reporting, and Verification (MRV)")
        m1 = st.checkbox("MRV systems and climate data tools are in place")
        m2 = st.checkbox("Stakeholders are actively engaged in MRV design")
        notes_mrv = st.text_area("Notes for MRV:", key="notes_mrv")
        
        st.markdown("#### Institutional Capacity")
        i1 = st.checkbox("Key institutions have the capacity to implement climate actions")
        i2 = st.checkbox("Government institutions coordinate effectively on climate finance")
        notes_institutional_capacity = st.text_area("Notes for Institutional Capacity:", key="notes_institutional_capacity")
        
        st.markdown("#### Climate Finance Policies")
        c1 = st.checkbox("Policies effectively promote climate resilience and low-carbon development")
        c2 = st.checkbox("Financial mechanisms are in place to support climate finance")
        notes_climate_policies = st.text_area("Notes for Climate Policies:", key="notes_climate_policies")
        
        # Compute maturity score
        score = sum([m1, m2, i1, i2, c1, c2])
        total_score = min(3, score)
        return total_score, "score-medium"  # You can adjust the color as per the score

    return None, None

# Add the sidebar for selecting categories
st.sidebar.title("Dimensions")
dimension = st.sidebar.radio(
    "Select a dimension to evaluate:",
    ["Instructions", "Enabling Environment", "Ecosystem Infrastructure", "Finance Providers"]
)

# Show the instructions first
if dimension == "Instructions":
    st.markdown("""
    ## Instructions
    1. Choose a dimension to evaluate.
    2. Use AI to score or fill in the manual inputs.
    3. AI-generated recommendations will be shown if selected.
    """)

elif dimension == "Ecosystem Infrastructure":
    # Run the scoring UI for Ecosystem Infrastructure
    ee_total_score, score_class = manual_scoring_ui(dimension)

    # AI-based scoring
    use_ai_ee = st.checkbox("Use AI to score Ecosystem Infrastructure", value=False)
    if use_ai_ee:
        narrative_ee = st.text_area("Provide a narrative description of the ecosystem infrastructure:", height=300)
        if narrative_ee:
            with st.spinner("Analyzing with AI..."):
                prompt = "You are a climate finance expert. Assess the maturity of the ecosystem infrastructure and provide a score with recommendations."
                output = get_ai_score(prompt, narrative_ee)
                st.markdown("**AI-Generated Assessment and Recommendations:**")
                st.markdown(output)
    st.markdown(f"### Ecosystem Infrastructure Score: {ee_total_score}/3")
    st.markdown(f"**AI Recommendations for Ecosystem Infrastructure:**")
    # Use AI for recommendations based on the score

# Footer
st.markdown("""
<style>
.footer-fixed {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100vw;
    background-color: #005670;
    color: white;
    text-align: center;
    padding: 10px;
    font-size: 13px;
    z-index: 1000;
}
</style>
<div class='footer-fixed'>
    © 2025 Chemonics International Inc. | Contact: Climate Finance Team
</div>
""", unsafe_allow_html=True)

