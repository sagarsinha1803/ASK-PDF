import streamlit as st
import os
from dotenv import load_dotenv
from llm_core import LLMCore

st.title("ASK PDF")

st.subheader("Chat with your PDF documents")

load_dotenv('./.env')
data_folder = os.getenv("FILE_PATH")
os.makedirs(data_folder, exist_ok=True)

user_id = st.text_input("Enter your user ID", value="user1")
st.write(f"User ID: {user_id}")
if user_id:
    bot = LLMCore()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.button("Clear Conversation"):
    st.session_state.chat_history = []
    
    history = bot.get_session_history(user_id)
    history.clear()

# PDF file upload
with st.sidebar.form('upload_form', clear_on_submit=True):
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], accept_multiple_files=True, key="pdf_uploader")
    submit_button = st.form_submit_button("Upload", 
                                          type="primary")

    if submit_button and uploaded_file:
        for file in uploaded_file:
            file_path = os.path.join(data_folder, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
        st.rerun()

# Display all the files in the directory
st.sidebar.subheader("Uploaded Files")
files = os.listdir(data_folder)
if files:
    for file in files:
        file_path = os.path.join(data_folder, file)
        col1, col2 = st.sidebar.columns([3,1])
        with col1:
            st.write(file)
        with col2:
            if st.button("🗑️", key=file):
                os.remove(file_path)
                st.rerun()
else:
    st.sidebar.write("No files uploaded yet.")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("You:")
# st.write(prompt)

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    # response = bot.chat_with_llm(user_id, prompt)

    with st.chat_message("assistant"):
        response = st.write_stream(bot.chat_with_pdf(user_id, prompt))
    
    st.session_state.chat_history.append({"role": "assistant", "content": response})