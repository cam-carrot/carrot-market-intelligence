from typing import List
from urllib.parse import urlparse
import tld
from tld.utils import update_tld_names
import logging
from config import IBUYERS

logger = logging.getLogger(__name__)

def extract_base_domain(url: str) -> str:
    """Extract base domain from URL."""
    try:
        # Update the TLD database
        update_tld_names()
        
        # Parse the URL
        parsed = urlparse(url)
        if not parsed.netloc:
            return None
            
        # Extract the domain using tld
        res = tld.get_tld(url, as_object=True, fail_silently=True)
        if not res:
            return parsed.netloc
            
        return res.fld
    except Exception as e:
        # Log the error but return a fallback
        logger.error(f"Error extracting domain from {url}: {str(e)}")
        try:
            # Fallback to simple domain extraction
            return urlparse(url).netloc.split(':')[0]
        except:
            return None

def is_ibuyer(domain: str) -> bool:
    """Check if domain is a known iBuyer."""
    return domain in IBUYERS

def deduplicate_domains(domains: List[str]) -> List[str]:
    """Remove duplicate domains while preserving order."""
    seen = set()
    return [x for x in domains if not (x in seen or seen.add(x))]