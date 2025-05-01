
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

# Custom CSS for styling
st.markdown("""
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
        z-index: 1000;
    }
    .header-bar img {
        width: 200px;
    }
    .live-score {
        position: fixed;
        top: 120px;
        right: 30px;
        background-color: #ffffff;
        border: 2px solid #005670;
        padding: 10px;
        border-radius: 8px;
        z-index: 1001;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #005670;
    }
    .stButton>button {
        background-color: #005670;
        color: white;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #003f4f;
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

# Title
st.title("Climate Finance Ecosystem Diagnostic (CFED)")
st.subheader("AI-Assisted Maturity Scoring Tool – Full Prototype")

# Walkthrough Guide
with st.expander("📘 Walkthrough Guide – How to Use This Tool"):
    st.markdown("""
    1. Start with **Enabling Environment**.
       - Use **AI Scoring** to type a short description, or **Manual Scoring** to answer yes/no questions.
    2. Move to **Ecosystem Infrastructure**, **Finance Providers**, and **Finance Seekers** the same way.
    3. Scores in the upper right will update as you provide responses. Scroll down to see recommended actions once you complete the assessment.
    4. Click the download links to **export results** as a PDF or CSV.
    5. You can go back and edit your responses at any time.
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

# --- Helper: AI scoring function ---
def get_ai_score(prompt, user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use your desired model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{prompt}\n{user_input}"}
            ],
            max_tokens=150  # Limit the number of tokens for response
        )
        return response.choices.message['content'].strip()  # Extract the AI-generated score
    except openai.error.OpenAIError as e:  # Handle specific OpenAI errors
        if e.http_status == 429:
            return "⚠️ Your OpenAI quota has been exceeded. Please use manual scoring."
        return f"Error from OpenAI: {e}"
    except Exception as e:
        return f"Unexpected error from OpenAI: {e}"

# --- Scoring Data ---
scores_data = []

# --- 1. Enabling Environment ---
st.markdown("""
<div style='background-color:#E5F3F8;padding:1.2em;border-radius:10px;'>
<h3 style='color:#005670'>1. Enabling Environment</h3>
</div>
""", unsafe_allow_html=True)

if st.checkbox("Use AI to score Enabling Environment", value=False):
    text_ee = st.text_area("Describe the enabling environment (e.g., NDCs, enforcement, sector policies):", height=200)
    if text_ee:
        with st.spinner("Scoring with AI..."):
            result_ee = get_ai_score("You are a climate finance expert. Score the enabling environment from 1 to 4 based on the country description. Justify the score.", text_ee)
            st.markdown("**AI Suggested Score and Rationale:**")
            st.markdown(result_ee)
else:
    has_ndc = st.radio("Has the country submitted an NDC?", ["No", "Yes"], index=1, help="NDC refers to a Nationally Determined Contribution under the Paris Agreement. This indicates whether the country has committed to climate targets.")
    ndc_quality = st.selectbox("How ambitious is the NDC?", ["Low", "Medium", "High"], help="Refers to how clearly the NDC outlines its goals, targets, and implementation measures.")
    has_sector_policies = st.radio("Are there sector-specific climate policies?", ["No", "Yes"], index=1, help="Considers whether climate adaptation or mitigation plans exist in key sectors such as energy, transport, agriculture, and health.")
    has_enforcement = st.radio("Are climate laws and policies enforced predictably?", ["No", "Yes"], index=1, help="Refers to how reliably climate-related regulations and policies are applied, monitored, and enforced by government institutions.")
    
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

if st.checkbox("Use AI to score Ecosystem Infrastructure", value=False):
    text_ei = st.text_area("Describe the ecosystem infrastructure (e.g., MRV systems, data, institutional capacity):", height=200)
    if text_ei:
        with st.spinner("Scoring with AI..."):
            result_ei = get_ai_score("You are a climate finance expert. Score the ecosystem infrastructure from 1 to 4 based on the country description. Justify the score.", text_ei)
            st.markdown("**AI Suggested Score and Rationale:**")
            st.markdown(result_ei)
else:
    has_mrv = st.radio("Are MRV systems and climate data tools in place?", ["No", "Yes"], index=1, help="MRV refers to Monitoring, Reporting, and Verification systems that track emissions, adaptation actions, or finance flows.")
    has_partnerships = st.radio("Are there active stakeholder networks and partnerships?", ["No", "Yes"], index=1, help="Refers to formal or informal collaboration among government, private sector, academia, and civil society on climate finance or policy.")
    has_climate_capacity = st.radio("Do institutions have adequate climate finance capacity?", ["No", "Yes"], index=1, help="Assesses whether national or subnational institutions have technical, administrative, and financial skills to design, implement, and monitor climate finance.")
    
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

if st.checkbox("Use AI to score Finance Providers", value=False):
    text_fp = st.text_area("Describe the finance providers landscape (e.g., public/private climate finance, carbon markets):", height=200)
    if text_fp:
        with st.spinner("Scoring with AI..."):
            result_fp = get_ai_score("You are a climate finance expert. Score the finance provider ecosystem from 1 to 4 based on the country description. Justify the score.", text_fp)
            st.markdown("**AI Suggested Score and Rationale:**")
            st.markdown(result_fp)
else:
    has_public_climate_funding = st.radio("Is there domestic public funding for climate?", ["No", "Yes"], index=1, help="Checks if the national budget or public financial institutions allocate domestic funds to climate action.")
    has_carbon_market = st.radio("Is the country active in voluntary or compliance carbon markets?", ["No", "Yes"], index=1, help="Carbon markets enable trading of emissions reductions, including domestic or international credits.")
    has_private_investment = st.radio("Is commercial/private capital flowing into climate sectors?", ["No", "Yes"], index=1, help="Determines whether banks, companies, or investors are financing climate-relevant activities such as renewable energy or resilience.")
    
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

if st.checkbox("Use AI to score Finance Seekers", value=False):
    text_fs = st.text_area("Describe the finance seekers (e.g., project pipeline, diversity, inclusion):", height=200)
    if text_fs:
        with st.spinner("Scoring with AI..."):
            result_fs = get_ai_score("You are a climate finance expert. Score the finance seeker readiness from 1 to 4 based on the country description. Justify the score.", text_fs)
            st.markdown("**AI Suggested Score and Rationale:**")
            st.markdown(result_fs)
else:
    has_project_pipeline = st.radio("Is there a robust pipeline of fundable climate projects?", ["No", "Yes"], index=1, help="Assesses if there are well-developed, ready-to-implement projects aligned with climate goals and financing requirements.")
    has_project_diversity = st.radio("Do projects span adaptation, mitigation, and nature-based solutions?", ["No", "Yes"], index=1, help="This means the project pipeline addresses multiple themes: climate adaptation, emission reductions, and ecosystem-based solutions.")
    inclusive_targeting = st.radio("Are vulnerable or underserved groups targeted in project design?", ["No", "Yes"], index=1, help="Considers whether projects prioritize or include groups such as women, youth, Indigenous Peoples, or the poor, who are disproportionately affected by climate change.")
    
    seekers_score = 1
    if has_project_pipeline == "Yes":
        seekers_score += 1
    if has_project_diversity == "Yes":
        seekers_score += 1
    if inclusive_targeting == "Yes":
        seekers_score += 1
    
    seekers_score = min(seekers_score, 4)
    scores_data.append(["Finance Seekers", seekers_score])

# --- Results Section ---
st.markdown("---")
st.markdown("""
<div style='background-color:#E5F3F8;padding:1.2em;border-radius:10px;'>
<h3 style='color:#005670'>Results Summary</h3>
</div>
""", unsafe_allow_html=True)

score_df = pd.DataFrame(scores_data, columns=["Dimension", "Score"])
if not score_df.empty:
    st.dataframe(score_df, use_container_width=True)
st.markdown(f"<div class='live-score'>🧮 <strong>Live Maturity Score:</strong> {round(score_df['Score'].mean(), 2)}/4</div>", unsafe_allow_html=True)
total_average = round(score_df["Score"].mean(), 2)
st.markdown(f"### 🧮 Average Ecosystem Maturity Score: {total_average}/4")

st.markdown("**Suggested Actions:**")
if total_average < 2:
    st.warning("Foundational support needed: Start with policy frameworks, MRV systems, and project pipeline development.")
elif 2 <= total_average < 3:
    st.info("Moderate maturity: Expand partnerships, deepen private finance engagement, and strengthen enforcement.")
else:
    st.success("Strong ecosystem: Prioritize scaling solutions, regional leadership, and blended finance innovation.")

# --- Downloadable CSV ---
csv = score_df.to_csv(index=False)
b64_csv = base64.b64encode(csv.encode()).decode()
href_csv = f'<a href="data:file/csv;base64,{b64_csv}" download="cfed_scores.csv">📥 Download scores as CSV</a>'
st.markdown(href_csv, unsafe_allow_html=True)

# --- Downloadable PDF ---
pdf = FPDF()
pdf.add_page()
logo_file = "Chemonics_RGB_Horizontal_BLUE-WHITE.png"
pdf.image(logo_file, x=10, y=8, w=50)
pdf.set_font("Arial", size=12)
pdf.ln(30)
pdf.cell(200, 10, txt="CFED Maturity Assessment Summary", ln=True, align="C")
pdf.ln(10)
for index, row in score_df.iterrows():
    pdf.cell(200, 10, txt=f"{row['Dimension']}: {row['Score']}/4", ln=True)
pdf.ln(10)
pdf.cell(200, 10, txt=f"Average Maturity Score: {total_average}/4", ln=True)
pdf.ln(20)
pdf.set_font("Arial", style="I", size=11)
pdf.multi_cell(0, 10, "Climate Finance Team\nChemonics International\n2025")
pdf_output = "cfed_scores.pdf"
pdf.output(pdf_output)
with open(pdf_output, "rb") as pdf_file:
    b64_pdf = base64.b64encode(pdf_file.read()).decode()
    href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="cfed_scores.pdf">📄 Download scores as PDF</a>'
st.markdown(href_pdf, unsafe_allow_html=True)

st.markdown("---")
st.caption("Prototype built for CFED AI tool – All Four Dimensions. To view a walkthrough of how to use this tool, visit: https://cfed-tool-guide.streamlit.app. For definitions, see the CFED Glossary.")
st.markdown("""
<style>
.sticky-footer {
  position: fixed;
  bottom: 0;
  width: 100%;
  background-color: #005670;
  color: white;
  text-align: center;
  padding: 10px;
  font-size: 13px;
  z-index: 1000;
}
</style>
<div class='sticky-footer'>
  © 2025 Chemonics International Inc. | Contact: Climate Finance Team
</div>
""", unsafe_allow_html=True)
