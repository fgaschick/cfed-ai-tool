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
    from urllib.request import urlopen
    import tempfile
    from PIL import Image
    import os

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header with Chemonics logo and dark blue background
    logo_url = "https://raw.githubusercontent.com/fgaschick/cfed-ai-tool/main/Chemonics_RGB_Horizontal_BLUE-WHITE.png"
    logo_temp_path = os.path.join(tempfile.gettempdir(), "chemonics_logo.png")
    with urlopen(logo_url) as response, open(logo_temp_path, 'wb') as out_file:
        out_file.write(response.read())

    pdf.set_fill_color(0, 86, 112)  # Dark blue
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.image(logo_temp_path, x=10, y=5, w=60)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 14)
    pdf.set_xy(70, 10)
    pdf.cell(130, 10, "Climate Finance Ecosystem Recommendations", ln=True, align="R")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt="Summary of Recommendations", ln=True, align="L")
    pdf.ln(10)

    # Scoring summary section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt="Scoring Summary", ln=True, align="L")
    pdf.ln(5)
    for dim, score in st.session_state.dimension_scores.items():
        tier = "Low"
        if score >= 2.5:
            tier = "High"
        elif score >= 1.5:
            tier = "Medium"
        pdf.set_font("Arial", style="B", size=11)
        pdf.cell(0, 10, f"{dim}: {score}/4 – {tier} Maturity", ln=True)
        justification = st.session_state.get(f"text_{dim.lower().replace(' ', '_')}", "No narrative provided.")
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 10, justification)
        pdf.ln(2)

    # Add recommendations text
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt="Recommendations", ln=True, align="L")
    pdf.ln(5)
    for recommendation in recommendations:
        pdf.multi_cell(0, 10, recommendation)

    pdf_bytes = pdf.output(dest='S').encode('latin1', 'replace')
    return BytesIO(pdf_bytes)

# Page setup
st.set_page_config(page_title="Climate Finance Maturity Tool", layout="wide")

# Sidebar and navigation
st.sidebar.image("https://raw.githubusercontent.com/fgaschick/cfed-ai-tool/main/Chemonics_RGB_Horizontal_BLUE-WHITE.png", use_container_width=True)
st.sidebar.markdown("""
    <style>
[data-testid="stSidebar"] > div:first-child {
    background-color: #005670;
    padding-top: 1rem;
    color: white;
}
/* Sidebar labels */
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] input[type="radio"] + div div {
    color: white !important;
}
}
/* Main area labels */
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
tabs = ["Instructions", "Enabling Environment", "Ecosystem Infrastructure", "Finance Providers", "Finance Seekers", "Summary & Recommendations"]
selected_tab = st.sidebar.radio("Choose a tab", tabs)

if "dimension_scores" not in st.session_state:
    st.session_state.dimension_scores = {
        "Enabling Environment": 0,
        "Ecosystem Infrastructure": 0,
        "Finance Providers": 0,
        "Finance Seekers": 0
    }

if "confirmation_flags" not in st.session_state:
    st.session_state.confirmation_flags = {
        "Enabling Environment": False,
        "Ecosystem Infrastructure": False,
        "Finance Providers": False,
        "Finance Seekers": False
    }

# Tab: Instructions
if selected_tab == "Instructions":
    st.markdown("""
        ## Instructions: How to Use the Tool

        Welcome to the **Climate Finance Ecosystem Diagnostic (CFED)** tool! This tool helps you assess the maturity of a country's climate finance ecosystem by evaluating key dimensions and subcomponents of climate finance. 
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
        - **AI-based recommendations** will be provided in the **Summary & Recommendations** tab, which will help you identify areas for improvement in the climate finance ecosystem.

        ### Downloading Results:
        Once all dimensions have been scored and recommendations are provided, you will be able to **download the recommendations as a PDF** for your records. 
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
        st.markdown("### Manual Scoring (based on sub-indicator evidence)")
        if title == "Enabling Environment":
            s1 = st.checkbox("Country has submitted an NDC", key=f"{key}_env_s1")
            s2 = st.checkbox("NDC is linked to investment or implementation plans", key=f"{key}_env_s2")
            s3 = st.checkbox("NDC or strategy includes financing targets or mechanisms", key=f"{key}_env_s3")
            s4 = st.checkbox("There is a national climate finance strategy or roadmap", key=f"{key}_env_s4")
        elif title == "Ecosystem Infrastructure":
            s1 = st.checkbox("Physical infrastructure for climate adaptation and mitigation exists", key=f"{key}_infra_s1")
            s2 = st.checkbox("There is a national or regional data infrastructure for monitoring climate impacts", key=f"{key}_infra_s2")
            s3 = st.checkbox("Climate-related digital platforms are available for stakeholders", key=f"{key}_infra_s3")
            s4 = st.checkbox("Regulatory frameworks for climate finance and development are in place", key=f"{key}_infra_s4")
        elif title == "Finance Providers":
            s1 = st.checkbox("Public finance providers are operational and engaged in climate finance", key=f"{key}_prov_s1")
            s2 = st.checkbox("Private finance providers are actively engaged in climate finance", key=f"{key}_prov_s2")
            s3 = st.checkbox("Development finance institutions provide substantial climate finance", key=f"{key}_prov_s3")
            s4 = st.checkbox("Multilateral development banks are active in the climate finance ecosystem", key=f"{key}_prov_s4")
        elif title == "Finance Seekers":
            s1 = st.checkbox("Project proposals are well developed and aligned with climate finance needs", key=f"{key}_seek_s1")
            s2 = st.checkbox("A pipeline of climate projects is available for financing", key=f"{key}_seek_s2")
            s3 = st.checkbox("There is easy access to finance for climate-related projects", key=f"{key}_seek_s3")
            s4 = st.checkbox("Stakeholder engagement is integral to project development", key=f"{key}_seek_s4")
                score = sum([s1, s2, s3, s4])
        st.session_state[f"score_{key}"] = score
                        st.session_state.dimension_scores[title] = score
        st.session_state[f"score_{key}"] = score
        st.markdown(f"**Score for {title}:** {score}/4")
        st.checkbox("I confirm that I have completed this dimension.", key=f"confirm_{key}")
        st.session_state.confirmation_flags[title] = st.session_state.get(f"confirm_{key}", False)
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
    if not all(st.session_state.confirmation_flags.values()):
        st.warning("⚠️ Please complete and confirm all dimension assessments before accessing recommendations.")
        st.stop()
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
tier = "Low"
color = "#e57373"
if combined_score >= 2.5:
    tier = "High"
    color = "#81c784"
elif combined_score >= 1.5:
    tier = "Medium"
    color = "#fdd835"
st.sidebar.markdown(f"**Combined Score**: <span style='color:{color}'>{combined_score}/4 – {tier} Maturity</span>", unsafe_allow_html=True)

# Reset button
if st.sidebar.button("Reset Scores"):
    st.session_state.dimension_scores = {
        "Enabling Environment": 0,
        "Ecosystem Infrastructure": 0,
        "Finance Providers": 0,
        "Finance Seekers": 0
    }
    for key in list(st.session_state.keys()):
        if key.startswith("ai_") or key.startswith("text_") or key.startswith("file_") or key.endswith(('_s1', '_s2', '_s3', '_s4')):
            del st.session_state[key]

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
