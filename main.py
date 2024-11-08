import streamlit as st
from openai import OpenAI
import random
import os
import sys
import time
import mysql.connector as mysql
import traceback


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
    queryLowercase = query.casefold()
    listOfWords = query.split()
    if ("show" in queryLowercase):
        messages = f"Displaying {listOfWords[1].replace(';','')}....  \n"
    if ("select" in queryLowercase):
        messages = f"Display queries from {listOfWords[len(listOfWords) -1].replace(';','')}....  \n"
    if ("use" in queryLowercase):
        return f'The "use" command cannot be executed. Please refer to the show and select commands to view tables, columns, and contents of a database.'
    try:
        cursor.execute(queryLowercase)

        for x in cursor.fetchall():
            messages += f'{x}  \n'
        return messages
        
    except mysql.errors.ProgrammingError: 
        if("show" in queryLowercase ):
            return f'Command cannot be executed. Refer to the "show tables in <databasename>" command.'
        if("select" in queryLowercase):
            return f'Command cannot be executed. Refer to the "select <column> from <databaseName>.<tablesName>" command.'
        else: 
            return f'Error in "{query}" command. Please exit sql mode by typing "/sql" and ask me more questions.'
        

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


#Initialize pop window ("title", "size of window")
@st.dialog("Welcome to SWIFT's No_Chatbot!", width= "large")
def display():

    #Description
    st.write("I only make SQL queries. I do not have a freedom of speech.")

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
        db = databaseConnection(os.environ["dbhost"],os.environ["dbuser"],os.environ["dbpassword"])
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

            response = "I do not speak anymore. Only do SQL queries"
            st.chat_message("assistant").markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:     
            exitSQL = "Connection to database has closed"
            st.chat_message("assistant").markdown(exitSQL)
            st.session_state.messages.append({"role": "assistant", "content": exitSQL})

