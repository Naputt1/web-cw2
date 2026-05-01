# Search Engine Tool - COMP3011 Coursework 2

## Project Overview
This project is a Python-based search engine tool designed to crawl the [Quotes to Scrape](https://quotes.toscrape.com/) website, build an inverted index of all words found on the pages, and provide a command-line interface (CLI) for searching.

### Features
- **Web Crawler**: Recursively crawls the target website while respecting a 6-second politeness window.
- **Inverted Indexer**: Processes HTML content into an inverted index that stores word frequencies and positions.
- **Search CLI**: Allows users to build, load, and query the index for single or multi-word search terms.
- **Persistence**: Saves and loads the index to/from the file system as a SQLite database file (`.db`).

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
Finds all pages containing all words in the search query.
```
> find good friends
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

The tests cover:
- **Crawler**: Mocked network requests and URL validation.
- **Indexer**: Text cleaning, tokenization, and SQLite index construction.
- **Search Logic**: Single and multi-word query intersection using SQL queries.
- **CLI Logic**: Command handling, default paths, and custom index loading.

## Project Structure
- `src/`: Source code (`crawler.py`, `indexer.py`, `search.py`, `main.py`)
- `tests/`: Unit tests
- `data/`: Directory for stored index files
- `requirements.txt`: Project dependencies
- `README.md`: Project documentation
