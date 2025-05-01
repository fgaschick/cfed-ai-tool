import streamlit as st
import openai
import os

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Page configuration
st.set_page_config(page_title="CFED AI Diagnostic Tool", layout="wide")
st.title("Climate Finance Ecosystem Diagnostic (CFED)")
st.subheader("AI-Assisted Maturity Scoring Tool – Full Prototype")

st.markdown("""
This interactive tool estimates the maturity of a country’s climate finance ecosystem across all four CFED dimensions:
1. Enabling Environment (AI-driven)
2. Ecosystem Infrastructure
3. Finance Providers
4. Finance Seekers

For Enabling Environment, you may now provide a written summary instead of answering checkboxes.
""")

st.markdown("---")

# --- 1. Enabling Environment (AI-Based Option) ---
st.header("1. Enabling Environment")
use_ai_input = st.checkbox("Use AI to score based on written input instead of answering questions")

if use_ai_input:
    user_input = st.text_area("Describe the enabling environment (e.g., NDCs, enforcement, sector policies):", height=200)
    if user_input:
        with st.spinner("Scoring with AI..."):
            try:
                completion = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a climate finance expert. Score the enabling environment from 1 to 4 based on the country description. Justify the score."},
                        {"role": "user", "content": user_input}
                    ]
                )
                ai_output = completion.choices[0].message.content
                st.markdown("**AI Suggested Score and Rationale:**")
                st.markdown(ai_output)
            except Exception as e:
                st.error(f"Error from OpenAI: {e}")
        enabling_score = None  # Leave undefined for now
else:
    has_ndc = st.radio("Has the country submitted an NDC?", ["Yes", "No"])
    ndc_quality = st.selectbox("How ambitious is the NDC?", ["High", "Medium", "Low"])
    has_sector_policies = st.radio("Are there sector-specific climate policies?", ["Yes", "No"])
    has_enforcement = st.radio("Are climate laws and policies enforced predictably?", ["Yes", "No"])

    enabling_score = 1
    if has_ndc == "Yes":
        enabling_score += 1
        if ndc_quality == "High":
            enabling_score += 1
    if has_sector_policies == "Yes":
        enabling_score += 1
    if has_enforcement == "Yes":
        enabling_score += 1
    enabling_score = min(enabling_score, 4)

# --- 2. Ecosystem Infrastructure ---
st.header("2. Ecosystem Infrastructure")
has_mrv = st.radio("Are MRV systems and climate data tools in place?", ["Yes", "No"])
has_partnerships = st.radio("Are there active stakeholder networks and partnerships?", ["Yes", "No"])
has_climate_capacity = st.radio("Do institutions have adequate climate finance capacity?", ["Yes", "No"])

infra_score = 1
if has_mrv == "Yes":
    infra_score += 1
if has_partnerships == "Yes":
    infra_score += 1
if has_climate_capacity == "Yes":
    infra_score += 1
infra_score = min(infra_score, 4)

# --- 3. Finance Providers ---
st.header("3. Finance Providers")
has_public_climate_funding = st.radio("Is there domestic public funding for climate?", ["Yes", "No"])
has_carbon_market = st.radio("Is the country active in voluntary or compliance carbon markets?", ["Yes", "No"])
has_private_investment = st.radio("Is commercial/private capital flowing into climate sectors?", ["Yes", "No"])

providers_score = 1
if has_public_climate_funding == "Yes":
    providers_score += 1
if has_carbon_market == "Yes":
    providers_score += 1
if has_private_investment == "Yes":
    providers_score += 1
providers_score = min(providers_score, 4)

# --- 4. Finance Seekers ---
st.header("4. Finance Seekers")
has_project_pipeline = st.radio("Is there a robust pipeline of fundable climate projects?", ["Yes", "No"])
has_project_diversity = st.radio("Do projects span adaptation, mitigation, and nature-based solutions?", ["Yes", "No"])
inclusive_targeting = st.radio("Are vulnerable or underserved groups targeted in project design?", ["Yes", "No"])

seekers_score = 1
if has_project_pipeline == "Yes":
    seekers_score += 1
if has_project_diversity == "Yes":
    seekers_score += 1
if inclusive_targeting == "Yes":
    seekers_score += 1
seekers_score = min(seekers_score, 4)

# --- Results Section ---
st.markdown("---")
st.header("Results Summary")

col1, col2 = st.columns(2)
with col1:
    if enabling_score is not None:
        st.metric("Enabling Environment", f"{enabling_score}/4")
    st.metric("Finance Providers", f"{providers_score}/4")
with col2:
    st.metric("Ecosystem Infrastructure", f"{infra_score}/4")
    st.metric("Finance Seekers", f"{seekers_score}/4")

if enabling_score is not None:
    total_average = round((enabling_score + infra_score + providers_score + seekers_score) / 4, 2)
    st.markdown(f"### 🧮 Average Ecosystem Maturity Score: {total_average}/4")

    st.markdown("**Suggested Actions:**")
    if total_average < 2:
        st.warning("Foundational support needed: Start with policy frameworks, MRV systems, and project pipeline development.")
    elif 2 <= total_average < 3:
        st.info("Moderate maturity: Expand partnerships, deepen private finance engagement, and strengthen enforcement.")
    else:
        st.success("Strong ecosystem: Prioritize scaling solutions, regional leadership, and blended finance innovation.")

st.markdown("---")
st.caption("Prototype built for CFED AI tool – All Four Dimensions.")
