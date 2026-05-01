import pytest
from unittest.mock import MagicMock, patch
import os
import sys

# Ensure src is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import SearchToolShell

@pytest.fixture
def shell_setup(tmp_path):
    # Mock Indexer and SearchEngine to avoid actual DB operations during shell testing
    with patch('main.Indexer') as MockIndexer, patch('main.SearchEngine') as MockSearch:
        mock_indexer_instance = MockIndexer.return_value
        mock_search_instance = MockSearch.return_value
        
        shell = SearchToolShell()
        default_path = str(tmp_path / "index.db")
        shell.index_path = default_path
        
        yield shell, mock_indexer_instance, mock_search_instance

def test_load_command_default(shell_setup):
    shell, mock_indexer, _ = shell_setup
    mock_indexer.load_index.return_value = True
    
    shell.do_load("")
    
    mock_indexer.load_index.assert_called_with(shell.index_path)

def test_load_command_custom_path(shell_setup):
    shell, mock_indexer, _ = shell_setup
    custom_path = "data/custom_index.db"
    mock_indexer.load_index.return_value = True
    
    shell.do_load(custom_path)
    
    mock_indexer.load_index.assert_called_with(custom_path)
    assert shell.index_path == custom_path

def test_load_command_failure(shell_setup):
    shell, mock_indexer, _ = shell_setup
    default_path = shell.index_path
    mock_indexer.load_index.return_value = False
    
    shell.do_load("invalid_path.db")
    
    # If load fails, index_path should NOT be updated
    assert shell.index_path == default_path

def test_find_command_output(shell_setup):
    shell, _, mock_search = shell_setup
    # Mock ranked results: (url, score)
    mock_search.find.return_value = [("url1", 1.2345), ("url2", 0.5)]
    
    # Ensure os.path.exists returns True for the find command
    with patch('os.path.exists', return_value=True):
        with patch('builtins.print') as mock_print:
            shell.do_find("test query")
            
            # Verify that output contains the URLs and formatted scores
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("url1" in c for c in calls)
            assert any("1.235" in c or "1.234" in c for c in calls)

def test_build_command(shell_setup):
    shell, mock_indexer, _ = shell_setup
    
    # Ensure os.path.exists returns False for this test so it doesn't try to remove
    with patch('os.path.exists', return_value=False), patch('main.Crawler') as MockCrawler:
        MockCrawler.return_value.crawl.return_value = [{'url': 'url1', 'content': 'html'}]
        shell.do_build("")
        
    assert mock_indexer.add_page.called
    assert "url1" in mock_indexer.add_page.call_args[0]
