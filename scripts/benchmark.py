import time
import os
import sys
from typing import List

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from indexer import Indexer
from search import SearchEngine

def benchmark_search():
    """Measures performance of the search engine."""
    db_path = "data/index.db"
    if not os.path.exists(db_path):
        print("Benchmark Error: index.db not found. Run 'build' in the CLI first.")
        return

    searcher = SearchEngine(db_path)
    
    # Test queries
    queries = [
        "life",
        "love",
        "the world",
        "+life -love",
        "inspirational quotes about success"
    ]
    
    print("="*60)
    print(f"{'Query':<40} {'Results':<10} {'Latency (ms)'}")
    print("-" * 60)
    
    for query in queries:
        start_time = time.perf_counter()
        results = searcher.find(query)
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        print(f"{query:<40} {len(results):<10} {latency_ms:<12.4f}")
        
    print("="*60)

if __name__ == "__main__":
    benchmark_search()
