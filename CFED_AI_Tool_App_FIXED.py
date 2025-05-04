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

# Categories and scoring for all dimensions
def manual_scoring_ui(dimension):
    st.markdown(f"### {dimension}")
    
    if dimension == "Enabling Environment":
        # Add relevant questions for Enabling Environment
        st.markdown("#### Strategy")
        s1 = st.checkbox("Country has submitted an NDC")
        s2 = st.checkbox("NDC is linked to investment or implementation plans")
        s3 = st.checkbox("NDC or strategy includes financing targets or mechanisms")
        s4 = st.checkbox("There is a national climate finance strategy or roadmap")
        notes_strategy = st.text_area("Notes for Strategy:", key="notes_strategy")

        st.markdown("#### Policy")
        p1 = st.checkbox("Sectoral policies (energy, land use, etc.) integrate climate objectives")
        p2 = st.checkbox("Policies include clear implementation mechanisms")
        p3 = st.checkbox("Private sector is consulted or involved in policy development")
        notes_policy = st.text_area("Notes for Policy:", key="notes_policy")

        st.markdown("#### Enforcement")
        e1 = st.checkbox("Climate-related laws or regulations exist")
        e2 = st.checkbox("There is a functioning judiciary or legal redress mechanism")
        e3 = st.checkbox("Anti-corruption measures are actively implemented")
        notes_enforcement = st.text_area("Notes for Enforcement:", key="notes_enforcement")

        st.markdown("#### Stakeholder Consultation")
        c1 = st.checkbox("Stakeholders (civil society, academia) are engaged in planning")
        c2 = st.checkbox("Indigenous Peoples, women, youth are specifically included")
        c3 = st.checkbox("Consultations are recurring and documented")
        notes_consultation = st.text_area("Notes for Consultation:", key="notes_consultation")

        # Compute maturity score
        score = sum([s1, s2, s3, s4, p1, p2, p3, e1, e2, e3, c1, c2, c3])
        total_score = min(3, score)
        return total_score, "score-medium"

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
        return total_score, "score-medium"

    if dimension == "Finance Providers":
        # Add relevant questions for Finance Providers
        st.markdown("#### Public Climate Finance")
        f1 = st.checkbox("Public funding is allocated to climate projects")
        f2 = st.checkbox("The national budget supports climate adaptation and mitigation")
        notes_public_funding = st.text_area("Notes for Public Funding:", key="notes_public_funding")
        
        st.markdown("#### Private Sector Engagement")
        p1 = st.checkbox("Private investment in climate projects is encouraged")
        p2 = st.checkbox("Public-private partnerships are established for climate finance")
        notes_private_sector = st.text_area("Notes for Private Sector:", key="notes_private_sector")
        
        # Compute maturity score
        score = sum([f1, f2, p1, p2])
        total_score = min(3, score)
        return total_score, "score-medium"

    if dimension == "Finance Seekers":
        # Add relevant questions for Finance Seekers
        st.markdown("#### Project Pipeline")
        p1 = st.checkbox("A robust pipeline of climate projects exists")
        p2 = st.checkbox("Projects are ready for financing")
        notes_project_pipeline = st.text_area("Notes for Project Pipeline:", key="notes_project_pipeline")
        
        st.markdown("#### Sectoral Engagement")
        s1 = st.checkbox("Projects span multiple sectors: mitigation, adaptation, NBS")
        s2 = st.checkbox("Key stakeholders are involved in the project design process")
        notes_sectoral_engagement = st.text_area("Notes for Sectoral Engagement:", key="notes_sectoral_engagement")
        
        # Compute maturity score
        score = sum([p1, p2, s1, s2])
        total_score = min(3, score)
        return total_score, "score-medium"

    return None, None

# Add the sidebar for selecting categories
st.sidebar.title("Dimensions")
dimension = st.sidebar.radio(
    "Select a dimension to evaluate:",
    ["Instructions", "Enabling Environment", "Ecosystem Infrastructure", "Finance Providers", "Finance Seekers"]
)

# Show the instructions first
if dimension == "Instructions":
    st.markdown("""
    ## Instructions
    1. Choose a dimension to evaluate.
    2. Use AI to score or fill in the manual inputs.
    3. AI-generated recommendations will be shown if selected.
    """)

else:
    # Run the scoring UI for the selected dimension
    ee_total_score, score_class = manual_scoring_ui(dimension)

    # AI-based scoring
    use_ai_ee = st.checkbox("Use AI to score this dimension", value=False)
    if use_ai_ee:
        narrative_ee = st.text_area(f"Provide a narrative description for {dimension}:", height=300)
        if narrative_ee:
            with st.spinner(f"Analyzing with AI for {dimension}..."):
                prompt = f"You are a climate finance expert. Assess the maturity of {dimension} and provide a score with recommendations."
                output = get_ai_score(prompt, narrative_ee)
                st.markdown("**AI-Generated Assessment and Recommendations:**")
                st.markdown(output)

    st.markdown(f"### {dimension} Score: {ee_total_score}/3")
    st.markdown(f"**AI Recommendations for {dimension}:**")
    # Use AI for recommendations based on the score

# Floating live score
if ee_total_score is not None:
    st.markdown(f"""
    <div class="bottom-box {score_class}" style="bottom: 60px; right: 30px; position: fixed;">
        <strong>Live {dimension} Score:</strong><br> {ee_total_score}/3
    </div>
    """, unsafe_allow_html=True)

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

