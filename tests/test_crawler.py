import sys
import os
from unittest.mock import MagicMock, patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from crawler import Crawler

@patch('requests.get')
@patch('time.sleep', return_value=None)  # Skip politeness window during tests
def test_crawler_basic(mock_sleep, mock_get):
    # Setup mock responses
    base_html = '<html><body><a href="/page1">Link</a></body></html>'
    page1_html = '<html><body>Content 1</body></html>'
    
    mock_response_base = MagicMock()
    mock_response_base.text = base_html
    mock_response_base.status_code = 200
    
    mock_response_page1 = MagicMock()
    mock_response_page1.text = page1_html
    mock_response_page1.status_code = 200
    
    # Side effect to return different responses based on URL
    def get_side_effect(url, *args, **kwargs):
        if url == "https://quotes.toscrape.com/":
            return mock_response_base
        elif "page1" in url:
            return mock_response_page1
        return MagicMock(status_code=404)

    mock_get.side_effect = get_side_effect
    
    crawler = Crawler("https://quotes.toscrape.com/", politeness_window=0)
    pages = crawler.crawl()
    
    assert len(pages) == 2
    urls = [p['url'] for p in pages]
    assert "https://quotes.toscrape.com/" in urls
    assert any("page1" in u for u in urls)

@patch('requests.get')
@patch('time.sleep', return_value=None)
def test_crawler_error_handling(mock_sleep, mock_get):
    # Test that crawler handles RequestException without crashing
    import requests
    mock_get.side_effect = requests.RequestException("Network Error")
    crawler = Crawler("https://error.com")
    pages = crawler.crawl()
    assert pages == []

def test_is_valid_url():
    crawler = Crawler("https://quotes.toscrape.com/")
    assert crawler.is_valid_url("https://quotes.toscrape.com/tag/life/") is True
    assert crawler.is_valid_url("https://google.com") is False
    # Relative paths
    assert crawler.is_valid_url("/page1") is True
    # Fragment normalization
    assert crawler.is_valid_url("https://quotes.toscrape.com/#fragment") is True
