import logging
from typing import Dict, List, Optional, Set
from datetime import datetime
import asyncio
from collections import defaultdict

from services.search_service import SearchService
from services.seo_service import SEOService
from models import MarketMetrics, SearchResult, SEOMetrics
from utils.domain_utils import extract_base_domain, deduplicate_domains, is_ibuyer

class SearchEngine:
    """Coordinates search and SEO analysis for market research."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.search_service = SearchService()
        self.seo_service = SEOService()

    async def analyze_market(self, city: str, state: str) -> Dict:
        """
        Perform comprehensive market analysis including search rankings and SEO metrics.
        
        Args:
            city: Target city name
            state: Target state code
            
        Returns:
            Dictionary containing complete market analysis
        """
        try:
            self.logger.info(f"Starting market analysis for {city}, {state}")
            
            # Step 1: Get search results
            search_results = await self.search_service.get_all_search_terms(city, state)
            if not search_results:
                raise ValueError(f"No search results found for {city}, {state}")
            
            self.logger.info(f"Retrieved search results for {len(search_results)} terms")
            
            # Step 2: Extract and process domains
            unique_domains = self._extract_unique_domains(search_results)
            self.logger.info(f"Found {len(unique_domains)} unique domains")
            
            # Step 3: Get SEO metrics
            seo_metrics = await self.seo_service.get_bulk_metrics(unique_domains)
            self.logger.info(f"Retrieved SEO metrics for {len(seo_metrics)} domains")
            
            # Step 4: Calculate various metrics
            ibuyer_metrics = self._calculate_ibuyer_metrics(unique_domains)
            ranking_analysis = self._analyze_rankings(search_results, seo_metrics)
            domain_performance = self._analyze_domain_performance(search_results, seo_metrics)
            
            # Step 5: Prepare chart data
            chart_data = self._prepare_chart_data(search_results.get("we buy houses", []), seo_metrics)
            
            # Step 6: Compile complete analysis
            analysis = {
                'timestamp': datetime.now(),
                'market': {
                    'city': city,
                    'state': state
                },
                'search_results': search_results,
                'seo_metrics': seo_metrics,
                'ibuyer_metrics': ibuyer_metrics,
                'ranking_analysis': ranking_analysis,
                'domain_performance': domain_performance,
                'chart_data': chart_data,
                'summary': self._create_summary(
                    unique_domains,
                    ibuyer_metrics,
                    seo_metrics,
                    domain_performance
                )
            }
            
            self.logger.info("Market analysis completed successfully")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in market analysis: {str(e)}")
            raise

    def _extract_unique_domains(self, search_results: Dict[str, List[SearchResult]]) -> Set[str]:
        """Extract and deduplicate domains from search results."""
        domains = set()
        for results in search_results.values():
            domains.update(result.domain for result in results)
        return domains

    def _calculate_ibuyer_metrics(self, domains: Set[str]) -> Dict:
        """Calculate ibuyer-related metrics."""
        ibuyer_domains = {d for d in domains if is_ibuyer(d)}
        return {
            'count': len(ibuyer_domains),
            'ratio': len(ibuyer_domains) / len(domains) if domains else 0,
            'domains': list(ibuyer_domains)
        }

    def _analyze_rankings(self, search_results: Dict[str, List[SearchResult]], 
                         seo_metrics: Dict[str, SEOMetrics]) -> Dict:
        """Analyze rankings across all search terms."""
        rankings = {}
        
        for term, results in search_results.items():
            for rank, result in enumerate(results, 1):
                domain = result.domain
                metrics = seo_metrics.get(domain)
                
                if domain not in rankings:
                    rankings[domain] = {
                        'best_rank': rank,
                        'appearances': 1,
                        'terms': [term],
                        'average_rank': rank,
                        'authority_score': metrics.authority_score if metrics else 0,
                        'backlink_count': metrics.backlink_count if metrics else 0,
                        'referring_domains': metrics.referring_domains if metrics else 0,
                        'is_ibuyer': is_ibuyer(domain),
                        'positions': {term: rank}
                    }
                else:
                    stats = rankings[domain]
                    stats['best_rank'] = min(stats['best_rank'], rank)
                    stats['appearances'] += 1
                    stats['terms'].append(term)
                    stats['average_rank'] = (
                        (stats['average_rank'] * (stats['appearances'] - 1) + rank) 
                        / stats['appearances']
                    )
                    stats['positions'][term] = rank
        
        return rankings

    def _analyze_domain_performance(self, search_results: Dict[str, List[SearchResult]], 
                                  seo_metrics: Dict[str, SEOMetrics]) -> Dict:
        """Analyze detailed domain performance metrics."""
        performance = defaultdict(lambda: {
            'visibility_score': 0,
            'rank_points': 0,
            'total_appearances': 0,
            'average_position': 0,
            'term_coverage': 0,
            'authority_score': 0,
            'backlink_strength': 0
        })
        
        # Calculate base metrics
        for term, results in search_results.items():
            for rank, result in enumerate(results, 1):
                domain = result.domain
                metrics = seo_metrics.get(domain)
                
                perf = performance[domain]
                perf['total_appearances'] += 1
                perf['rank_points'] += (11 - rank)  # Higher points for better ranks
                perf['average_position'] = (
                    (perf['average_position'] * (perf['total_appearances'] - 1) + rank)
                    / perf['total_appearances']
                )
                
                if metrics:
                    perf['authority_score'] = metrics.authority_score
                    perf['backlink_strength'] = metrics.backlink_count
        
        # Calculate derived metrics
        total_terms = len(search_results)
        for domain, perf in performance.items():
            perf['term_coverage'] = perf['total_appearances'] / total_terms
            perf['visibility_score'] = (
                (perf['rank_points'] / perf['total_appearances']) * 
                perf['term_coverage'] * 
                (perf['authority_score'] / 100)
            )
        
        return dict(performance)

    def _prepare_chart_data(self, results: List[SearchResult], 
                           seo_metrics: Dict[str, SEOMetrics]) -> List[Dict]:
        """Prepare data for ranking/metrics chart."""
        chart_data = []
        
        for result in results[:10]:  # Top 10 only
            metrics = seo_metrics.get(result.domain)
            if metrics:
                chart_data.append({
                    'position': result.rank,
                    'domain': result.domain,
                    'authority_score': metrics.authority_score,
                    'backlink_count': metrics.backlink_count,
                    'referring_domains': metrics.referring_domains,
                    'is_ibuyer': is_ibuyer(result.domain)
                })
            
        return chart_data

    def _create_summary(self, unique_domains: Set[str], 
                       ibuyer_metrics: Dict, 
                       seo_metrics: Dict[str, SEOMetrics],
                       domain_performance: Dict) -> Dict:
        """Create summary metrics for the market analysis."""
        return {
            'total_domains': len(unique_domains),
            'ibuyer_ratio': ibuyer_metrics['ratio'],
            'ibuyer_count': ibuyer_metrics['count'],
            'investor_count': len(unique_domains) - ibuyer_metrics['count'],
            'avg_authority_score': self._calculate_avg_authority(seo_metrics),
            'avg_backlinks': self._calculate_avg_backlinks(seo_metrics),
            'top_performers': sorted(
                domain_performance.items(),
                key=lambda x: x[1]['visibility_score'],
                reverse=True
            )[:5]
        }

    def _calculate_avg_authority(self, seo_metrics: Dict[str, SEOMetrics]) -> float:
        """Calculate average authority score."""
        scores = [m.authority_score for m in seo_metrics.values()]
        return sum(scores) / len(scores) if scores else 0

    def _calculate_avg_backlinks(self, seo_metrics: Dict[str, SEOMetrics]) -> float:
        """Calculate average backlink count."""
        backlinks = [m.backlink_count for m in seo_metrics.values()]
        return sum(backlinks) / len(backlinks) if backlinks else 0