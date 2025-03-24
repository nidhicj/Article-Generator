import os
from ariticle_scraper import scrape
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import (
    CharacterTextSplitter,
)
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate
from requests import post
from typing import List
from ollamaEmbeddings import OllamaEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

HOST_IP="192.168.137.1"
CORPORA_PATH="/mnt/hdd/yourProjects/OnGoing/webScraper/docs/"
EMBEDDING_MODEL="nomic-embed-text"
RETRIEVAL_MODEL = "llama2" 

# template: str = """/
    # You are a Tech Journalist at AI news broadcast. /
    # question: {question}. You need to keep the readers updated with quirky news headlines based on {context} /
    # and  technical development. /
    # """
# system_message_prompt = SystemMessagePromptTemplate.from_template(template)
# human_message_prompt = HumanMessagePromptTemplate.from_template(
#     input_variables=["question", "context"],
#     template="{question}",
# )
# chat_prompt_template = ChatPromptTemplate.from_messages(
#     [system_message_prompt, human_message_prompt]
# )

# Function to load text files from a directory
def getDocuments(directory) :
    """Load text files from a directory and convert them into Document objects."""
    documents = []
    print("Loading text files from directory")
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):  # Only process .txt files
            file_path = os.path.join(directory, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
                # Create a Document object with the file content and metadata
                documents.append(Document(page_content=text, metadata={"source": filename}))
    
    # Split the documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
    chunks = text_splitter.split_documents(documents)
    
    return chunks


def getEmbeddings(documents: List[Document], user_query):
    """Create a vector store from a set of documents using custom embeddings."""
    # Generate embeddings for each document
    # Initialize the custom embedding function
    embedding_function = OllamaEmbeddings(base_url=f"http://{HOST_IP}:11434", model=EMBEDDING_MODEL)

    # Extract texts and metadata from documents
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]

    # Create Chroma vector store
    db = Chroma.from_texts(
        texts=texts,
        embedding=embedding_function,  # Use the custom embedding function
        metadatas=metadatas
    )
    print("Created Chroma vector store")

    # Perform similarity search
    docs = db.similarity_search(user_query)
    print("Performed similarity search")
    # print(docs)
    return db.as_retriever()
                                           


# Define the prompt template
chat_prompt_template = ChatPromptTemplate.from_template(
    """
    Use the following context to answer the question:
    Context: {context}
    Question: {question}
    Answer:
    """
)

def call_OllamaAPI(prompt):
    url = f"http://{HOST_IP}:11434/api/generate"
    
    # Send the prompt to the Ollama API
    payload = {
        "model": RETRIEVAL_MODEL,
        "prompt": prompt,
        "stream": False  # Set to True if you want streaming responses
    }
    response = post(url, json=payload)

    if response.status_code == 200:
        # Parse the response from Ollama
        response_data = response.json()
        return response_data.get("response", "No response generated.")
    else:
        raise Exception(f"Failed to generate response: {response.status_code} {response.text}")

def generateResponse(retriever, query):
    # Create the chain
    # Retrieve relevant documents using the retriever
    context = retriever.invoke(query)
    context_text = " ".join([doc.page_content for doc in context])  # Combine context into a single string

    # Format the prompt using the context and query
    prompt = chat_prompt_template.format(context=context_text, question=query)

    # Call the Ollama API with the formatted prompt
    response = call_OllamaAPI(prompt)
    return response

def query(query):

    documents = getDocuments(CORPORA_PATH)
    retriever = getEmbeddings(documents, query)
    response = generateResponse(retriever, query)
    return response

#Web crawl and gaher corpus for the given url
# url_list = ['https://www.infor.com/blog/',
            # 'https://www.manh.com/our-insights/resources/blog?page=1&sort=recent'
            # ]
# scrape(url_list, max_depth=2)


# prompt = "Generate an article about Master the end-to-end procurement to ledger process with FSM from the given context and question."
# response = query(prompt)
# print(response)
