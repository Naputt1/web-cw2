import requests
from bs4 import BeautifulSoup, Tag
import time
import logging
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set

# Configure logging for professional feedback
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Crawler:
    """
    A web crawler that recursively visits pages within a target domain.
    
    Attributes:
        base_url (str): The starting URL and domain boundary for the crawl.
        politeness_window (int): Seconds to wait between requests.
        timeout (int): Request timeout in seconds.
        visited (Set[str]): Set of already visited URLs.
        pages (List[Dict[str, str]]): List of crawled page data.
    """

    def __init__(self, base_url: str, politeness_window: int = 6, timeout: int = 10):
        """
        Initializes the crawler with a base URL and politeness settings.
        
        Args:
            base_url: The starting URL.
            politeness_window: Seconds to wait between requests. Default is 6.
            timeout: Request timeout in seconds. Default is 10.
        """
        self.base_url = base_url
        self.politeness_window = politeness_window
        self.timeout = timeout
        self.visited: Set[str] = set()
        self.pages: List[Dict[str, str]] = []

    def is_valid_url(self, url: str) -> bool:
        """
        Checks if a URL is within the target domain and has not been visited.
        
        Args:
            url: The URL to validate.
            
        Returns:
            True if the URL is valid for crawling, False otherwise.
        """
        parsed_base = urlparse(self.base_url)
        parsed_url = urlparse(url)
        
        # Ensure the URL is in the same domain or relative
        is_same_domain = (parsed_url.netloc == parsed_base.netloc or parsed_url.netloc == "")
        return is_same_domain and url not in self.visited

    def crawl(self) -> List[Dict[str, str]]:
        """
        Starts the crawling process from the base URL.
        
        Returns:
            A list of dictionaries, each containing 'url' and 'content' of a page.
        """
        queue: List[str] = [self.base_url]
        
        while queue:
            url = queue.pop(0)
            if url in self.visited:
                continue
                
            logger.info(f"Crawling: {url}")
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                self.visited.add(url)
                self.pages.append({'url': url, 'content': response.text})
                
                # Extract links using BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                for a_tag in soup.find_all('a', href=True):
                    if not isinstance(a_tag, Tag):
                        continue
                    
                    href = a_tag.get('href')
                    if not isinstance(href, str):
                        continue
                        
                    link = urljoin(url, href)
                    # Normalize by removing URL fragments
                    link = link.split('#')[0]
                    
                    if self.is_valid_url(link):
                        queue.append(link)
                
                # Respect the politeness window
                if queue:
                    logger.debug(f"Waiting {self.politeness_window} seconds...")
                    time.sleep(self.politeness_window)
                    
            except requests.RequestException as e:
                logger.error(f"Error crawling {url}: {e}")
                
        return self.pages

if __name__ == "__main__":
    # Example usage
    crawler = Crawler("https://quotes.toscrape.com/")
    # pages = crawler.crawl()
    # logger.info(f"Crawled {len(pages)} pages.")
