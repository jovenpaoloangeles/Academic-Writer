"""
DOI utilities for reference management
"""
import re
import requests
from typing import Optional, Dict

def extract_doi(text: str) -> list[str]:
    """Extract DOIs from text using regex."""
    doi_pattern = r'\b(10\.\d{4,}/[-._;()/:\w]+)\b'
    return re.findall(doi_pattern, text)

def fetch_citation(doi: str, format: str = 'bibtex') -> Optional[str]:
    """Fetch citation data for a DOI."""
    url = f'https://doi.org/{doi}'
    headers = {
        'Accept': f'application/{format}',
        'User-Agent': 'Mozilla/5.0 Academic Writing Assistant'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching citation for DOI {doi}: {str(e)}")
    
    return None

def process_references(text: str) -> Dict[str, str]:
    """Process text to extract and fetch citations for all DOIs."""
    dois = extract_doi(text)
    references = {}
    
    for doi in dois:
        citation = fetch_citation(doi)
        if citation:
            references[doi] = citation
            
    return references
