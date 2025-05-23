import streamlit as st
from openai import OpenAI
import os
import base64
import pandas as pd

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

# Set page configuration
st.set_page_config(page_title="Climate Finance Maturity Tool", layout="wide")

# Custom CSS for sidebar and main content
import streamlit.components.v1 as components

components.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    body {
        font-family: 'Roboto', sans-serif;
        background-color: #f5f5f5;
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

    /* Sidebar Customization */
    .sidebar .sidebar-content {
        background-color: #005670;  /* Chemonics Dark Blue */
        color: white;
    }
    .sidebar .sidebar-header {
        background-color: #005670;  /* Chemonics Dark Blue */
        color: white;
    }
    .sidebar .sidebar-title, .sidebar .sidebar-subheader {
        color: white;
    }
    .sidebar .sidebar-sticky {
        position: fixed;
    }
    </style>
""", height=150)

# Sidebar setup for navigation
st.sidebar.image("https://raw.githubusercontent.com/fgaschick/cfed-ai-tool/main/Chemonics_RGB_Horizontal_BLUE-WHITE.png", width=300)
st.sidebar.title("Climate Finance Ecosystem Diagnostic (CFED)")
st.sidebar.subheader("AI-Assisted Climate Finance Ecosystem Maturity Scoring Tool – Prototype")

# Sidebar menu tabs
tabs = ["Instructions", "Enabling Environment", "Ecosystem Infrastructure", "Finance Providers", "Finance Seekers", "Summary & Recommendations"]
selected_tab = st.sidebar.radio("Choose a tab", tabs)

# Initialize variables for tracking scores
dimension_scores = {"Enabling Environment": 0, "Ecosystem Infrastructure": 0, "Finance Providers": 0, "Finance Seekers": 0}
combined_score = 0

# Function to calculate the combined score
def calculate_combined_score():
    return sum(dimension_scores.values()) / 4

# --- Instructions Tab ---
if selected_tab == "Instructions":
    st.markdown("""
        ## Instructions
        This tool helps to assess the maturity of a country's climate finance ecosystem. 
        There are four main dimensions that need to be scored: 
        - Enabling Environment
        - Ecosystem Infrastructure
        - Finance Providers
        - Finance Seekers
        
        You can use either **AI-based scoring** (by providing a narrative description) or **manual scoring** (based on checkboxes). 
        In each dimension, after scoring, you will receive an overall score for that dimension and prioritized recommendations for improvement.
        
        After completing all dimensions, you can see the **Summary & Recommendations** tab where you will find AI-based suggestions for improvements based on your inputs.
    """)

# --- Summary & Recommendations Tab ---
elif selected_tab == "Summary & Recommendations":
    st.markdown("## AI-based Recommendations for Action")
    recommendations = []
    for dimension, score in dimension_scores.items():
        if score < 3:
            prompt = f"Provide 3-5 concrete, prioritized recommendations for improving the {dimension} based on the score of {score}."
            recommendations.append(f"### {dimension} Recommendations:\n{get_ai_score(prompt, '')}")

    for recommendation in recommendations:
        st.markdown(recommendation)

    st.markdown("### Download Recommendations as CSV")
    # Download the AI recommendations as CSV
    data = {"Dimension": list(dimension_scores.keys()), "Score": list(dimension_scores.values()), "Recommendations": recommendations}
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # encoding as base64
    href = f'<a href="data:file/csv;base64,{b64}" download="recommendations.csv">Download as CSV</a>'
    st.markdown(href, unsafe_allow_html=True)

# --- Enabling Environment Dimension ---
elif selected_tab == "Enabling Environment":
    st.title("Enabling Environment Scoring")

    # AI-based scoring option
    use_ai_ee = st.checkbox("Use AI to score Enabling Environment", value=False)
    if use_ai_ee:
        narrative_ee = st.text_area("Provide a narrative description of the enabling environment:", height=300)
        if narrative_ee:
            with st.spinner("Analyzing with AI..."):
                prompt = (
                    "You are a climate finance expert. Based on the following narrative, assess the maturity of the enabling environment using the four sub-components: "
                    "(1) Strategy (NDCs, national plans), (2) Policy (sectoral climate policies), (3) Enforcement (rule of law, anti-corruption), and (4) Stakeholder consultation. "
                    "Assign a maturity score from 0 to 3 for each sub-component and explain each score briefly. Then provide 3 prioritized action recommendations that would help improve the enabling environment if any score is below 3."
                )
                output = get_ai_score(prompt, narrative_ee)
                st.markdown("**AI-Generated Assessment and Recommendations:**")
                st.markdown(output)
            dimension_scores["Enabling Environment"] = 2  # Placeholder value for AI-based score
    else:
        st.markdown("### Manual Scoring (based on sub-indicator evidence)")
        # Manual scoring based on checkboxes
        s1 = st.checkbox("Country has submitted an NDC")
        s2 = st.checkbox("NDC is linked to investment or implementation plans")
        s3 = st.checkbox("NDC or strategy includes financing targets or mechanisms")
        s4 = st.checkbox("There is a national climate finance strategy or roadmap")

        # Compute score for Enabling Environment
        ee_score = sum([s1, s2, s3, s4])
        dimension_scores["Enabling Environment"] = ee_score

        st.markdown(f"**Score for Enabling Environment:** {ee_score}/4")

# --- Ecosystem Infrastructure Dimension ---
elif selected_tab == "Ecosystem Infrastructure":
    st.title("Ecosystem Infrastructure Scoring")
    use_ai_ecosystem = st.checkbox("Use AI to score Ecosystem Infrastructure", value=False)
    if use_ai_ecosystem:
        narrative_ecosystem = st.text_area("Provide a narrative description of the ecosystem infrastructure:", height=300)
        if narrative_ecosystem:
            with st.spinner("Analyzing with AI..."):
                prompt = (
                    "You are a climate finance expert. Based on the following narrative, assess the maturity of the ecosystem infrastructure using the relevant sub-components: "
                    "(1) Physical infrastructure, (2) Data infrastructure, (3) Digital platforms, (4) Regulatory frameworks."
                )
                output = get_ai_score(prompt, narrative_ecosystem)
                st.markdown("**AI-Generated Assessment and Recommendations:**")
                st.markdown(output)
            dimension_scores["Ecosystem Infrastructure"] = 2  # Placeholder value for AI-based score
    else:
        st.markdown("### Manual Scoring (based on sub-indicator evidence)")
        # Manual scoring based on checkboxes
        e1 = st.checkbox("Physical infrastructure for climate adaptation and mitigation exists")
        e2 = st.checkbox("There is a national or regional data infrastructure for monitoring climate impacts")
        e3 = st.checkbox("Climate-related digital platforms are available for stakeholders")
        e4 = st.checkbox("Regulatory frameworks for climate finance and development are in place")

        # Compute score for Ecosystem Infrastructure
        ecosystem_score = sum([e1, e2, e3, e4])
        dimension_scores["Ecosystem Infrastructure"] = ecosystem_score

        st.markdown(f"**Score for Ecosystem Infrastructure:** {ecosystem_score}/4")

# --- Finance Providers Dimension ---
elif selected_tab == "Finance Providers":
    st.title("Finance Providers Scoring")
    use_ai_finance_providers = st.checkbox("Use AI to score Finance Providers", value=False)
    if use_ai_finance_providers:
        narrative_finance_providers = st.text_area("Provide a narrative description of the finance providers:", height=300)
        if narrative_finance_providers:
            with st.spinner("Analyzing with AI..."):
                prompt = (
                    "You are a climate finance expert. Based on the following narrative, assess the maturity of the finance providers using the relevant sub-components: "
                    "(1) Public finance providers, (2) Private finance providers, (3) Development finance institutions, (4) Multilateral development banks."
                )
                output = get_ai_score(prompt, narrative_finance_providers)
                st.markdown("**AI-Generated Assessment and Recommendations:**")
                st.markdown(output)
            dimension_scores["Finance Providers"] = 2  # Placeholder value for AI-based score
    else:
        st.markdown("### Manual Scoring (based on sub-indicator evidence)")
        # Manual scoring based on checkboxes
        f1 = st.checkbox("Public finance providers are operational and engaged in climate finance")
        f2 = st.checkbox("Private finance providers are actively engaged in climate finance")
        f3 = st.checkbox("Development finance institutions provide substantial climate finance")
        f4 = st.checkbox("Multilateral development banks are active in the climate finance ecosystem")

        # Compute score for Finance Providers
        finance_providers_score = sum([f1, f2, f3, f4])
        dimension_scores["Finance Providers"] = finance_providers_score

        st.markdown(f"**Score for Finance Providers:** {finance_providers_score}/4")

# --- Finance Seekers Dimension ---
elif selected_tab == "Finance Seekers":
    st.title("Finance Seekers Scoring")
    use_ai_finance_seekers = st.checkbox("Use AI to score Finance Seekers", value=False)
    if use_ai_finance_seekers:
        narrative_finance_seekers = st.text_area("Provide a narrative description of the finance seekers:", height=300)
        if narrative_finance_seekers:
            with st.spinner("Analyzing with AI..."):
                prompt = (
                    "You are a climate finance expert. Based on the following narrative, assess the maturity of the finance seekers using the relevant sub-components: "
                    "(1) Project proposals, (2) Pipeline of projects, (3) Access to finance, (4) Stakeholder engagement."
                )
                output = get_ai_score(prompt, narrative_finance_seekers)
                st.markdown("**AI-Generated Assessment and Recommendations:**")
                st.markdown(output)
            dimension_scores["Finance Seekers"] = 2  # Placeholder value for AI-based score
    else:
        st.markdown("### Manual Scoring (based on sub-indicator evidence)")
        # Manual scoring based on checkboxes
        s1 = st.checkbox("Project proposals are well developed and aligned with climate finance needs")
        s2 = st.checkbox("A pipeline of climate projects is available for financing")
        s3 = st.checkbox("There is easy access to finance for climate-related projects")
        s4 = st.checkbox("Stakeholder engagement is integral to project development")

        # Compute score for Finance Seekers
        finance_seekers_score = sum([s1, s2, s3, s4])
        dimension_scores["Finance Seekers"] = finance_seekers_score

        st.markdown(f"**Score for Finance Seekers:** {finance_seekers_score}/4")

# --- Floating Sidebar with Scores ---
st.sidebar.markdown("## Scores Overview")
for dimension, score in dimension_scores.items():
    st.sidebar.markdown(f"**{dimension}**: {score}/4")

combined_score = calculate_combined_score()
st.sidebar.markdown(f"**Combined Score**: {combined_score}/4")

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
