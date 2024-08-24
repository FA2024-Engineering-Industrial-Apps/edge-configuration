import streamlit as st
from factory import create_vehicle
import os

st.title("Vehicle Configuration Generator")

st.markdown("Set your OPENAI_API_KEY in the input below and write your description in the chat input. The assistant will generate a configuration for you.")

if prompt := st.chat_input("Describe the recipe you want to configure"):
    st.chat_message("user").markdown(prompt)
    vehicle = create_vehicle(prompt)
    st.chat_message("assistant").markdown(f"""
        ```javascript
        {vehicle.model_dump_json()}
        ```
        """)
    
st.divider()
    
with st.expander("Your OpenAI API Key"):
    key = st.text_input("Key", type="password", key="key")

    def save_cred():
        st.session_state['openai_key'] = key
        os.environ['OPENAI_API_KEY'] = key
        st.success("Saved Key!")

    btn = st.button("Save", on_click=save_cred)