# Search Engine Tool - COMP3011 Coursework 2

## Project Overview
This project is a Python-based search engine tool designed to crawl the [Quotes to Scrape](https://quotes.toscrape.com/) website, build an inverted index of all words found on the pages, and provide a command-line interface (CLI) for searching.

- **Advanced Search Engine**: Implements **TF-IDF (Term Frequency-Inverse Document Frequency)** ranking for highly relevant search results.
- **Linguistic Processing**: Includes **Stop Word removal** and **Basic Stemming** to optimize the index and improve recall.
- **Advanced Query Syntax**: Supports strict inclusion (`+`) and exclusion (`-`) operators.
- **Persistence**: Saves and loads the index to/from the file system as a professional SQLite database file (`.db`).
- **Professional Engineering**: Features full type hints, Google-style docstrings, and a CI/CD pipeline.

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Install Dependencies
Navigate to the project root and run:
```bash
pip install -r requirements.txt
```

## Usage Instructions
To start the search tool, run:
```bash
python src/main.py
```

Once inside the CLI (`>`), you can use the following commands:

### 1. `build`
Crawls the website, builds the index, and saves it to `data/index.db`.
**Note:** This command respects a 6-second delay between requests and may take several minutes to complete.
```
> build
```

### 2. `load [path]`
Loads a previously built index from the file system. If no path is provided, it defaults to `data/index.db`.
```
> load
> load data/custom_index.db
```

### 3. `print <word>`
Prints the inverted index entry (URLs, frequency, positions) for a specific word.
```
> print life
```

### 4. `find <query>`
Finds all pages matching the query, ranked by TF-IDF relevance.
- `+word`: MUST be in the page.
- `-word`: MUST NOT be in the page.
```
> find life
> find +good +friends
> find -indifference
```

### 5. `exit`
Exits the search tool.
```
> exit
```

## Testing
The project includes a comprehensive test suite using `pytest`.

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
To generate a code coverage report:
```bash
pytest --cov=src tests/
```

The tests cover:
- **Crawler**: Mocked network requests and URL validation.
- **Indexer**: Text cleaning, tokenization, and SQLite index construction.
- **Search Logic**: Single and multi-word query intersection using SQL queries.
- **CLI Logic**: Command handling, default paths, and custom index loading.

### Advanced Analysis
A benchmarking script is provided to analyze search performance:
```bash
python scripts/benchmark.py
```

## Project Structure
- `src/`: Source code (`crawler.py`, `indexer.py`, `search.py`, `main.py`, `utils.py`)
- `tests/`: Unit tests (Crawler, Indexer, Search, CLI)
- `scripts/`: Benchmarking and utility scripts
- `.github/`: CI/CD workflows
- `data/`: Directory for stored index files
- `requirements.txt`: Project dependencies
- `README.md`: Project documentation
