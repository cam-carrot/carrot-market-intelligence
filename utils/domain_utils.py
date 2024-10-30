from typing import List
from urllib.parse import urlparse
import tldextract
import logging
from config import IBUYERS

logger = logging.getLogger(__name__)

def extract_base_domain(url: str) -> str:
    """Extract base domain from URL."""
    try:
        # Force tldextract to not use cache in Heroku environment
        if 'DYNO' in os.environ:
            extracted = tldextract.extract(url, cache_dir=False)
        else:
            extracted = tldextract.extract(url)
        
        # Combine domain and suffix (e.g., example.com)
        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}"
        
        # Fallback to simple parsing if tldextract fails
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        
        # Remove www. and any ports
        domain = domain.replace('www.', '').split(':')[0]
        
        # Remove any paths if they got included
        domain = domain.split('/')[0]
        
        return domain if domain else None
            
    except Exception as e:
        # Log the error but don't crash
        logger.error(f"Error extracting domain from {url}: {str(e)}")
        try:
            # Last resort fallback using basic parsing
            parsed = urlparse(url if '://' in url else f'http://{url}')
            return parsed.netloc.replace('www.', '').split(':')[0]
        except:
            return None

def is_ibuyer(domain: str) -> bool:
    """Check if domain is a known iBuyer."""
    return domain in IBUYERS

def deduplicate_domains(domains: List[str]) -> List[str]:
    """Remove duplicate domains while preserving order."""
    seen = set()
    return [x for x in domains if not (x in seen or seen.add(x))]