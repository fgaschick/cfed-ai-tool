import streamlit as st
import openai
import pandas as pd
import os  # Import os for environment variables

# --- Data Structure ---
cfe_framework = {
    "Enabling Environment": {
        "Strategy": {
            "Paris documents and commitments": {
                "indicators": {
                    "NDC Submission Status": {
                        "type": "selectbox",
                        "options": [
                            "0 - No NDC submitted",
                            "1 - NDC submitted",
                            "2 - NDC submitted, some enhancements",
                            "3 - NDC submitted, significant enhancements",
                        ],
                        "help": "Status of Nationally Determined Contribution...",
                    },
                    "CAT Rating": {
                        "type": "selectbox",
                        "options": [
                            "0 - Not rated or insufficient",
                            "1 - Highly insufficient to insufficient",
                            "2 - Almost sufficient",
                            "3 - 1.5C compatible",
                        ],
                        "help": "Climate Action Tracker rating...",
                    },
                    # ... other indicators ...
                },
                "ai_prompt": "You are a climate finance expert...",
                "weight": 0.3,  # Example weight for the component
            },
            "Policy": {
                "Development of climate policies": {
                    "indicators": {
                        "National climate change policy": {
                            "type": "selectbox",
                            "options": [
                                "0 - No policy",
                                "1 - Policy enacted",
                                "2 - Sectoral policies",
                                "3 - Codified policies",
                            ],
                            "help": "National climate change policy...",
                        },
                        # ... other indicators ...
                    },
                    "ai_prompt": "You are a climate policy expert...",
                    "weight": 0.4,
                },
                # ... other components ...
            },
            # ... other components ...
        },
        "Ecosystem Infrastructure": {
            # ...
        },
        # ... other dimensions ...
    },
    "Finance Providers": {
        # ...
    },
    "Finance Seekers": {
        "Built environment": {
            "indicators": {
                "Green building codes": {
                    "type": "selectbox",
                    "options": [
                        "0 - No building codes",
                        "1 - Voluntary green building codes",
                        "2 - Mandatory green building codes",
                        "3 - Enforcement of green building codes",
                    ],
                    "help": "Status of green building codes...",
                },
                # ... other indicators
            },
            "ai_prompt": "You are an expert on sustainable buildings...",
            "weight": 0.5,
        },
        # ... other components
    },
}


# --- Helper Functions ---
def get_user_input(dimension, component, sub_component, indicators):
    """
    Generates Streamlit input elements based on the indicator types.
    Returns a dictionary of user inputs.
    """
    user_inputs = {}
    if indicators:  # Check if indicators is not None or empty
        for indicator, details in indicators.items():
            label = f"{component} - {sub_component} - {indicator}" if sub_component else f"{component} - {indicator}"
            if details["type"] == "selectbox":
                user_inputs[indicator] = st.selectbox(label, details["options"], help=details["help"])
            elif details["type"] == "number_input":
                user_inputs[indicator] = st.number_input(label, help=details["help"])
            elif details["type"] == "checkbox":
                user_inputs[indicator] = st.checkbox(label, help=details["help"])
            elif details["type"] == "text_area":
                user_inputs[indicator] = st.text_area(label, help=details["help"])
    else:
        st.warning(f"No indicators found for {dimension} - {component} - {sub_component}")
    return user_inputs


def score_component(dimension, component, sub_component, user_inputs):
    """
    Calculates a score for a component based on user inputs and indicator weights.
    (This is a placeholder - you'll need to implement the scoring logic
    from the document)
    """
    score = 0
    if dimension == "Enabling Environment" and component == "Strategy" and user_inputs:  # Check if user_inputs is not empty
        ndc_status = int(user_inputs["NDC Submission Status"][0])
        cat_rating = int(user_inputs["CAT Rating"][0])
        score = max(ndc_status, cat_rating)
        # ... more scoring logic ...
    elif dimension == "Finance Seekers" and component == "Built environment" and sub_component is None and user_inputs:  # Explicit None check and user_inputs check
        green_building_code = int(user_inputs["Green building codes"][0])
        score = green_building_code
    elif user_inputs:  # Check if user_inputs is not empty
        score = len(user_inputs)  # A basic placeholder
    return score


def get_ai_score(prompt, user_input):
    """
    Calls the OpenAI API to get an AI-generated score and rationale.
    """
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Use environment variable
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI Error: {e}"


# --- Main Assessment Logic ---

# Header and User Guide (as in the original script)
st.title("CFE Maturity Assessment Tool")
st.markdown(
    """
    This tool helps assess the maturity of a country's Climate Finance Ecosystem (CFE).
    It is based on a framework that considers four dimensions:
    Enabling Environment, Ecosystem Infrastructure, Finance Providers, and Finance Seekers.
    """
)

# Add user guide here (e.g., read from a file or define as a string)
user_guide = """
## User Guide

1.  **Select a dimension** to begin the assessment.
2.  For each component, provide inputs for the indicators.
3.  You can choose to use AI for scoring or use the tool's scoring mechanism.
4.  The results will be displayed at the end.

    ... (Add more detailed instructions)
    """
st.sidebar.markdown(user_guide)

all_scores = {}

for dimension, components in cfe_framework.items():
    with st.expander(dimension):
        for component, details in components.items():
            st.subheader(component)
            if "sub_components" in details:
                tabs = st.tabs(details["sub_components"].keys())
                for tab_index, (sub_component, sub_component_details) in enumerate(details["sub_components"].items()):
                    with tabs[tab_index]:
                        user_inputs = get_user_input(dimension, component, sub_component, sub_component_details.get("indicators"))  # Use .get()
                        if st.checkbox(f"Use AI for {component} - {sub_component}"):
                            ai_input = "\n".join([f"{k}: {v}" for k, v in user_inputs.items()])
                            # Debugging output
                            # st.write(f"DEBUG: Calling get_ai_score for {dimension} - {component} - {sub_component}")
                            ai_prompt = sub_component_details.get("ai_prompt", "You are a helpful AI assistant.")  # Provide default
                            ai_result = get_ai_score(ai_prompt, ai_input)
                            st.markdown(f"**AI Score & Rationale:** {ai_result}")
                            try:
                                ai_score = int(ai_result.split(":")[0]) if ai_result and ":" in ai_result else 0
                            except ValueError:
                                ai_score = 0
                                st.warning(f"Could not parse AI score from: '{ai_result}'. Using 0.")
                            component_score = ai_score * details.get("weight", 1)
                        else:
                            component_score = score_component(dimension, component, sub_component, user_inputs) * details.get("weight", 1)
                        all_scores.setdefault(dimension, {}).setdefault(component, [])
                        all_scores[dimension][component].append({"sub_component": sub_component, "score": component_score})
            else:
                user_inputs = get_user_input(dimension, component, None, details.get("indicators"))  # Use .get()
                if st.checkbox(f"Use AI for {component}"):
                    ai_input = "\n".join([f"{k}: {v}" for k, v in user_inputs.items()])
                    # Debugging output
                    # st.write(f"DEBUG: Calling get_ai_score for {dimension} - {component}")
                    ai_prompt = details.get("ai_prompt", "You are a helpful AI assistant.")  # Provide default
                    ai_result = get_ai_score(ai_prompt, ai_input)
                    st.markdown(f"**AI Score & Rationale:** {ai_result}")
                    try:
                        ai_score = int(ai_result.split(":")[0]) if ai_result and ":" in ai_result else 0
                    except ValueError:
                        ai_score = 0
                        st.warning(f"Could not parse AI score from: '{ai_result}'. Using 0.")
                    component_score = score_component(dimension, component, None, user_inputs)  # Changed "" to None
                else:
                    component_score = score_component(dimension, component, None, user_inputs)  # Changed "" to None
                all_scores.setdefault(dimension, {}).setdefault(component, [])
                all_scores[dimension][component].append({"sub_component": None, "score": component_score})

# --- Display Results ---
st.header("Assessment Results")
# (Implement display of results, visualizations, downloads)
print(all_scores)

# Footer
st.markdown("---")
st.markdown("This tool was developed to support climate finance ecosystem assessments.")
