import cmd
import os
import logging
from crawler import Crawler
from indexer import Indexer
from search import SearchEngine

# Professional logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class SearchToolShell(cmd.Cmd):
    """
    A professional Command-Line Interface (CLI) for the Search Engine Tool.
    
    Provides commands to crawl a website, build a ranked inverted index, 
    and perform advanced relevance-based searches.
    """
    intro = (
        '\n'
        '=================================================================\n'
        '           WELCOME TO THE ADVANCED SEARCH ENGINE TOOL           \n'
        '=================================================================\n'
        'Type "help" or "?" to list commands. Use "exit" to quit.\n'
    )
    prompt = '(search) > '
    
    def __init__(self):
        """Initializes the shell with default paths and components."""
        super().__init__()
        self.index_path: str = os.path.join('data', 'index.db')
        self.indexer: Indexer = Indexer(self.index_path)
        self.base_url: str = "https://quotes.toscrape.com/"

    def do_build(self, arg: str) -> None:
        """
        Crawls the target website and builds a ranked inverted index.
        
        Usage: build
        """
        print(f"[*] Starting crawl of {self.base_url}...")
        crawler = Crawler(self.base_url)
        pages = crawler.crawl()
        
        if not pages:
            print("[!] Crawl failed or returned no data. Check connectivity.")
            return
            
        print(f"[*] Crawling complete. Processing {len(pages)} pages into SQLite index...")
        
        # Reset the database for a fresh build
        if os.path.exists(self.index_path):
            self.indexer.close()
            os.remove(self.index_path)
        
        self.indexer = Indexer(self.index_path)
        
        for page in pages:
            self.indexer.add_page(page['url'], page['content'])
            
        print(f"[+] Build successful. Persistent index saved to {self.index_path}")

    def do_load(self, arg: str) -> None:
        """
        Loads an existing index from the file system.
        
        Usage: load [path_to_db]
        """
        path = arg.strip() if arg else self.index_path
        
        if self.indexer.load_index(path):
            self.index_path = path
            print(f"[+] Index successfully loaded from: {path}")
        else:
            print(f"[!] Error: Could not find or open index at: {path}")

    def do_print(self, arg: str) -> None:
        """
        Displays detailed index statistics and positions for a specific word.
        
        Usage: print <word>
        """
        if not arg:
            print("Usage: print <word>")
            return
        
        if not os.path.exists(self.index_path):
            print("[!] Error: No index found. Please run 'build' or 'load' first.")
            return
            
        searcher = SearchEngine(self.index_path)
        print(searcher.print_word_info(arg))

    def do_find(self, arg: str) -> None:
        """
        Performs a ranked search for a query phrase.
        
        Advanced Syntax:
          +word : Document MUST contain this word.
          -word : Document MUST NOT contain this word.
          word  : Used for TF-IDF relevance ranking.
          
        Usage: find <query_string>
        """
        if not arg:
            print("Usage: find <query>")
            return
        
        if not os.path.exists(self.index_path):
            print("[!] Error: No index found. Please run 'build' or 'load' first.")
            return
            
        searcher = SearchEngine(self.index_path)
        results = searcher.find(arg)
        
        if not results:
            print(f"[*] No documents matched the query: '{arg}'")
        else:
            print(f"[*] Found {len(results)} results for '{arg}' (Ranked by TF-IDF):")
            print("-" * 60)
            print(f"{'Rank':<5} {'Score':<8} {'URL'}")
            print("-" * 60)
            
            for i, (url, score) in enumerate(results, 1):
                print(f"{i:<5} {score:<8.3f} {url}")
            
            print("-" * 60)

    def do_exit(self, arg: str) -> bool:
        """Exits the search tool gracefully."""
        self.indexer.close()
        print("Exiting. Goodbye!")
        return True

    def do_EOF(self, arg: str) -> bool:
        """Exits the shell on Ctrl-D."""
        print()
        return self.do_exit(arg)

if __name__ == '__main__':
    # Ensure the data directory exists before starting
    os.makedirs('data', exist_ok=True)
    try:
        SearchToolShell().cmdloop()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")
