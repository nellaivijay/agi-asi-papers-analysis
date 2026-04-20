"""
Data Fetcher Module for AI-Papers-of-the-Week
Fetches weekly reports from the AI-Papers-of-the-Week GitHub repository
"""

import requests
import re
from datetime import datetime
import json
from typing import Dict, List, Optional


class AIPapersFetcher:
    """Fetch and parse weekly AI papers reports from AI-Papers-of-the-Week"""
    
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/dair-ai/AI-Papers-of-the-Week/main/years"
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
    
    def fetch_year_data(self, year: str) -> Optional[Dict]:
        """Fetch all weekly reports for a given year"""
        cache_key = f"year_{year}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                return cached_data
        
        # Fetch from GitHub
        url = f"{self.base_url}/{year}.md"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                parsed_data = self.parse_year_data(response.text)
                self.cache[cache_key] = (parsed_data, datetime.now())
                return parsed_data
            else:
                print(f"Failed to fetch data for {year}: Status {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching data for {year}: {e}")
            return None
    
    def parse_year_data(self, markdown_content: str) -> Dict:
        """Parse yearly markdown into weekly paper data"""
        # Split by weekly sections
        sections = re.split(r'## Top AI Papers of the Week', markdown_content)
        
        weekly_data = {}
        
        for section in sections[1:]:  # Skip first empty section
            week_info = self.extract_week_info(section)
            if week_info:
                papers = self.extract_papers(section)
                weekly_data[week_info['week']] = {
                    'date_range': week_info['date_range'],
                    'papers': papers,
                    'total_papers': len(papers)
                }
        
        return weekly_data
    
    def extract_week_info(self, content: str) -> Optional[Dict]:
        """Extract week and date range from content"""
        # Pattern: "Top AI Papers of the Week (April 6 - April 12) - 2026"
        pattern = r'\(([^)]+)\)\s*-\s*(\d{4})'
        match = re.search(pattern, content)
        
        if match:
            date_range = match.group(1)
            year = match.group(2)
            week_key = f"{date_range} - {year}"
            
            return {
                'week': week_key,
                'date_range': date_range,
                'year': year
            }
        
        return None
    
    def extract_papers(self, content: str) -> List[Dict]:
        """Extract individual papers from weekly content"""
        papers = []
        
        # The AI-Papers-of-the-Week format uses table format with paper titles
        # Pattern: "| 1) **Paper Title** - Description | [Paper](url), [Tweet](url) |"
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check if this is a paper entry (starts with |, number, ), **)
            paper_match = re.match(r'^\|?\s*\d+\)\s*\*\*(.+?)\*\*', line)
            if paper_match:
                # Extract title
                title = paper_match.group(1).strip()
                
                # Extract the full paper content (everything between the ** and the | before links)
                # Pattern: "**Title** - Description... | [Paper](url), [Tweet](url) |"
                content_match = re.search(r'\*\*.+?\*\*\s*(.+?)\s*\|', line)
                if content_match:
                    summary = content_match.group(1).strip()
                else:
                    summary = line
                
                # Extract links from the end of the line
                paper_link = ''
                tweet_link = ''
                
                paper_match = re.search(r'\[Paper\]\(([^)]+)\)', line)
                if paper_match:
                    paper_link = paper_match.group(1)
                
                tweet_match = re.search(r'\[Tweet\]\(([^)]+)\)', line)
                if tweet_match:
                    tweet_link = tweet_match.group(1)
                
                paper = {
                    'title': title,
                    'summary': summary,
                    'links': {
                        'paper': paper_link,
                        'tweet': tweet_link
                    },
                    'full_entry': line
                }
                papers.append(paper)
        
        return papers
    
    def parse_paper_entry(self, entry: str) -> Optional[Dict]:
        """Parse individual paper entry"""
        try:
            # Extract title (first line before first dash)
            lines = entry.strip().split('\n')
            title_line = lines[0].strip()
            title = title_line.split('-')[0].strip()
            
            # Extract description/summary
            summary = ' '.join(lines[1:]).strip()
            
            # Extract links (Paper, Tweet, etc.)
            links = self.extract_links(entry)
            
            return {
                'title': title,
                'summary': summary,
                'links': links,
                'full_entry': entry.strip()
            }
        except Exception as e:
            print(f"Error parsing paper entry: {e}")
            return None
    
    def extract_links(self, content: str) -> Dict[str, str]:
        """Extract paper and tweet links"""
        links = {}
        
        # Extract paper links
        paper_match = re.search(r'\[Paper\]\(([^)]+)\)', content)
        if paper_match:
            links['paper'] = paper_match.group(1)
        
        # Extract tweet links
        tweet_match = re.search(r'\[Tweet\]\(([^)]+)\)', content)
        if tweet_match:
            links['tweet'] = tweet_match.group(1)
        
        return links
    
    def get_available_years(self) -> List[str]:
        """Get list of available years"""
        return ["2026", "2025", "2024", "2023"]
    
    def get_available_weeks(self, year: str) -> List[str]:
        """Get list of available weeks for a given year"""
        year_data = self.fetch_year_data(year)
        if year_data:
            return list(year_data.keys())
        return []
    
    def fetch_all_years(self) -> Dict:
        """Fetch data for all available years"""
        all_data = {}
        for year in self.get_available_years():
            year_data = self.fetch_year_data(year)
            if year_data:
                all_data[year] = year_data
        return all_data


# Test the fetcher
if __name__ == "__main__":
    fetcher = AIPapersFetcher()
    
    # Test fetching 2026 data
    print("Testing data fetcher...")
    data_2026 = fetcher.fetch_year_data("2026")
    
    if data_2026:
        print(f"Successfully fetched {len(data_2026)} weeks from 2026")
        for week, info in list(data_2026.items())[:2]:  # Show first 2 weeks
            print(f"\nWeek: {week}")
            print(f"Papers: {info['total_papers']}")
            if info['papers']:
                print(f"First paper: {info['papers'][0]['title'][:50]}...")
    else:
        print("Failed to fetch data")