import streamlit as st
from openai import OpenAI
import os

# Set OpenAI API key using environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY environment variable not set.")
    st.stop()

client = OpenAI(api_key=api_key)

# Function to call OpenAI API for AI scoring
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

# Function to calculate score for each subcategory based on user input
def score_subcategory(answers):
    return min(4, sum(answers))  # Adjusting max score to 4 for each subcategory

# Initialize session state for combined score and dimension scores
if 'combined_score' not in st.session_state:
    st.session_state.combined_score = 0
if 'dimension_scores' not in st.session_state:
    st.session_state.dimension_scores = {dim: 0 for dim in ["Enabling Environment", "Ecosystem Infrastructure", "Finance Providers", "Finance Seekers"]}

# Define the dimensions and their subcategories with questions
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

# Sidebar for selecting dimension
selected_dimension = st.sidebar.selectbox("Select Dimension", list(DIMENSIONS.keys()))

# Function to display and score each dimension's subcategories
def display_dimension_scoring(dimension_name):
    dimension_data = DIMENSIONS[dimension_name]
    total_dimension_score = 0
    for subcategory_name, questions in dimension_data["subcategories"].items():
        st.markdown(f"### {subcategory_name}")
        answers = [st.checkbox(q) for q in questions]
        subcategory_score = score_subcategory(answers)
        total_dimension_score += subcategory_score
        st.markdown(f"Score for {subcategory_name}: {subcategory_score}/{len(questions)*4}")
    
    # Store the dimension score in session state
    st.session_state.dimension_scores[dimension_name] = total_dimension_score
    return total_dimension_score

# Show the dimension UI and calculate the score
total_dimension_score = display_dimension_scoring(selected_dimension)

# Calculate the combined score across all dimensions (max score per dimension is 4)
combined_score = sum(st.session_state.dimension_scores.values())
combined_score_avg = round(combined_score / (4 * len(DIMENSIONS)), 2)  # Maximum score for each dimension is 4

# Display the total score for the selected dimension
st.markdown(f"### Total Score for {selected_dimension}: {total_dimension_score}/{4 * sum(len(DIMENSIONS[selected_dimension]['subcategories'][subcat]) for subcat in DIMENSIONS[selected_dimension]['subcategories'])}")

# Floating live score on the sidebar
st.sidebar.markdown(f"**Live Score for {selected_dimension}:** {total_dimension_score}/{4 * sum(len(DIMENSIONS[selected_dimension]['subcategories'][subcat]) for subcat in DIMENSIONS[selected_dimension]['subcategories'])}")

# Display the overall combined score
st.sidebar.markdown(f"**Combined Score of All Dimensions:** {combined_score_avg}/4")

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
