import streamlit as st
from openai import OpenAI
import os
from io import StringIO
import PyPDF2
import docx

# Set OpenAI API key using environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY environment variable not set.")
    st.stop()

client = OpenAI(api_key=api_key)

# Function to extract text from PDF
def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from DOCX
def extract_docx_text(uploaded_file):
    doc = docx.Document(uploaded_file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Function to get AI score
def get_ai_score(prompt, user_input, doc_text=""):
    try:
        combined_input = user_input + "\n" + doc_text
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": combined_input}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI error: {str(e)}"

# Set page configuration
st.set_page_config(page_title="Enabling Environment Scoring", layout="wide")

# Sidebar with instructions and tabs for different dimensions
st.sidebar.title("Climate Finance Tool")
dimension = st.sidebar.radio(
    "Select Dimension", 
    ["Instructions", "Enabling Environment", "Ecosystem Infrastructure", "Finance Providers", "Finance Seekers"]
)

# Display Instructions
if dimension == "Instructions":
    st.markdown("""
    ### 📘 Instructions
    This tool helps evaluate the maturity of a country's climate finance ecosystem. Choose a dimension to start the assessment.
    - **Enabling Environment**: Evaluate the national climate strategy, policies, and enforcement.
    - **Ecosystem Infrastructure**: Assess the availability of tools and partnerships.
    - **Finance Providers**: Check the involvement of public/private funding and carbon markets.
    - **Finance Seekers**: Evaluate the readiness of climate projects and inclusion of vulnerable groups.
    """)

# Document Upload
uploaded_file = st.file_uploader("Upload a document for AI analysis", type=["pdf", "docx"])

# Track score separately so it can be rendered globally
ee_total_score = None
score_class = ""

# If document is uploaded, extract text
doc_text = ""
if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        doc_text = extract_pdf_text(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc_text = extract_docx_text(uploaded_file)
    st.text_area("Extracted Document Text", value=doc_text, height=300)

# If dimension is "Enabling Environment", show questions and AI scoring
if dimension == "Enabling Environment":
    st.markdown("### Enabling Environment Questions")
    use_ai_ee = st.checkbox("Use AI to score Enabling Environment", value=False)
    
    # Input from the user for Enabling Environment
    if use_ai_ee:
        narrative_ee = st.text_area("Provide a narrative description of the enabling environment:", height=300)
        if narrative_ee:
            with st.spinner("Analyzing with AI..."):
                prompt = (
                    "You are a climate finance expert. Based on the following narrative, assess the maturity of the enabling environment using the four sub-components: "
                    "(1) Strategy (NDCs, national plans), (2) Policy (sectoral climate policies), (3) Enforcement (rule of law, anti-corruption), and (4) Stakeholder consultation. "
                    "Assign a maturity score from 0 to 3 for each sub-component and explain each score briefly. Then provide 3 prioritized action recommendations that would help improve the enabling environment if any score is below 3."
                )
                output = get_ai_score(prompt, narrative_ee, doc_text)
                st.markdown("**AI-Generated Assessment and Recommendations:**")
                st.markdown(output)

        # Dummy value to indicate AI mode
        ee_total_score = "AI-Based"
        score_class = "score-medium"
    else:
        st.markdown("### Manual Scoring")

        # STRATEGY
        s1 = st.checkbox("Country has submitted an NDC")
        s2 = st.checkbox("NDC is linked to investment or implementation plans")
        s3 = st.checkbox("NDC or strategy includes financing targets or mechanisms")
        s4 = st.checkbox("There is a national climate finance strategy or roadmap")
        notes_strategy = st.text_area("Notes for Strategy:", key="notes_strategy")

        # POLICY
        p1 = st.checkbox("Sectoral policies (energy, land use, etc.) integrate climate objectives")
        p2 = st.checkbox("Policies include clear implementation mechanisms")
        p3 = st.checkbox("Private sector is consulted or involved in policy development")
        notes_policy = st.text_area("Notes for Policy:", key="notes_policy")

        # ENFORCEMENT
        e1 = st.checkbox("Climate-related laws or regulations exist")
        e2 = st.checkbox("There is a functioning judiciary or legal redress mechanism")
        e3 = st.checkbox("Anti-corruption measures are actively implemented")
        notes_enforcement = st.text_area("Notes for Enforcement:", key="notes_enforcement")

        # STAKEHOLDER CONSULTATION
        c1 = st.checkbox("Stakeholders (civil society, academia) are engaged in planning")
        c2 = st.checkbox("Indigenous Peoples, women, youth are specifically included")
        c3 = st.checkbox("Consultations are recurring and documented")
        notes_consultation = st.text_area("Notes for Consultation:", key="notes_consultation")

        # Compute maturity per sub-component
        def score_subcomponent(answers):
            return min(3, sum(answers))

        strategy_score = score_subcomponent([s1, s2, s3, s4])
        policy_score = score_subcomponent([p1, p2, p3])
        enforcement_score = score_subcomponent([e1, e2, e3])
        consultation_score = score_subcomponent([c1, c2, c3])

        ee_total_score = round((strategy_score + policy_score + enforcement_score + consultation_score) / 4, 2)

        # Assign color class
        if ee_total_score < 1.5:
            score_class = "score-low"
        elif ee_total_score < 2.5:
            score_class = "score-medium"
        else:
            score_class = "score-high"

        st.markdown(f"""
        <div class='bottom-box {score_class}' style='margin: 4em auto 1em auto; position: relative; text-align: left; max-width: 900px;'>
            <strong>Average Score for Enabling Environment:</strong> {ee_total_score}/3
        </div>
        """, unsafe_allow_html=True)

        # AI-generated recommendations based on manual scores and notes
        if st.button("✅ Entries complete – Generate AI Recommendations"):
            if any(score < 3 for score in [strategy_score, policy_score, enforcement_score, consultation_score]):
                combined_notes = f"""Strategy notes: {notes_strategy}
                Policy notes: {notes_policy}
                Enforcement notes: {notes_enforcement}
                Consultation notes: {notes_consultation}"""
                ai_prompt_manual = f"""
                You are a climate finance advisor. The user has manually assessed maturity scores as follows:
                - Strategy: {strategy_score}/3
                - Policy: {policy_score}/3
                - Enforcement: {enforcement_score}/3
                - Stakeholder Consultation: {consultation_score}/3

                The user also provided these notes:
                {combined_notes}

                Please provide 3-5 concrete, prioritized action recommendations to improve any sub-component that scored below 3.
                """
                with st.spinner("Generating AI-based action recommendations..."):
                    ai_actions = get_ai_score(ai_prompt_manual, "")
                st.markdown("**AI Recommendations for Action:**")
                st.markdown(ai_actions)

# Floating score box always shown
if ee_total_score is not None:
    st.markdown(f"""
    <div class="bottom-box {score_class}" style="bottom: 60px; right: 30px; position: fixed;">
        <strong>Live Enabling Env Score:</strong><br> {ee_total_score}/3
    </div>
    """, unsafe_allow_html=True)

# Proper footer now added at the end of the app
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
