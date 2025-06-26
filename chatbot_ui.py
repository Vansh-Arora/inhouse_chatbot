import streamlit as st
import requests

st.set_page_config(page_title="Secure Barclays Chatbot", layout="centered")

st.title("🛡️ Barclays Secure Chatbot")
st.caption("Type your prompt below. Sensitive information is automatically redacted.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle user input
prompt = st.chat_input("Ask me anything...")
if prompt:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call backend API
    try:
        response = requests.post("http://localhost:8000/chat", json={"prompt": prompt})
        response.raise_for_status()
        answer = response.json()["response"]
    except Exception as e:
        answer = f"❌ Error: {str(e)}"

    # Show bot message
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)