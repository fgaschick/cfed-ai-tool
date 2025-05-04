import streamlit as st
from openai import OpenAI
import os

# Set OpenAI API key using environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY environment variable not set.")
    st.stop()

client = OpenAI(api_key=api_key)

# Function to get AI-based scores
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

# Initialize the variable `use_ai_ee` to False initially
use_ai_ee = False

# Set the page configuration
st.set_page_config(page_title="Climate Finance Scoring", layout="wide")

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

# Function to handle AI scoring
def ai_scoring_ui(dimension_name):
    narrative_ee = st.text_area(f"Provide a narrative description of the {dimension_name}:", height=300)
    
    # File upload appears below the text input
    uploaded_file = st.file_uploader("Upload a document for AI analysis (PDF/Word)", type=["pdf", "docx"])
    
    if uploaded_file is not None:
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
        
        if file_content:
            with st.spinner(f"Analyzing document for {dimension_name} with AI..."):
                prompt = (
                    f"You are a climate finance expert. Based on the following document, assess the maturity of the {dimension_name} using relevant sub-components."
                    "Assign a maturity score from 0 to 3 for each sub-component and explain each score briefly. Then provide 3 prioritized action recommendations that would help improve the {dimension_name} if any score is below 3."
                )
                output = get_ai_score(prompt, file_content)
                st.markdown(f"**AI-Generated Assessment and Recommendations for {dimension_name}:**")
                st.markdown(output)

    # Dummy value to indicate AI mode (actual average not parsed from AI)
    ee_total_score = "AI-Based"
    score_class = "score-medium"
    
    return ee_total_score, score_class

def manual_scoring_ui(dimension_name):
    st.markdown(f"### \u270D\ufe0f Manual Scoring for {dimension_name} (based on sub-indicator evidence)")

    # STRATEGY (example, adapt for each section)
    st.markdown(f"#### {dimension_name} Strategy")
    s1 = st.checkbox("Criteria 1 for Strategy")
    s2 = st.checkbox("Criteria 2 for Strategy")
    s3 = st.checkbox("Criteria 3 for Strategy")
    notes_strategy = st.text_area(f"Notes for {dimension_name} Strategy:", key="notes_strategy")

    # Compute maturity per sub-component (Dummy logic here for illustration)
    def score_subcomponent(answers):
        return min(3, sum(answers))

    strategy_score = score_subcomponent([s1, s2, s3])

    ee_total_score = round(strategy_score / 3, 2)

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
    <strong>Average Score for {dimension_name}:</strong> {ee_total_score}/3
</div>
""", unsafe_allow_html=True)

    return ee_total_score, score_class

# Main content area
st.title("Climate Finance Scoring Tool")

# Show the sections one after the other
dimensions = ["Enabling Environment", "Ecosystem Infrastructure", "Finance Providers", "Finance Seekers"]

for dimension in dimensions:
    st.header(f"{dimension} Scoring")
    
    use_ai_ee = st.checkbox(f"Use AI to score {dimension}", value=False)
    
    if use_ai_ee:
        ee_total_score, score_class = ai_scoring_ui(dimension)
    else:
        ee_total_score, score_class = manual_scoring_ui(dimension)

    # Floating live score box always shown
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
