import streamlit as st
from openai import OpenAI
import os

# Set OpenAI API key using environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY environment variable not set.")
    st.stop()

client = OpenAI(api_key=api_key)

# Function to get AI score (reused from previous implementation)
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

# Sidebar Styling for Chemonics
st.markdown("""
    <style>
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background-color: #005670; /* Chemonics blue */
        color: white;
        font-family: 'Roboto', sans-serif;
    }
    .sidebar .sidebar-header {
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 20px;
        font-weight: bold;
    }
    .sidebar .sidebar-tabs {
        margin-top: 30px;
        color: white;
        padding: 10px;
        font-weight: bold;
        cursor: pointer;
        text-align: center;
    }
    .sidebar .sidebar-tabs:hover {
        background-color: #003f4f; /* Darker blue for hover */
    }
    .sidebar .active-tab {
        background-color: #003f4f;
    }
    .sidebar .tab-content {
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar: Dimension Selection
dimension = st.sidebar.radio(
    "Select Dimension", 
    ["Instructions", "Enabling Environment", "Ecosystem Infrastructure", "Finance Providers", "Finance Seekers"]
)

# Function to display questions based on selected dimension
def display_dimension_questions(dimension):
    if dimension == "Enabling Environment":
        st.markdown("### Enabling Environment Questions")
        s1 = st.checkbox("Has the country submitted an NDC?")
        s2 = st.checkbox("Are NDCs linked to investment or implementation plans?")
        s3 = st.checkbox("Does the NDC include financing targets or mechanisms?")
        # Add more questions as needed
        # Score calculation
        ee_score = s1 + s2 + s3
        st.sidebar.markdown(f"**Live Score**: {ee_score}/3")
        
    elif dimension == "Ecosystem Infrastructure":
        st.markdown("### Ecosystem Infrastructure Questions")
        mrv = st.checkbox("Are MRV systems and climate data tools in place?")
        partnerships = st.checkbox("Are there active stakeholder networks?")
        climate_capacity = st.checkbox("Do institutions have adequate climate finance capacity?")
        # Score calculation
        infra_score = mrv + partnerships + climate_capacity
        st.sidebar.markdown(f"**Live Score**: {infra_score}/3")
        
    elif dimension == "Finance Providers":
        st.markdown("### Finance Providers Questions")
        public_funding = st.checkbox("Is there domestic public funding for climate?")
        carbon_market = st.checkbox("Is the country active in voluntary or compliance carbon markets?")
        private_investment = st.checkbox("Is commercial/private capital flowing into climate sectors?")
        # Score calculation
        providers_score = public_funding + carbon_market + private_investment
        st.sidebar.markdown(f"**Live Score**: {providers_score}/3")
        
    elif dimension == "Finance Seekers":
        st.markdown("### Finance Seekers Questions")
        project_pipeline = st.checkbox("Is there a robust pipeline of fundable climate projects?")
        project_diversity = st.checkbox("Do projects span adaptation, mitigation, and nature-based solutions?")
        inclusive_targeting = st.checkbox("Are vulnerable or underserved groups targeted in project design?")
        # Score calculation
        seekers_score = project_pipeline + project_diversity + inclusive_targeting
        st.sidebar.markdown(f"**Live Score**: {seekers_score}/3")

# Display the selected tab's content
if dimension == "Instructions":
    st.markdown("""
    ### 📘 Instructions
    This tool helps evaluate the maturity of a country's climate finance ecosystem. Choose a dimension to start the assessment.
    - **Enabling Environment**: Evaluate the national climate strategy, policies, and enforcement.
    - **Ecosystem Infrastructure**: Assess the availability of tools and partnerships.
    - **Finance Providers**: Check the involvement of public/private funding and carbon markets.
    - **Finance Seekers**: Evaluate the readiness of climate projects and inclusion of vulnerable groups.
    """)
else:
    # Display the questions for the selected dimension
    display_dimension_questions(dimension)

# Display Live Score in Sidebar for Each Dimension (floating score)
if dimension != "Instructions":
    st.sidebar.markdown(f"**Live Score for {dimension}:** {ee_score}/3")

# AI-generated recommendations for each dimension
if st.button("✅ Generate AI-Based Recommendations"):
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

