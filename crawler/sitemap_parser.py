import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
import time
from config import DEFAULT_CRAWL_LIMIT, DEFAULT_TIMEOUT, USER_AGENT

class WebsiteCrawler:
    def __init__(self, base_url, crawl_limit=DEFAULT_CRAWL_LIMIT):
        self.base_url = base_url.rstrip('/')
        self.crawl_limit = crawl_limit
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        
    def get_sitemap_urls(self):
        """Extract URLs from sitemap.xml"""
        sitemap_urls = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/sitemap_index.xml",
            f"{self.base_url}/robots.txt"
        ]
        
        urls = []
        
        for sitemap_url in sitemap_urls:
            try:
                response = self.session.get(sitemap_url, timeout=DEFAULT_TIMEOUT)
                if response.status_code == 200:
                    if 'sitemap.xml' in sitemap_url:
                        urls.extend(self._parse_sitemap(response.text))
                    elif 'robots.txt' in sitemap_url:
                        sitemap_from_robots = self._extract_sitemap_from_robots(response.text)
                        if sitemap_from_robots:
                            for sm_url in sitemap_from_robots:
                                sm_response = self.session.get(sm_url, timeout=DEFAULT_TIMEOUT)
                                if sm_response.status_code == 200:
                                    urls.extend(self._parse_sitemap(sm_response.text))
                    break
            except Exception as e:
                print(f"Could not fetch {sitemap_url}: {e}")
                continue
                
        return urls[:self.crawl_limit] if urls else []
    
    def _parse_sitemap(self, xml_content):
        """Parse sitemap XML and extract URLs"""
        urls = []
        try:
            root = ET.fromstring(xml_content)
            # Handle different sitemap namespaces
            for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None:
                    urls.append(loc_elem.text)
            
            # If no URLs found, try without namespace
            if not urls:
                for url_elem in root.findall('.//url'):
                    loc_elem = url_elem.find('loc')
                    if loc_elem is not None:
                        urls.append(loc_elem.text)
                        
        except ET.ParseError as e:
            print(f"Error parsing sitemap XML: {e}")
            
        return urls
    
    def _extract_sitemap_from_robots(self, robots_content):
        """Extract sitemap URLs from robots.txt"""
        sitemaps = []
        for line in robots_content.split('\n'):
            if line.lower().startswith('sitemap:'):
                sitemap_url = line.split(':', 1)[1].strip()
                sitemaps.append(sitemap_url)
        return sitemaps
    
    def crawl_pages_manual(self):
        """Manually crawl pages if no sitemap is available"""
        urls_to_crawl = [self.base_url]
        crawled_urls = set()
        page_data = []
        
        while urls_to_crawl and len(crawled_urls) < self.crawl_limit:
            current_url = urls_to_crawl.pop(0)
            
            if current_url in crawled_urls:
                continue
                
            try:
                response = self.session.get(current_url, timeout=DEFAULT_TIMEOUT)
                if response.status_code == 200:
                    crawled_urls.add(current_url)
                    
                    # Parse the page
                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_info = self._extract_page_data(current_url, soup, response.text)
                    page_data.append(page_info)
                    
                    # Find more internal links (limit to avoid infinite crawling)
                    if len(crawled_urls) < self.crawl_limit:
                        internal_links = self._extract_internal_links(soup, current_url)
                        for link in internal_links[:3]:  # Only add 3 links per page
                            if link not in crawled_urls and link not in urls_to_crawl:
                                urls_to_crawl.append(link)
                
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                print(f"Error crawling {current_url}: {e}")
                
        return page_data
    
    def get_page_data(self, urls):
        """Fetch and parse page data for given URLs"""
        page_data = []
        
        for url in urls:
            try:
                response = self.session.get(url, timeout=DEFAULT_TIMEOUT)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_info = self._extract_page_data(url, soup, response.text)
                    # --- Always wrap in {'url':..., 'seo_data':...} for compatibility ---
                    page_data.append({
                        "url": url,
                        "seo_data": {
                            "title": page_info.get("title") or "",
                            "meta_description": page_info.get("meta_description") or "",
                            "h1_tags": page_info.get("h1_tags") or [],
                            "word_count": page_info.get("word_count") or 0,
                        },
                        "raw_html": page_info.get("raw_html", ""),
                        # Optionally you can add more, but these are the main ones used in your dashboard
                    })
                else:
                    print(f"Failed to fetch {url}: Status {response.status_code}")
                    
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                
        return page_data
    
    def _extract_page_data(self, url, soup, raw_html):
        """Extract relevant data from a webpage"""
        return {
            'url': url,
            'title': soup.find('title').get_text().strip() if soup.find('title') else None,
            'meta_description': self._get_meta_description(soup),
            'h1_tags': [h1.get_text().strip() for h1 in soup.find_all('h1')],
            'h2_tags': [h2.get_text().strip() for h2 in soup.find_all('h2')],
            'word_count': len(soup.get_text().split()),
            'images': len(soup.find_all('img')),
            'images_without_alt': len([img for img in soup.find_all('img') if not img.get('alt')]),
            'internal_links': len(self._extract_internal_links(soup, url)),
            'external_links': len(self._extract_external_links(soup, url)),
            'raw_html': raw_html
        }
    
    def _get_meta_description(self, soup):
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()
        return None
    
    def _extract_internal_links(self, soup, base_url):
        """Extract internal links from the page"""
        internal_links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            if urlparse(full_url).netloc == base_domain:
                internal_links.append(full_url)
                
        return list(set(internal_links))  # Remove duplicates
    
    def _extract_external_links(self, soup, base_url):
        """Extract external links from the page"""
        external_links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            if urlparse(full_url).netloc != base_domain and urlparse(full_url).netloc:
                external_links.append(full_url)
                
        return list(set(external_links))  # Remove duplicates