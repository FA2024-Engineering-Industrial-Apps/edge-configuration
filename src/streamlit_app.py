import streamlit as st
import os
from strategy import Strategy, EdgeConfigStrategy
st.title("Configuration Generator")

#Initialization of authentication variable
if "authentication" not in st.session_state:
        st.session_state.authentication = False
        print("Counter")
        
if st.session_state.authentication is not True:        
# Sidebar for API credentials (username and password)
    with st.sidebar:
        st.subheader("API Credentials")

        # Username input
        username = st.text_input("Username", key="hesam")

        # Password input (hidden with `type="password"`)
        password = st.text_input("Password", type="password", key="123123")

        # Predefined correct credentials (for the purpose of this example)
        correct_username = "edge"
        correct_password = "edge"

        # Button to save credentials
        if st.button("Save Credentials"):
            if username and password:
                # Check if credentials are correct
                if username == correct_username and password == correct_password:
                    # Store the credentials in session state
                    st.session_state["username"] = username
                    st.session_state["password"] = password
                    st.success("Credentials saved successfully!")
                    st.session_state.authentication = True
                    st.rerun()

                else:
                    st.error("Incorrect username or password.")
                    st.stop()
            else:
                st.error("Please enter both username and password.")
                st.stop()


#Check wether log in successfull 
if st.session_state.authentication is not True:
    st.stop()


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


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Write something"):
    # Calling the LLM and possibly change values
    with st.chat_message("user"):
     st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})

    response_message, current_model = strategy.send_message(prompt, st.session_state.messages)

    with st.chat_message("assistant"):
        st.markdown(response_message)

    st.session_state.messages.append({"role": "assistant", "content": response_message})

    # TODO: Add an potential extra system promt to st.session_state.messages to tell the LLM
    # that a validation failed and the value was not se

    with st.sidebar:
        st.subheader("Configuration Parameters")
        st.markdown(current_model.generate_prompt_sidebar())





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
