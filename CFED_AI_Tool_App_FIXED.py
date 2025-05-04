import streamlit as st
from openai import OpenAI
import os

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

# Set page configuration
st.set_page_config(page_title="Enabling Environment Scoring", layout="wide")

# Sidebar setup
st.sidebar.title("Tool Navigation")
st.sidebar.markdown("### Use this tool to score the enabling environment")

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

# Title for the main content
st.title("Enabling Environment Scoring Prototype")

# Track score separately so it can be rendered globally
ee_total_score = None
score_class = ""

# Sidebar content
use_ai_ee = st.sidebar.checkbox("Use AI to score Enabling Environment", value=False)

if use_ai_ee:
    # Show text input first, followed by file upload only when AI option is selected
    narrative_ee = st.text_area("\U0001F50D Provide a narrative description of the enabling environment:", height=300)
    
    # File upload appears below the text input
    uploaded_file = st.file_uploader("Upload a document for AI analysis (PDF/Word)", type=["pdf", "docx"])
    
    if uploaded_file is not None:
        # Process the uploaded file (you can add logic to extract text and analyze it)
        file_content = None
        
        if uploaded_file.type == "application/pdf":
            import PyPDF2
            reader = PyPDF2.PdfReader(uploaded_file)
            file_content = ""
            for page in reader.pages:
                file_content += page.extract_text()
        
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            import docx
            doc = docx.Document(uploaded_file)
            file_content = "\n".join([para.text for para in doc.paragraphs])
        
        # Once the file is uploaded and its content is extracted, you can pass it to the AI model.
        if file_content:
            with st.spinner("Analyzing document with AI..."):
                prompt = (
                    "You are a climate finance expert. Based on the following document, assess the maturity of the enabling environment using the four sub-components: "
                    "(1) Strategy (NDCs, national plans), (2) Policy (sectoral climate policies), (3) Enforcement (rule of law, anti-corruption), and (4) Stakeholder consultation. "
                    "Assign a maturity score from 0 to 3 for each sub-component and explain each score briefly. Then provide 3 prioritized action recommendations that would help improve the enabling environment if any score is below 3."
                )
                output = get_ai_score(prompt, file_content)
                st.markdown("**AI-Generated Assessment and Recommendations:**")
                st.markdown(output)

        # Dummy value to indicate AI mode (actual average not parsed from AI)
        ee_total_score = "AI-Based"
        score_class = "score-medium"

else:
    st.markdown("### \u270D\ufe0f Manual Scoring (based on sub-indicator evidence)")

    # STRATEGY
    st.markdown("#### Strategy")
    s1 = st.checkbox("Country has submitted an NDC")
    s2 = st.checkbox("NDC is linked to investment or implementation plans")
    s3 = st.checkbox("NDC or strategy includes financing targets or mechanisms")
    s4 = st.checkbox("There is a national climate finance strategy or roadmap")
    notes_strategy = st.text_area("Notes for Strategy:", key="notes_strategy")

    # POLICY
    st.markdown("#### Policy")
    p1 = st.checkbox("Sectoral policies (energy, land use, etc.) integrate climate objectives")
    p2 = st.checkbox("Policies include clear implementation mechanisms")
    p3 = st.checkbox("Private sector is consulted or involved in policy development")
    notes_policy = st.text_area("Notes for Policy:", key="notes_policy")

    # ENFORCEMENT
    st.markdown("#### Enforcement")
    e1 = st.checkbox("Climate-related laws or regulations exist")
    e2 = st.checkbox("There is a functioning judiciary or legal redress mechanism")
    e3 = st.checkbox("Anti-corruption measures are actively implemented")
    notes_enforcement = st.text_area("Notes for Enforcement:", key="notes_enforcement")

    # STAKEHOLDER CONSULTATION
    st.markdown("#### Stakeholder Consultation")
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

    avg_color_class = score_class
    st.markdown(f"""
<div class='bottom-box {score_class}' style='margin: 4em auto 1em auto; position: relative; text-align: left; max-width: 900px;'>
    <strong>Average Score for Enabling Environment:</strong> {ee_total_score}/3</strong> {ee_total_score}/3
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


# Floating live score
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
