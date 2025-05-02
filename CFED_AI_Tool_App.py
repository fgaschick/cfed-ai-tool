import streamlit as st
import openai
import os
import base64
import pandas as pd
from fpdf import FPDF
from io import BytesIO

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="CFED AI Diagnostic Tool", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
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
        width: 100%; 
        background-color: #005670; 
        color: white; 
        text-align: center; 
        padding: 10px; 
        font-size: 13px; 
    }
    .header-bar {
        position: fixed;
        top: 0;
        width: 100%;
        background-color: #005670;
        padding: 1em;
        text-align: center;
        z-index: 1000;
    }
    .header-bar img {
        width: 200px;
    }
    .live-score {
        position: fixed;
        top: 120px;
        right: 30px;
        background-color: #ffffff;
        border: 2px solid #005670;
        padding: 10px;
        border-radius: 8px;
        z-index: 1001;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #005670;
    }
    .stButton>button {
        background-color: #005670;
        color: white;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #003f4f;
    }
    </style>
    <div class='custom-footer'>
        © 2025 Chemonics International Inc. | Contact: Climate Finance Team
    </div>
    <div class='header-bar'>
        <img src='https://raw.githubusercontent.com/fgaschick/cfed-ai-tool/main/Chemonics_RGB_Horizontal_BLUE-WHITE.png' alt='Chemonics Logo'/>
    </div>
    <br><br><br><br>
""", unsafe_allow_html=True)

st.title("Climate Finance Ecosystem Diagnostic (CFED)")
st.subheader("AI-Assisted Climate Finance Ecosystem Maturity Scoring Tool – Prototype")

with st.expander("📘 Walkthrough Guide – How to Use This Tool"):
    st.markdown("""
    1. Start with **Enabling Environment**.
       - Use **AI Scoring** to type a short description, or **Manual Scoring** to answer yes/no questions.
    2. Move to **Ecosystem Infrastructure**, **Finance Providers**, and **Finance Seekers** the same way.
    3. Scores in the upper right will update as you provide responses. Scroll down to see recommended actions once you complete the assessment.
    4. Click the download links to **export results** as a PDF or CSV.
    5. You can go back and edit your responses at any time.
    """)

st.markdown("""
    This tool is designed by Chemonics International to help governments, donors, and implementing partners rapidly assess the maturity of a country's climate finance ecosystem.

    Users can choose either AI-generated scoring or manual scoring for four key areas:
    - Enabling Environment
    - Ecosystem Infrastructure
    - Finance Providers
    - Finance Seekers

    The tool helps identify maturity gaps, prioritize investments, and track progress over time. Results can be exported in PDF and CSV formats.
""")

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
    except openai.RateLimitError:
        return "⚠️ Your OpenAI quota has been exceeded. Please use manual scoring."
    except Exception as e:
        return f"Unexpected error from OpenAI: {e}"

def generate_pdf(score_df, total_average):
    pdf = FPDF()
    pdf.add_page()
    logo_file = "Chemonics_RGB_Horizontal_BLUE-WHITE.png"
    try:
        pdf.image(logo_file, x=10, y=8, w=50)
    except:
        pass
    pdf.set_font("Arial", size=12)
    pdf.ln(30)
    pdf.cell(200, 10, txt="CFED Maturity Assessment Summary", ln=True, align="C")
    pdf.ln(10)
    for index, row in score_df.iterrows():
        pdf.cell(200, 10, txt=f"{row['Dimension']}: {row['Score']}/4", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Average Maturity Score: {total_average}/4", ln=True)
    pdf.ln(20)
    pdf.set_font("Arial", style="I", size=11)
    pdf.multi_cell(0, 10, "Climate Finance Team\nChemonics International\n2025")
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

def render_export_buttons(score_df):
    csv = score_df.to_csv(index=False)
    b64_csv = base64.b64encode(csv.encode()).decode()
    href_csv = f'<a href="data:file/csv;base64,{b64_csv}" download="cfed_scores.csv">📅 Download scores as CSV</a>'
    st.markdown(href_csv, unsafe_allow_html=True)
    total_average = round(score_df["Score"].mean(), 2)
    pdf_buffer = generate_pdf(score_df, total_average)
    b64_pdf = base64.b64encode(pdf_buffer.read()).decode()
    href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="cfed_scores.pdf">📄 Download scores as PDF</a>'
    st.markdown(href_pdf, unsafe_allow_html=True)

scores_data = []

# Scoring sections
with st.form("score_form"):
    st.markdown("### 1. Enabling Environment")
    use_ai_ee = st.checkbox("Use AI to score Enabling Environment", value=False)
    if use_ai_ee:
        input_ee = st.text_area("Describe the enabling environment:")
        if input_ee:
            result = get_ai_score("You are a climate finance expert. Score the enabling environment from 1 to 4 based on the country description. Justify the score.", input_ee)
            st.markdown("**AI Suggested Score and Rationale:**")
            st.markdown(result)
    else:
        score = 1
        if st.radio("Has NDC?", ["No", "Yes"]) == "Yes":
            score += 1
            if st.selectbox("NDC Quality", ["Low", "Medium", "High"]) == "High":
                score += 1
        if st.radio("Sector policies?", ["No", "Yes"]) == "Yes":
            score += 1
        if st.radio("Enforcement?", ["No", "Yes"]) == "Yes":
            score += 1
        scores_data.append(["Enabling Environment", min(score, 4)])

    st.markdown("### 2. Ecosystem Infrastructure")
    use_ai_ei = st.checkbox("Use AI to score Ecosystem Infrastructure", value=False)
    if use_ai_ei:
        input_ei = st.text_area("Describe the ecosystem infrastructure:")
        if input_ei:
            result = get_ai_score("You are a climate finance expert. Score the ecosystem infrastructure from 1 to 4 based on the country description. Justify the score.", input_ei)
            st.markdown("**AI Suggested Score and Rationale:**")
            st.markdown(result)
    else:
        score = 1
        if st.radio("MRV systems?", ["No", "Yes"]) == "Yes":
            score += 1
        if st.radio("Stakeholder networks?", ["No", "Yes"]) == "Yes":
            score += 1
        if st.radio("Institutional capacity?", ["No", "Yes"]) == "Yes":
            score += 1
        scores_data.append(["Ecosystem Infrastructure", min(score, 4)])

    st.markdown("### 3. Finance Providers")
    use_ai_fp = st.checkbox("Use AI to score Finance Providers", value=False)
    if use_ai_fp:
        input_fp = st.text_area("Describe the finance providers:")
        if input_fp:
            result = get_ai_score("You are a climate finance expert. Score the finance providers from 1 to 4 based on the country description. Justify the score.", input_fp)
            st.markdown("**AI Suggested Score and Rationale:**")
            st.markdown(result)
    else:
        score = 1
        if st.radio("Public climate funding?", ["No", "Yes"]) == "Yes":
            score += 1
        if st.radio("Carbon market?", ["No", "Yes"]) == "Yes":
            score += 1
        if st.radio("Private investment?", ["No", "Yes"]) == "Yes":
            score += 1
        scores_data.append(["Finance Providers", min(score, 4)])

    st.markdown("### 4. Finance Seekers")
    use_ai_fs = st.checkbox("Use AI to score Finance Seekers", value=False)
    if use_ai_fs:
        input_fs = st.text_area("Describe the finance seekers:")
        if input_fs:
            result = get_ai_score("You are a climate finance expert. Score the finance seekers from 1 to 4 based on the country description. Justify the score.", input_fs)
            st.markdown("**AI Suggested Score and Rationale:**")
            st.markdown(result)
    else:
        score = 1
        if st.radio("Project pipeline?", ["No", "Yes"]) == "Yes":
            score += 1
        if st.radio("Project diversity?", ["No", "Yes"]) == "Yes":
            score += 1
        if st.radio("Inclusive targeting?", ["No", "Yes"]) == "Yes":
            score += 1
        scores_data.append(["Finance Seekers", min(score, 4)])

    submitted = st.form_submit_button("Finish Scoring and Show Results")

if submitted:
    score_df = pd.DataFrame(scores_data, columns=["Dimension", "Score"])
    if not score_df.empty:
        st.dataframe(score_df, use_container_width=True)
        st.markdown(f"<div class='live-score'>🧮 <strong>Live Maturity Score:</strong> {round(score_df['Score'].mean(), 2)}/4</div>", unsafe_allow_html=True)
        st.markdown(f"### 🧮 Average Ecosystem Maturity Score: {round(score_df['Score'].mean(), 2)}/4")
        st.markdown("**Suggested Actions:**")
        avg = round(score_df["Score"].mean(), 2)
        if avg < 2:
            st.warning("Foundational support needed: Start with policy frameworks, MRV systems, and project pipeline development.")
        elif 2 <= avg < 3:
            st.info("Moderate maturity: Expand partnerships, deepen private finance engagement, and strengthen enforcement.")
        else:
            st.success("Strong ecosystem: Prioritize scaling solutions, regional leadership, and blended finance innovation.")
        render_export_buttons(score_df)
