

import streamlit as st
from fpdf import FPDF
import base64

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Sample PDF Content", ln=True, align="C")

    pdf.ln(20)
    pdf.set_font("Arial", style="I", size=11)
    pdf.multi_cell(0, 10, "Climate Finance Team\nChemonics International\n2025")
    pdf_output = "cfed_scores.pdf"
    pdf.output(pdf_output)
    with open(pdf_output, "rb") as pdf_file:
        b64_pdf = base64.b64encode(pdf_file.read()).decode()
        href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="cfed_scores.pdf">📄 Download scores as PDF</a>'
        st.markdown(href_pdf, unsafe_allow_html=True)
