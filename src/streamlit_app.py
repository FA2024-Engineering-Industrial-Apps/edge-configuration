import streamlit as st
import os
from strategy import Strategy, EdgeConfigStrategy
import json
from code_editor import code_editor  # type: ignore

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
        /* Adjusts the sidebar width */
        .css-1d391kg {
            width: 25% !important;  /* You can adjust this percentage */
        }
        .css-18e3th9 {
            padding-top: 2rem;  /* Adjust padding as needed */
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# print header
st.title("Configuration Generator")
st.markdown(
    """Configure your LLM Access in the input below and write your description in the chat input. 
            The assistant will generate a configuration for you."""
)

target = st.radio("Target", ["Edge Config"])

if target == "Edge Config":
    # create strategy but only in first run
    if "strategy" not in st.session_state:
        st.session_state.strategy = EdgeConfigStrategy()

messages = st.session_state.strategy.history.getPromtHistory_withoutSysPromts()
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# wait for user input
if prompt := st.chat_input("Write something"):

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.strategy.history.addPromt_withStrs("user", prompt)

    with st.spinner("Waiting for assistant response..."):
        # Calling the LLM and possibly change values
        st.session_state.strategy.send_message()

    with st.chat_message("assistant"):
        st.markdown(st.session_state.strategy.history.getLatestPromtAsStr("assistant"))


with st.sidebar:
    if st.session_state.strategy.model != None:
        st.subheader("Configuration Parameters")

        my_buttons = [
            {
                "name": "Submit",
                "feather": "Save",
                "alwaysOn": True,
                "commands": ["submit"],
                "style": {"top": "0.46rem", "right": "0.4rem"},
            }
        ]
        # The default value for the lang argument is "python"
        response_dict = code_editor(
            json.dumps(
                st.session_state.strategy.model.generate_prompt_sidebar(), indent=2
            ),
            lang="javascript",
            buttons=my_buttons,
        )

        if "text" in response_dict and response_dict["type"] == "submit":
            print("Save clicked")
            print(response_dict["text"])
            st.session_state.strategy.model.apps[0].config.fill_from_json(
                json.loads(response_dict["text"])
            )
    else:
        st.write("No configuration loaded")

    st.divider()

    with st.expander("Your API Settings"):
        model = st.radio("Model", ["gpt-4o", "mixtral-7b-instruct"])
        st.session_state["model"] = model

        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            key="openai_key",
            disabled=model != "gpt-4o",
        )

        def save_cred_openai():
            st.session_state["openai_key"] = openai_key
            os.environ["OPENAI_API_KEY"] = openai_key
            st.success("Saved Key!")

        openai_btn = st.button("Save", on_click=save_cred_openai, key="openai_btn")

        mixtral_key = st.text_input(
            "Siemens LLM Key",
            type="password",
            key="mixtral_key",
            disabled=model != "mixtral-7b-instruct",
        )

        def save_cred_mixtral():
            st.session_state["mixtral_key"] = mixtral_key
            os.environ["MIXTRAL_KEY"] = mixtral_key
            st.success("Saved Key!")

        mixtral_btn = st.button("Save", on_click=save_cred_mixtral, key="mixtral_btn")

        st.markdown("IEM API Credentials")

        iem_user = st.text_input("Username", key="iem_user")
        iem_pass = st.text_input("Password", type="password", key="iem_pass")

        def save_cred_iem():
            st.session_state["iem_user"] = iem_user
            st.session_state["iem_pass"] = iem_pass

            st.success("Saved Credentials!")

        st.button("Save", key="iem_btn", on_click=save_cred_iem)
