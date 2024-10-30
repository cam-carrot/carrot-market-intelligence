from typing import List
from urllib.parse import urlparse
import tldextract
import logging
from config import IBUYERS

logger = logging.getLogger(__name__)

def extract_base_domain(url: str) -> str:
    """Extract base domain from URL."""
    try:
        ext = tldextract.extract(url)
        return f"{ext.domain}.{ext.suffix}"
    except Exception as e:
        logger.error(f"Error extracting base domain from {url}: {str(e)}")
        return ""

def is_ibuyer(domain: str) -> bool:
    """Check if domain is a known iBuyer."""
    return domain in IBUYERS

def deduplicate_domains(domains: List[str]) -> List[str]:
    """Remove duplicate domains while preserving order."""
    seen = set()
    return [x for x in domains if not (x in seen or seen.add(x))]