import streamlit as st
import random
import time

#Change page title (shown on browser tab)
st.set_page_config(page_title="SWIFT's Chatbot")
def response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

# Checks in the dialog has been initialized
if "dialog" not in st.session_state:
    #Sets the variable to 0, indicating popup window has not been shown. 
    st.session_state.dialog = 0


#Initialize pop window ("title", "size of window")
@st.dialog("Welcome to SWIFT's Chatbot @ CSAF 2024", width= "large")
def display():

    #Description
    st.write("Chatbot is work in progress. Please come back on October 17th")

    #Close button
    if st.button("Close"):
        st.rerun()

# Checks if there are any messages stored in the session
if "messages" not in st.session_state:
    st.session_state.messages = []
    display()
    

#Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if not st.session_state.messages:
    with st.chat_message("assistant"):
        greetings = st.write_stream(response_generator())
    st.session_state.messages.append({"role": "assistant", "content": greetings})
if prompt := st.chat_input("What is up?"):
    
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    response = f"Echo '{prompt}'"
    # Display assistant response in chat message container
    if len(st.session_state.messages) >= 2:
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
            

