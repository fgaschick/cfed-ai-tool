import streamlit as st
from openai import OpenAI
import os

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

# Dimension Definitions
DIMENSIONS = {
    "Enabling Environment": {
        "subcategories": ["Strategy", "Policy", "Enforcement", "Stakeholder Consultation"],
        "ai_prompt": "You are a climate finance expert. Based on the following narrative, assess the maturity of the enabling environment using the four sub-components: Strategy, Policy, Enforcement, and Stakeholder Consultation."
    },
    "Ecosystem Infrastructure": {
        "subcategories": ["MRV Systems", "Stakeholder Networks", "Capacity Building", "Financing Mechanisms"],
        "ai_prompt": "Assess the maturity of the ecosystem infrastructure using sub-components like MRV systems, stakeholder networks, capacity building, and financing mechanisms."
    },
    "Finance Providers": {
        "subcategories": ["Public Funding", "Private Investment", "Carbon Markets", "Donor Support"],
        "ai_prompt": "Assess the finance providers' landscape including public funding, private investment, carbon markets, and donor support."
    },
    "Finance Seekers": {
        "subcategories": ["Project Pipeline", "Diversification", "Inclusion", "Stakeholder Engagement"],
        "ai_prompt": "Assess the readiness of finance seekers, considering project pipeline, diversification, inclusion, and stakeholder engagement."
    }
}

# Display the UI for the selected dimension
def show_dimension_ui(dimension_name):
    dimension = DIMENSIONS[dimension_name]
    total_score = None
    score_class = ""
    
    st.markdown(f"### {dimension_name} Scoring")
    
    use_ai = st.checkbox(f"Use AI to score {dimension_name}", value=False)
    
    if use_ai:
        narrative = st.text_area(f"Provide a narrative description of the {dimension_name.lower()}:")
        if narrative:
            with st.spinner("Analyzing with AI..."):
                output = get_ai_score(dimension["ai_prompt"], narrative)
                st.markdown("**AI-Generated Assessment and Recommendations:**")
                st.markdown(output)
            total_score = "AI-Based"
            score_class = "score-medium"
    else:
        st.markdown(f"### Manual Scoring for {dimension_name}")
        
        # Manual scoring for subcategories
        scores = {}
        for subcategory in dimension["subcategories"]:
            scores[subcategory] = st.checkbox(f"Assess {subcategory}")
        
        # Calculate the score for this dimension
        total_score = sum([1 for score in scores.values() if score])
        total_score = min(total_score, len(dimension["subcategories"]))
        
        if total_score < 1.5:
            score_class = "score-low"
        elif total_score < 2.5:
            score_class = "score-medium"
        else:
            score_class = "score-high"
        
        st.markdown(f"**Score for {dimension_name}:** {total_score}/{len(dimension['subcategories'])}")
    
    # Floating live score
    if total_score is not None:
        st.markdown(f"""
        <div class="bottom-box {score_class}" style="bottom: 60px; right: 30px; position: fixed;">
            <strong>Live {dimension_name} Score:</strong><br> {total_score}/{len(dimension['subcategories'])}
        </div>
        """, unsafe_allow_html=True)

# Display dimension selector in the sidebar
selected_dimension = st.sidebar.selectbox("Select Dimension", list(DIMENSIONS.keys()))

# Show the UI for the selected dimension
show_dimension_ui(selected_dimension)

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
