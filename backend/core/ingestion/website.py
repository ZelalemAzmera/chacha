import httpx
from bs4 import BeautifulSoup

def extract_text_from_website(url: str) -> str:
    """
    Fetches a webpage and extracts clean text from it.
    """
    try:
        response = httpx.get(url, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(["script", "style", "header", "footer", "nav"]):
            script_or_style.decompose()
            
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        print(f"Error scraping website {url}: {e}")
        return ""
