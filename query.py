import os
import streamlit as st


import openai
from langchain_community.document_loaders import DirectoryLoader
from langchain.chains.question_answering import load_qa_chain

from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# Function to load documents from a directory
def load_documents(directory_path):
    loader = DirectoryLoader(directory_path, glob="**/*.txt")  # Modify file types as needed
    documents = loader.load()
    return documents

# Function to generate a response using OpenAI and Langchain
def generate_response(query, documents):
    # Load the OpenAI model
    llm = OpenAI(temperature=0.9)
    
    # Define the prompt for the query
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="You are given the following context: {context}. Now, answer this question: {question}"
    )

    # Load the Question-Answering chain
    qa_chain = load_qa_chain(llm, chain_type="stuff")

    # Run the QA chain with documents and query
    answer = qa_chain.run(input_documents=documents, question=query)
    return answer
