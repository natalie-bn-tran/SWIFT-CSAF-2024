import streamlit as st
from openai import OpenAI
import random
import os
import time
import mysql.connector as mysql
import traceback
from query import load_documents, generate_response

def databaseConnection(dbhost, dbuser, dbpassword):
    conn = mysql.connect(
        host = dbhost,
        user = dbuser,
        passwd = dbpassword
    )
    return conn
def sqlExecution(query,cursor):

    #if ("databases" in query.casefold()) | ('database' in query.casefold()):
    #Prvovide extra information like selecting from tableXX....
    listOfWords = query.split()
    if ("show" in query.casefold()):
        messages = f"Displaying {listOfWords[1].replace(';','')}...."
    try:
        print(query.split())
        cursor.execute(query)
        message = ""
        for x in cursor.fetchall():
            message += f'{x}  \n'
        print(message) 
    except Exception:
        print(traceback.format_exc())
    # else:
    #     try:
    #         cursor.execute(query)
    #         print(cursor.fetchall())
    #     except Exception:
    #          print(traceback.format_exc())
        

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

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"
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
   
    #Matches for the "sql" command to enter the sql mode
    numberOfSQL = sum([d['content'] == 'sql' for d in st.session_state.messages])
    if (numberOfSQL % 2 > 0): 
        db = databaseConnection("192.168.1.120","ccdc","ccdc")
        cursor = db.cursor()
        if(prompt == 'sql'):
            sqlMessage = 'Entering SQL mode...  \nAvailable commands:  \nSELECT and SHOW'          
            st.chat_message("assistant").markdown(sqlMessage)
            st.session_state.messages.append({"role": "assistant", "content": sqlMessage})
        
        else:
            try:
                sqlExecution(prompt, cursor)
            except:
                print("SQL query is unrecognizeable")
            else:
                db.close()

        
    else:
    # Display assistant response in chat message container
        if ((len(st.session_state.messages) >= 2) & (prompt != 'sql')) :
            
            # with st.chat_message("assistant"):
            #     stream = client.chat.completions.create(
            #         model=st.session_state["openai_model"],
            #         messages=[
            #             {"role": m["role"], "content": m["content"]}
            #             for m in st.session_state.messages
            #         ],
            #         stream=True,
            #     )
            # # Add assistant response to chat history
            #     response = st.write_stream(stream)
            message_placeholder = st.empty()
            dataDirectory = "./data/"
            documents = load_documents(dataDirectory)
            response = generate_response(prompt,documents)
            st.chat_message("assistant").markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:     
            exitSQL = "Connection to database has closed"
            st.chat_message("assistant").markdown(exitSQL)
            st.session_state.messages.append({"role": "assistant", "content": exitSQL})

