import cmd
import os
from crawler import Crawler
from indexer import Indexer
from search import SearchEngine

class SearchToolShell(cmd.Cmd):
    intro = 'Welcome to the Search Engine Tool. Type help or ? to list commands.\n'
    prompt = '> '
    
    def __init__(self):
        super().__init__()
        self.indexer = Indexer()
        self.index_path = os.path.join('data', 'index.json')
        self.base_url = "https://quotes.toscrape.com/"

    def do_build(self):
        """Build the inverted index by crawling the website."""
        print(f"Starting build from {self.base_url}...")
        crawler = Crawler(self.base_url)
        pages = crawler.crawl()
        
        print(f"Crawling complete. Indexed {len(pages)} pages.")
        for page in pages:
            self.indexer.add_page(page['url'], page['content'])
            
        self.indexer.save_index(self.index_path)
        print(f"Index saved to {self.index_path}")

    def do_load(self):
        """Load the index from the file system."""
        if self.indexer.load_index(self.index_path):
            print(f"Index loaded successfully from {self.index_path}")
        else:
            print(f"Error: Index file not found at {self.index_path}. Run 'build' first.")

    def do_print(self, arg):
        """Print the inverted index for a particular word. Usage: print <word>"""
        if not arg:
            print("Usage: print <word>")
            return
        
        searcher = SearchEngine(self.indexer.index)
        print(searcher.print_word_info(arg))

    def do_find(self, arg):
        """Find pages containing the query phrase. Usage: find <query>"""
        if not arg:
            print("Usage: find <query>")
            return
        
        searcher = SearchEngine(self.indexer.index)
        results = searcher.find(arg)
        
        if not results:
            print(f"No pages found for query: '{arg}'")
        else:
            print(f"Found {len(results)} page(s) for query: '{arg}':")
            for url in results:
                print(f"  - {url}")

    def do_exit(self):
        """Exit the search tool."""
        print("Goodbye!")
        return True

    def do_EOF(self):
        """Exit on Ctrl-D."""
        print("Goodbye!")
        return True

if __name__ == '__main__':
    SearchToolShell().cmdloop()
