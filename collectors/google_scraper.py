"""
Google Search Scraper using SerpAPI
"""
import time
from typing import List, Optional
from serpapi import GoogleSearch
from database.models import SearchResult
from config.config import SERPAPI_KEY, SEARCH_KEYWORDS, MAX_RESULTS_PER_KEYWORD, RATE_LIMIT_DELAY


class GoogleScraper:
    """Scrape pharma companies from Google Search using SerpAPI"""
    
    def __init__(self, api_key: str = SERPAPI_KEY):
        self.api_key = api_key
        
    def search(self, query: str, num_results: int = MAX_RESULTS_PER_KEYWORD) -> List[SearchResult]:
        """Execute a single Google search and return results"""
        if not self.api_key:
            print("⚠️  Warning: SERPAPI_KEY not set. Skipping Google search.")
            return []
        
        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": num_results,
                "gl": "in",  # India
                "hl": "en",
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            search_results = []
            organic_results = results.get("organic_results", [])
            
            for item in organic_results:
                search_results.append(SearchResult(
                    title=item.get("title", ""),
                    link=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source="google",
                    keyword_used=query
                ))
            
            return search_results
            
        except Exception as e:
            print(f"⚠️  Google search error for '{query}': {e}")
            return []
    
    def search_all_keywords(self, keywords: Optional[List[str]] = None) -> List[SearchResult]:
        """Search all pharma keywords and aggregate results"""
        if keywords is None:
            keywords = SEARCH_KEYWORDS
        
        all_results = []
        
        for i, keyword in enumerate(keywords):
            print(f"🔍 Searching ({i+1}/{len(keywords)}): {keyword[:50]}...")
            results = self.search(keyword)
            all_results.extend(results)
            print(f"   Found {len(results)} results")
            
            # Rate limiting
            if i < len(keywords) - 1:
                time.sleep(RATE_LIMIT_DELAY)
        
        print(f"✅ Total Google results: {len(all_results)}")
        return all_results
