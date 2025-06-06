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
    def safe_latin1(text):
        return text.encode('latin1', 'replace').decode('latin1')

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="AI-Based Recommendations for Action", ln=True, align="C")
    pdf.ln(10)
    for recommendation in recommendations:
        pdf.multi_cell(0, 10, safe_latin1(recommendation))
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
    st.session_state.dimension_inputs = {}
    st.session_state.dimension_scores = {
        "Enabling Environment": 0,
        "Ecosystem Infrastructure": 0,
        "Finance Providers": 0,
        "Finance Seekers": 0
    }
    st.session_state.selected_tab = "Instructions"
    st.session_state.reset_triggered = False
    for flag in ["env_done", "infra_done", "providers_done", "seekers_done"]:
        st.session_state[flag] = False
    st.rerun()

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
    st.rerun()

# Tab setup
tabs = ["Instructions", "Enabling Environment", "Ecosystem Infrastructure", "Finance Providers", "Finance Seekers"]
if all(st.session_state.get(done_flag, False) for done_flag in ["env_done", "infra_done", "providers_done", "seekers_done"]):
    tabs.append("Summary & Recommendations")
if not all(st.session_state.get(done_flag, False) for done_flag in ["env_done", "infra_done", "providers_done", "seekers_done"]):
    st.sidebar.info("🔒 Summary & Recommendations will unlock once all dimensions are marked as complete.")
selected_tab = st.sidebar.radio("Choose a tab", tabs, index=tabs.index(st.session_state.get("selected_tab", "Instructions")))
st.session_state.selected_tab = selected_tab

# Instructions tab
if selected_tab == "Instructions":
    st.markdown("""
    ## Instructions: How to Use the Tool

    Welcome to the **Climate Finance Ecosystem Diagnostic (CFED)** tool of Chemonics International! This tool helps you assess the maturity of a country's climate finance ecosystem by evaluating key dimensions and subcomponents of climate finance. 
    The tool uses **both manual scoring** and **AI-based analysis** to provide a comprehensive overview of the climate finance landscape in your country. 

    ### Tool Structure:
    The tool is structured into four main dimensions, each with its respective subcomponents and indicators. These dimensions are:
    1. **Enabling Environment**
    2. **Ecosystem Infrastructure**
    3. **Finance Providers**
    4. **Finance Seekers**

    ### How to Use the Tool:
    - **AI-Based Scoring**: You can choose to use **AI-based scoring** by providing a **narrative description** of each dimension. When you select this option, the tool will ask for detailed information about your country's climate finance system. 
    - **Document Upload**: Along with the narrative, you can upload **relevant documents** (PDF/Word) that provide more in-depth information on the dimension you're scoring. The AI will analyze both the narrative and the document to generate a score and recommendations.
    - **Manual Scoring**: If you prefer, you can manually score the dimension by selecting checkboxes for the provided indicators and subcomponents. This will allow you to evaluate the maturity of each dimension based on specific questions. Each indicator corresponds to an element of the climate finance ecosystem, such as policies, infrastructure, or finance flows.

    ### Scoring and Results:
    - After completing the scoring for each dimension (whether using AI or manual input), you will see the **score for each dimension** displayed on the sidebar.
    - The **combined score** is automatically calculated based on the individual dimension scores.
    - Once all dimensions are marked as finalized, the **Summary & Recommendations** tab becomes available.
    - **AI-based recommendations** will be provided in the **Summary & Recommendations** tab, which will help you identify areas for improvement in the climate finance ecosystem.

    ### Downloading Results:
    Once all dimensions have been scored and recommendations are provided, you will be able to **download the recommendations as a PDF** for your records.
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
        narrative_help_text = {
            "env": "Describe national climate strategies, policy commitments, financing targets, and stakeholder consultation practices.",
            "infra": "Describe physical infrastructure, climate data systems, digital platforms, and regulatory frameworks supporting climate goals.",
            "providers": "Describe the role and engagement of public, private, DFI, and multilateral actors in providing climate finance.",
            "seekers": "Describe quality of project proposals, project pipelines, accessibility of finance, and stakeholder inclusion in project development."
        }
        narrative = st.text_area("Enter narrative description:", height=300, value=narrative, help=narrative_help_text.get(key, "Provide relevant information."))
        st.session_state.dimension_inputs[f"text_{key}"] = narrative
        upload_help_text = {
            "env": "Upload relevant documents such as NDCs, national climate policies, and climate finance strategies.",
            "infra": "Upload documents such as infrastructure assessments, digital platform documentation, or data monitoring reports.",
            "providers": "Upload reports showing participation of public/private finance institutions or MDB/DFI engagement.",
            "seekers": "Upload project concept notes, funding proposals, or stakeholder engagement reports."
        }
        uploaded_file = st.file_uploader("Upload document (PDF/DOCX)", type=["pdf", "docx"], key=f"file_{key}", help=upload_help_text.get(key, "Upload supporting evidence."))
        if uploaded_file:
            file_text = extract_text_from_file(uploaded_file)
            narrative += file_text
            st.session_state.dimension_inputs[f"text_{key}"] = narrative
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
                (f"{key}_env_s1", "Country has submitted an NDC", "The country has formally submitted its Nationally Determined Contribution to the UNFCCC."),
                (f"{key}_env_s2", "NDC is linked to investment or implementation plans", "The NDC includes clear links to how implementation or financing will be achieved."),
                (f"{key}_env_s3", "NDC or strategy includes financing targets or mechanisms", "The document outlines financial goals, instruments, or specific funding mechanisms."),
                (f"{key}_env_s4", "There is a national climate finance strategy or roadmap", "A dedicated national plan or roadmap guides domestic and international climate finance efforts.")
            ]
        elif title == "Ecosystem Infrastructure":
            keys_labels = [
                (f"{key}_infra_s1", "Physical infrastructure for climate adaptation and mitigation exists", "Infrastructure such as sea walls, renewable energy plants, or forest buffers are operational."),
                (f"{key}_infra_s2", "There is a national or regional data infrastructure for monitoring climate impacts", "Data systems exist to track climate vulnerabilities, emissions, or adaptation needs."),
                (f"{key}_infra_s3", "Climate-related digital platforms are available for stakeholders", "Platforms share climate data or facilitate finance access for implementers."),
                (f"{key}_infra_s4", "Regulatory frameworks for climate finance and development are in place", "Climate finance and low-carbon development are supported by enforceable regulations.")
            ]
        elif title == "Finance Providers":
            keys_labels = [
                (f"{key}_prov_s1", "Public finance providers are operational and engaged in climate finance", "Government ministries or national funds disburse climate-targeted finance."),
                (f"{key}_prov_s2", "Private finance providers are actively engaged in climate finance", "Commercial banks or private investors participate in climate-aligned investments."),
                (f"{key}_prov_s3", "Development finance institutions provide substantial climate finance", "Institutions like regional or bilateral DFIs fund adaptation or mitigation projects."),
                (f"{key}_prov_s4", "Multilateral development banks are active in the climate finance ecosystem", "MDBs such as the World Bank or ADB provide loans or grants for climate action.")
            ]
        elif title == "Finance Seekers":
            keys_labels = [
                (f"{key}_seek_s1", "Project proposals are well developed and aligned with climate finance needs", "Proposals are technically sound and reflect country or sectoral climate goals."),
                (f"{key}_seek_s2", "A pipeline of climate projects is available for financing", "There is a prioritized list of climate projects ready for donor or investor review."),
                (f"{key}_seek_s3", "There is easy access to finance for climate-related projects", "Barriers to entry for communities or local governments are minimal."),
                (f"{key}_seek_s4", "Stakeholder engagement is integral to project development", "Project beneficiaries are consulted and reflected in design and implementation.")
            ]

        for k, label, tip in keys_labels:
            st.session_state.dimension_inputs.setdefault(k, False)
            val = st.checkbox(label, value=st.session_state.dimension_inputs[k], key=k, help=tip)
            st.session_state.dimension_inputs[k] = val
            checkbox_list.append(val)

        score = sum([int(bool(x)) for x in checkbox_list])
        st.session_state.dimension_scores[title] = score
        colored_score, maturity_label = get_colored_score(score)
        st.markdown(f"**Score for {title}:** {colored_score}/4 – _{maturity_label}_", unsafe_allow_html=True)

        flag_map = {
            "env": "env_done",
            "infra": "infra_done",
            "providers": "providers_done",
            "seekers": "seekers_done"
        }
        if key in flag_map:
            flag = flag_map[key]
            st.session_state[flag] = st.checkbox(f"✅ I have finalized inputs for {title}",
                                                value=st.session_state.get(flag, False),
                                                key=f"{flag}_box")


# Dimension Tabs
completion_flags = {
    "Enabling Environment": "env_done",
    "Ecosystem Infrastructure": "infra_done",
    "Finance Providers": "providers_done",
    "Finance Seekers": "seekers_done"
}

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
        if score < 4:
            rec_prompt = f"Provide 3–5 recommendations for improving {dim} with a current score of {score}."
            ai_output = str(get_ai_score(rec_prompt, "")).strip()
            recommendations.append(f"### {dim}\n{ai_output}")

    if not recommendations:
        st.info("All dimensions scored high. No improvement recommendations necessary.")
    else:
        for rec in recommendations:
            st.markdown(rec)
    if recommendations:
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
