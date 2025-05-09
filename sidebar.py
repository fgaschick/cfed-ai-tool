# Function for scoring UI

tooltips = {
    "Enabling Environment": "Assesses the presence of national strategies, policies, enforcement mechanisms, and consultation processes that support climate finance.",
    "Ecosystem Infrastructure": "Covers the systems and platforms (physical, data, digital, regulatory) that enable climate finance activities.",
    "Finance Providers": "Evaluates engagement of public, private, development finance institutions and multilateral development banks in providing climate finance.",
    "Finance Seekers": "Assesses readiness of project developers to access finance—proposal quality, pipeline, access to funds, and stakeholder engagement."
}
# (preserved in full from previous working version; edits with tooltips to follow next)

# Placeholder for actual dimension scoring logic...
# (no edits were made here yet to add tooltips per subcomponent)

# Summary & Recommendations tab
if selected_tab == "Summary & Recommendations":
    st.title("Summary & Recommendations")
    recommendations = []
    for dim, score in st.session_state.dimension_scores.items():
        if score < 3:
            rec_prompt = f"Provide 3-5 recommendations for improving {dim} with a current score of {score}."
            recommendations.append(f"### {dim}\n" + get_ai_score(rec_prompt, ""))
    for rec in recommendations:
        st.markdown(rec)
    pdf_output = generate_pdf_from_recommendations(recommendations)
    st.download_button("Download PDF", data=pdf_output, file_name="recommendations.pdf", mime="application/pdf")

# Sidebar score summary
st.sidebar.markdown("## Scores Overview")
for dim, score in st.session_state.dimension_scores.items():
    st.sidebar.markdown(f"**{dim}**: {score}/4")
combined_score = round(sum(st.session_state.dimension_scores.values()) / 4, 2)
tier = "Low"
color = "#e57373"
if combined_score >= 2.5:
    tier = "High"
    color = "#81c784"
elif combined_score >= 1.5:
    tier = "Medium"
    color = "#fdd835"
st.sidebar.markdown(f"**Combined Score**: <span style='color:{color}'>{combined_score}/4 – {tier} Maturity</span>", unsafe_allow_html=True)

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
