import streamlit as st
import requests
import json
from datetime import datetime

def main():
    st.set_page_config(page_title="Environmental Guidelines Bot", layout="wide")
    st.title("Environmental Guidelines Bot")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "token" not in st.session_state:
        st.session_state.token = None

    # Sidebar for login/upload
    with st.sidebar:
        if st.session_state.token is None:
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                try:
                    response = requests.post(
                        "http://localhost:8000/token",
                        data={"username": username, "password": password}
                    )
                    if response.status_code == 200:
                        st.session_state.token = response.json()["access_token"]
                        st.success("Logged in successfully!")
                    else:
                        st.error("Login failed")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.subheader("Upload Document")
            uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
            if uploaded_file is not None:
                if st.button("Process Document"):
                    try:
                        files = {"file": uploaded_file}
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        response = requests.post(
                            "http://localhost:8000/upload-document",
                            files=files,
                            headers=headers
                        )
                        if response.status_code == 200:
                            st.success("Document uploaded successfully!")
                        else:
                            st.error("Upload failed")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # Chat interface
    if st.session_state.token is not None:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask about environmental guidelines"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            try:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                response = requests.post(
                    "http://localhost:8000/chat",
                    json={"message": prompt},
                    headers=headers
                )
                
                if response.status_code == 200:
                    bot_response = response.json()["response"]
                    st.session_state.messages.append(
                        {"role": "assistant", "content": bot_response}
                    )
                else:
                    st.error("Failed to get response")
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()