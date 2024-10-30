import httpx
import logging
import asyncio
from typing import List, Dict, Optional
from models import SearchResult
from utils.domain_utils import extract_base_domain
from config import SERPER_API_KEY

class SearchService:
    """Service for handling Serper.dev API interactions."""
    
    def __init__(self):
        self.api_key = SERPER_API_KEY
        self.base_url = "https://google.serper.dev/search"
        self.logger = logging.getLogger(__name__)
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        self._request_semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
        
        # Define search terms
        self.search_terms = [
            "we buy houses",
            "sell my house fast",
            "sell my house fast for cash"
        ]

    async def get_search_results(self, search_term: str, city: str, state: str) -> List[SearchResult]:
        """
        Get search results for a specific term in a location.
        
        Args:
            search_term: The search query
            city: Target city
            state: Target state
            
        Returns:
            List of SearchResult objects
        """
        try:
            location = f"{city}, {state}"
            payload = {
                "q": f"{search_term} {location}",
                "num": 10,
                "gl": "us",
                "hl": "en",
                "autocorrect": True
            }
            
            self.logger.debug(f"Making Serper request for '{search_term}' in {location}")
            
            async with self._request_semaphore:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.base_url,
                        headers=self.headers,
                        json=payload,
                        timeout=30.0
                    )
                    
                    # Log response status
                    self.logger.debug(f"Serper API response status: {response.status_code}")
                    
                    if response.status_code != 200:
                        self.logger.error(f"Serper API error: {response.status_code} - {response.text}")
                        return []
                    
                    data = response.json()
                    organic_results = data.get('organic', [])
                    
                    if not organic_results:
                        self.logger.warning(f"No organic results found for '{search_term}' in {location}")
                        return []
                    
                    results = []
                    for rank, result in enumerate(organic_results, 1):
                        url = result.get('link', '')
                        if not url:
                            continue
                            
                        domain = extract_base_domain(url)
                        if domain:
                            search_result = SearchResult(
                                domain=domain,
                                rank=rank,
                                url=url,
                                title=result.get('title', '')
                            )
                            results.append(search_result)
                            self.logger.debug(f"Found result: Rank {rank} - {domain}")
                    
                    self.logger.info(f"Retrieved {len(results)} results for '{search_term}' in {location}")
                    return results
                
        except httpx.RequestError as e:
            self.logger.error(f"Serper API request error for '{search_term}' in {location}: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error getting search results for '{search_term}' in {location}: {str(e)}")
            return []

    async def get_all_search_terms(self, city: str, state: str) -> Dict[str, List[SearchResult]]:
        """
        Get results for all predefined search terms.
        
        Args:
            city: Target city
            state: Target state
            
        Returns:
            Dictionary mapping search terms to their results
        """
        try:
            self.logger.info(f"Starting search term analysis for {city}, {state}")
            
            results = {}
            total_terms = len(self.search_terms)
            
            for idx, term in enumerate(self.search_terms, 1):
                self.logger.info(f"Processing term {idx}/{total_terms}: '{term}'")
                
                term_results = await self.get_search_results(term, city, state)
                if term_results:
                    results[term] = term_results
                else:
                    self.logger.warning(f"No results found for term: '{term}'")
                
                if idx < total_terms:  # Don't sleep after the last term
                    await asyncio.sleep(1)  # Rate limiting
            
            self.logger.info(f"Completed search term analysis. Found results for {len(results)}/{total_terms} terms")
            
            # Log summary of results
            for term, term_results in results.items():
                self.logger.info(f"Term '{term}': {len(term_results)} results")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in get_all_search_terms for {city}, {state}: {str(e)}")
            raise

    def _clean_search_term(self, term: str, location: str) -> str:
        """Clean and format search term with location."""
        cleaned_term = term.strip().lower()
        cleaned_location = location.strip()
        return f"{cleaned_term} {cleaned_location}".strip()