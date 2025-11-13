from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random
from urllib.parse import urljoin, quote
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

class Rumah123Crawler:
    def __init__(self, max_workers=5):
        self.base_url = "https://www.rumah123.com/"
        self.max_workers = max_workers
        self.properties = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.rumah123.com/'
        }
    
    def get_listing_urls(self, search_query="kos", pages=3):
        urls = []
        for page in range(1, pages + 1):
            search_url = f"{self.base_url}/jual/cari/?q={quote(search_query)}&page={page}"
            print(f"📄 Fetching page {page}")
            
            try:
                response = requests.get(search_url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    if '/properti/' in href or '/jual/' in href:
                        full_url = urljoin(self.base_url, href)
                        if full_url not in urls and 'cari' not in full_url:
                            urls.append(full_url)
                
                time.sleep(random.uniform(1, 2))
            except Exception as e:
                print(f"❌ Error: {e}")
        
        return list(set(urls))[:50]
    
    def scrape_property(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data
            title = self._extract_text(soup, ['h1', '[data-testid="listing-title"]'])
            price = self._extract_price(soup)
            location = self._extract_text(soup, ['address', '[class*="location"]'])
            
            specs_text = soup.get_text()
            bedrooms = self._extract_number(specs_text, r'(\d+)\s*(?:kt|kamar tidur)', 'KT')
            bathrooms = self._extract_number(specs_text, r'(\d+)\s*(?:km|kamar mandi)', 'KM')
            land_size = self._extract_number(specs_text, r'(\d+)\s*m².*tanah', 'm²')
            building_size = self._extract_number(specs_text, r'(\d+)\s*m².*bangunan', 'm²')
            
            description = self._extract_text(soup, ['[class*="description"]', 'p'], max_len=300)
            agent = self._extract_text(soup, ['[class*="agent"]'])
            
            time.sleep(random.uniform(0.5, 1.5))
            
            return {
                'url': url,
                'title': title,
                'price': price,
                'location': location,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'land_size': land_size,
                'building_size': building_size,
                'description': description,
                'agent': agent,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"❌ Error scraping: {e}")
            return None
    
    def _extract_text(self, soup, selectors, max_len=None):
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if len(text) > 20:
                    return text[:max_len] + "..." if max_len and len(text) > max_len else text
        return "N/A"
    
    def _extract_price(self, soup):
        text = soup.get_text()
        patterns = [
            r'Rp\s*[\d.,]+\s*(?:Juta|Miliar)?',
            r'IDR\s*[\d.,]+',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return "Hubungi Agen"
    
    def _extract_number(self, text, pattern, unit):
        match = re.search(pattern, text, re.IGNORECASE)
        return f"{match.group(1)} {unit}" if match else "N/A"
    
    def crawl(self, search_query="kos", pages=2):
        print(f"🚀 Starting crawler: '{search_query}'")
        self.properties = []
        
        listing_urls = self.get_listing_urls(search_query, pages)
        print(f"✅ Found {len(listing_urls)} listings")
        
        if not listing_urls:
            return []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.scrape_property, url): url for url in listing_urls}
            
            for future in as_completed(futures):
                data = future.result()
                if data:
                    self.properties.append(data)
                    print(f"✓ Scraped: {data['title'][:50]}...")
        
        print(f"🎉 Done! {len(self.properties)} properties")
        return self.properties

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crawl', methods=['POST'])
def crawl():
    try:
        data = request.json
        search_query = data.get('query', 'kos')
        num_pages = max(1, min(int(data.get('pages', 2)), 10))
        num_workers = max(1, min(int(data.get('workers', 5)), 20))
        
        crawler = Rumah123Crawler(max_workers=num_workers)
        properties = crawler.crawl(search_query=search_query, pages=num_pages)
        
        return jsonify({
            'success': True,
            'properties': properties,
            'total': len(properties)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🏠 RUMAH123 PROFESSIONAL CRAWLER")
    print("=" * 60)
    print("\n🌐 Server starting...")
    print("📍 Open: http://localhost:5000")
    print("\n⚠  Press CTRL+C to stop")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)