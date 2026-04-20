"""
Test suite for data_fetcher module
"""

import pytest
from data_fetcher import AIPapersFetcher


def test_fetcher_initialization():
    """Test that fetcher initializes correctly"""
    fetcher = AIPapersFetcher()
    assert fetcher.base_url is not None
    assert fetcher.cache is not None


def test_get_available_years():
    """Test getting available years"""
    fetcher = AIPapersFetcher()
    years = fetcher.get_available_years()
    
    assert len(years) > 0
    assert "2026" in years


def test_fetch_year_data():
    """Test fetching year data"""
    fetcher = AIPapersFetcher()
    data = fetcher.fetch_year_data("2026")
    
    assert data is not None
    assert isinstance(data, dict)


def test_get_available_weeks():
    """Test getting available weeks for a year"""
    fetcher = AIPapersFetcher()
    weeks = fetcher.get_available_weeks("2026")
    
    assert len(weeks) > 0
    assert isinstance(weeks, list)


def test_parse_year_data():
    """Test parsing year data from markdown"""
    fetcher = AIPapersFetcher()
    
    test_markdown = """
    ## Top AI Papers of the Week (April 6 - April 12) - 2026
    
    | 1) **Test Paper** - This is a test paper
    | [Paper](https://arxiv.org/abs/1234)
    
    ## Top AI Papers of the Week (April 13 - April 19) - 2026
    
    | 2) **Another Paper** - Another test
    """
    
    parsed = fetcher.parse_year_data(test_markdown)
    
    assert len(parsed) == 2
    assert "April 6 - April 12 - 2026" in parsed


def test_extract_week_info():
    """Test extracting week information"""
    fetcher = AIPapersFetcher()
    
    test_content = "## Top AI Papers of the Week (April 6 - April 12) - 2026"
    
    week_info = fetcher.extract_week_info(test_content)
    
    assert week_info is not None
    assert week_info['week'] == "April 6 - April 12 - 2026"
    assert week_info['date_range'] == "April 6 - April 12"
    assert week_info['year'] == "2026"


def test_extract_papers():
    """Test extracting papers from content"""
    fetcher = AIPapersFetcher()
    
    test_content = """
    | 1) **Test Paper One** - This is the first paper
    | [Paper](https://arxiv.org/abs/1234) [Tweet](https://twitter.com/test)
    | 2) **Test Paper Two** - This is the second paper
    | [Paper](https://arxiv.org/abs/5678)
    """
    
    papers = fetcher.extract_papers(test_content)
    
    assert len(papers) == 2
    assert papers[0]['title'] == 'Test Paper One'
    assert papers[1]['title'] == 'Test Paper Two'


def test_extract_links():
    """Test extracting paper and tweet links"""
    fetcher = AIPapersFetcher()
    
    test_content = "Check out this paper [Paper](https://arxiv.org/abs/1234) and tweet [Tweet](https://twitter.com/test)"
    
    links = fetcher.extract_links(test_content)
    
    assert 'paper' in links
    assert links['paper'] == 'https://arxiv.org/abs/1234'
    assert 'tweet' in links
    assert links['tweet'] == 'https://twitter.com/test'


def test_cache_mechanism():
    """Test that caching works"""
    fetcher = AIPapersFetcher()
    
    # First fetch
    data1 = fetcher.fetch_year_data("2026")
    
    # Second fetch (should use cache)
    data2 = fetcher.fetch_year_data("2026")
    
    assert data1 == data2
