import streamlit as st

# Title of the section
st.title("Configuration Generator")

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

            else:
                st.error("Incorrect username or password.")
                st.stop()
        else:
            st.error("Please enter both username and password.")



#https://docs.streamlit.io/develop/api-reference/widgets/st.text_inputrun