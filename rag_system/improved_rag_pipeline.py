# ===================================================================
# 🎯 ENHANCED RAG PIPELINE v4.0 - KAGGLE OPTIMIZED
# Automated News Crawling & Vector DB Update Pipeline
# ===================================================================

import os
import re
import sys
import time
import json
import uuid
import pickle
import logging
import traceback
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Core libraries
import boto3
import faiss
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from tqdm.notebook import tqdm
import concurrent.futures
from kaggle_secrets import UserSecretsClient

# ML libraries
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Installing sentence-transformers...")
    os.system("pip install sentence-transformers")
    from sentence_transformers import SentenceTransformer

# ===================================================================
# ⚙️ CONFIGURATION
# ===================================================================

# Environment settings
LOCAL_WORK_DIR = "/kaggle/working/rag_pipeline"
os.makedirs(LOCAL_WORK_DIR, exist_ok=True)

# Model configuration
MODEL_NAME = "keepitreal/vietnamese-sbert"

# File names
INPUT_MASTER_FILENAME = "finance_news.csv"
PROCESSED_MASTER_FILENAME = "financial_news_cleaned_ver01.csv"

# S3 structure
S3_INPUT_KEY = "rag/input/"
S3_PROCESSED_KEY = "rag/processed/"
S3_VECTORDB_KEY = "rag/vectordb/"
S3_LOGS_KEY = "rag/logs/"

# Performance settings
MAX_WORKERS = 20
BATCH_SIZE = 64
REQUEST_TIMEOUT = 15
REQUEST_DELAY = 0.2
RETRY_ATTEMPTS = 3
MIN_CONTENT_LENGTH = 200
MAX_CONTENT_LENGTH = 50000

# ===================================================================
# 📝 ENHANCED LOGGING SETUP
# ===================================================================

LOG_TIMESTAMP = time.strftime('%Y%m%d_%H%M%S')
LOCAL_LOG_PATH = os.path.join(LOCAL_WORK_DIR, f"enhanced_pipeline_{LOG_TIMESTAMP}.log")

# Setup enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOCAL_LOG_PATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ===================================================================
# 🔐 SECRETS MANAGEMENT
# ===================================================================

def load_secrets():
    """Load secrets from Kaggle"""
    try:
        logger.info("🔐 Loading secrets from Kaggle...")
        secrets = UserSecretsClient()
        
        config = {
            'AWS_KEY': secrets.get_secret("AWS_ACCESS_KEY_ID"),
            'AWS_SECRET': secrets.get_secret("AWS_SECRET_ACCESS_KEY"),
            'S3_BUCKET': secrets.get_secret("S3_BUCKET"),
            'GOOGLE_API_KEY': secrets.get_secret("GOOGLE_API_KEY"),
            'GOOGLE_CSE_ID': secrets.get_secret("GOOGLE_CSE_ID")
        }
        
        logger.info("✅ All secrets loaded successfully")
        return config
        
    except Exception as e:
        logger.error(f"❌ Failed to load secrets: {e}")
        raise

# Load configuration
SECRETS = load_secrets()


# ===================================================================
# 🛠️ UTILITY CLASSES
# ===================================================================

class S3Manager:
    """Enhanced S3 operations with retry mechanism"""
    
    def __init__(self, aws_key, aws_secret):
        self.client = boto3.client('s3', aws_access_key_id=aws_key, aws_secret_access_key=aws_secret)
    
    def upload_file(self, local_path, bucket, key, retries=3):
        """Upload file to S3 with retry"""
        for attempt in range(retries):
            try:
                self.client.upload_file(local_path, bucket, key)
                logger.info(f"🚀 Uploaded '{os.path.basename(local_path)}' to 's3://{bucket}/{key}'")
                return True
            except Exception as e:
                if attempt < retries - 1:
                    logger.warning(f"Upload attempt {attempt + 1} failed, retrying... Error: {e}")
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"❌ Failed to upload after {retries} attempts: {e}")
                    return False
        return False
    
    def download_file(self, bucket, key, local_path, retries=3):
        """Download file from S3 with retry"""
        for attempt in range(retries):
            try:
                self.client.download_file(bucket, key, local_path)
                logger.info(f"📥 Downloaded '{key}' to '{local_path}'")
                return True
            except self.client.exceptions.NoSuchKey:
                logger.info(f"📄 File 's3://{bucket}/{key}' not found")
                return False
            except Exception as e:
                if attempt < retries - 1:
                    logger.warning(f"Download attempt {attempt + 1} failed, retrying... Error: {e}")
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"❌ Failed to download after {retries} attempts: {e}")
                    return False
        return False


class EnhancedNewsCollector:
    """Enhanced news collection with comprehensive financial keywords"""
    
    def __init__(self, api_key, cse_id):
        self.api_key = api_key
        self.cse_id = cse_id
        self.collected_links = set()
        
        # Enhanced Vietnamese financial domains
        self.financial_domains = [
            "vnexpress.net", "cafef.vn", "dantri.com.vn", "baodautu.vn",
            "nguoidothi.net.vn", "tinnhanhchungkhoan.vn", "vietstock.vn",
            "cophieu68.vn", "stockbiz.vn", "thesaigontimes.vn", "baomoi.com",
            "tuoitre.vn", "thanhnien.vn", "laodong.vn", "vtv.vn",
            "vietnamnews.vn", "vietnamnet.vn", "24h.com.vn", "tienphong.vn",
            "ndh.vn", "tapchitaichinh.vn", "kinhdoanh.net", "nhandan.vn"
        ]
        
        # Comprehensive financial keywords for Vietnamese market
        self.financial_keywords = [
            # Market Indices & Analysis
            "VN-Index", "VN30", "HNX-Index", "UPCOM", "chỉ số chứng khoán Việt Nam",
            "thị trường chứng khoán", "phiên giao dịch", "thanh khoản thị trường",
            
            # Technical Analysis
            "phân tích kỹ thuật", "chỉ báo RSI", "đường trung bình di động MA",
            "MACD", "Bollinger Bands", "Ichimoku", "khối lượng giao dịch",
            "hỗ trợ kháng cự", "đột phá giá", "xu hướng thị trường",
            
            # Economic Indicators
            "GDP Việt Nam", "tăng trưởng kinh tế", "lạm phát CPI", "PMI",
            "chỉ số giá sản xuất PPI", "xuất khẩu nhập khẩu", "FDI",
            "tỷ giá USD/VND", "dự trữ ngoại hối", "cán cân thương mại",
            
            # Monetary Policy
            "chính sách tiền tệ", "lãi suất điều hành", "Ngân hàng Nhà nước",
            "tín dụng ngân hàng", "thanh khoản hệ thống", "tỷ lệ dự trữ bắt buộc",
            
            # Banking Sector
            "ngành ngân hàng", "lợi nhuận ngân hàng", "nợ xấu NPL",
            "tăng trưởng tín dụng", "huy động vốn", "CAR",
            
            # Real Estate
            "bất động sản", "thị trường BDS", "giá nhà đất",
            "dự án bất động sản", "quy hoạch đô thị", "đầu tư BDS",
            
            # Major Stock Codes
            "VIC Vingroup", "VHM Vinhomes", "VRE Vincom Retail",
            "TCB Techcombank", "VCB Vietcombank", "BID BIDV", "CTG VietinBank",
            "ACB Asia Commercial Bank", "HPG Hoa Phat", "HSG Hoa Sen",
            "SSI chứng khoán", "VND VnDirect", "MWG Mobile World",
            "FPT Corporation", "VJC Vietjet", "HVN Vietnam Airlines",
            
            # Sectors
            "ngành thép", "ngành xi măng", "ngành dầu khí", "ngành điện lực",
            "ngành viễn thông", "ngành công nghệ", "ngành thủy sản",
            "ngành dệt may", "ngành ô tô", "ngành bán lẻ",
            
            # International Trade
            "EVFTA", "CPTPP", "RCEP", "WTO", "ASEAN",
            "xuất khẩu gạo", "xuất khẩu cà phê", "xuất khẩu thủy sản",
            "xuất khẩu dệt may", "xuất khẩu điện thoại",
            
            # Corporate Finance
            "báo cáo tài chính", "kết quả kinh doanh Q", "doanh thu",
            "lợi nhuận sau thuế", "EPS", "P/E", "ROE", "ROA",
            "cổ tức", "phát hành cổ phiếu", "tăng vốn điều lệ",
            
            # Investment & Capital Markets
            "quỹ đầu tư", "chứng chỉ quỹ", "trái phiếu doanh nghiệp",
            "trái phiếu chính phủ", "IPO", "niêm yết mới",
            "đầu tư nước ngoài", "room ngoại", "margin"
        ]
    
    def google_search(self, query, start_index=1):
        """Enhanced Google Search with better error handling"""
        url = "https://www.googleapis.com/customsearch/v1"
        
        domain_filter = " OR ".join([f"site:{domain}" for domain in self.financial_domains])
        
        params = {
            'q': f"{query} ({domain_filter})",
            'key': self.api_key,
            'cx': self.cse_id,
            'num': 10,
            'start': start_index,
            'gl': 'vn',
            'hl': 'vi',
            'dateRestrict': 'd7'
        }
        
        for attempt in range(RETRY_ATTEMPTS):
            try:
                response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                return response.json().get("items", [])
            except Exception as e:
                if attempt < RETRY_ATTEMPTS - 1:
                    logger.warning(f"Search attempt {attempt + 1} failed for '{query}', retrying...")
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"❌ Search failed for '{query}': {e}")
                    return []
        return []
    
    def collect_urls(self):
        """Collect URLs from all keywords"""
        all_results = []
        
        logger.info(f"🔍 Starting URL collection for {len(self.financial_keywords)} keywords")
        
        for i, keyword in enumerate(self.financial_keywords, 1):
            if i % 10 == 0:
                logger.info(f"🔍 Progress: [{i}/{len(self.financial_keywords)}] keywords processed")
            
            for page in range(1, 3):  # 2 pages max per keyword
                start_index = (page - 1) * 10 + 1
                items = self.google_search(keyword, start_index)
                
                if not items:
                    break
                
                for item in items:
                    link = item.get("link")
                    if link and self._is_valid_url(link) and link not in self.collected_links:
                        self.collected_links.add(link)
                        
                        result = {
                            "id": str(uuid.uuid4()),
                            "query": keyword,
                            "title": item.get("title", "").strip(),
                            "link": link,
                            "snippet": item.get("snippet", "").strip(),
                            "source": "google_cse",
                            "collection_time": datetime.now().isoformat(),
                            "domain": urlparse(link).netloc
                        }
                        all_results.append(result)
                
                time.sleep(1.2)  # Rate limiting
        
        df = pd.DataFrame(all_results)
        logger.info(f"✅ Collected {len(df)} unique URLs")
        return df
    
    def _is_valid_url(self, url):
        """Validate URL"""
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in ['http', 'https'] and
                parsed.netloc and
                any(domain in parsed.netloc for domain in self.financial_domains)
            )
        except:
            return False


class ContentProcessor:
    """Enhanced content processing"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_content(self, args):
        """Fetch content with logging"""
        url, idx, total = args
        
        if idx % 100 == 0:
            logger.info(f"📰 Processing content... [{idx+1}/{total}]: {url[:50]}...")
        
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Remove unwanted elements
            for tag in soup(["script", "style", "footer", "nav", "header", 
                           "aside", "form", "button", "iframe", "noscript"]):
                tag.decompose()
            
            content = soup.get_text(separator=" ", strip=True)
            
            if len(content) < MIN_CONTENT_LENGTH:
                return ""
            
            if len(content) > MAX_CONTENT_LENGTH:
                content = content[:MAX_CONTENT_LENGTH]
            
            time.sleep(REQUEST_DELAY)
            return content
            
        except Exception:
            return ""
    
    def process_batch(self, urls):
        """Process URLs in batch"""
        logger.info(f"📄 Processing {len(urls)} URLs for content extraction")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tasks = [(url, i, len(urls)) for i, url in enumerate(urls)]
            results = list(tqdm(
                executor.map(self.fetch_content, tasks),
                total=len(urls),
                desc="Extracting Content"
            ))
        
        return results
    
    def clean_text(self, text):
        """Enhanced text cleaning"""
        if not isinstance(text, str) or not text.strip():
            return ""
        
        # Remove HTML entities
        text = BeautifulSoup(text, "html.parser").get_text()
        
        # Remove URLs and unwanted patterns
        text = re.sub(r'http\S+|www\S+', ' ', text)
        text = re.sub(r'[^a-zA-ZÀ-ỹ0-9\s.,!?đĐ\-]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Filter sentences
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
        return '. '.join(sentences).strip()


class VectorDBManager:
    """Enhanced vector database management"""
    
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = None
        self.index = None
        self.metadata = {"ids": [], "texts": []}
    
    def load_model(self):
        """Load sentence transformer model"""
        if self.model is None:
            logger.info(f"🤖 Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("✅ Model loaded successfully")
    
    def load_existing_index(self, s3_manager, bucket):
        """Load existing FAISS index from S3"""
        faiss_path = os.path.join(LOCAL_WORK_DIR, "faiss_index.bin")
        meta_path = os.path.join(LOCAL_WORK_DIR, "faiss_metadata.pkl")
        
        faiss_exists = s3_manager.download_file(bucket, f"{S3_VECTORDB_KEY}faiss_index.bin", faiss_path)
        meta_exists = s3_manager.download_file(bucket, f"{S3_VECTORDB_KEY}faiss_metadata.pkl", meta_path)
        
        if faiss_exists and meta_exists:
            try:
                self.index = faiss.read_index(faiss_path)
                with open(meta_path, "rb") as f:
                    self.metadata = pickle.load(f)
                logger.info(f"📦 Loaded existing index with {self.index.ntotal:,} vectors")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to load existing index: {e}")
                return False
        return False
    
    def create_embeddings(self, texts):
        """Create embeddings for texts"""
        if not texts:
            return np.array([])
        
        self.load_model()
        
        logger.info(f"🔄 Creating embeddings for {len(texts)} texts")
        embeddings = self.model.encode(
            texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embeddings
    
    def update_index(self, new_df, existing_ids):
        """Update index with new documents"""
        new_docs = new_df[~new_df['id'].isin(existing_ids)].copy()
        
        if new_docs.empty:
            logger.info("✅ No new documents to add to vector database")
            return 0
        
        new_embeddings = self.create_embeddings(new_docs["combined_text"].tolist())
        
        if new_embeddings.size == 0:
            return 0
        
        if self.index is None:
            self.index = faiss.IndexFlatIP(new_embeddings.shape[1])
        
        self.index.add(new_embeddings)
        
        self.metadata["ids"].extend(new_docs["id"].tolist())
        self.metadata["texts"].extend(new_docs["combined_text"].tolist())
        
        added_count = len(new_docs)
        logger.info(f"📦 Added {added_count:,} new vectors. Total: {self.index.ntotal:,}")
        return added_count
    
    def save_to_s3(self, s3_manager, bucket):
        """Save index to S3"""
        if self.index is None:
            return
        
        faiss_path = os.path.join(LOCAL_WORK_DIR, "faiss_index.bin")
        meta_path = os.path.join(LOCAL_WORK_DIR, "faiss_metadata.pkl")
        info_path = os.path.join(LOCAL_WORK_DIR, "embeddings_info.json")
        
        faiss.write_index(self.index, faiss_path)
        
        with open(meta_path, "wb") as f:
            pickle.dump(self.metadata, f)
        
        info_data = {
            "model_name": self.model_name,
            "vector_dim": int(self.index.d),
            "total_docs": int(self.index.ntotal),
            "last_updated": datetime.now().isoformat()
        }
        
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(info_data, f, indent=4, ensure_ascii=False)
        
        # Upload to S3
        s3_manager.upload_file(faiss_path, bucket, f"{S3_VECTORDB_KEY}faiss_index.bin")
        s3_manager.upload_file(meta_path, bucket, f"{S3_VECTORDB_KEY}faiss_metadata.pkl")
        s3_manager.upload_file(info_path, bucket, f"{S3_VECTORDB_KEY}embeddings_info.json")
        
        # Create backup
        backup_date = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_key = f"{S3_VECTORDB_KEY}backup/faiss_index_{backup_date}.bin"
        s3_manager.upload_file(faiss_path, bucket, backup_key)
        
        logger.info("💾 Vector database saved and backed up to S3")


# ===================================================================
# 🚀 MAIN PIPELINE ORCHESTRATOR
# ===================================================================

class RAGPipeline:
    """Main RAG pipeline orchestrator"""
    
    def __init__(self):
        self.config = SECRETS
        self.s3_manager = S3Manager(self.config['AWS_KEY'], self.config['AWS_SECRET'])
        self.collector = EnhancedNewsCollector(
            self.config['GOOGLE_API_KEY'], 
            self.config['GOOGLE_CSE_ID']
        )
        self.content_processor = ContentProcessor()
        self.vector_db = VectorDBManager(MODEL_NAME)
        self.bucket = self.config['S3_BUCKET']
    
    def update_master_file(self, new_df, filename, s3_prefix):
        """Update master file with new data"""
        local_path = os.path.join(LOCAL_WORK_DIR, filename)
        s3_key = s3_prefix + filename
        
        # Download existing file
        if self.s3_manager.download_file(self.bucket, s3_key, local_path):
            existing_df = pd.read_csv(local_path)
            updated_df = pd.concat([existing_df, new_df]).drop_duplicates(
                subset=['link'], keep='last'
            ).reset_index(drop=True)
        else:
            updated_df = new_df
        
        # Save updated file
        updated_df.to_csv(local_path, index=False, encoding='utf-8-sig')
        self.s3_manager.upload_file(local_path, self.bucket, s3_key)
        
        logger.info(f"📊 Updated {filename}: +{len(new_df)} new, total: {len(updated_df)}")
        return updated_df
    
    def collect_news(self):
        """Step 1: Collect news URLs"""
        logger.info("🔍 STEP 1: Collecting news URLs...")
        
        new_articles = self.collector.collect_urls()
        
        if new_articles.empty:
            logger.warning("⚠️ No new articles collected")
            return new_articles
        
        # Update master input file
        self.update_master_file(new_articles, INPUT_MASTER_FILENAME, S3_INPUT_KEY)
        
        return new_articles
    
    def process_content(self, articles_df):
        """Step 2: Process article content"""
        if articles_df.empty:
            return articles_df
        
        logger.info("📄 STEP 2: Processing article content...")
        
        # Extract content
        urls = articles_df['link'].tolist()
        contents = self.content_processor.process_batch(urls)
        articles_df['content_raw'] = contents
        
        # Filter articles with sufficient content
        processed_df = articles_df[
            articles_df['content_raw'].str.len() >= MIN_CONTENT_LENGTH
        ].copy()
        
        if processed_df.empty:
            logger.warning("⚠️ No articles with sufficient content")
            return processed_df
        
        # Clean and combine text
        logger.info("🧹 Cleaning and combining text...")
        
        # Use tqdm for progress tracking
        tqdm.pandas(desc="Cleaning titles")
        processed_df['title_clean'] = processed_df['title'].progress_apply(
            self.content_processor.clean_text
        )
        
        tqdm.pandas(desc="Cleaning content")
        processed_df['content_clean'] = processed_df['content_raw'].progress_apply(
            self.content_processor.clean_text
        )
        
        processed_df['combined_text'] = (
            processed_df['title_clean'] + ". " + processed_df['content_clean']
        )
        
        # Final filtering
        processed_df = processed_df[
            processed_df['combined_text'].str.len() >= MIN_CONTENT_LENGTH
        ].copy()
        
        logger.info(f"✅ Successfully processed {len(processed_df)} articles")
        
        # Update master processed file
        self.update_master_file(processed_df, PROCESSED_MASTER_FILENAME, S3_PROCESSED_KEY)
        
        return processed_df
    
    def update_vector_db(self, processed_df):
        """Step 3: Update vector database"""
        if processed_df.empty:
            return 0
        
        logger.info("🔍 STEP 3: Updating vector database...")
        
        # Load existing index
        index_loaded = self.vector_db.load_existing_index(self.s3_manager, self.bucket)
        
        if index_loaded:
            existing_ids = set(self.vector_db.metadata.get('ids', []))
            logger.info(f"📊 Found {len(existing_ids):,} existing documents")
        else:
            existing_ids = set()
            logger.info("🆕 Creating new vector database")
        
        # Update with new documents
        added_count = self.vector_db.update_index(processed_df, existing_ids)
        
        if added_count > 0:
            # Save to S3
            self.vector_db.save_to_s3(self.s3_manager, self.bucket)
        
        return added_count
    
    def run(self):
        """Execute the complete pipeline"""
        start_time = time.time()
        
        try:
            logger.info("🚀 Starting Enhanced RAG Pipeline v4.0")
            logger.info(f"📅 Run timestamp: {LOG_TIMESTAMP}")
            
            # Step 1: Collect news
            articles_df = self.collect_news()
            
            # Step 2: Process content
            processed_df = self.process_content(articles_df)
            
            # Step 3: Update vector database
            added_count = self.update_vector_db(processed_df)
            
            # Summary
            duration = time.time() - start_time
            logger.info("🎯 PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info("📊 EXECUTION SUMMARY:")
            logger.info(f"   ├── Collected articles: {len(articles_df)}")
            logger.info(f"   ├── Processed articles: {len(processed_df)}")
            logger.info(f"   ├── Added to vector DB: {added_count}")
            logger.info(f"   └── Total duration: {duration:.2f} seconds")
            
            return {
                'collected': len(articles_df),
                'processed': len(processed_df),
                'added_to_db': added_count,
                'duration': duration,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"❌ PIPELINE FAILED: {e}")
            logger.error(traceback.format_exc())
            return {
                'status': 'failed',
                'error': str(e),
                'duration': time.time() - start_time
            }


def run_pipeline():
    """Main pipeline execution function"""
    logger.info("🎯 Enhanced RAG Pipeline v4.0 - Kaggle Optimized")
    logger.info("=" * 60)
    
    try:
        # Initialize and run pipeline
        pipeline = RAGPipeline()
        results = pipeline.run()
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Critical error in pipeline execution: {e}")
        logger.error(traceback.format_exc())
        raise
    
    finally:
        # Upload log file to S3
        try:
            logger.info("📤 Uploading log file to S3...")
            s3_client = boto3.client(
                's3',
                aws_access_key_id=SECRETS['AWS_KEY'],
                aws_secret_access_key=SECRETS['AWS_SECRET']
            )
            s3_log_key = f"{S3_LOGS_KEY}enhanced_pipeline_{LOG_TIMESTAMP}.log"
            s3_client.upload_file(LOCAL_LOG_PATH, SECRETS['S3_BUCKET'], s3_log_key)
            logger.info(f"✅ Log uploaded to s3://{SECRETS['S3_BUCKET']}/{s3_log_key}")
        except Exception as e:
            logger.error(f"❌ Failed to upload log: {e}")


# ===================================================================
# 🎯 MAIN EXECUTION
# ===================================================================

if __name__ == "__main__":
    logger.info("🚀 Starting Enhanced RAG Pipeline v4.0")
    
    try:
        results = run_pipeline()
        
        if results and results.get('status') == 'success':
            logger.info("🎉 Pipeline completed successfully!")
        else:
            logger.error("💥 Pipeline failed!")
            
    except KeyboardInterrupt:
        logger.info("⏹️ Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)