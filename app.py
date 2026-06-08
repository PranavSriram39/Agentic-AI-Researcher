import streamlit as st
from ai_agent import graph, INITIAL_PROMPT, config 
from pathlib import Path
import logging
from langchain_core.messages import AIMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Agentic AI Researcher", layout="wide")
st.title("Agentic AI Researcher")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    logger.info("Initialized chat history in session state.")

if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None
    logger.info("Initialized PDF path in session state.")

user_input = st.chat_input("What research topic would you like to explore?")

if user_input:
    logger.info(f"User input: {user_input}")
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    chat_input = {
        "messages": [{"role": "system", "content": INITIAL_PROMPT}] + st.session_state.chat_history
    }
    logger.info("Starting agent process...")
    full_response = ""
    for s in graph.stream(chat_input, config=config, stream_mode="values"):
        message = s["messages"][-1]
        if getattr(message, "tool_calls", None):
            for tool_call in message.tool_calls:
                logger.info(f"Tool call: {tool_call['name']}")

        if isinstance(message, AIMessage) and message.content:
            text_content = message.content if isinstance(message.content, str) else str(message.content)
            full_response += text_content + " "
            st.chat_message("assistant").write(full_response)

    if full_response:
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})
        logger.info("Agent process completed and response added to chat history.")

if st.session_state.pdf_path and st.session_state.pdf_path.exists():
    with open(st.session_state.pdf_path, "rb") as f:
        st.download_button(
            label="Download Generated Research Paper PDF",
            data=f,
            file_name=st.session_state.pdf_path.name,
            mime="application/pdf",
        )
        logger.info(f"PDF download button displayed for {st.session_state.pdf_path.name}.")