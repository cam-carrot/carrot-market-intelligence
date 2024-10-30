from typing import Dict, List, Any
import logging
from utils.domain_utils import extract_base_domain, is_ibuyer, deduplicate_domains

class DomainService:
    """Service for analyzing domains and search rankings."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_search_results(self, search_results: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Analyze search results for domain patterns and rankings.
        
        Args:
            search_results: Dictionary of search terms and their results
            
        Returns:
            Dict containing analysis including ibuyer ratio, rankings, etc.
        """
        all_domains = []
        for term, results in search_results.items():
            all_domains.extend(results)
        
        unique_domains = deduplicate_domains(all_domains)
        ibuyer_count = sum(1 for domain in unique_domains if is_ibuyer(domain))
        
        return {
            'total_domains': len(all_domains),
            'unique_domains': len(unique_domains),
            'ibuyer_ratio': ibuyer_count / len(unique_domains) if unique_domains else 0,
            'rankings': self._analyze_rankings(search_results)
        }

    def _analyze_rankings(self, search_results: Dict[str, List[str]]) -> Dict[str, Dict[str, float]]:
        """
        Analyze domain rankings across different search terms.
        
        Args:
            search_results: Dictionary of search terms and their results
            
        Returns:
            Dict containing ranking analysis for each domain
        """
        rankings = {}
        for term, domains in search_results.items():
            for rank, domain in enumerate(domains, 1):
                base_domain = extract_base_domain(domain)
                if base_domain not in rankings:
                    rankings[base_domain] = {
                        'best_rank': rank,
                        'appearances': 1,
                        'average_rank': rank
                    }
                else:
                    stats = rankings[base_domain]
                    stats['best_rank'] = min(stats['best_rank'], rank)
                    stats['appearances'] += 1
                    stats['average_rank'] = (
                        (stats['average_rank'] * (stats['appearances'] - 1) + rank) 
                        / stats['appearances']
                    )
        
        return rankings