import streamlit as st
from openai import OpenAI
import random
import os
import sys
import time
import mysql.connector as mysql
import traceback
from query import load_documents, generate_response

script_directory= os.path.dirname(os.path.abspath(sys.argv[0]))
sqlCommand = "/sql"
def databaseConnection(dbhost, dbuser, dbpassword):
    conn = mysql.connect(
        host = dbhost,
        user = dbuser,
        passwd = dbpassword
    )
    return conn
def sqlExecution(query,cursor):

    listOfWords = query.split()
    if ("show" in query.casefold()):
        messages = f"Displaying {listOfWords[1].replace(';','')}....  \n"
    if ("select" in query.casefold()):
        messages = f"Display queries from {listOfWords[len(listOfWords) -1].replace(';','')}....  \n"
    try:
        cursor.execute(query.casefold())

        for x in cursor.fetchall():
            messages += f'{x}  \n'
        return messages
        
    except mysql.errors.ProgrammingError: 
        return f'Error in "{query}" command. Please exit sql mode by typing "/sql" and ask me more questions.'
    # except Exception as e:
    #     exc_type, exc_value, exc_tb = sys.exc_info() 
    #     tb = traceback.TracebackException(exc_type, exc_value,exc_tb) 
    #     #
    #     return ''.join(tb.format_exception_only())
        
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

if prompt := st.chat_input("Type here..."):
    
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
   
    #Matches for the "sql" command to enter the sql mode
    numberOfSQL = sum([d['content'] == sqlCommand for d in st.session_state.messages])
    if (numberOfSQL % 2 > 0): 
        db = databaseConnection(st.secrets["host"],st.secrets["user"],st.secrets["password"])
        cursor = db.cursor()
        if(prompt == sqlCommand):
            sqlMessage = 'Entering SQL mode...  \nPlease type "/sql" again to exit sql mode  \nAvailable commands:  \nSELECT and SHOW'          
            st.chat_message("assistant").markdown(sqlMessage)
            st.session_state.messages.append({"role": "assistant", "content": sqlMessage})
        
        else:
            try:
                sqlResponse = sqlExecution(prompt.casefold(), cursor)
                st.chat_message("assistant").markdown(sqlResponse)
                st.session_state.messages.append({"role": "assistant", "content": sqlResponse})
            except:
                st.chat_message("assistant").markdown("SQL query is unrecognizeable")
                st.session_state.messages.append({"role": "assistant", "content": "SQL query is unrecognizeable"})
            else:
                db.close()

        
    else:
    # Display assistant response in chat message container
        if ((len(st.session_state.messages) >= 2) & (prompt != sqlCommand)) :

            message_placeholder = st.empty()
            dataDirectory = f"{script_directory}/data/"
            documents = load_documents(dataDirectory)
            response = generate_response(prompt,documents)
            st.chat_message("assistant").markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:     
            exitSQL = "Connection to database has closed"
            st.chat_message("assistant").markdown(exitSQL)
            st.session_state.messages.append({"role": "assistant", "content": exitSQL})

