import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from trafilatura import fetch_url, extract
from urllib.robotparser import RobotFileParser

# Set to store visited URLs
visited_urls = set()

def is_promotional(url):
    """Check if a given URL is promotional."""
    # Check if the URL contains promotional words
    promotional_websites = ["www.instagram.com", "www.facebook.com", "www.twitter.com", "www.linkedin.com"]
    # promotional_words = ["promo", "discount", "sale", "offer", "free", "deal", "coupon", "ad", "advert", "sponsored", "affiliate", "partnership", "partners", "partner", "collaboration", "collab", "brand", "branding"]
    
    promo_web = False
    promo_word = False

    for website in promotional_websites:
        if website in url:
            promo_web = True
    # for word in promotional_words:
    #     if word in url:
    #         promo_word = True
    return (promo_web or promo_word)

def get_links(url, base_url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all <a> tags and get their href attributes
        links = set()
        print(f"while extracting links, {base_url}")
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
        downloaded = fetch_url(url)
        if downloaded:
            content = extract(downloaded)
            return content
        else:
            print(f"Failed to fetch content from {url}")
            return None
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None

def crawl(url, max_depth=2, current_depth=0):
    """Crawl a website up to a specified depth."""
    # if current_depth > max_depth:
    #     return
    if url in visited_urls:
        return
    visited_urls.add(url)
    
    print(f"Crawling: {url} (Depth: {current_depth})")
    content = extract_content(url)
    if content:
        
        print(f"doc_id: {len(visited_urls)}")  
        with open(f"./docs/dataset_{len(visited_urls)}.txt", "w+", encoding="utf-8") as file:
            file.write(url + "\n")
            file.write(content.split("\n",1)[0]+ "\n")
            file.write(content.split("\n",1)[1]+ "\n")
        print("-----------------------------------")
        
        
    # if current_depth < max_depth:
    links = get_links(url,base_url)
    for link in links:
        crawl(link, max_depth, current_depth + 1)


def scrape(url_list, max_depth,  user_agent="*", path="/"):
    """
    Check if a website allows scraping for a given URL, user-agent, and path.

    :param url: The base URL of the website (e.g., "https://example.com").
    :param user_agent: The user-agent string to check (default is "*" for all bots).
    :param path: The specific path to check (default is "/" for the homepage).
    :return: True if scraping is allowed, False otherwise.
    """
    allowed_urls = []
    for url in url_list:
        
        try:
            headers = {
                "User-Agent": "Omega923/1.0"  # Replace with a custom user-agent
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad status codes

            if response.status_code == 200:
                print(f"Successfully fetched {url}")
                allowed_urls.append(url)

        except requests.exceptions.RequestException as e:
            
            print(f"Error fetching robots.txt: {e}")
            return False
    
    global base_url

    for base_url in allowed_urls:
        print("base_url: ",base_url)
        crawl(base_url,max_depth=max_depth)