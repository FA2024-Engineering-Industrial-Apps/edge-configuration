import streamlit as st
import os
from strategy import Strategy, EdgeConfigStrategy

st.title("Configuration Generator")

st.markdown(
    "Configure your LLM Access in the input below and write your description in the chat input. The assistant will generate a configuration for you."
)

target = st.radio("Target", ["Edge Config"])

strategy: Strategy = None  # type: ignore

if target == "Edge Config":
    strategy = EdgeConfigStrategy()


    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Create two columns: left for chat, right for displaying parameters or updates


        for message in st.session_state.messages:
            if message["role"] == "system":
                continue

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

if prompt := st.chat_input("Write something"):
    with st.chat_message("user"):
        st.markdown(prompt)
    pydantic_out = strategy.send_message(prompt, st.session_state.messages)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": pydantic_out})
    st.chat_message("assistant").markdown(
        f"""
        ```javascript
        {pydantic_out}
        """
    )

 # Display parameters or updates
    with st.sidebar:
        st.subheader("Configuration Parameters")
        st.markdown("Name")
        st.markdown("OPC-UA URL")
        st.markdown("Port number")



st.divider()

with st.expander("Your API Settings"):
    model = st.radio("Model", ["gpt-4o", "mixtral-7b-instruct"])
    st.session_state["model"] = model

    openai_key = st.text_input(
        "OpenAI API Key", type="password", key="openai_key", disabled=model != "gpt-4o"
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
