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

def extract_text_from_pdf(uploaded_file):
    pdf = PdfReader(uploaded_file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    text = ""
    for para in doc.paragraphs:
        text += para.text
    return text

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
            uploaded_file = st.file_uploader(f"Upload a document for {dimension} analysis", type=["pdf", "docx"])
            
            if uploaded_file:
                if uploaded_file.type == "application/pdf":
                    document_text = extract_text_from_pdf(uploaded_file)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    document_text = extract_text_from_docx(uploaded_file)
                else:
                    st.error("Unsupported file type.")
                
                # Combine document text and user input for AI scoring
                combined_input = document_text + "\n" + narrative_ee
                with st.spinner(f"Analyzing with AI for {dimension}..."):
                    prompt = f"You are a climate finance expert. Assess the maturity of {dimension} and provide a score with recommendations."
                    output = get_ai_score(prompt, combined_input)
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
