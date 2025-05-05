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

st.set_page_config(page_title="Climate Finance Maturity Assessment", layout="wide")

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

# Define subcategories and associated questions for each dimension
DIMENSIONS = {
    "Enabling Environment": {
        "subcategories": {
            "Strategy": [
                "Has the country submitted an NDC?",
                "Does the NDC link to investment or implementation plans?",
                "Does the NDC or strategy include financing targets or mechanisms?",
                "Is there a national climate finance strategy or roadmap?"
            ],
            "Policy": [
                "Do sectoral policies (energy, land use, etc.) integrate climate objectives?",
                "Do policies include clear implementation mechanisms?",
                "Is the private sector consulted or involved in policy development?"
            ],
            "Enforcement": [
                "Do climate-related laws or regulations exist?",
                "Is there a functioning judiciary or legal redress mechanism?",
                "Are anti-corruption measures actively implemented?"
            ],
            "Stakeholder Consultation": [
                "Are stakeholders (civil society, academia) engaged in planning?",
                "Are Indigenous Peoples, women, youth specifically included?",
                "Are consultations recurring and documented?"
            ]
        }
    },
    # Repeat the same for Ecosystem Infrastructure, Finance Providers, and Finance Seekers
}

# Function for scoring and displaying questions
def show_scoring_ui(dimension_name, subcategory_name):
    st.markdown(f"### {subcategory_name} Scoring")
    answers = []

    # For each question in the selected subcategory
    for question in DIMENSIONS[dimension_name]["subcategories"][subcategory_name]:
        answer = st.checkbox(question)
        answers.append(answer)

    # Calculate score for subcategory
    subcategory_score = sum(answers)
    st.markdown(f"**Score for {subcategory_name}:** {subcategory_score}/{len(answers)}")

    return subcategory_score

# Sidebar for selecting dimension
selected_dimension = st.sidebar.selectbox("Select Dimension", list(DIMENSIONS.keys()))

# Display the dimension and allow subcategory scoring
st.markdown(f"## {selected_dimension} Scoring")

dimension_score = 0
for subcategory_name in DIMENSIONS[selected_dimension]["subcategories"]:
    subcategory_score = show_scoring_ui(selected_dimension, subcategory_name)
    dimension_score += subcategory_score

dimension_score = round(dimension_score / sum(len(DIMENSIONS[selected_dimension]["subcategories"][subcat]) for subcat in DIMENSIONS[selected_dimension]["subcategories"]), 2)

# Display the overall dimension score
st.markdown(f"### Overall Score for {selected_dimension}: {dimension_score}/3")

# Floating live score on the sidebar
st.sidebar.markdown(f"**Live {selected_dimension} Score:** {dimension_score}/3")

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
