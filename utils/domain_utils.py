from typing import List
from urllib.parse import urlparse
import tldextract
import logging
from config import IBUYERS

logger = logging.getLogger(__name__)

def extract_base_domain(url: str) -> str:
    """Extract base domain from URL."""
    try:
        # Use tldextract which is more reliable than tld
        extracted = tldextract.extract(url)
        
        # Combine domain and suffix (e.g., example.com)
        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}"
            
        # Fallback to netloc if tldextract fails
        if not extracted.domain:
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
            
        return None
    except Exception as e:
        # Log the error but don't crash
        logger.error(f"Error extracting domain from {url}: {str(e)}")
        try:
            # Last resort fallback
            return urlparse(url).netloc.replace('www.', '')
        except:
            return None

def is_ibuyer(domain: str) -> bool:
    """Check if domain is a known iBuyer."""
    return domain in IBUYERS

def deduplicate_domains(domains: List[str]) -> List[str]:
    """Remove duplicate domains while preserving order."""
    seen = set()
    return [x for x in domains if not (x in seen or seen.add(x))]