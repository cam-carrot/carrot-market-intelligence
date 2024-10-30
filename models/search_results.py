from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class SearchResult:
    """Individual search result from Serper API."""
    domain: str
    rank: int
    url: str
    title: str
    
@dataclass
class SEOMetrics:
    """SEO metrics from SEMrush API."""
    domain: str
    authority_score: float
    backlink_count: int
    referring_domains: int
    
@dataclass
class DomainAnalysis:
    """Analysis of a single domain's performance."""
    domain: str
    best_rank: int
    appearances: int
    average_rank: float
    terms_found: List[str]
    authority_score: float
    backlink_count: int
    referring_domains: int
    is_ibuyer: bool

@dataclass
class MarketAnalysis:
    """Complete market analysis results."""
    city: str
    state: str
    timestamp: datetime
    search_results: Dict[str, List[SearchResult]]
    seo_metrics: Dict[str, SEOMetrics]
    domain_analysis: Dict[str, DomainAnalysis]
    summary: Dict[str, float]
    chart_data: List[Dict]
    
    @property
    def total_domains(self) -> int:
        """Get total number of unique domains found."""
        domains = set()
        for results in self.search_results.values():
            domains.update(result.domain for result in results)
        return len(domains)
    
    @property
    def ibuyer_ratio(self) -> float:
        """Calculate ratio of iBuyer domains to total domains."""
        ibuyer_count = sum(1 for analysis in self.domain_analysis.values() if analysis.is_ibuyer)
        return ibuyer_count / len(self.domain_analysis) if self.domain_analysis else 0.0
    
    @property
    def average_authority_score(self) -> float:
        """Calculate average authority score across all domains."""
        scores = [metrics.authority_score for metrics in self.seo_metrics.values()]
        return sum(scores) / len(scores) if scores else 0.0
    
    @property
    def top_domains(self) -> List[DomainAnalysis]:
        """Get top 10 domains by best rank."""
        return sorted(
            self.domain_analysis.values(),
            key=lambda x: (x.best_rank, -x.authority_score)
        )[:10]

@dataclass
class ChartDataPoint:
    """Data point for ranking/metrics chart."""
    position: int
    domain: str
    authority_score: float
    backlink_count: int
    referring_domains: int
    is_ibuyer: bool

@dataclass
class SearchTermResults:
    """Results for a specific search term."""
    term: str
    results: List[SearchResult]
    timestamp: datetime
    
    @property
    def ibuyer_count(self) -> int:
        """Count of iBuyer domains in results."""
        from utils.domain_utils import is_ibuyer
        return sum(1 for result in self.results if is_ibuyer(result.domain))
    
    @property
    def average_rank(self) -> Dict[str, float]:
        """Calculate average rank for each domain."""
        domain_ranks = {}
        for result in self.results:
            if result.domain not in domain_ranks:
                domain_ranks[result.domain] = []
            domain_ranks[result.domain].append(result.rank)
        
        return {
            domain: sum(ranks) / len(ranks)
            for domain, ranks in domain_ranks.items()
        }

@dataclass
class MarketMetrics:
    """Summary metrics for a market."""
    total_results: int
    unique_domains: int
    ibuyer_ratio: float
    avg_authority_score: float
    avg_backlinks: float
    top_domains: List[str]
    timestamp: datetime
    
    @classmethod
    def from_analysis(cls, analysis: MarketAnalysis) -> 'MarketMetrics':
        """Create MarketMetrics from a MarketAnalysis object."""
        return cls(
            total_results=sum(len(results) for results in analysis.search_results.values()),
            unique_domains=analysis.total_domains,
            ibuyer_ratio=analysis.ibuyer_ratio,
            avg_authority_score=analysis.average_authority_score,
            avg_backlinks=sum(m.backlink_count for m in analysis.seo_metrics.values()) / len(analysis.seo_metrics) if analysis.seo_metrics else 0,
            top_domains=[d.domain for d in analysis.top_domains],
            timestamp=analysis.timestamp
        )