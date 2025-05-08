# --- Summary & Recommendations Tab ---
elif selected_tab == "Summary & Recommendations":
    st.markdown("## AI-based Recommendations for Action")
    recommendations = []
    for dimension, score in st.session_state.dimension_scores.items():
        if score < 3:
            prompt = f"Provide 3-5 concrete, prioritized recommendations for improving the {dimension} based on the score of {score}."
            recommendations.append(f"### {dimension} Recommendations:\n{get_ai_score(prompt, '')}")

    for recommendation in recommendations:
        st.markdown(recommendation)

    st.markdown("### Download Recommendations as PDF")
    # Generate PDF for the recommendations
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add title
    pdf.cell(200, 10, txt="AI-Based Recommendations for Action", ln=True, align="C")
    pdf.ln(10)

    for recommendation in recommendations:
        pdf.multi_cell(0, 10, recommendation)

    # Save PDF to memory
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    # Use Streamlit to provide a download button for the PDF
    st.download_button(
        label="Download Recommendations as PDF",
        data=pdf_output,
        file_name="recommendations.pdf",
        mime="application/pdf"
    )
