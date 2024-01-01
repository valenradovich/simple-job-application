from io import BytesIO, StringIO
import os
import pathlib
import tempfile
import time
from pypdf import PdfFileMerger
import streamlit as st
from src.ml_logic.data import load_resume
from src.ml_logic.model import load_model
from src.interface.main import prepare_data, talk_to_link
from src.params import VECTOR_DB_PATH

file_path = st.secrets.get("VECTOR_DB_PATH")

st.set_page_config(
    page_title="Simple Jobs Application", page_icon="📑", layout="wide", initial_sidebar_state="expanded"
)

st.title("Simple Jobs Application 📑")
st.caption("🚀 Make job applications easier and faster with AI.")

st.sidebar.markdown("## How to use")
st.sidebar.write(
    """
    1. Enter your [OpenAI API](https://platform.openai.com/account/api-keys) key below🔑
    2. Upload your resume as PDF file📄
    3. Paste the direct link to the job offer you want to apply to🔗
    3. Done!
    """)

openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="You can get your API key from [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys).")

if openai_api_key:
    llm = load_model(openai_api_key)
    #st.success(openai_api_key)
else:
    st.error("❌ Please enter your OpenAI API key.")

st.sidebar.divider()

st.sidebar.markdown("## What can I do?")
st.sidebar.write(
    """
    - Generate personalized cover letters in seconds✍️
    - Ask any question about the job post you want to apply to❓

    Tip: Use the chat to ask the questions needed to submit your application😉
    """)

st.sidebar.divider()

st.sidebar.markdown("## Upload your resume")

temp_dir = tempfile.TemporaryDirectory()
#st.write(temp_dir.name)

resume = st.sidebar.file_uploader("", type=["pdf"])

if resume:
    resume_file_path = pathlib.Path(temp_dir.name) / resume.name
    with open(resume_file_path, 'wb') as output_temporary_file:
        output_temporary_file.write(resume.read())


process_resume_clicked = st.sidebar.button("Process resume")

st.sidebar.divider()

st.sidebar.markdown("## Job posts URLs")

urls = []
url = st.sidebar.text_input(f"Remember to use the direct link to the job post🔗")
if url:
    urls.append(url)

process_url_clicked = st.sidebar.button("Process URLs")

st.sidebar.divider()

st.sidebar.markdown("## About")
st.sidebar.write(
    """
    **📑Simple Job Application** allows you to speak with every link you want.
    It uses [OpenAI's API](https://openai.com/), [LangChain](https://www.langchain.com) and [FAISS](https://github.com/facebookresearch/faiss).

    This tool is just a demo created for testing purposes. You can find the source code on [GitHub](https://github.com/valenradovich/talk-to-link). I appreciate any feedback or suggestions.

    Made by [Valentin Radovich](https://www.linkedin.com/in/valentin-fernandez-radovich/).
    """
    )
main_placeholder = st.empty()

vector_db = None

st.session_state["resume"] = ' '

if process_resume_clicked:
    if not openai_api_key:
        st.error("❌ Please enter your OpenAI API key.")
        st.stop()
    st.info("⏳ Please wait while we process your resume...")

    st.session_state['resume'] = load_resume(output_temporary_file.name)

    if st.session_state["resume"] is False:
        st.exception(
            "❌ Could not prepare resume data. Please check your pdf and try again."
        )
    else:
        st.success(
            "✅ Resume successfully loaded."
        )
        st.write(st.session_state["resume"][0].page_content)

st.session_state["vector_db"] = None

if process_url_clicked:
    if not openai_api_key:
        st.error("❌ Please enter your OpenAI API key.")
        st.stop()
    st.info("⏳ Please wait while we process your Job Post URL...")

    st.session_state["vector_db"] = prepare_data(urls, openai_api_key)

    if st.session_state["vector_db"] is False:
        st.exception(
            "❌ Could not prepare job post. Please check your urls and try again."
        )
    else:
        st.text(f"{st.session_state['vector_db']}") ### DEBUG
        st.success(
            "✅ Job post data successfully loaded."
        )

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# user_resume = st.session_state['resume'][0].page_content

user_prompt = st.chat_input()

if user_prompt:
    cover_letter_prompt = f"You are a professional HR manager, specialized in writing cover letters.\
                            Based in the following resume: {st.session_state['resume'][0].page_content} \
                            and the following job post: {st.session_state['vector_db']}, write the best \
                            cover letter for this job offer. Remember: You must not allucinate or lie."

    final_prompt = f"You are a professional HR manager, specialized in writing cover letters.\
                    Based in the following resume and context: {st.session_state['resume'][0].page_content} \
                    answer the following question: {user_prompt} about the following job post: \
                    {st.session_state['vector_db']}"

    if not openai_api_key:
        st.error("❌ Please enter your OpenAI API key.")
        st.stop()
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    st.chat_message("user").write(user_prompt)
    with st.spinner("Thinking..."):
        time.sleep(1)
        result = talk_to_link(llm=llm, prompt=final_prompt, vectorstore=st.session_state['vector_db'])

        if isinstance(result, dict) and "answer" in result:
            st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
            # Display sources, if available
            sources = result.get("sources", "")
            if sources:
                sources_list = sources.split("\n")  # Split the sources by newline
                for source in sources_list:
                    st.chat_message("assistant").write(result["answer"] + "\nSources: " + source)
            else:
                with st.spinner("Thinking..."):
                    time.sleep(3)
                    st.chat_message("assistant").write(result["answer"])
        else:
            st.exception("❌ Could not get an answer. Please try again.")
