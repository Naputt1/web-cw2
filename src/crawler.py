import requests
from bs4 import BeautifulSoup, Tag
import time
from urllib.parse import urljoin, urlparse

class Crawler:
    def __init__(self, base_url, politeness_window=6, timeout=10):
        self.base_url = base_url
        self.politeness_window = politeness_window
        self.timeout = timeout
        self.visited = set()
        self.pages = []  # List of dicts: {'url': url, 'content': html}

    def is_valid_url(self, url):
        """Check if the URL is within the target domain and not visited."""
        parsed_base = urlparse(self.base_url)
        parsed_url = urlparse(url)
        return (
            parsed_url.netloc == parsed_base.netloc or parsed_url.netloc == ""
        ) and url not in self.visited

    def crawl(self):
        """Start crawling from the base URL."""
        queue = [self.base_url]
        
        while queue:
            url = queue.pop(0)
            if url in self.visited:
                continue
                
            print(f"Crawling: {url}")
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                self.visited.add(url)
                self.pages.append({'url': url, 'content': response.text})
                
                # Extract links
                soup = BeautifulSoup(response.text, 'html.parser')
                for a_tag in soup.find_all('a', href=True):
                    # Ensure it's a Tag and not a NavigableString to satisfy Pylance
                    if not isinstance(a_tag, Tag):
                        continue
                    
                    # Use get() to safely access href and check if it's a string
                    href = a_tag.get('href')
                    if not isinstance(href, str):
                        continue
                        
                    link = urljoin(url, href)
                    # Basic normalization (strip fragment)
                    link = link.split('#')[0]
                    if self.is_valid_url(link):
                        queue.append(link)
                
                # Politeness window
                if queue:
                    print(f"Waiting {self.politeness_window} seconds...")
                    time.sleep(self.politeness_window)
                    
            except requests.RequestException as e:
                print(f"Error crawling {url}: {e}")
                
        return self.pages

if __name__ == "__main__":
    # Test crawler with a short run if needed
    crawler = Crawler("https://quotes.toscrape.com/")
    # For testing, we might want to limit pages, but coursework says "all pages"
    # pages = crawler.crawl()
    # print(f"Crawled {len(pages)} pages.")
