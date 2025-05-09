import streamlit as st
from openai import OpenAI
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

client = OpenAI(api_key=api_key)

# AI scoring function
def get_ai_score(prompt, user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt},
                      {"role": "user", "content": user_input}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI error: {str(e)}"

# Extract average score from AI response
def extract_avg_score(output):
    scores = [int(m.group(1)) for m in re.finditer(r"\(\d\)\s+\w+:\s+(\d)", output)]
    if len(scores) == 4:
        return round(sum(scores) / 4, 2)
    return None

# Function to extract text from uploaded document (PDF/Word)
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

# Function to generate a downloadable PDF
def generate_pdf_from_recommendations(recommendations):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="AI-Based Recommendations for Action", ln=True, align="C")
    pdf.ln(10)
    for recommendation in recommendations:
        pdf.multi_cell(0, 10, recommendation)
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer, 'F')
    pdf_buffer.seek(0)
    return pdf_buffer

# Page setup
st.set_page_config(page_title="Climate Finance Maturity Tool", layout="wide")

# Sidebar and navigation
st.sidebar.title("Climate Finance Ecosystem Diagnostic (CFED)")
st.sidebar.subheader("AI-Assisted Maturity Scoring Tool")
tabs = ["Instructions", "Enabling Environment", "Ecosystem Infrastructure", "Finance Providers", "Finance Seekers", "Summary & Recommendations"]
selected_tab = st.sidebar.radio("Choose a tab", tabs)

if "dimension_scores" not in st.session_state:
    st.session_state.dimension_scores = {
        "Enabling Environment": 0,
        "Ecosystem Infrastructure": 0,
        "Finance Providers": 0,
        "Finance Seekers": 0
    }

# Tab: Instructions
if selected_tab == "Instructions":
    st.markdown("""
        ## Instructions
        This tool helps assess the maturity of a country’s climate finance ecosystem.
        You can either manually score each dimension using checkboxes or use the AI to analyze uploaded documents and narratives.
    """)

# Shared function for AI scoring tabs
def ai_scoring_tab(title, prompt, key):
    st.title(f"{title} Scoring")
    use_ai = st.checkbox(f"Use AI to score {title}", value=False, key=f"ai_{key}")
    if use_ai:
        narrative = st.text_area("Enter narrative description:", height=300, key=f"text_{key}")
        uploaded_file = st.file_uploader("Upload document (PDF/DOCX)", type=["pdf", "docx"], key=f"file_{key}")
        if uploaded_file:
            narrative += extract_text_from_file(uploaded_file)
        if narrative:
            with st.spinner("Analyzing with AI..."):
                output = get_ai_score(prompt, narrative)
                st.markdown("**AI-Generated Output:**")
                st.markdown(output)
                avg_score = extract_avg_score(output)
                if avg_score is not None:
                    st.session_state.dimension_scores[title] = avg_score
                else:
                    st.warning("Could not extract scores. Defaulting to 2.")
                    st.session_state.dimension_scores[title] = 2
    else:
        st.write("Manual scoring not shown here. Expand to implement.")

# Tabs for each dimension
if selected_tab == "Enabling Environment":
    ai_scoring_tab("Enabling Environment",
        "You are a climate finance expert. Assess the enabling environment using: (1) Strategy, (2) Policy, (3) Enforcement, (4) Stakeholder consultation. Assign a score 0-3 for each and justify.",
        "env")

elif selected_tab == "Ecosystem Infrastructure":
    ai_scoring_tab("Ecosystem Infrastructure",
        "You are a climate finance expert. Assess ecosystem infrastructure including: (1) Physical infrastructure, (2) Data infrastructure, (3) Digital platforms, (4) Regulatory frameworks. Score 0-3.",
        "infra")

elif selected_tab == "Finance Providers":
    ai_scoring_tab("Finance Providers",
        "You are a climate finance expert. Assess finance providers: (1) Public, (2) Private, (3) DFIs, (4) MDBs. Assign scores 0-3 and justify.",
        "providers")

elif selected_tab == "Finance Seekers":
    ai_scoring_tab("Finance Seekers",
        "You are a climate finance expert. Assess finance seekers: (1) Project proposals, (2) Pipeline of projects, (3) Access to finance, (4) Stakeholder engagement. Score 0-3 each.",
        "seekers")

elif selected_tab == "Summary & Recommendations":
    st.title("Summary & Recommendations")
    recommendations = []
    for dim, score in st.session_state.dimension_scores.items():
        if score < 3:
            rec_prompt = f"Provide 3-5 recommendations for improving {dim} with a current score of {score}."
            recommendations.append(f"### {dim}\n" + get_ai_score(rec_prompt, ""))
    for rec in recommendations:
        st.markdown(rec)
    pdf_output = generate_pdf_from_recommendations(recommendations)
    st.download_button("Download PDF", data=pdf_output, file_name="recommendations.pdf", mime="application/pdf")

# Sidebar Score Summary
st.sidebar.markdown("## Scores Overview")
for dim, score in st.session_state.dimension_scores.items():
    st.sidebar.markdown(f"**{dim}**: {score}/4")
combined_score = round(sum(st.session_state.dimension_scores.values()) / 4, 2)
st.sidebar.markdown(f"**Combined Score**: {combined_score}/4")

# Footer styling
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
