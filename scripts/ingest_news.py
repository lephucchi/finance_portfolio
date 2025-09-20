import os
import sys
from dotenv import load_dotenv
import boto3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import hashlib
import json
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
import random
import argparse
import warnings

# Add utils to path for logging
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from logger import log_news_execution

warnings.filterwarnings('ignore')

# Load secrets từ file .env
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET") or os.getenv("AWS_BUCKET_NAME")

# Cấu hình AWS S3
s3_client = None
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_REGION:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )
else:
    print("⚠️  AWS credentials chưa được cấu hình đầy đủ. Script sẽ chạy ở mode test (lưu file local).")

# Cấu hình scraping
DEFAULT_CONFIG = {
    'max_pages_per_site': 5,
    'max_articles_per_page': 15,
    'delay_between_requests': (1, 3),
    'request_timeout': 15
}

# Headers chống phát hiện bot
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Comprehensive banking keywords từ notebook
BANKING_KEYWORDS = [
    # Nhóm 1: Ngân hàng tổng quát
    'ngân hàng', 'ngan hang', 'nhà băng', 'nha bang',
    'tín dụng', 'tin dung', 'lãi suất', 'lai suat',
    'vay vốn', 'vay von', 'tiền gửi', 'tien gui',
    'thẻ tín dụng', 'the tin dung', 'thanh toán', 'thanh toan',
    'ví điện tử', 'vi dien tu', 'banking', 'bank', 'credit', 'loan', 'fintech',
    
    # Nhóm 2: Ngân hàng cụ thể (major banks)
    'vietcombank', 'vcb', 'vietinbank', 'ctg', 'bidv', 'bid',
    'agribank', 'agr', 'techcombank', 'tcb', 'mbbank', 'mbb',
    'vpbank', 'vpb', 'acb', 'á châu', 'tpbank', 'tpb',
    'sacombank', 'stb', 'hdbank', 'hdb', 'vib', 'shb',
    'ocb', 'seabank', 'ssb', 'lienvietpostbank', 'lpb',
    'eximbank', 'eib', 'abbank', 'abb', 'bac a bank', 'bab',
    
    # Nhóm 3: Kinh tế vĩ mô
    'kinh tế', 'tăng trưởng', 'lạm phát', 'tỷ giá', 'ngoại tệ',
    'usd', 'đô la', 'vàng', 'chứng khoán', 'bất động sản',
    'thanh khoản', 'đầu tư', 'thị trường tài chính',
    
    # Nhóm 4: Chính sách
    'ngân hàng nhà nước', 'nhnn', 'chính phủ', 'bộ tài chính',
    'chính sách tiền tệ', 'basel', 'an toàn vốn', 'nợ xấu',
    
    # Nhóm 5: Fintech
    'ngân hàng số', 'digital banking', 'mobile banking',
    'fintech', 'blockchain', 'tiền ảo', 'cryptocurrency'
]

# Cấu hình các trang báo
NEWS_SITES = {
    'vneconomy.vn': {
        'base_url': 'https://vneconomy.vn',
        'search_urls': [
            'https://vneconomy.vn/ngan-hang.htm',
            'https://vneconomy.vn/tai-chinh.htm',
            'https://vneconomy.vn/dau-tu.htm',
            'https://vneconomy.vn/thi-truong.htm'
        ]
    },
    'vnexpress.net': {
        'base_url': 'https://vnexpress.net',
        'search_urls': [
            'https://vnexpress.net/kinh-doanh/ngan-hang',
            'https://vnexpress.net/kinh-doanh'
        ]
    },
    'cafef.vn': {
        'base_url': 'https://cafef.vn',
        'search_urls': [
            'https://cafef.vn/tai-chinh-ngan-hang.chn',
            'https://cafef.vn/thi-truong-chung-khoan.chn'
        ]
    },
    'thoibaotaichinhvietnam.vn': {
        'base_url': 'https://thoibaotaichinhvietnam.vn',
        'search_urls': [
            'https://thoibaotaichinhvietnam.vn/ngan-hang',
            'https://thoibaotaichinhvietnam.vn/tai-chinh'
        ]
    }
}

def clean_text(text):
    """Làm sạch text"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'[^\w\s\.\,\?\!\-\:\;\(\)]', ' ', text)
    return text.strip()

def is_banking_related(title, content):
    """Kiểm tra có liên quan đến ngân hàng không"""
    full_text = (title + " " + content).lower()
    return any(keyword.lower() in full_text for keyword in BANKING_KEYWORDS[:20])  # Check top 20 keywords

def calculate_sentiment_basic(title, content):
    """Tính sentiment cơ bản"""
    positive_words = ['tăng', 'tốt', 'khả quan', 'phát triển', 'lợi nhuận', 
                     'thành công', 'mạnh', 'cao', 'cải thiện', 'tăng trưởng']
    negative_words = ['giảm', 'xấu', 'khó khăn', 'thua lỗ', 'rủi ro', 
                     'suy giảm', 'yếu', 'thấp', 'khủng hoảng', 'thiệt hại']
    
    full_text = (title + " " + content).lower()
    positive_count = sum(1 for word in positive_words if word in full_text)
    negative_count = sum(1 for word in negative_words if word in full_text)
    
    if positive_count > negative_count:
        return 1.0
    elif negative_count > positive_count:
        return -1.0
    else:
        return 0.0

def generate_article_id(title, url, published_date):
    """Tạo ID duy nhất cho bài báo"""
    unique_string = f"{title[:50]}{url}{published_date}"
    return hashlib.md5(unique_string.encode('utf-8')).hexdigest()[:12]

def extract_publish_date(soup, url):
    """Trích xuất ngày đăng"""
    date_selectors = [
        'meta[property="article:published_time"]',
        'meta[name="pubdate"]',
        'meta[name="date"]',
        '[class*="date"]',
        '[class*="time"]',
        'time'
    ]
    
    for selector in date_selectors:
        date_elem = soup.select_one(selector)
        if date_elem:
            date_text = date_elem.get('content') or date_elem.get_text()
            if date_text:
                try:
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                        try:
                            parsed_date = datetime.strptime(date_text[:10], fmt)
                            return parsed_date.strftime('%Y-%m-%d')
                        except:
                            continue
                except:
                    pass
    
    # Fallback to today
    return datetime.now().strftime('%Y-%m-%d')

def test_s3_connection():
    """Test S3 connection"""
    if not s3_client or not S3_BUCKET:
        return False
    
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET)
        print(f"✅ S3 connection successful to bucket: {S3_BUCKET}")
        return True
    except Exception as e:
        print(f"❌ S3 connection failed: {e}")
        return False

def upload_to_s3(data: str, key: str):
    """Upload dữ liệu lên S3 bucket với fallback local storage"""
    try:
        if S3_BUCKET is None or s3_client is None:
            print(f"⚠️  S3 chưa được cấu hình. Sẽ lưu file local thay thế.")
            local_path = f"/tmp/{key}"
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"💾 Đã lưu file local: {local_path}")
            return True
            
        if not isinstance(data, str):
            data = str(data)
            
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=data.encode("utf-8"),
            ContentType='application/json'
        )
        return True
    except Exception as e:
        print(f"❌ Lỗi khi upload {key} lên S3: {e}")
        print(f"⚠️  Đang fallback về local storage...")
        
        try:
            local_path = f"/tmp/{key}"
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"💾 Đã lưu file local: {local_path}")
            return True
        except Exception as local_e:
            print(f"❌ Lỗi cả local storage: {local_e}")
            return False

class VietnamBankingNewsScraper:
    """News scraper cho tin tức ngân hàng Việt Nam"""
    
    def __init__(self, config=None):
        self.config = config or DEFAULT_CONFIG
        self.session = None
        self.articles_scraped = []
    
    def _ensure_session(self):
        """Tạo session khi cần thiết (lazy loading)"""
        if self.session is None:
            self.session = requests.Session()
            self.session.headers.update(HEADERS)
    
    def find_article_links(self, url):
        """Tìm các link bài báo từ trang danh sách"""
        try:
            self._ensure_session()
            time.sleep(random.uniform(*self.config['delay_between_requests']))
            
            response = self.session.get(url, timeout=self.config['request_timeout'])
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = set()
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                
                # Chuyển thành URL đầy đủ
                if href.startswith('/'):
                    parsed = urlparse(url)
                    full_url = f"{parsed.scheme}://{parsed.netloc}{href}"
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                
                # Lọc các link có vẻ là bài báo
                if any(ext in href for ext in ['.htm', '.html', '.aspx']) or '/news/' in href or '/kinh-te/' in href:
                    title_text = a.get_text().strip()
                    if title_text and len(title_text) > 10:
                        # Quick keyword check
                        if any(keyword.lower() in title_text.lower() for keyword in BANKING_KEYWORDS[:10]):
                            links.add(full_url)
            
            return list(links)[:self.config['max_articles_per_page']]
            
        except Exception as e:
            print(f"    ❌ Lỗi tìm link từ {url}: {e}")
            return []
    
    def scrape_article_detail(self, url):
        """Scrape chi tiết một bài báo"""
        try:
            self._ensure_session()
            time.sleep(random.uniform(0.5, 1.5))
            
            response = self.session.get(url, timeout=self.config['request_timeout'])
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tìm tiêu đề
            title = ""
            title_selectors = [
                'h1', 'h2', 
                '[class*="title"]', '[class*="headline"]',
                '[id*="title"]', '.entry-title'
            ]
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = clean_text(title_elem.get_text())
                    if title and len(title) > 5:
                        break
            
            if not title:
                return None
            
            # Tìm nội dung
            content = ""
            content_selectors = [
                '[class*="content"]', '[class*="body"]', 
                '[class*="article"]', '[id*="content"]',
                '.entry-content', '.post-content', 'p'
            ]
            
            for selector in content_selectors:
                content_elems = soup.select(selector)
                if content_elems:
                    content_texts = []
                    for elem in content_elems:
                        text = clean_text(elem.get_text())
                        if text and len(text) > 20:
                            content_texts.append(text)
                    
                    if content_texts:
                        content = " ".join(content_texts)[:2000]
                        break
            
            # Kiểm tra có liên quan đến ngân hàng không
            if not is_banking_related(title, content):
                return None
            
            # Trích xuất ngày đăng
            published_date = extract_publish_date(soup, url)
            
            # Tạo article data
            article_data = {
                'article_id': generate_article_id(title, url, published_date),
                'published_at': published_date,
                'source': urlparse(url).netloc,
                'title': title,
                'content': content,
                'sentiment_score': calculate_sentiment_basic(title, content),
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
            
            return article_data
            
        except Exception as e:
            return None
    
    def scrape_website(self, site_name, site_config):
        """Scrape một website"""
        print(f"\n🌐 Đang scrape {site_name}...")
        articles = []
        
        max_pages = min(len(site_config['search_urls']), self.config['max_pages_per_site'])
        
        for i, search_url in enumerate(site_config['search_urls'][:max_pages]):
            print(f"  📄 Trang {i+1}/{max_pages}: {search_url}")
            
            # Tìm các link bài báo
            article_links = self.find_article_links(search_url)
            print(f"    🔗 Tìm thấy {len(article_links)} link bài báo")
            
            # Scrape từng bài báo
            scraped_count = 0
            for link in article_links:
                article = self.scrape_article_detail(link)
                if article:
                    articles.append(article)
                    scraped_count += 1
                    print(f"    ✅ [{scraped_count:2d}] {article['title'][:60]}...")
        
        return articles
    
    def crawl_news_daily(self, target_date=None):
        """Crawl tin tức cho một ngày cụ thể"""
        if target_date is None:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"🚀 Bắt đầu crawl tin tức ngân hàng ngày {target_date}")
        print("=" * 60)
        
        start_time = time.time()
        all_articles = []
        sources_stats = {}
        
        for site_name, site_config in NEWS_SITES.items():
            try:
                articles = self.scrape_website(site_name, site_config)
                all_articles.extend(articles)
                sources_stats[site_name] = len(articles)
                print(f"📊 {site_name}: {len(articles)} bài báo")
                
            except Exception as e:
                print(f"❌ Lỗi scraping {site_name}: {e}")
                sources_stats[site_name] = 0
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n🎉 HOÀN THÀNH CRAWL!")
        print(f"⏱️ Thời gian: {duration:.1f} giây")
        print(f"📊 Tổng cộng: {len(all_articles)} bài báo")
        
        # Upload từng bài lên S3
        if all_articles:
            successful_uploads, failed_uploads = self.upload_articles_to_s3(all_articles, target_date)
            
            # Log execution
            status = "success" if failed_uploads == 0 else ("partial" if successful_uploads > 0 else "failed")
            log_news_execution(
                target_date=target_date,
                status=status,
                details={
                    "total_articles": len(all_articles),
                    "successful_uploads": successful_uploads,
                    "failed_uploads": failed_uploads,
                    "execution_time_seconds": duration,
                    "sources_stats": sources_stats,
                    "success_rate": (successful_uploads / len(all_articles)) * 100 if all_articles else 0,
                    "config": self.config
                }
            )
            
            return successful_uploads, failed_uploads
        else:
            print("❌ Không thu thập được bài báo nào!")
            
            # Log failed execution
            log_news_execution(
                target_date=target_date,
                status="failed",
                error="Không thu thập được bài báo nào",
                details={
                    "execution_time_seconds": duration,
                    "sources_stats": sources_stats,
                    "config": self.config
                }
            )
            
            return 0, 0
    
    def upload_articles_to_s3(self, articles, target_date):
        """Upload articles lên S3 với partition structure"""
        successful_uploads = 0
        failed_uploads = 0
        
        print(f"\n📤 Bắt đầu upload {len(articles)} bài báo lên S3...")
        
        for article in articles:
            try:
                # Tạo S3 key theo pattern: raw/news/source={source}/date={YYYY-MM-DD}/{article_id}.json
                source = article['source'].replace('.', '_')
                s3_key = f"raw/news/source={source}/date={target_date}/{article['article_id']}.json"
                
                # Convert sang JSON
                json_data = json.dumps(article, ensure_ascii=False, indent=2)
                
                # Upload lên S3
                if upload_to_s3(json_data, s3_key):
                    print(f"✅ {article['article_id']} - {article['title'][:50]}...")
                    successful_uploads += 1
                else:
                    failed_uploads += 1
                
            except Exception as e:
                print(f"❌ Lỗi upload article {article.get('article_id', 'unknown')}: {e}")
                failed_uploads += 1
        
        print(f"\n📈 Kết quả upload:")
        print(f"   ✅ Thành công: {successful_uploads}/{len(articles)}")
        print(f"   ❌ Thất bại: {failed_uploads}/{len(articles)}")
        
        return successful_uploads, failed_uploads

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crawl tin tức ngân hàng Việt Nam')
    parser.add_argument('--date', type=str, help='Ngày cần crawl (YYYY-MM-DD), mặc định là hôm nay')
    parser.add_argument('--max-pages', type=int, default=5, help='Số trang tối đa mỗi site')
    parser.add_argument('--max-articles', type=int, default=15, help='Số bài báo tối đa mỗi trang')
    parser.add_argument('--test-s3', action='store_true', help='Chỉ test S3 connection')
    
    args = parser.parse_args()
    
    # Test S3 connection nếu được yêu cầu
    if args.test_s3:
        print("🔧 Testing S3 connection...")
        print(f"AWS_ACCESS_KEY_ID: {'✅ Set' if AWS_ACCESS_KEY_ID else '❌ Not set'}")
        print(f"AWS_SECRET_ACCESS_KEY: {'✅ Set' if AWS_SECRET_ACCESS_KEY else '❌ Not set'}")
        print(f"AWS_REGION: {AWS_REGION}")
        print(f"S3_BUCKET: {S3_BUCKET}")
        
        if s3_client and S3_BUCKET:
            test_s3_connection()
        else:
            print("❌ S3 client not initialized")
        exit(0)
    
    target_date = args.date
    if target_date is None:
        target_date = datetime.now().strftime('%Y-%m-%d')
    
    # Cấu hình scraper
    config = {
        'max_pages_per_site': args.max_pages,
        'max_articles_per_page': args.max_articles,
        'delay_between_requests': (1, 3),
        'request_timeout': 15
    }
    
    print(f"📰 VN Banking News Crawler")
    print(f"📅 Target date: {target_date}")
    print(f"☁️  S3 Bucket: {S3_BUCKET}")
    print(f"📊 Config: {args.max_pages} pages/site, {args.max_articles} articles/page")
    
    # Test S3 connection nếu có cấu hình
    if S3_BUCKET and s3_client:
        s3_connected = test_s3_connection()
        if not s3_connected:
            print("⚠️  S3 connection failed. Script sẽ chạy ở local mode.")
    
    print("=" * 60)
    
    # Khởi tạo và chạy scraper
    scraper = VietnamBankingNewsScraper(config)
    successful, failed = scraper.crawl_news_daily(target_date)
    
    if failed == 0:
        print(f"\n🎉 Crawl hoàn thành thành công!")
    else:
        print(f"\n⚠️  Crawl hoàn thành với {failed} lỗi")
        
    print("=" * 60)
    print("✨ Script completed!")
