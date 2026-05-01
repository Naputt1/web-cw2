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
        # Use .db extension for SQLite
        self.index_path = os.path.join('data', 'index.db')
        self.indexer = Indexer(self.index_path)
        self.base_url = "https://quotes.toscrape.com/"

    def do_build(self, arg):
        """Build the inverted index by crawling the website."""
        print(f"Starting build from {self.base_url}...")
        crawler = Crawler(self.base_url)
        pages = crawler.crawl()
        
        print(f"Crawling complete. Indexed {len(pages)} pages.")
        
        # Fresh build: remove existing database if it exists
        if os.path.exists(self.index_path):
            self.indexer.close()
            os.remove(self.index_path)
        
        # Re-initialize indexer to create fresh tables
        self.indexer = Indexer(self.index_path)
        
        for page in pages:
            self.indexer.add_page(page['url'], page['content'])
            
        print(f"Index saved to {self.index_path}")

    def do_load(self, arg):
        """Load the index from the file system. Usage: load [path]"""
        path = arg.strip() if arg else self.index_path
        
        if self.indexer.load_index(path):
            self.index_path = path  # Update current index path to the loaded one
            print(f"Index loaded successfully from {path}")
        else:
            print(f"Error: Index file not found at {path}. Run 'build' first.")

    def do_print(self, arg):
        """Print the inverted index for a particular word. Usage: print <word>"""
        if not arg:
            print("Usage: print <word>")
            return
        
        # Check if database exists
        if not os.path.exists(self.index_path):
            print(f"Error: Index file not found. Run 'build' first.")
            return
            
        searcher = SearchEngine(self.index_path)
        print(searcher.print_word_info(arg))

    def do_find(self, arg):
        """Find pages containing the query phrase. Usage: find <query>"""
        if not arg:
            print("Usage: find <query>")
            return
        
        # Check if database exists
        if not os.path.exists(self.index_path):
            print(f"Error: Index file not found. Run 'build' first.")
            return
            
        searcher = SearchEngine(self.index_path)
        results = searcher.find(arg)
        
        if not results:
            print(f"No pages found for query: '{arg}'")
        else:
            print(f"Found {len(results)} page(s) for query: '{arg}':")
            for url in results:
                print(f"  - {url}")

    def do_exit(self, arg):
        """Exit the search tool."""
        self.indexer.close()
        print("Goodbye!")
        return True

    def do_EOF(self, arg):
        """Exit on Ctrl-D."""
        self.indexer.close()
        print("Goodbye!")
        return True

if __name__ == '__main__':
    SearchToolShell().cmdloop()
