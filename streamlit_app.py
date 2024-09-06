import streamlit as st
from factory import create_vehicle
import os

st.title("Vehicle Configuration Generator")

st.markdown(
    "Set your OPENAI_API_KEY in the input below and write your description in the chat input. The assistant will generate a configuration for you."
)

if prompt := st.chat_input("Describe the recipe you want to configure"):
    st.chat_message("user").markdown(prompt)
    vehicle = create_vehicle(prompt)
    st.chat_message("assistant").markdown(
        f"""
        ```javascript
        {vehicle.model_dump_json(indent=2)}
        """
    )

st.divider()

with st.expander("Your API Settings"):
    model = st.radio("Model", ["gpt-4o", "mixtral-7b-instruct"])
    st.session_state["model"] = model

    openai_key = st.text_input("OpenAI API Key", type="password", key="openai_key")

    def save_cred_openai():
        st.session_state["openai_key"] = openai_key
        os.environ["OPENAI_API_KEY"] = openai_key
        st.success("Saved Key!")

    openai_btn = st.button("Save", on_click=save_cred_openai, key="openai_btn")

    mixtral_key = st.text_input("Siemens LLM Key", type="password", key="mixtral_key")

    def save_cred_mixtral():
        st.session_state["mixtral_key"] = mixtral_key
        os.environ["MIXTRAL_KEY"] = mixtral_key
        st.success("Saved Key!")

    mixtral_btn = st.button("Save", on_click=save_cred_mixtral, key="mixtral_btn")
