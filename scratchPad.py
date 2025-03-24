'''
import ollama 

# Connect to the remote Ollama server
client = ollama.Client(host='http://192.168.1.147:11434')

note = "./docs/dataset.txt"

with open(note,'r') as file:
    content = file.read()

my_prompt = f'what is capital of France?'

# Use the client instance you created
response = client.generate(model='deepseek-r1', prompt=my_prompt)
actual_response = response['response']
print(actual_response)

##---------------------------------------------------------------

import requests
from bs4 import BeautifulSoup

# URL of the website
base_url = "https://aimagazine.com"

# Fetch the sitemap
sitemap_url = "https://aimagazine.com/sitemap.xml"
response = requests.get(sitemap_url)
sitemap_content = response.text

# Parse the sitemap to extract URLs (example using BeautifulSoup)
from bs4 import BeautifulSoup
soup = BeautifulSoup(sitemap_content, "xml")
urls = [loc.text for loc in soup.find_all("loc")]

# Scrape allowed pages
for url in urls:
    if not any(disallowed in url for disallowed in ["/cdn-cgi/", "/404", "/search", "/my-account", "/executives", "/homepage-beta"]):
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Scraping: {url}")
            # Process the page content here
        else:
            print(f"Failed to access: {url}")
'''
'''
# Create a vector store with a sample text
from langchain_core.vectorstores import InMemoryVectorStore # type: ignore
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import TextLoader
import os
# List of file paths to the text documents
root = "/mnt/hdd/yourProjects/OnGoing/webScraper/sampleCopora/"
file_paths=os.listdir(root)

# List to store the loaded documents
documents = []

# Load each document
for file_path in file_paths:
    loader = TextLoader(root + file_path)
    loaded_docs = loader.load()
    documents.extend(loaded_docs)

print("Documents loaded: ", len(documents))

# # Now `documents` contains all the loaded documents
# for doc in documents:
#     print(doc.page_content)  # Access the content of each document

# Initialize the custom embedding model
embedding_model = OllamaEmbeddings(model="nomic-embed-text")
print("Embedding model initialized")

for doc in documents:
    # Use the custom embedding model with InMemoryVectorStore
    vectorstore = InMemoryVectorStore.from_texts(
        texts=doc.page_content,
        embedding=embedding_model
    )
print("Vector store created")
# Use the vectorstore as a retriever
retriever = vectorstore.as_retriever()

# Retrieve the most similar text
retrieved_documents = retriever.invoke("What is 3 things that didn’t make the 10 Breakthrough Technologies of 2025 ?")

# Show the retrieved document's content
if retrieved_documents:
    print(retrieved_documents[0].page_content)
else:
    print("No documents retrieved.")

'''

import requests
from bs4 import BeautifulSoup
from trafilatura import fetch_url, extract
from urllib.parse import urljoin

def get_links_old(url):
    """Extract all links from a given URL."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = set()
    for a_tag in soup.find_all('a', href=True):
        link = urljoin(url, a_tag['href'])
        links.add(link)
    return links

def get_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all <a> tags and get their href attributes
        links = set()
        print(f"while extracting links, {base_url}")
        for a_tag in soup.find_all('a', href=True):
            print(f"extracted link: {a_tag['href']}")
            link = urljoin(base_url, a_tag['href'])  # Resolve relative URLs
            if base_url in link:  # Only include links from the same domain
                links.add(link)
        return links
    except Exception as e:
        print(f"Error extracting links from {url}: {e}")
        return set()

def crawl(url, max_depth=2, current_depth=0):
    """Crawl a website up to a specified depth."""
    if current_depth > max_depth:
        return

    print(f"Crawling: {url} (Depth: {current_depth})")
    # content = fetch_url(url)
    # if content:
    #     extracted_content = extract(content)
    #     print(extracted_content)  # Or save/process the content as needed
    print("-------------------------------------------------")
    if current_depth < max_depth:
        links = get_links(url)
        for link in links:
            crawl(link, max_depth, current_depth + 1)

# Example usage
# base_url = 'https://www.infor.com/blog/'
# crawl(base_url, max_depth=2)

from trafilatura import sitemaps


import requests
from bs4 import BeautifulSoup
 
 
url = 'https://www.infor.com/blog'
reqs = requests.get(url)
soup = BeautifulSoup(reqs.text, 'html.parser')
 
content = fetch_url(url)
print(content)
+