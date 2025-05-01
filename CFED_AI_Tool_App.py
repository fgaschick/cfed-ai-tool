
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
    <style>.custom-footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #005670; color: white; text-align: center; padding: 10px; font-size: 13px; }</style>
    <div class='custom-footer'>
        © 2025 Chemonics International Inc. | Contact: Climate Finance Team
    </div>
""", unsafe_allow_html=True)
st.markdown("""
<div style='position:fixed;top:0;width:100%;background-color:#005670;padding:1em;text-align:center;z-index:999;'>
  <img src='https://raw.githubusercontent.com/fgaschick/cfed-ai-tool/main/Chemonics_RGB_Horizontal_BLUE-WHITE.png' width='200'/>
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
    except openai.OpenAIError as e:
        if hasattr(e, 'http_status') and e.http_status == 429:
            return "⚠️ Your OpenAI quota has been exceeded. Please use manual scoring."
        return f"Error from OpenAI: {e}"
    except Exception as e:
        return f"Error from OpenAI: {e}"

# --- Scoring Data ---
scores_data = []

# --- 1. Enabling Environment ---
st.markdown("""
<div style='background-color:#E5F3F8;padding:1.2em;border-radius:10px;'>
<h3 style='color:#005670'>1. Enabling Environment</h3>
</div>
""", unsafe_allow_html=True)
if st.checkbox("Use AI to score Enabling Environment"):
    text_ee = st.text_area("Describe the enabling environment (e.g., NDCs, enforcement, sector policies):", height=200)
    if text_ee:
        with st.spinner("Scoring with AI..."):
            result_ee = get_ai_score("You are a climate finance expert. Score the enabling environment from 1 to 4 based on the country description. Justify the score.", text_ee)
            st.markdown("**AI Suggested Score and Rationale:**")
            st.markdown(result_ee)
    enabling_score = None
else:
    has_ndc = st.radio("Has the country submitted an NDC?", ["Yes", "No"], help="NDC refers to a Nationally Determined Contribution under the Paris Agreement. This indicates whether the country has committed to climate targets.")
    ndc_quality = st.selectbox("How ambitious is the NDC?", ["High", "Medium", "Low"], help="Refers to how clearly the NDC outlines its goals, targets, and implementation measures. High ambition includes measurable climate outcomes and financing strategies.")
    has_sector_policies = st.radio("Are there sector-specific climate policies?", ["Yes", "No"], help="Considers whether climate adaptation or mitigation plans exist in key sectors such as energy, transport, agriculture, and health.")
    has_enforcement = st.radio("Are climate laws and policies enforced predictably?", ["Yes", "No"], help="Refers to how reliably climate-related regulations and policies are applied, monitored, and enforced by government institutions.")
    enabling_score = 1
    if has_ndc == "Yes":
        enabling_score += 1
        if ndc_quality == "High":
            enabling_score += 1
    if has_sector_policies == "Yes":
        enabling_score += 1
    if has_enforcement == "Yes":
        enabling_score += 1
    enabling_score = min(enabling_score, 4)
    scores_data.append(["Enabling Environment", enabling_score])

# --- 2. Ecosystem Infrastructure ---
st.markdown("""
<div style='background-color:#E5F3F8;padding:1.2em;border-radius:10px;'>
<h3 style='color:#005670'>2. Ecosystem Infrastructure</h3>
</div>
""", unsafe_allow_html=True)
if st.checkbox("Use AI to score Ecosystem Infrastructure"):
    text_ei = st.text_area("Describe the ecosystem infrastructure (e.g., MRV systems, data, institutional capacity):", height=200)
    if text_ei:
        with st.spinner("Scoring with AI..."):
            result_ei = get_ai_score("You are a climate finance expert. Score the ecosystem infrastructure from 1 to 4 based on the country description. Justify the score.", text_ei)
            st.markdown("**AI Suggested Score and Rationale:**")
            st.markdown(result_ei)
    infra_score = None
else:
    has_mrv = st.radio("Are MRV systems and climate data tools in place?", ["Yes", "No"], help="MRV refers to Monitoring, Reporting, and Verification systems that track emissions, adaptation actions, or finance flows.")
    has_partnerships = st.radio("Are there active stakeholder networks and partnerships?", ["Yes", "No"], help="Refers to formal or informal collaboration among government, private sector, academia, and civil society on climate finance or policy.")
    has_climate_capacity = st.radio("Do institutions have adequate climate finance capacity?", ["Yes", "No"], help="Assesses whether national or subnational institutions have technical, administrative, and financial skills to design, implement, and monitor climate finance.")
    infra_score = 1
    if has_mrv == "Yes":
        infra_score += 1
    if has_partnerships == "Yes":
        infra_score += 1
    if has_climate_capacity == "Yes":
        infra_score += 1
    infra_score = min(infra_score, 4)
    scores_data.append(["Ecosystem Infrastructure", infra_score])

# --- 3. Finance Providers ---
st.markdown("""
<div style='background-color:#E5F3F8;padding:1.2em;border-radius:10px;'>
<h3 style='color:#005670'>3. Finance Providers</h3>
</div>
""", unsafe_allow_html=True)
if st.checkbox("Use AI to score Finance Providers"):
    text_fp = st.text_area("Describe the finance providers landscape (e.g., public/private climate finance, carbon markets):", height=200)
    if text_fp:
        with st.spinner("Scoring with AI..."):
            result_fp = get_ai_score("You are a climate finance expert. Score the finance provider ecosystem from 1 to 4 based on the country description. Justify the score.", text_fp)
            st.markdown("**AI Suggested Score and Rationale:**")
            st.markdown(result_fp)
    providers_score = None
else:
    has_public_climate_funding = st.radio("Is there domestic public funding for climate?", ["Yes", "No"], help="Checks if the national budget or public financial institutions allocate domestic funds to climate action.")
    has_carbon_market = st.radio("Is the country active in voluntary or compliance carbon markets?", ["Yes", "No"], help="Carbon markets enable trading of emissions reductions, including domestic or international credits.")
    has_private_investment = st.radio("Is commercial/private capital flowing into climate sectors?", ["Yes", "No"], help="Determines whether banks, companies, or investors are financing climate-relevant activities such as renewable energy or resilience.")
    providers_score = 1
    if has_public_climate_funding == "Yes":
        providers_score += 1
    if has_carbon_market == "Yes":
        providers_score += 1
    if has_private_investment == "Yes":
        providers_score += 1
    providers_score = min(providers_score, 4)
    scores_data.append(["Finance Providers", providers_score])

# --- 4. Finance Seekers ---
st.markdown("""
<div style='background-color:#E5F3F8;padding:1.2em;border-radius:10px;'>
<h3 style='color:#005670'>4. Finance Seekers</h3>
</div>
""", unsafe_allow_html=True)
if st.checkbox("Use AI to score Finance Seekers"):
    text_fs = st.text_area("Describe the finance seekers (e.g., project pipeline, diversity, inclusion):", height=200)
    if text_fs:
        with st.spinner("Scoring with AI..."):
            result_fs = get_ai_score("You are a climate finance expert. Score the finance seeker readiness from 1 to 4 based on the country description. Justify the score.", text_fs)
            st.markdown("**AI Suggested Score and Rationale:**")
            st.markdown(result_fs)
    seekers_score = None
else:
    has_project_pipeline = st.radio("Is there a robust pipeline of fundable climate projects?", ["Yes", "No"], help="Assesses if there are well-developed, ready-to-implement projects aligned with climate goals and financing requirements.")
    has_project_diversity = st.radio("Do projects span adaptation, mitigation, and nature-based solutions?", ["Yes", "No"], help="This means the project pipeline addresses multiple themes: climate adaptation, emission reductions, and ecosystem-based solutions.")
    inclusive_targeting = st.radio("Are vulnerable or underserved groups targeted in project design?", ["Yes", "No"], help="Considers whether projects prioritize or include groups such as women, youth, Indigenous Peoples, or the poor, who are disproportionately affected by climate change.")
    seekers_score = 1
    if has
