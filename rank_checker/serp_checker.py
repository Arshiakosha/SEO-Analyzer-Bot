import requests
import time
from urllib.parse import quote_plus, urlparse
from bs4 import BeautifulSoup
from config import SERPAPI_KEY, USER_AGENT

class RankChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
    
    def check_keyword_rank(self, domain, keyword, country='us', language='en'):
        """Check the rank of a domain for a specific keyword"""
        if SERPAPI_KEY:
            return self._check_with_serpapi(domain, keyword, country, language)
        else:
            return self._check_with_scraping(domain, keyword)
    
    def _check_with_serpapi(self, domain, keyword, country, language):
        """Use SerpAPI for rank checking (if API key available)"""
        try:
            url = "https://serpapi.com/search"
            params = {
                'engine': 'google',
                'q': keyword,
                'gl': country,
                'hl': language,
                'num': 100,  # up to 100 results
                'api_key': SERPAPI_KEY
            }
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                organic_results = data.get('organic_results', [])
                for i, result in enumerate(organic_results, 1):
                    result_domain = urlparse(result.get('link', '')).netloc
                    if domain.lower() in result_domain.lower():
                        return {
                            'keyword': keyword,
                            'domain': domain,
                            'rank': i,
                            'url': result.get('link'),
                            'title': result.get('title'),
                            'snippet': result.get('snippet'),
                            'method': 'serpapi'
                        }
                return {
                    'keyword': keyword,
                    'domain': domain,
                    'rank': None,
                    'message': 'Not found in top 100 results',
                    'method': 'serpapi'
                }
            else:
                return {
                    'keyword': keyword,
                    'domain': domain,
                    'rank': None,
                    'error': f'API Error: {response.status_code}',
                    'method': 'serpapi'
                }
        except Exception as e:
            return {
                'keyword': keyword,
                'domain': domain,
                'rank': None,
                'error': str(e),
                'method': 'serpapi'
            }
    
    def _check_with_scraping(self, domain, keyword):
        """Scrape Google search results (free method)"""
        try:
            search_url = f"https://www.google.com/search?q={quote_plus(keyword)}&num=50"
            headers = {
                'User-Agent': USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            response = requests.get(search_url, headers=headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                search_results = soup.find_all('div', class_='g')
                for i, result in enumerate(search_results, 1):
                    link_elem = result.find('a')
                    if link_elem and link_elem.get('href'):
                        result_url = link_elem['href']
                        result_domain = urlparse(result_url).netloc
                        if domain.lower() in result_domain.lower():
                            title_elem = result.find('h3')
                            title = title_elem.get_text() if title_elem else 'No title'
                            snippet_elem = result.find('span', {'class': ['st', 'aCOpRe']})
                            snippet = snippet_elem.get_text() if snippet_elem else 'No snippet'
                            return {
                                'keyword': keyword,
                                'domain': domain,
                                'rank': i,
                                'url': result_url,
                                'title': title,
                                'snippet': snippet,
                                'method': 'scraping'
                            }
                return {
                    'keyword': keyword,
                    'domain': domain,
                    'rank': None,
                    'message': f'Not found in top {len(search_results)} results',
                    'method': 'scraping'
                }
            else:
                return {
                    'keyword': keyword,
                    'domain': domain,
                    'rank': None,
                    'error': f'HTTP Error: {response.status_code}',
                    'method': 'scraping'
                }
        except Exception as e:
            return {
                'keyword': keyword,
                'domain': domain,
                'rank': None,
                'error': str(e),
                'method': 'scraping'
            }
    
    def check_multiple_keywords(self, domain, keywords):
        """Check ranks for multiple keywords"""
        results = []
        for keyword in keywords:
            result = self.check_keyword_rank(domain, keyword)
            results.append(result)
            time.sleep(2)  # Respectful delay
        return results
    
    def get_rank_summary(self, rank_results):
        total_keywords = len(rank_results)
        ranked_keywords = [r for r in rank_results if r.get('rank')]
        top_10_ranks = [r for r in ranked_keywords if r['rank'] <= 10]
        top_50_ranks = [r for r in ranked_keywords if r['rank'] <= 50]
        summary = {
            'total_keywords': total_keywords,
            'ranked_keywords': len(ranked_keywords),
            'not_ranked': total_keywords - len(ranked_keywords),
            'top_10_positions': len(top_10_ranks),
            'top_50_positions': len(top_50_ranks),
            'average_rank': round(sum(r['rank'] for r in ranked_keywords) / len(ranked_keywords), 1) if ranked_keywords else None,
            'best_rank': min(r['rank'] for r in ranked_keywords) if ranked_keywords else None,
            'worst_rank': max(r['rank'] for r in ranked_keywords) if ranked_keywords else None
        }
        return summary