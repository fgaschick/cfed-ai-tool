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
    st.session_state.selected_tab = "Instructions"
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

# Colored score display
def get_colored_score(score):
    if score <= 1:
        return f"<span style='color:#e57373; font-weight:bold;'>{score}</span>", "Nascent – Early-stage systems with significant gaps."
    elif score == 2:
        return f"<span style='color:#fdd835; font-weight:bold;'>{score}</span>", "Emerging – Some key structures exist, but inconsistent or weak."
    elif score >= 3:
        return f"<span style='color:#81c784; font-weight:bold;'>{score}</span>", "Mature – Robust, inclusive, and sustainable systems in place."
    return str(score), "Unknown maturity"

# ---- COMPLETE ai_scoring_tab FUNCTION ----
def ai_scoring_tab(title, prompt, key):
    st.title(f"{title} Scoring")
    use_ai = st.checkbox(f"Use AI to score {title}", value=st.session_state.get(f"ai_{key}", False), key=f"ai_{key}")

    flag_map = {
        "env": "env_done",
        "infra": "infra_done",
        "providers": "providers_done",
        "seekers": "seekers_done"
    }
    flag = flag_map.get(key)

    if use_ai:
        # Get and store narrative input
        narrative_key = f"text_{key}"
        narrative = st.session_state.get(narrative_key, "")
        narrative_help = {
            "env": "Describe national climate strategies, policy commitments, financing targets, and stakeholder consultation practices.",
            "infra": "Describe physical infrastructure, climate data systems, digital platforms, and regulatory frameworks supporting climate goals.",
            "providers": "Describe the role and engagement of public, private, DFI, and multilateral actors in providing climate finance.",
            "seekers": "Describe project pipelines, proposal quality, finance accessibility, and inclusion in project development."
        }
        narrative = st.text_area("Enter narrative description:", value=narrative, height=300, help=narrative_help.get(key, ""))
        st.session_state[narrative_key] = narrative

        # Handle file upload
        upload_key = f"file_{key}"
        uploaded_file = st.file_uploader("Upload document (PDF or DOCX)", type=["pdf", "docx"], key=upload_key)
        if uploaded_file:
            file_text = extract_text_from_file(uploaded_file)
            narrative += file_text
            st.session_state[narrative_key] = narrative

        # "Ready for AI" checkbox
        ready_key = f"ready_{key}"
        if narrative.strip():
            st.session_state.setdefault(ready_key, False)
            st.session_state[ready_key] = st.checkbox("✅ Ready for AI analysis and recommendations", value=st.session_state.get(ready_key, False), key=ready_key)

        # Run AI if narrative is marked as ready
        if st.session_state.get(ready_key, False) and narrative.strip():
            with st.spinner("Analyzing with AI..."):
                # Run AI
                output = get_ai_score(prompt, narrative)
                st.markdown("**AI-Generated Output:**")
                st.markdown(output)
                avg_score = extract_avg_score(output)
                st.session_state.dimension_scores[title] = avg_score if avg_score is not None else 2

            # Finalize checkbox for AI path
            colored_score, maturity_label = get_colored_score(st.session_state.dimension_scores[title])
            st.markdown(f"**Score for {title}:** {colored_score}/4 – _{maturity_label}_", unsafe_allow_html=True)

        # Always show finalize checkbox even if AI output was not triggered
        if flag:
            st.session_state[flag] = st.checkbox(
                    f"✅ I have finalized inputs for {title}",
                    value=st.session_state.get(flag, False),
                    key=f"{flag}_box_ai"
                )

    else:
        # Manual scoring
        st.markdown("### Manual Scoring (based on sub-indicator evidence)")
        checkbox_list = []

        if title == "Enabling Environment":
            keys_labels = [
                (f"{key}_env_s1", "Country has submitted an NDC", "Submitted to UNFCCC."),
                (f"{key}_env_s2", "NDC is linked to investment or implementation plans", "Includes implementation or financing details."),
                (f"{key}_env_s3", "NDC includes financing targets or mechanisms", "Financial targets or mechanisms mentioned."),
                (f"{key}_env_s4", "National climate finance strategy or roadmap exists", "Specific strategy or roadmap document available.")
            ]
        elif title == "Ecosystem Infrastructure":
            keys_labels = [
                (f"{key}_infra_s1", "Physical infrastructure exists", "E.g., sea walls, renewable energy plants."),
                (f"{key}_infra_s2", "National/regional data infrastructure exists", "Systems to track climate data."),
                (f"{key}_infra_s3", "Digital climate platforms exist", "Publicly available platforms."),
                (f"{key}_infra_s4", "Climate finance regulatory frameworks exist", "Supports low-carbon investment.")
            ]
        elif title == "Finance Providers":
            keys_labels = [
                (f"{key}_prov_s1", "Public finance providers are engaged", "Government-managed climate finance."),
                (f"{key}_prov_s2", "Private finance actors are engaged", "Banks, funds, or insurers providing climate-aligned capital."),
                (f"{key}_prov_s3", "DFIs provide substantial climate finance", "Presence of national/regional DFIs."),
                (f"{key}_prov_s4", "MDBs are active in the ecosystem", "World Bank, ADB, etc.")
            ]
        elif title == "Finance Seekers":
            keys_labels = [
                (f"{key}_seek_s1", "Quality project proposals exist", "Aligned with national or donor climate goals."),
                (f"{key}_seek_s2", "Pipeline of climate projects exists", "Priority project lists available."),
                (f"{key}_seek_s3", "Finance is accessible", "Barriers to access are low."),
                (f"{key}_seek_s4", "Stakeholder engagement is strong", "Communities or groups involved in design.")
            ]
        else:
            keys_labels = []

        for k, label, help_text in keys_labels:
            st.session_state.setdefault(k, False)
            value = st.checkbox(label, value=st.session_state[k], key=k, help=help_text)
            st.session_state[k] = value
            checkbox_list.append(value)

        # Calculate and show score
        score = sum([int(bool(x)) for x in checkbox_list])
        st.session_state.dimension_scores[title] = score
        colored_score, maturity_label = get_colored_score(score)
        st.markdown(f"**Score for {title}:** {colored_score}/4 – _{maturity_label}_", unsafe_allow_html=True)

        # Finalize checkbox for manual path
        if flag:
            st.session_state[flag] = st.checkbox(f"✅ I have finalized inputs for {title}",
                                                 value=st.session_state.get(flag, False),
                                                 key=f"{flag}_box_manual")

# ---- END OF ai_scoring_tab ----

# Streamlit UI setup
st.set_page_config(page_title="Climate Finance Maturity Tool", layout="wide")
st.sidebar.image("https://raw.githubusercontent.com/fgaschick/cfed-ai-tool/main/Chemonics_RGB_Horizontal_BLUE-WHITE.png", use_container_width=True)
st.sidebar.title("Climate Finance Ecosystem Diagnostic (CFED)")
st.sidebar.subheader("AI-Assisted Maturity Scoring Tool")

# Handle early reset
if "reset_triggered" in st.session_state and st.session_state.reset_triggered:
    st.session_state.dimension_inputs = {}
    st.session_state.dimension_scores = {
        "Enabling Environment": 0,
        "Ecosystem Infrastructure": 0,
        "Finance Providers": 0,
        "Finance Seekers": 0
    }
    for flag in ["env_done", "infra_done", "providers_done", "seekers_done"]:
        st.session_state[flag] = False
    st.session_state.selected_tab = "Instructions"
    st.session_state.reset_triggered = False
    st.rerun()

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

if st.sidebar.button("🔁 Reset All Inputs"):
    st.session_state.reset_triggered = True
    st.rerun()

# Tab setup
tabs = ["Instructions", "Enabling Environment", "Ecosystem Infrastructure", "Finance Providers", "Finance Seekers"]
if all(st.session_state.get(flag, False) for flag in ["env_done", "infra_done", "providers_done", "seekers_done"]):
    tabs.append("Summary & Recommendations")
else:
    st.sidebar.info("🔒 Summary & Recommendations will unlock once all dimensions are marked as complete.")

selected_tab = st.sidebar.radio("Choose a tab", tabs, index=tabs.index(st.session_state.get("selected_tab", "Instructions")))
st.session_state.selected_tab = selected_tab

# Instructions tab
if selected_tab == "Instructions":
    st.markdown("""
    ## Instructions
    
    This tool helps assess a country's climate finance ecosystem maturity through four key dimensions:
    
    1. Enabling Environment  
    2. Ecosystem Infrastructure  
    3. Finance Providers  
    4. Finance Seekers

    Users can choose AI-assisted or manual scoring. All inputs must be finalized to unlock summary recommendations.
    """)

# Dimension tabs
if selected_tab == "Enabling Environment":
    ai_scoring_tab("Enabling Environment", "You are a climate finance expert. Assess the enabling environment using: (1) Strategy, (2) Policy, (3) Enforcement, (4) Stakeholder consultation. Assign a score 0–3 for each.", "env")
elif selected_tab == "Ecosystem Infrastructure":
    ai_scoring_tab("Ecosystem Infrastructure", "You are a climate finance expert. Assess infrastructure: (1) Physical, (2) Data, (3) Digital platforms, (4) Regulatory frameworks.", "infra")
elif selected_tab == "Finance Providers":
    ai_scoring_tab("Finance Providers", "You are a climate finance expert. Assess: (1) Public, (2) Private, (3) DFIs, (4) MDBs. Score 0–3.", "providers")
elif selected_tab == "Finance Seekers":
    ai_scoring_tab("Finance Seekers", "You are a climate finance expert. Assess: (1) Proposals, (2) Pipeline, (3) Access to finance, (4) Stakeholder engagement.", "seekers")

# Summary tab
if selected_tab == "Summary & Recommendations":
    st.title("Summary & Recommendations")
    recommendations = []
    for dim, score in st.session_state.dimension_scores.items():
        if score < 4:
            rec_prompt = f"Provide 3–5 recommendations for improving {dim} with a current score of {score}."
            ai_output = get_ai_score(rec_prompt, "")
            recommendations.append(f"### {dim}
{ai_output}")

    if not recommendations:
        st.info("All dimensions scored high. No recommendations needed.")
    else:
        for rec in recommendations:
            st.markdown(rec)
        pdf = generate_pdf_from_recommendations(recommendations)
        st.download_button("Download Recommendations as PDF", data=pdf, file_name="cfed_recommendations.pdf")

# Sidebar score summary
st.sidebar.markdown("## Scores Overview")
for dim, score in st.session_state.dimension_scores.items():
    colored, _ = get_colored_score(score)
    st.sidebar.markdown(f"**{dim}**: {colored}/4", unsafe_allow_html=True)
combined = round(sum(st.session_state.dimension_scores.values()) / 4, 2)
tier = "Low"
color = "#e57373"
if combined >= 2.5:
    tier = "High"
    color = "#81c784"
elif combined >= 1.5:
    tier = "Medium"
    color = "#fdd835"
st.sidebar.markdown(f"**Combined Score**: <span style='color:{color}'>{combined}/4 – {tier} Maturity</span>", unsafe_allow_html=True)
