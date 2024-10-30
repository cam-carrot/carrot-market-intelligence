from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SearchResult:
    domain: str
    rank: int
    url: str
    title: str
    
@dataclass
class SEOMetrics:
    domain: str
    authority_score: float
    backlink_count: int
    referring_domains: int

@dataclass
class MarketMetrics:
    search_results: List[SearchResult]
    seo_metrics: Dict[str, SEOMetrics]
    ibuyer_ratio: float

__all__ = ['SearchResult', 'SEOMetrics', 'MarketMetrics']