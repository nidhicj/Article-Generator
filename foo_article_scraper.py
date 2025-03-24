import requests
from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import urljoin

# Base URL to crawl
base_url = 'https://www.infor.com/blog/'

# Set to store visited URLs
visited_urls = set()

# Function to extract all links from a page
def extract_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all <a> tags and get their href attributes
        links = set()
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(base_url, a_tag['href'])  # Resolve relative URLs
            if base_url in link:  # Only include links from the same domain
                links.add(link)
        return links
    except Exception as e:
        print(f"Error extracting links from {url}: {e}")
        return set()

# Function to extract content from a page using trafilatura
def extract_content(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            content = trafilatura.extract(downloaded)
            return content
        else:
            print(f"Failed to fetch content from {url}")
            return None
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None

# Function to crawl the website recursively
def crawl(url):
    if url in visited_urls:
        return
    visited_urls.add(url)
    
    print(f"Crawling: {url}")
    
    # Extract content from the current page
    # content = extract_content(url)
    # if content:
    #     # Save the content (you can modify this to save to a file or database)
    #     print(f"Extracted content from {url}:")
    #     # print(content[:500])  # Print the first 500 characters as a preview
    #     print("-" * 80)
    
    # Extract links from the current page and crawl them
    links = extract_links(url)
    for link in links:
        crawl(link)

# Start crawling from the base URL
crawl(base_url)