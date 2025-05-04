import streamlit as st
import openai
import os

# For openai>=1.0.0 use openai directly, not OpenAI()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_score(prompt, user_input):
    try:
        response = openai.chat.completions.create(
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
st.title("Enabling Environment Scoring Prototype")

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
else:
    st.markdown("### \u270D\ufe0f Manual Scoring (based on sub-indicator evidence)")

    # STRATEGY
    st.markdown("#### Strategy")
    s1 = st.checkbox("Country has submitted an NDC")
    s2 = st.checkbox("NDC is linked to investment or implementation plans")
    s3 = st.checkbox("NDC or strategy includes financing targets or mechanisms")
    s4 = st.checkbox("There is a national climate finance strategy or roadmap")
    st.text_area("Notes for Strategy:", key="notes_strategy")

    # POLICY
    st.markdown("#### Policy")
    p1 = st.checkbox("Sectoral policies (energy, land use, etc.) integrate climate objectives")
    p2 = st.checkbox("Policies include clear implementation mechanisms")
    p3 = st.checkbox("Private sector is consulted or involved in policy development")
    st.text_area("Notes for Policy:", key="notes_policy")

    # ENFORCEMENT
    st.markdown("#### Enforcement")
    e1 = st.checkbox("Climate-related laws or regulations exist")
    e2 = st.checkbox("There is a functioning judiciary or legal redress mechanism")
    e3 = st.checkbox("Anti-corruption measures are actively implemented")
    st.text_area("Notes for Enforcement:", key="notes_enforcement")

    # STAKEHOLDER CONSULTATION
    st.markdown("#### Stakeholder Consultation")
    c1 = st.checkbox("Stakeholders (civil society, academia) are engaged in planning")
    c2 = st.checkbox("Indigenous Peoples, women, youth are specifically included")
    c3 = st.checkbox("Consultations are recurring and documented")
    st.text_area("Notes for Consultation:", key="notes_consultation")

    # Compute maturity per sub-component
    def score_subcomponent(answers):
        return min(3, sum(answers))

    strategy_score = score_subcomponent([s1, s2, s3, s4])
    policy_score = score_subcomponent([p1, p2, p3])
    enforcement_score = score_subcomponent([e1, e2, e3])
    consultation_score = score_subcomponent([c1, c2, c3])

    ee_total_score = round((strategy_score + policy_score + enforcement_score + consultation_score) / 4, 2)
    st.success(f"Average Score for Enabling Environment: {ee_total_score}/3")
