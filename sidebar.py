# Enhanced Climate Finance Maturity Tool (Streamlit App)
import streamlit as st
import openai
import os
import base64
import pandas as pd
from fpdf import FPDF
import PyPDF2
import docx
from io import BytesIO
import re

# Set OpenAI API key using environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY environment variable not set.")
    st.stop()
openai.api_key = api_key

# AI scoring function with refined prompt and error handling
def get_ai_score(prompt, user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return response["choices"][0]["message"]["content"].strip()
    except openai.OpenAIError as oe:
        return f"OpenAI API error: {str(oe)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# More reliable score extraction from AI output
def extract_avg_score(output):
    scores = re.findall(r"\(\d\)[^:\n]+:\s*(\d)", output)
    digits = [int(s) for s in scores if s.isdigit() and 0 <= int(s) <= 3]
    return round(sum(digits) / len(digits), 2) if digits else None

# Function to extract text from uploaded file
def extract_text_from_file(uploaded_file):
    text = ""
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text
    return text

# PDF generation

def generate_pdf_from_recommendations(recommendations):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="AI-Based Recommendations for Action", ln=True, align="C")
    pdf.ln(10)
    for recommendation in recommendations:
        pdf.multi_cell(0, 10, recommendation)
    pdf_bytes = pdf.output(dest='S').encode('latin1', 'replace')
    return BytesIO(pdf_bytes)

# Streamlit UI setup
st.set_page_config(page_title="Climate Finance Maturity Tool", layout="wide")
st.sidebar.image("https://raw.githubusercontent.com/fgaschick/cfed-ai-tool/main/Chemonics_RGB_Horizontal_BLUE-WHITE.png", use_container_width=True)
st.sidebar.markdown("""
<style>
[data-testid="stSidebar"] > div:first-child {
    background-color: #005670;
    padding-top: 1rem;
    color: white;
}
[data-testid="stSidebar"] * {
    color: white !important;
}
section.main label span,
section.main div[class^="st"] label span,
section.main input[type="checkbox"] + div div,
section.main input[type="radio"] + div div {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)
st.sidebar.title("Climate Finance Ecosystem Diagnostic (CFED)")
st.sidebar.subheader("AI-Assisted Maturity Scoring Tool")

# Tabs
TABS = ["Instructions", "Enabling Environment", "Ecosystem Infrastructure", "Finance Providers", "Finance Seekers", "Summary & Recommendations"]
selected_tab = st.sidebar.radio("Choose a tab", TABS)

# Score storage
if "dimension_scores" not in st.session_state:
    st.session_state.dimension_scores = {
        "Enabling Environment": 0,
        "Ecosystem Infrastructure": 0,
        "Finance Providers": 0,
        "Finance Seekers": 0
    }

# Instructions Tab
if selected_tab == "Instructions":
    st.markdown("""
    ## Instructions
    This tool assesses the maturity of a country's climate finance ecosystem.
    You may either manually score each dimension (via checkboxes) or let AI assign a score (via text + upload).
    Once all dimensions are scored, visit the "Summary & Recommendations" tab to view results and download.
    """)

# Main AI/Manual scoring tab logic
def ai_scoring_tab(title, prompt, key):
    st.title(f"{title} Scoring")
    use_ai = st.checkbox(f"Use AI to score {title}", value=False, key=f"ai_{key}")
    if use_ai:
        narrative = st.text_area("Enter narrative:", height=300, key=f"text_{key}", value=st.session_state.get(f"text_{key}", ""))
        uploaded_file = st.file_uploader("Upload file (PDF or DOCX)", type=["pdf", "docx"], key=f"file_{key}")
        if uploaded_file:
            narrative += extract_text_from_file(uploaded_file)
        if narrative:
            with st.spinner("Scoring with AI..."):
                output = get_ai_score(prompt, narrative)
                st.markdown("**AI Output:**")
                st.markdown(output)
                avg_score = extract_avg_score(output)
                st.session_state.dimension_scores[title] = avg_score if avg_score is not None else 2
                if avg_score is None:
                    st.warning("Could not extract valid scores. Defaulting to 2.")
    else:
        st.markdown("### Manual Scoring")
        st.info("Each checkbox equals 1 point. Max score is 4.")
        checklist = []
        if title == "Enabling Environment":
            checklist = [
                st.checkbox("NDC submitted", key=f"{key}_s1"),
                st.checkbox("NDC linked to implementation plans", key=f"{key}_s2"),
                st.checkbox("NDC includes finance targets/mechanisms", key=f"{key}_s3"),
                st.checkbox("National climate finance strategy exists", key=f"{key}_s4")
            ]
        elif title == "Ecosystem Infrastructure":
            checklist = [
                st.checkbox("Physical infrastructure for mitigation/adaptation exists", key=f"{key}_s1"),
                st.checkbox("National climate data system in place", key=f"{key}_s2"),
                st.checkbox("Digital platforms accessible", key=f"{key}_s3"),
                st.checkbox("Regulatory frameworks operational", key=f"{key}_s4")
            ]
        elif title == "Finance Providers":
            checklist = [
                st.checkbox("Public providers active", key=f"{key}_s1"),
                st.checkbox("Private sector engaged", key=f"{key}_s2"),
                st.checkbox("DFIs provide substantial support", key=f"{key}_s3"),
                st.checkbox("MDBs active in ecosystem", key=f"{key}_s4")
            ]
        elif title == "Finance Seekers":
            checklist = [
                st.checkbox("Good quality proposals developed", key=f"{key}_s1"),
                st.checkbox("Strong pipeline exists", key=f"{key}_s2"),
                st.checkbox("Finance is accessible", key=f"{key}_s3"),
                st.checkbox("Stakeholder engagement strong", key=f"{key}_s4")
            ]
        score = sum(checklist)
        st.session_state.dimension_scores[title] = score
        st.markdown(f"**Score: {score}/4**")

# Tabs
if selected_tab == "Enabling Environment":
    ai_scoring_tab("Enabling Environment", "Assess strategy, policy, enforcement, and stakeholder consultation (0–3 each). Format: (1) Strategy: x ... (4) Stakeholder: x.", "env")
elif selected_tab == "Ecosystem Infrastructure":
    ai_scoring_tab("Ecosystem Infrastructure", "Assess physical infrastructure, data systems, digital platforms, and regulatory frameworks (0–3 each).", "infra")
elif selected_tab == "Finance Providers":
    ai_scoring_tab("Finance Providers", "Assess public, private, DFI, and MDB engagement in climate finance (0–3 each).", "providers")
elif selected_tab == "Finance Seekers":
    ai_scoring_tab("Finance Seekers", "Assess quality of proposals, project pipeline, accessibility of finance, and stakeholder engagement (0–3 each).", "seekers")
elif selected_tab == "Summary & Recommendations":
    st.title("Summary & Recommendations")
    recommendations = []
    for dim, score in st.session_state.dimension_scores.items():
        if score < 3:
            prompt = f"Provide 3–5 targeted recommendations to improve the '{dim}' dimension, currently scored {score}/4."
            recs = get_ai_score(prompt, "")
            recommendations.append(f"### {dim}\n{recs}")
    for rec in recommendations:
        st.markdown(rec)
    pdf_output = generate_pdf_from_recommendations(recommendations)
    st.download_button("Download Recommendations as PDF", data=pdf_output, file_name="cfed_recommendations.pdf", mime="application/pdf")

# Sidebar Overview
st.sidebar.markdown("## Scores Overview")
for dim, score in st.session_state.dimension_scores.items():
    st.sidebar.markdown(f"**{dim}**: {score}/4")
combined_score = round(sum(st.session_state.dimension_scores.values()) / 4, 2)
tier, color = ("Low", "#e57373") if combined_score < 1.5 else ("Medium", "#fdd835") if combined_score < 2.5 else ("High", "#81c784")
st.sidebar.markdown(f"**Combined Score**: <span style='color:{color}'>{combined_score}/4 – {tier} Maturity</span>", unsafe_allow_html=True)

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
