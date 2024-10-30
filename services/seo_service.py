import httpx
import logging
from typing import Dict, Optional, List, Set
import asyncio
import csv
from io import StringIO
from datetime import datetime, timedelta

from config import SEMRUSH_API_KEY
from models import SEOMetrics
from utils.domain_utils import extract_base_domain

class SEOService:
    """Service for handling SEMrush API interactions and SEO metrics."""
    
    def __init__(self):
        self.api_key = SEMRUSH_API_KEY
        self.base_url = "https://api.semrush.com"
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_duration = timedelta(hours=24)
        self._request_semaphore = asyncio.Semaphore(5)
        
    async def get_domain_metrics(self, domain: str) -> Optional[SEOMetrics]:
        """Get SEO metrics for a single domain using SEMrush Backlinks API."""
        try:
            # Check cache first
            cache_key = f"metrics_{domain}"
            cached = self._get_from_cache(cache_key)
            if cached:
                self.logger.debug(f"Cache hit for domain: {domain}")
                return cached

            # Clean domain
            domain = extract_base_domain(domain)
            if not domain:
                self.logger.error(f"Failed to extract base domain from: {domain}")
                return None

            # Parameters for backlinks API
            params = {
                "key": self.api_key,
                "target": f"{domain}",  # No protocol needed
                "type": "backlinks_overview",
                "target_type": "root_domain",
                "display_date": "latest",
                "export_columns": "target,ascore,total,domains_num",
                "display_limit": 1,
                "database": "us"
            }
            
            self.logger.debug(f"Making SEMrush API request for domain: {domain}")
            
            async with self._request_semaphore:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/analytics/v1/",
                        params=params,
                        timeout=30.0
                    )
                    
                    # Log full request URL for debugging (remove sensitive info)
                    debug_url = str(response.url).replace(self.api_key, 'API_KEY')
                    self.logger.debug(f"SEMrush API URL: {debug_url}")
                    
                    if response.status_code != 200:
                        self.logger.error(f"SEMrush API error: {response.status_code} - {response.text}")
                        return None
                    
                    # Log raw response for debugging
                    self.logger.debug(f"Raw response: {response.text}")
                    
                    try:
                        # Parse CSV response
                        csv_data = StringIO(response.text)
                        reader = csv.reader(csv_data, delimiter=';')
                        header = next(reader)  # Skip header
                        self.logger.debug(f"CSV Headers: {header}")
                        
                        row = next(reader)
                        self.logger.debug(f"Data row: {row}")
                        
                        # Create metrics object
                        metrics = SEOMetrics(
                            domain=domain,
                            authority_score=float(row[1]) if row[1] and row[1] != "none" else 0.0,
                            backlink_count=int(row[2]) if row[2] and row[2] != "none" else 0,
                            referring_domains=int(row[3]) if row[3] and row[3] != "none" else 0
                        )
                        
                        # Cache the result
                        self._add_to_cache(cache_key, metrics)
                        self.logger.debug(f"Successfully got metrics for {domain}: {metrics}")
                        return metrics
                        
                    except (IndexError, ValueError) as e:
                        self.logger.error(f"Error parsing SEMrush data for {domain}: {str(e)}")
                        return None

        except httpx.RequestError as e:
            self.logger.error(f"SEMrush API request error for {domain}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error for {domain}: {str(e)}")
            return None

    async def get_bulk_metrics(self, domains: Set[str]) -> Dict[str, SEOMetrics]:
        """Get SEO metrics for multiple domains efficiently."""
        results = {}
        total_domains = len(domains)
        processed = 0
        
        # Process domains in smaller chunks
        chunk_size = 5
        domains_list = list(domains)
        
        for i in range(0, len(domains_list), chunk_size):
            chunk = domains_list[i:i + chunk_size]
            chunk_tasks = []
            
            for domain in chunk:
                chunk_tasks.append(self.get_domain_metrics(domain))
            
            # Process chunk
            chunk_results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
            
            # Handle results
            for domain, result in zip(chunk, chunk_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Error processing {domain}: {str(result)}")
                elif result is not None:
                    results[domain] = result
                
                processed += 1
                self.logger.info(f"Processed {processed}/{total_domains} domains")
            
            # Add delay between chunks
            if i + chunk_size < len(domains_list):
                await asyncio.sleep(1)
        
        self.logger.info(f"Completed bulk metrics fetch. Got {len(results)} results out of {total_domains} domains")
        return results

    def _get_from_cache(self, key: str) -> Optional[SEOMetrics]:
        """Get metrics from cache if still valid."""
        if key in self.cache:
            timestamp, value = self.cache[key]
            if datetime.now() - timestamp < self.cache_duration:
                return value
            del self.cache[key]
        return None

    def _add_to_cache(self, key: str, value: SEOMetrics):
        """Add metrics to cache with timestamp."""
        self.cache[key] = (datetime.now(), value)

    def clear_cache(self):
        """Clear the metrics cache."""
        self.cache.clear()