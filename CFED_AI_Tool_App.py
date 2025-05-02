import streamlit as st
import openai
import os
import base64
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import re

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

def extract_score(text):
    match = re.search(r"([1-4])", text)
    return int(match.group(1)) if match else None

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
    pdf.multi_cell(0, 10, "Climate Finance Team
Chemonics International
2025")

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_buffer = BytesIO(pdf_bytes)
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

sections = [
    ("Enabling Environment", "Describe the enabling environment (e.g., NDCs, enforcement, sector policies):"),
    ("Ecosystem Infrastructure", "Describe the ecosystem infrastructure (e.g., MRV systems, data, institutional capacity):"),
    ("Finance Providers", "Describe the finance providers landscape (e.g., public/private climate finance, carbon markets):"),
    ("Finance Seekers", "Describe the finance seekers (e.g., project pipeline, diversity, inclusion):")
]

for section_title, prompt_text in sections:
    st.markdown(f"""
    <div style='background-color:#E5F3F8;padding:1.2em;border-radius:10px;'>
    <h3 style='color:#005670'> {section_title} </h3>
    </div>
    """, unsafe_allow_html=True)

    use_ai = st.checkbox(f"Use AI to score {section_title}", value=False, key=section_title)
    if use_ai:
        user_input = st.text_area(prompt_text, height=200, key=section_title + "_ai")
        if user_input:
            with st.spinner("Scoring with AI..."):
                ai_response = get_ai_score(f"You are a climate finance expert. Score the {section_title.lower()} from 1 to 4 based on the country description. Justify the score.", user_input)
                st.markdown("**AI Suggested Score and Rationale:**")
                st.markdown(ai_response)
                ai_score = extract_score(ai_response)
                if ai_score:
                    scores_data.append([section_title, ai_score])
    else:
        score = 1
        for i in range(3):
            answer = st.radio(f"{section_title} question {i+1}", ["No", "Yes"], key=section_title + str(i))
            if answer == "Yes":
                score += 1
        scores_data.append([section_title, min(score, 4)])

if scores_data:
    score_df = pd.DataFrame(scores_data, columns=["Dimension", "Score"])
    st.markdown("---")
    st.dataframe(score_df, use_container_width=True)
    total_average = round(score_df["Score"].mean(), 2)
    st.markdown(f"<div class='live-score'>🧮 <strong>Live Maturity Score:</strong> {total_average}/4</div>", unsafe_allow_html=True)
    st.markdown(f"### 🧮 Average Ecosystem Maturity Score: {total_average}/4")
    st.markdown("**Suggested Actions:**")
    if total_average < 2:
        st.warning("Foundational support needed: Start with policy frameworks, MRV systems, and project pipeline development.")
    elif 2 <= total_average < 3:
        st.info("Moderate maturity: Expand partnerships, deepen private finance engagement, and strengthen enforcement.")
    else:
        st.success("Strong ecosystem: Prioritize scaling solutions, regional leadership, and blended finance innovation.")
    render_export_buttons(score_df)

st.markdown("---")
st.caption("Prototype built for CFED AI tool – All Four Dimensions. To view a walkthrough of how to use this tool, visit: https://cfed-tool-guide.streamlit.app. For definitions, see the CFED Glossary.")
st.markdown("""
<style>
.sticky-footer {
  position: fixed;
  bottom: 0;
  width: 100%;
  background-color: #005670;
  color: white;
  text-align: center;
  padding: 10px;
  font-size: 13px;
  z-index: 1000;
}
</style>
<div class='sticky-footer'>
  © 2025 Chemonics International Inc. | Contact: Climate Finance Team
</div>
""", unsafe_allow_html=True)
