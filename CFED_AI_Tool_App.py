import streamlit as st
import openai
import os
import base64
import pandas as pd
from fpdf import FPDF

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Page configuration
st.set_page_config(page_title="CFED AI Diagnostic Tool", layout="wide")
st.title("Climate Finance Ecosystem Diagnostic (CFED)")
st.subheader("AI-Assisted Maturity Scoring Tool – Full Prototype")

st.markdown("""
This interactive tool estimates the maturity of a country’s climate finance ecosystem across all four CFED dimensions. You can either use AI-generated scoring (by describing the situation) or answer simple questions.
""")

st.markdown("---")

# --- Helper: AI scoring function ---
def get_ai_score(prompt, user_input):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error from OpenAI: {e}"

# --- Scoring Data ---
scores_data = []

# --- Section Handlers (omitted for brevity, same as before) ---
# Keep the full dimension sections as they are (AI/manual)

# ... [all scoring sections stay unchanged] ...

# --- Results Section ---
st.markdown("---")
st.header("Results Summary")

score_df = pd.DataFrame(scores_data, columns=["Dimension", "Score"])
if not score_df.empty:
    st.dataframe(score_df, use_container_width=True)
    total_average = round(score_df["Score"].mean(), 2)
    st.markdown(f"### 🧮 Average Ecosystem Maturity Score: {total_average}/4")

    st.markdown("**Suggested Actions:**")
    if total_average < 2:
        st.warning("Foundational support needed: Start with policy frameworks, MRV systems, and project pipeline development.")
    elif 2 <= total_average < 3:
        st.info("Moderate maturity: Expand partnerships, deepen private finance engagement, and strengthen enforcement.")
    else:
        st.success("Strong ecosystem: Prioritize scaling solutions, regional leadership, and blended finance innovation.")

    # --- Downloadable CSV ---
    csv = score_df.to_csv(index=False)
    b64_csv = base64.b64encode(csv.encode()).decode()
    href_csv = f'<a href="data:file/csv;base64,{b64_csv}" download="cfed_scores.csv">📥 Download scores as CSV</a>'
    st.markdown(href_csv, unsafe_allow_html=True)

    # --- Downloadable PDF ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="CFED Maturity Assessment Summary", ln=True, align="C")
    pdf.ln(10)
    for index, row in score_df.iterrows():
        pdf.cell(200, 10, txt=f"{row['Dimension']}: {row['Score']}/4", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Average Maturity Score: {total_average}/4", ln=True)
    pdf_output = "cfed_scores.pdf"
    pdf.output(pdf_output)
    with open(pdf_output, "rb") as pdf_file:
        b64_pdf = base64.b64encode(pdf_file.read()).decode()
        href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="cfed_scores.pdf">📄 Download scores as PDF</a>'
        st.markdown(href_pdf, unsafe_allow_html=True)

st.markdown("---")
st.caption("Prototype built for CFED AI tool – All Four Dimensions. To view a walkthrough of how to use this tool, visit: https://cfed-tool-guide.streamlit.app")
