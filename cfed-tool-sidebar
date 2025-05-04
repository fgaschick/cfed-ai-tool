import streamlit as st
from openai import OpenAI
import os

# Set OpenAI API key using environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY environment variable not set.")
    st.stop()

client = OpenAI(api_key=api_key)

# Custom Sidebar Styling for Chemonics
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
    .sidebar .sidebar-selectbox, .sidebar .stButton button {
        background-color: #005670;
        color: white;
        border-radius: 5px;
    }
    .sidebar .sidebar-selectbox:hover, .sidebar .stButton button:hover {
        background-color: #003f4f; /* Darker blue for hover */
    }
    .sidebar .stCheckbox input {
        background-color: #005670;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar: Select dimension
dimension = st.sidebar.selectbox(
    "Select Dimension",
    ["Enabling Environment", "Ecosystem Infrastructure", "Finance Providers", "Finance Seekers"]
)

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

# Function to display questions based on selected dimension
def display_dimension_questions(dimension):
    if dimension == "Enabling Environment":
        st.markdown("### Enabling Environment Questions")
        st.checkbox("Has the country submitted an NDC?")
        st.checkbox("Are NDCs linked to investment or implementation plans?")
        st.checkbox("Does the NDC include financing targets or mechanisms?")
        # Add more questions as needed
        
    elif dimension == "Ecosystem Infrastructure":
        st.markdown("### Ecosystem Infrastructure Questions")
        st.checkbox("Are MRV systems and climate data tools in place?")
        st.checkbox("Are there active stakeholder networks?")
        # Add more questions as needed
        
    elif dimension == "Finance Providers":
        st.markdown("### Finance Providers Questions")
        st.checkbox("Is there domestic public funding for climate?")
        st.checkbox("Is the country active in voluntary or compliance carbon markets?")
        # Add more questions as needed
        
    elif dimension == "Finance Seekers":
        st.markdown("### Finance Seekers Questions")
        st.checkbox("Is there a robust pipeline of fundable climate projects?")
        st.checkbox("Do projects span adaptation, mitigation, and nature-based solutions?")
        # Add more questions as needed

# Display the questions for the selected dimension
display_dimension_questions(dimension)

# Live Score (floating score displayed on the sidebar)
live_score = 3  # Replace with your score calculation logic
st.sidebar.markdown(f"### Live Score: {live_score}/3")
