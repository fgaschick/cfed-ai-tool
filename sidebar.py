import streamlit as st
from openai import OpenAI
import os
from PyPDF2 import PdfReader
import docx
import io

# Set OpenAI API key using environment variable, as in original working script
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
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def handle_file_upload(uploaded_file):
    if uploaded_file is not None:
        file_type = uploaded_file.type
        if file_type == "application/pdf":
            return extract_text_from_pdf(uploaded_file)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return extract_text_from_docx(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload a PDF or DOCX file.")
            return None
    return None

st.set_page_config(page_title="Climate Finance Ecosystem Diagnostic (CFED)", layout="wide")

# Custom header and footer with logo
import streamlit.components.v1 as components

components.html("""
    <style>
    .sidebar .sidebar-content {
        background-color: #005670;
        color: white;
        padding: 10px;
    }
    .sidebar .sidebar-content h2, .sidebar .sidebar-content h3, .sidebar .sidebar-content p {
        color: white;
    }
    </style>
""", height=0)

# Title
st.title("Climate Finance Ecosystem Diagnostic (CFED) - AI-Assisted Climate Finance Ecosystem Maturity Scoring Tool")

# Track score separately so it can be rendered globally
total_score = 0
score_class = ""

# Sidebar layout
with st.sidebar:
    st.image("https://raw.githubusercontent.com/fgaschick/cfed-ai-tool/main/Chemonics_RGB_Horizontal_BLUE-WHITE.png", width=200)
    st.markdown("### Climate Finance Ecosystem Diagnostic (CFED)")
    st.markdown("AI-Assisted Climate Finance Ecosystem Maturity Scoring Tool – Prototype")

    # Display the tabs in the sidebar
    dimension = st.radio("Select Dimension", ["Enabling Environment", "Ecosystem Infrastructure", "Finance Providers", "Finance Seekers"])

    use_ai = st.checkbox("Use AI to score", value=False)

    # File upload section
    uploaded_file = None
    if use_ai:
        uploaded_file = st.file_uploader("Upload a document for AI analysis", type=["pdf", "docx"])
        if uploaded_file:
            text_from_file = handle_file_upload(uploaded_file)

            if text_from_file:
                st.text_area("Extracted Document Text", value=text_from_file, height=200)

    st.markdown("---")
    st.markdown(f"**Total Score:** {total_score}/4")

# Main content based on selected dimension
if dimension == "Enabling Environment":
    st.header("Enabling Environment")

    # AI Scoring
    if use_ai and text_from_file:
        prompt = (
            "You are a climate finance expert. Based on the following narrative, assess the maturity of the enabling environment using the four sub-components: "
            "(1) Strategy (NDCs, national plans), (2) Policy (sectoral climate policies), (3) Enforcement (rule of law, anti-corruption), and (4) Stakeholder consultation. "
            "Assign a maturity score from 0 to 3 for each sub-component and explain each score briefly. Then provide 3 prioritized action recommendations that would help improve the enabling environment if any score is below 3."
        )
        result = get_ai_score(prompt, text_from_file)
        st.markdown("### AI-Generated Assessment and Recommendations:")
        st.write(result)
        
        total_score = 3  # Use the result of AI scoring (can be refined later based on AI output)
        score_class = "score-high"  # Update this based on AI scoring result
    else:
        # Manual Scoring based on checkboxes
        st.markdown("#### Strategy")
        s1 = st.checkbox("Country has submitted an NDC")
        s2 = st.checkbox("NDC is linked to investment or implementation plans")
        s3 = st.checkbox("NDC or strategy includes financing targets or mechanisms")
        s4 = st.checkbox("There is a national climate finance strategy or roadmap")
        notes_strategy = st.text_area("Notes for Strategy:", key="notes_strategy")

        # Policy Section
        st.markdown("#### Policy")
        p1 = st.checkbox("Sectoral policies (energy, land use, etc.) integrate climate objectives")
        p2 = st.checkbox("Policies include clear implementation mechanisms")
        p3 = st.checkbox("Private sector is consulted or involved in policy development")
        notes_policy = st.text_area("Notes for Policy:", key="notes_policy")

        # Other sections follow similar pattern

        # Assign score
        strategy_score = sum([s1, s2, s3, s4])
        policy_score = sum([p1, p2, p3])
        total_score = (strategy_score + policy_score) / 2
        score_class = "score-medium"  # Update this based on score

        st.markdown(f"**Total Manual Score for Enabling Environment:** {total_score}/3")
    
# Other dimensions can follow similar logic, repeat the structure above for the "Ecosystem Infrastructure", "Finance Providers", and "Finance Seekers" dimensions.

# Floating score box always shown
if total_score is not None:
    st.markdown(f"""
    <div class="bottom-box {score_class}" style="bottom: 60px; right: 30px; position: fixed;">
        <strong>Live Score for {dimension}:</strong><br> {total_score}/3
    </div>
    """, unsafe_allow_html=True)

# Summary and Recommendations tab, AI-based recommendations
with st.sidebar:
    if st.button("Generate Recommendations"):
        st.write("### AI-Based Recommendations")
        recommendations_prompt = f"Please generate recommendations for the {dimension} based on the manual scores and notes provided."
        recommendations = get_ai_score(recommendations_prompt, "")
        st.write(recommendations)
        
        st.download_button("Download Recommendations", recommendations, "recommendations.txt")

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
