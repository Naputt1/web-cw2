import pytest
from unittest.mock import patch
import os
import sys

# Ensure src is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import SearchToolShell

@pytest.fixture
def shell_setup(tmp_path):
    # Mock Indexer to avoid actual DB operations during shell testing
    with patch('main.Indexer') as MockIndexer:
        mock_indexer_instance = MockIndexer.return_value
        shell = SearchToolShell()
        # Set a predictable default path for testing
        default_path = str(tmp_path / "index.db")
        shell.index_path = default_path
        yield shell, mock_indexer_instance

def test_load_command_default(shell_setup):
    shell, mock_indexer = shell_setup
    mock_indexer.load_index.return_value = True
    
    # Execute load without arguments
    shell.do_load("")
    
    # Should call load_index with the default path
    mock_indexer.load_index.assert_called_with(shell.index_path)

def test_load_command_custom_path(shell_setup):
    shell, mock_indexer = shell_setup
    custom_path = "data/custom_index.db"
    mock_indexer.load_index.return_value = True
    
    # Execute load with a custom path
    shell.do_load(custom_path)
    
    # Should call load_index with the custom path
    mock_indexer.load_index.assert_called_with(custom_path)
    # The shell's index_path should be updated to the custom path
    assert shell.index_path == custom_path

def test_load_command_failure(shell_setup, tmp_path):
    shell, mock_indexer = shell_setup
    default_path = shell.index_path
    mock_indexer.load_index.return_value = False
    
    # Execute load with a path that fails
    shell.do_load("invalid_path.db")
    
    # If load fails, index_path should NOT be updated
    assert shell.index_path == default_path

def test_build_clears_existing_db(shell_setup, tmp_path):
    shell, mock_indexer = shell_setup
    db_path = str(tmp_path / "build_test.db")
    shell.index_path = db_path
    
    # Create a dummy file to represent an existing DB
    with open(db_path, "w") as f:
        f.write("dummy data")
    
    with patch('main.Crawler') as MockCrawler:
        MockCrawler.return_value.crawl.return_value = []
        shell.do_build("")
        
    # File should have been removed and recreated (or at least removed by os.remove)
    # Since we mocked Indexer, it won't actually recreate the file unless we tell it to,
    # but we can verify the mock was called.
    assert mock_indexer.close.called
