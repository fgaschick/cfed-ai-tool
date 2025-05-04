import streamlit as st
import openai
import os
import base64
import pandas as pd
from fpdf import FPDF

# Set your OpenAI API key
openai.api_key = 'your-openai-api-key'

# Function to generate AI-driven recommendations based on scores
def generate_recommendations(scores_data, dimension_name):
    try:
        # Convert the scores data into a formatted string for the AI
        scores_str = "\n".join([f"{dimension}: {score}" for dimension, score in scores_data])
        
        prompt = f"Given the following scores for each dimension in the Climate Finance Ecosystem:\n\n{scores_str}\n\n" \
                 f"Based on the {dimension_name} dimension, provide tailored, actionable recommendations. " \
                 "The recommendations should be specific, actionable, and grounded in the context of climate finance. " \
                 "Please suggest improvements for the {dimension_name} dimension."
        
        # Call OpenAI to generate recommendations
        response = openai.Completion.create(
            model="gpt-4",  # Using GPT-4 for advanced responses
            prompt=prompt,
            max_tokens=300
        )
        
        recommendations = response.choices[0].text.strip()
        return recommendations
    
    except Exception as e:
        return f"Error generating recommendations: {e}"

# Streamlit UI for displaying the tool
st.title("Climate Finance Ecosystem Diagnostic Tool")
st.subheader("AI-driven Recommendations for Climate Finance Ecosystem Maturity")

# Sample scores data for testing the recommendation engine
scores_data = [
    ("Enabling Environment", 3),
    ("Ecosystem Infrastructure", 2),
    ("Finance Providers", 4),
    ("Finance Seekers", 3)
]

# Function to display dynamic recommendations per dimension
def display_dynamic_recommendations():
    # Collecting inputs for each dimension
    enabling_env_score = st.slider("Enabling Environment", 1, 4, 3)
    ecosystem_score = st.slider("Ecosystem Infrastructure", 1, 4, 2)
    finance_providers_score = st.slider("Finance Providers", 1, 4, 4)
    finance_seekers_score = st.slider("Finance Seekers", 1, 4, 3)
    
    # User scores
    user_scores = [
        ("Enabling Environment", enabling_env_score),
        ("Ecosystem Infrastructure", ecosystem_score),
        ("Finance Providers", finance_providers_score),
        ("Finance Seekers", finance_seekers_score)
    ]
    
    # Display the user scores
    st.write("User Scores:", user_scores)

    # Generate dynamic recommendations per dimension
    st.subheader("Recommendations per Dimension")

    # Enabling Environment Recommendations
    enabling_env_recommendations = generate_recommendations(user_scores, "Enabling Environment")
    st.write("### Enabling Environment Recommendations:")
    st.write(enabling_env_recommendations)

    # Ecosystem Infrastructure Recommendations
    ecosystem_recommendations = generate_recommendations(user_scores, "Ecosystem Infrastructure")
    st.write("### Ecosystem Infrastructure Recommendations:")
    st.write(ecosystem_recommendations)

    # Finance Providers Recommendations
    finance_providers_recommendations = generate_recommendations(user_scores, "Finance Providers")
    st.write("### Finance Providers Recommendations:")
    st.write(finance_providers_recommendations)

    # Finance Seekers Recommendations
    finance_seekers_recommendations = generate_recommendations(user_scores, "Finance Seekers")
    st.write("### Finance Seekers Recommendations:")
    st.write(finance_seekers_recommendations)

    # Summary of recommendations
    st.subheader("Summary of Recommendations")
    overall_recommendations = generate_recommendations(user_scores, "Overall")
    st.write("### General Action Plan:")
    st.write(overall_recommendations)

# Streamlit UI for displaying the tool and collecting user inputs
with st.expander("📘 Walkthrough Guide – How to Use This Tool"):
    st.markdown("""
    1. Start with **Enabling Environment**.
       - Use **AI Scoring** to type a short description, or **Manual Scoring** to answer yes/no questions.
    2. Move to **Ecosystem Infrastructure**, **Finance Providers**, and **Finance Seekers** the same way.
    3. Scores in the upper right will update as you provide responses. Scroll down to see recommended actions once you complete the assessment.
    4. Click the download links to **export results** as a PDF or CSV.
    5. You can go back and edit your responses at any time.
    """)

# Display recommendations dynamically
display_dynamic_recommendations()

# --- Helper: PDF Export ---
def generate_pdf_report(scores_data, overall_recommendations):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Climate Finance Ecosystem Diagnostic Tool - Recommendations", ln=True, align="C")
    pdf.ln(10)
    
    # Add recommendations for each dimension
    for dimension, score in scores_data:
        pdf.cell(200, 10, txt=f"{dimension}: {score}/4", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, txt="### Summary of Recommendations:", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, overall_recommendations)
    
    # Output the PDF
    pdf_output = "climate_finance_recommendations.pdf"
    pdf.output(pdf_output)
    return pdf_output

# --- Downloadable PDF ---
def download_pdf(pdf_output):
    with open(pdf_output, "rb") as pdf_file:
        b64_pdf = base64.b64encode(pdf_file.read()).decode()
        href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="climate_finance_recommendations.pdf">📄 Download Recommendations as PDF</a>'
        st.markdown(href_pdf, unsafe_allow_html=True)

# Generate PDF and allow download
pdf_output = generate_pdf_report(scores_data, overall_recommendations)
download_pdf(pdf_output)

# --- Downloadable CSV ---
def download_csv(scores_data):
    score_df = pd.DataFrame(scores_data, columns=["Dimension", "Score"])
    csv = score_df.to_csv(index=False)
    b64_csv = base64.b64encode(csv.encode()).decode()
    href_csv = f'<a href="data:file/csv;base64,{b64_csv}" download="cfed_scores.csv">📥 Download scores as CSV</a>'
    st.markdown(href_csv, unsafe_allow_html=True)

download_csv(scores_data)

st.markdown("---")
st.caption("Prototype built for CFED AI tool – All Four Dimensions. To view a walkthrough of how to use this tool, visit: https://cfed-tool-guide.streamlit.app.")
