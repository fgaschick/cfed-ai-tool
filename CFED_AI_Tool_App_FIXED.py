import streamlit as st
from openai import OpenAI
import os

# Set OpenAI API key using environment variable, as in original working script
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY environment variable not set.")
    st.stop()

client = OpenAI(api_key=api_key)

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

st.set_page_config(page_title="Enabling Environment Scoring", layout="wide")

# Custom header and footer with logo
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
        z-index: 1000;
    }
    .header-bar {
        position: relative;
        top: 0;
        width: 100%;
        background-color: #005670;
        padding: 0.8em 1em;
        text-align: center;
        z-index: 1000;
    }
    .header-bar img {
        max-height: 30px;
    }
    .bottom-box {
        position: fixed;
        bottom: 60px;
        right: 30px;
        background-color: #ffffff;
        border: 2px solid #005670;
        padding: 15px;
        border-radius: 8px;
        z-index: 1001;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
    }
    </style>
    <div class='custom-footer'>
        © 2025 Chemonics International Inc. | Contact: Climate Finance Team
    </div>
    <div class='header-bar'>
        <img src='https://raw.githubusercontent.com/fgaschick/cfed-ai-tool/main/Chemonics_RGB_Horizontal_BLUE-WHITE.png' alt='Chemonics Logo'/>
    </div>
    <br><br><br>
""", unsafe_allow_html=True)

st.title("Enabling Environment Scoring Prototype")

# Track score separately so it can be rendered globally
ee_total_score = None

use_ai_ee = st.checkbox("\U0001F9E0 Use AI to score Enabling Environment", value=False)

if use_ai_ee:
    narrative_ee = st.text_area("\U0001F50D Provide a narrative description of the enabling environment:", height=300)
    if narrative_ee:
        with st.spinner("Analyzing with AI..."):
            prompt = (
                "You are a climate finance expert. Based on the following narrative, assess the maturity of the enabling environment using the four sub-components: "
                "(1) Strategy (NDCs, national plans), (2) Policy (sectoral climate policies), (3) Enforcement (rule of law, anti-corruption), and (4) Stakeholder consultation. "
                "Assign a maturity score from 0 to 3 for each sub-component and explain each score briefly. Then provide 3 prioritized action recommendations that would help improve the enabling environment if any score is below 3."
            )
            output = get_ai_score(prompt, narrative_ee)
            st.markdown("**AI-Generated Assessment and Recommendations:**")
            st.markdown(output)

        # Dummy value to indicate AI mode (actual average not parsed from AI)
        ee_total_score = "AI-Based"
else:
    st.markdown("### \u270D\ufe0f Manual Scoring (based on sub-indicator evidence)")

    # STRATEGY
    st.markdown("#### Strategy")
    s1 = st.checkbox("Country has submitted an NDC")
    s2 = st.checkbox("NDC is linked to investment or implementation plans")
    s3 = st.checkbox("NDC or strategy includes financing targets or mechanisms")
    s4 = st.checkbox("There is a national climate finance strategy or roadmap")
    notes_strategy = st.text_area("Notes for Strategy:", key="notes_strategy")

    # POLICY
    st.markdown("#### Policy")
    p1 = st.checkbox("Sectoral policies (energy, land use, etc.) integrate climate objectives")
    p2 = st.checkbox("Policies include clear implementation mechanisms")
    p3 = st.checkbox("Private sector is consulted or involved in policy development")
    notes_policy = st.text_area("Notes for Policy:", key="notes_policy")

    # ENFORCEMENT
    st.markdown("#### Enforcement")
    e1 = st.checkbox("Climate-related laws or regulations exist")
    e2 = st.checkbox("There is a functioning judiciary or legal redress mechanism")
    e3 = st.checkbox("Anti-corruption measures are actively implemented")
    notes_enforcement = st.text_area("Notes for Enforcement:", key="notes_enforcement")

    # STAKEHOLDER CONSULTATION
    st.markdown("#### Stakeholder Consultation")
    c1 = st.checkbox("Stakeholders (civil society, academia) are engaged in planning")
    c2 = st.checkbox("Indigenous Peoples, women, youth are specifically included")
    c3 = st.checkbox("Consultations are recurring and documented")
    notes_consultation = st.text_area("Notes for Consultation:", key="notes_consultation")

    # Compute maturity per sub-component
    def score_subcomponent(answers):
        return min(3, sum(answers))

    strategy_score = score_subcomponent([s1, s2, s3, s4])
    policy_score = score_subcomponent([p1, p2, p3])
    enforcement_score = score_subcomponent([e1, e2, e3])
    consultation_score = score_subcomponent([c1, c2, c3])

    ee_total_score = round((strategy_score + policy_score + enforcement_score + consultation_score) / 4, 2)
    st.success(f"Average Score for Enabling Environment: {ee_total_score}/3")

    # AI-generated recommendations based on manual scores and notes
    if st.button("\U0001F916 Generate AI Recommendations Based on Manual Input"):
        combined_notes = f"Strategy notes: {notes_strategy}\nPolicy notes: {notes_policy}\nEnforcement notes: {notes_enforcement}\nConsultation notes: {notes_consultation}"
        ai_prompt_manual = (
            f"You are a climate finance advisor. The user has manually assessed maturity scores as follows:\n"
            f"- Strategy: {strategy_score}/3\n- Policy: {policy_score}/3\n- Enforcement: {enforcement_score}/3\n- Stakeholder Consultation: {consultation_score}/3\n"
            f"The user also provided these notes:\n{combined_notes}\n"
            f"Please provide 3-5 concrete, prioritized action recommendations to improve any sub-component that scored below 3."
        )
        with st.spinner("Generating recommendations..."):
            ai_actions = get_ai_score(ai_prompt_manual, "")
            st.markdown("**AI Recommendations for Action:**")
            st.markdown(ai_actions)

# Floating score box always shown
if ee_total_score is not None:
    st.markdown(f"""
    <div class="bottom-box">
        <strong>Live Enabling Env Score:</strong><br> {ee_total_score}/3
    </div>
    """, unsafe_allow_html=True)
