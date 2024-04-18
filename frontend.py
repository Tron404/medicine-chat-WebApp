import streamlit as st
from llm_commands import *

st.title("Legal Medicine Q&A")

if "message_history" not in st.session_state:
    st.session_state["message_history"] = [{"role": "assistant", "content": "How can I help you?"}]

if "message_fail" not in st.session_state:
    st.session_state["message_fail"] = False

if "previous_context_limit" not in st.session_state:
    st.session_state["previous_context_limit"] = None

for message in st.session_state["message_history"]:
    st.chat_message(message["role"]).write(message["content"])

user_input = st.chat_input("Write smth")
if user_input:
    st.session_state.message_history.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    if "URL" not in st.session_state.keys():
        st.session_state.URL = url
    res = send_request(st.session_state)
    st.session_state.message_history.append({"role": "assistant", "content": res})
    st.chat_message("assistant").write(res)

# """
# 'I developed sepsis after my laparoscopic surgery to treat colon cancer. Why did this happen?', 
# 'did my surgeon make a mistake? Is it possible for a surgeon to do something wrong in the surgery that causes sepsis?'
# 'is this specific to colon surgery? how can surgical technique contribute to sepsis?', 
# "what is the most common cause of sepsis after colon surgery?"
# "how can surgeons prevent sepsis complications after colon surgery?",
# "how often is sepsis after colon surgery caused by a surgeon's mistake?", 
# 'should i talk to a lawyer or my surgeon first?', 
# """