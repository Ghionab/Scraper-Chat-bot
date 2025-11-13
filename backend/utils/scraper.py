"""
Web scraping module using Crawl4AI for content extraction.
"""

from crawl4ai import AsyncWebCrawler
import asyncio
from typing import Dict
import re


class WebScraper:
    """
    Web scraper class that uses Crawl4AI to extract content from websites.
    """
    
    def __init__(self):
        """Initialize the WebScraper."""
        pass
    
    async def scrape_url(self, url: str) -> Dict[str, any]:
        """
        Asynchronously scrape a website and extract its content in markdown format.
        
        Args:
            url: The target website URL to scrape
            
        Returns:
            Dictionary containing:
                - success (bool): Whether the scraping was successful
                - content (str): Extracted markdown content
                - title (str): Page title
                - error (str|None): Error message if scraping failed
        """
        # Validate URL format
        if not self._is_valid_url(url):
            return {
                'success': False,
                'content': '',
                'title': '',
                'error': 'Invalid URL format'
            }
        
        try:
            # Create crawler instance
            async with AsyncWebCrawler(verbose=False) as crawler:
                # Run the crawler
                result = await crawler.arun(url=url)
                
                if result.success:
                    return {
                        'success': True,
                        'content': result.markdown or '',
                        'title': result.metadata.get('title', '') if result.metadata else '',
                        'error': None
                    }
                else:
                    return {
                        'success': False,
                        'content': '',
                        'title': '',
                        'error': result.error_message or 'Failed to scrape website'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'content': '',
                'title': '',
                'error': f'Scraping error: {str(e)}'
            }
    
    def scrape_sync(self, url: str) -> Dict[str, any]:
        """
        Synchronous wrapper for the async scrape_url method.
        This is useful for Flask routes that don't support async/await.
        
        Args:
            url: The target website URL to scrape
            
        Returns:
            Dictionary with same structure as scrape_url()
        """
        return asyncio.run(self.scrape_url(url))
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL string to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        # Basic URL pattern validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
