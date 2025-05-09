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
import time

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
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI error: {str(e)}"

# More reliable score extraction
def extract_avg_score(output):
    score_lines = re.findall(r"\(\d\)\s*[^:\n]+:\s*(\d)", output)
    scores = [int(s) for s in score_lines if s.isdigit()]
    if scores:
        return round(sum(scores) / len(scores), 2)
    return None

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

# Handle early reset before anything renders
if "reset_triggered" in st.session_state and st.session_state.reset_triggered:
    # Delay rerun to avoid race condition
    st.session_state.reset_triggered = False
    time.sleep(0.1)
    st.session_state.dimension_inputs = {}
    st.session_state.dimension_scores = {
        "Enabling Environment": 0,
        "Ecosystem Infrastructure": 0,
        "Finance Providers": 0,
        "Finance Seekers": 0
    }
    st.toast("Inputs have been reset. Please wait...", icon="🔄")
    st.stop()

# Reset and session state setup
if "dimension_scores" not in st.session_state:
    st.session_state.dimension_scores = {
        "Enabling Environment": 0,
        "Ecosystem Infrastructure": 0,
        "Finance Providers": 0,
        "Finance Seekers": 0
    }
if "dimension_inputs" not in st.session_state:
    st.session_state.dimension_inputs = {}
if "reset_triggered" not in st.session_state:
    st.session_state.reset_triggered = False

st.sidebar.markdown("""
<style>
section[data-testid="stSidebar"] button {
    color: #2196F3 !important;
    border: 1px solid #2196F3 !important;
    background-color: transparent !important;
}
section[data-testid="stSidebar"] button:hover {
    background-color: #e3f2fd !important;
    color: #1565c0 !important;
    border-color: #1565c0 !important;
}
</style>
""", unsafe_allow_html=True)

if st.sidebar.button("🔁 Reset All Inputs"):
    st.session_state.reset_triggered = True
    st.experimental_rerun()

# Tab setup
tabs = ["Instructions", "Enabling Environment", "Ecosystem Infrastructure", "Finance Providers", "Finance Seekers", "Summary & Recommendations"]
selected_tab = st.sidebar.radio("Choose a tab", tabs)

# Instructions tab
if selected_tab == "Instructions":
    st.markdown("""
    ## Instructions: How to Use the Tool

    This tool assesses the maturity of a country's climate finance ecosystem.
    You can score each dimension manually (checkboxes) or with AI (narrative + file upload).
    Once all dimensions are scored, you’ll see summary and recommendations you can export.
    """)

# Colored score display
def get_colored_score(score):
    if score <= 1:
        return f"<span style='color:#e57373; font-weight:bold;'>{score}</span>", "Nascent – Early-stage systems with significant gaps."
    elif score == 2:
        return f"<span style='color:#fdd835; font-weight:bold;'>{score}</span>", "Emerging – Some key structures exist, but inconsistent or weak."
    elif score >= 3:
        return f"<span style='color:#81c784; font-weight:bold;'>{score}</span>", "Mature – Robust, inclusive, and sustainable systems in place."
    return str(score), "Unknown maturity"

# Dimension Tabs (Reusing your existing scoring logic placeholder here)
# AI/Manual scoring tab function
def ai_scoring_tab(title, prompt, key):
    st.title(f"{title} Scoring")
    use_ai = st.checkbox(f"Use AI to score {title}", value=False, key=f"ai_{key}")
    if use_ai:
        narrative = st.session_state.dimension_inputs.setdefault(f"text_{key}", "")
        narrative = st.text_area("Enter narrative description:", height=300, value=narrative)
        st.session_state.dimension_inputs[f"text_{key}"] = narrative
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
        st.markdown("### Manual Scoring (based on sub-indicator evidence)")
        checkbox_list = []

        if title == "Enabling Environment":
            keys_labels = [
                (f"{key}_env_s1", "Country has submitted an NDC"),
                (f"{key}_env_s2", "NDC is linked to investment or implementation plans"),
                (f"{key}_env_s3", "NDC or strategy includes financing targets or mechanisms"),
                (f"{key}_env_s4", "There is a national climate finance strategy or roadmap")
            ]
        elif title == "Ecosystem Infrastructure":
            keys_labels = [
                (f"{key}_infra_s1", "Physical infrastructure for climate adaptation and mitigation exists"),
                (f"{key}_infra_s2", "There is a national or regional data infrastructure for monitoring climate impacts"),
                (f"{key}_infra_s3", "Climate-related digital platforms are available for stakeholders"),
                (f"{key}_infra_s4", "Regulatory frameworks for climate finance and development are in place")
            ]
        elif title == "Finance Providers":
            keys_labels = [
                (f"{key}_prov_s1", "Public finance providers are operational and engaged in climate finance"),
                (f"{key}_prov_s2", "Private finance providers are actively engaged in climate finance"),
                (f"{key}_prov_s3", "Development finance institutions provide substantial climate finance"),
                (f"{key}_prov_s4", "Multilateral development banks are active in the climate finance ecosystem")
            ]
        elif title == "Finance Seekers":
            keys_labels = [
                (f"{key}_seek_s1", "Project proposals are well developed and aligned with climate finance needs"),
                (f"{key}_seek_s2", "A pipeline of climate projects is available for financing"),
                (f"{key}_seek_s3", "There is easy access to finance for climate-related projects"),
                (f"{key}_seek_s4", "Stakeholder engagement is integral to project development")
            ]

        for k, label in keys_labels:
            st.session_state.dimension_inputs.setdefault(k, False)
            val = st.checkbox(label, value=st.session_state.dimension_inputs[k], key=k)
            st.session_state.dimension_inputs[k] = val
            checkbox_list.append(val)

        score = sum([int(bool(x)) for x in checkbox_list])
        st.session_state.dimension_scores[title] = score
        st.markdown(f"**Score for {title}:** {score}/4")

# Dimension Tabs
if selected_tab == "Enabling Environment":
    ai_scoring_tab("Enabling Environment", "You are a climate finance expert. Assess the enabling environment using: (1) Strategy, (2) Policy, (3) Enforcement, (4) Stakeholder consultation. Assign a score 0–3 for each.", "env")
elif selected_tab == "Ecosystem Infrastructure":
    ai_scoring_tab("Ecosystem Infrastructure", "You are a climate finance expert. Assess infrastructure: (1) Physical, (2) Data, (3) Digital platforms, (4) Regulatory frameworks.", "infra")
elif selected_tab == "Finance Providers":
    ai_scoring_tab("Finance Providers", "You are a climate finance expert. Assess: (1) Public, (2) Private, (3) DFIs, (4) MDBs. Score 0–3.", "providers")
elif selected_tab == "Finance Seekers":
    ai_scoring_tab("Finance Seekers", "You are a climate finance expert. Assess: (1) Proposals, (2) Pipeline, (3) Access to finance, (4) Stakeholder engagement.", "seekers")

# Summary & Recommendations tab
if selected_tab == "Summary & Recommendations":
    st.title("Summary & Recommendations")
    recommendations = []
    for dim, score in st.session_state.dimension_scores.items():
        if score < 3:
            rec_prompt = f"Provide 3–5 recommendations for improving {dim} with a current score of {score}."
            recommendations.append(f"### {dim}
" + get_ai_score(rec_prompt, ""))

    if not recommendations:
        st.info("All dimensions scored high. No improvement recommendations necessary.")
    else:
        for rec in recommendations:
            st.markdown(rec)
    for rec in recommendations:
        st.markdown(rec)
    pdf_output = generate_pdf_from_recommendations(recommendations)
    st.download_button("Download PDF", data=pdf_output, file_name="recommendations.pdf", mime="application/pdf")

# Sidebar scores overview
st.sidebar.markdown("## Scores Overview")
for dim, score in st.session_state.dimension_scores.items():
    colored, _ = get_colored_score(score)
    st.sidebar.markdown(f"**{dim}**: {colored}/4", unsafe_allow_html=True)

combined_score = round(sum(st.session_state.dimension_scores.values()) / 4, 2)
tier = "Low"
color = "#e57373"
if combined_score >= 2.5:
    tier = "High"
    color = "#81c784"
elif combined_score >= 1.5:
    tier = "Medium"
    color = "#fdd835"
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
