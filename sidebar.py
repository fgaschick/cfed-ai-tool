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

# Function to display scoring UI for subcategories
def show_scoring_ui(subcategory_name, dimension_name, dimension_data):
    st.markdown(f"### {subcategory_name} Scoring")
    answers = []

    # For each question in the selected subcategory, display a checkbox
    for question in dimension_data["subcategories"][subcategory_name]:
        answer = st.checkbox(question)
        answers.append(answer)

    # Calculate score for subcategory
    subcategory_score = sum(answers)
    st.markdown(f"**Score for {subcategory_name}:** {subcategory_score}/{len(answers)}")

    return subcategory_score

# DIMENSIONS structure to include questions for each subcategory
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
    "Ecosystem Infrastructure": {
        "subcategories": {
            "Monitoring Systems": [
                "Are there systems in place for monitoring and evaluating ecosystem data?",
                "Are these systems effectively capturing climate data?"
            ],
            "Institutional Capacity": [
                "Are there institutions with sufficient capacity to implement climate finance?",
                "Is there adequate staff training and expertise in climate finance?"
            ],
            "Data Availability": [
                "Is data on climate impacts and vulnerabilities available?",
                "Are data systems transparent and accessible?"
            ]
        }
    },
    "Finance Providers": {
        "subcategories": {
            "Public Finance": [
                "Is there public finance allocated for climate projects?",
                "Are public funds mobilized for mitigation and adaptation?"
            ],
            "Private Finance": [
                "Is there active private investment in climate action?",
                "Do banks and financial institutions fund climate-relevant projects?"
            ],
            "International Support": [
                "Does the country receive international climate finance?",
                "Are foreign investments supporting local climate initiatives?"
            ]
        }
    },
    "Finance Seekers": {
        "subcategories": {
            "Project Pipeline": [
                "Is there a robust pipeline of fundable climate projects?",
                "Are projects aligned with national climate goals?"
            ],
            "Private Sector Engagement": [
                "Are private sector entities engaged in climate projects?",
                "Do they contribute to climate resilience or emission reduction?"
            ],
            "Capacity to Absorb Funds": [
                "Does the country have institutions capable of managing climate finance?",
                "Are there transparent processes for fund distribution?"
            ]
        }
    }
}

# Initialize session state for combined score and dimension scores
if 'combined_score' not in st.session_state:
    st.session_state.combined_score = 0
if 'dimension_scores' not in st.session_state:
    st.session_state.dimension_scores = {dim: 0 for dim in DIMENSIONS}

# Sidebar for selecting dimension
selected_dimension = st.sidebar.selectbox("Select Dimension", list(DIMENSIONS.keys()))

# Function for AI-based scoring
def ai_scoring_ui(dimension_name):
    use_ai = st.checkbox(f"Use AI to score {dimension_name}", value=False)
    if use_ai:
        narrative = st.text_area(f"Provide a narrative description for {dimension_name}:", height=300)
        if narrative:
            prompt = (
                f"You are a climate finance expert. Based on the following narrative, assess the maturity of the {dimension_name} using the relevant sub-components "
                "and assign a maturity score from 0 to 3 for each sub-component. Please also provide prioritized action recommendations."
            )
            with st.spinner(f"Analyzing {dimension_name} with AI..."):
                ai_output = get_ai_score(prompt, narrative)
            st.markdown("**AI-Generated Assessment and Recommendations:**")
            st.markdown(ai_output)

# Initialize variable to store total dimension score
dimension_score = 0

# Function to calculate combined score for all dimensions
combined_score = st.session_state.combined_score
total_dimensions = len(DIMENSIONS)

# Display dimension and subcategories
st.markdown(f"## {selected_dimension} Scoring")

# AI scoring
ai_scoring_ui(selected_dimension)

# Manual rule-based scoring
for subcategory_name in DIMENSIONS[selected_dimension]["subcategories"]:
    subcategory_score = show_scoring_ui(subcategory_name, selected_dimension, DIMENSIONS[selected_dimension])
    dimension_score += subcategory_score

# Update dimension score in session state
st.session_state.dimension_scores[selected_dimension] = dimension_score

# Calculate overall score for the dimension
dimension_score = round(dimension_score / sum(len(DIMENSIONS[selected_dimension]["subcategories"][subcat]) for subcat in DIMENSIONS[selected_dimension]["subcategories"]), 2)

# Update combined score
combined_score += dimension_score

# Update session state for combined score
st.session_state.combined_score = combined_score

# Display the overall dimension score
st.markdown(f"### Overall Score for {selected_dimension}: {dimension_score}/3")

# Floating live score on the sidebar
st.sidebar.markdown(f"**Live {selected_dimension} Score:** {dimension_score}/3")

# Calculate and display the combined score
combined_score_avg = round(st.session_state.combined_score / total_dimensions, 2)
st.sidebar.markdown(f"**Combined Score of All Dimensions:** {combined_score_avg}/3")

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
