"""
Directory Scraper using SerpAPI site: searches
Scrapes IndiaMART, TradeIndia, and PharmaBiz via Google site: operator
"""
import time
from typing import List
from serpapi import GoogleSearch
from database.models import SearchResult
from config.config import SERPAPI_KEY, DIRECTORY_SITES, MAX_RESULTS_PER_DIRECTORY, RATE_LIMIT_DELAY


class DirectoryScraper:
    """Scrape pharma directories using SerpAPI site: searches"""
    
    def __init__(self, api_key: str = SERPAPI_KEY):
        self.api_key = api_key
        
    def search_site(self, site: str, query: str = "pharma manufacturing", 
                    num_results: int = MAX_RESULTS_PER_DIRECTORY) -> List[SearchResult]:
        """Search within a specific site using site: operator"""
        if not self.api_key:
            print("⚠️  Warning: SERPAPI_KEY not set. Skipping directory search.")
            return []
        
        try:
            full_query = f"site:{site} {query}"
            
            params = {
                "q": full_query,
                "api_key": self.api_key,
                "num": num_results,
                "gl": "in",
                "hl": "en",
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            search_results = []
            organic_results = results.get("organic_results", [])
            
            # Determine source name from site
            source = site.replace(".com", "").replace("www.", "")
            
            for item in organic_results:
                search_results.append(SearchResult(
                    title=item.get("title", ""),
                    link=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source=source,
                    keyword_used=full_query
                ))
            
            return search_results
            
        except Exception as e:
            print(f"⚠️  Directory search error for '{site}': {e}")
            return []
    
    def search_all_directories(self, sites: List[str] = None) -> List[SearchResult]:
        """Search all pharma directories and aggregate results"""
        if sites is None:
            sites = DIRECTORY_SITES
        
        # Pharma-specific search queries for directories
        directory_queries = [
            "pharma third party manufacturing",
            "loan license pharmaceutical",
            "pharma marketing company",
            "contract manufacturing pharma",
        ]
        
        all_results = []
        
        for site in sites:
            print(f"📂 Scraping directory: {site}")
            
            for query in directory_queries:
                results = self.search_site(site, query)
                all_results.extend(results)
                time.sleep(RATE_LIMIT_DELAY)
            
            print(f"   Found {len([r for r in all_results if site.replace('.com', '') in r.source])} results from {site}")
        
        print(f"✅ Total directory results: {len(all_results)}")
        return all_results
