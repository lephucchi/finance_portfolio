// Simple i18n implementation without external dependencies
export type Language = 'en' | 'vi';

export type TranslationValue = string | string[] | { [key: string]: TranslationValue };

export interface Translations {
  [key: string]: {
    [key: string]: TranslationValue;
  };
}

let currentLanguage: Language = 'en';

export const translations: Translations = {
  en: {
    // Common
    language: 'English',
    languageCode: 'en',
    
    // Home page
    home: {
      title: 'AEGIS LUMINA',
      subtitle: 'The AI Shield That Illuminates Your Data',
      description: 'Named after the divine shield of Zeus and Athena combined with the light of wisdom. An enterprise-grade AI system that protects and illuminates all your financial data with cutting-edge Lakehouse architecture and intelligent RAG chatbot.',
      startWithMetallica: 'Start with Metallica AI',
      viewDashboard: 'View Dashboard',
      productionReady: 'Production Ready',
      version: 'Version 1.0',
      november2025: 'November 2025',
      
      // Features
      aegisProtection: 'AEGIS Protection',
      aegisProtectionDesc: 'Divine shield protecting your data with AWS Lakehouse architecture - Bronze, Silver, Gold layers ensuring data quality.',
      aegisStats: '10,950 stocks • 12,027 news • 18,250 indicators',
      
      luminaIntelligence: 'LUMINA Intelligence',
      luminaIntelligenceDesc: 'AI-powered insights that illuminate patterns in Vietnamese financial markets using advanced RAG chatbot technology.',
      luminaStats: '10,585 vectors • <10ms search • 768 dimensions',
      
      lakehouseArch: 'Lakehouse Architecture',
      lakehouseArchDesc: 'Modern data platform combining data lake flexibility with data warehouse performance on AWS S3.',
      lakehouseStats: '92% compression • $6.32/month • 0.5-1s queries',
      
      vietnameseSBERT: 'Vietnamese SBERT',
      vietnameseSBERTDesc: 'Specialized embeddings for Vietnamese language using keepitreal/vietnamese-sbert model with FAISS vector database.',
      vietnameseSBERTStats: '768-dim embeddings • Batch processing • Real-time',
      
      airflowPipeline: 'Airflow ETL Pipeline',
      airflowPipelineDesc: 'Automated daily data pipeline with PySpark processing through 7 stages - from ingestion to validation.',
      airflowStats: '7 stages • 99.8% uptime • ~7h daily cycle',
      
      awsCloud: 'AWS Cloud Infrastructure',
      awsCloudDesc: 'Scalable cloud platform with S3 storage, Glue Catalog, and Athena queries for high performance analytics.',
      awsCloudStats: 'S3 • Glue • Athena • Cost-optimized',
      
      // Quick Access
      quickAccess: 'Quick Access',
      
      metallicaAI: 'Metallica AI Chatbot',
      metallicaAIDesc: 'Ask questions about Vietnamese financial markets in natural language',
      aiPowered: 'AI-Powered',
      
      analyticsDashboard: 'Analytics Dashboard',
      analyticsDashboardDesc: 'Real-time visualization of stocks, news sentiment, and market trends',
      realTime: 'Real-time',
      
      assetFinder: 'Asset Finder',
      assetFinderDesc: 'Search and filter 10,950+ Vietnamese stocks with advanced criteria',
      stocks: '10,950 stocks',
      
      aboutAegis: 'About AEGIS LUMINA',
      aboutAegisDesc: 'Learn about our Lakehouse, RAG system, and Airflow pipeline architecture',
      documentation: 'Documentation',
      
      // Performance
      systemPerformance: 'System Performance',
      costSavings: 'Cost Savings',
      querySpeed: 'Query Speed',
      faster: 'faster',
      uptime: 'Uptime',
      compression: 'Compression',
      spaceSaved: 'space saved',
      totalStocks: 'Total Stocks',
      newsArticles: 'News Articles',
      vectorsIndexed: 'Vectors Indexed',
      monthlyCost: 'Monthly Cost',
      
      // CTA
      readyToExplore: 'Ready to Explore?',
      readyToExploreDesc: 'Start your journey with AEGIS LUMINA. Discover insights, analyze data, and make informed decisions with our AI-powered financial analytics platform.',
      viewUserGuide: 'View User Guide',
      learnMore: 'Learn More',
    },
    
    // Chatbot page
    chatbot: {
      title: '🤖 AI Financial Assistant',
      description: 'Ask about Vietnamese stock market with RAG + Gemini technology',
      statsBanner: {
        newsArticles: 'financial news',
        model: 'Model:',
        vectorDim: 'Vector dimension:',
      },
      apiKeySetup: {
        title: 'Gemini API Key',
        description: 'To use the chatbot, you need to provide your Gemini API key.',
        label: 'API Key',
        placeholder: 'AIzaSy...',
        validate: 'Validate API Key',
        validating: 'Checking...',
        valid: 'API key is valid! You can start chatting.',
        invalid: 'API key is invalid. Please check again.',
        tipTitle: 'Get free API key:',
        getApiKey: 'Google AI Studio',
      },
      chat: {
        welcome: '👋 Hello! How can I help you?',
        suggestions: 'Suggested questions:',
        placeholder: 'Enter your question...',
        disabledPlaceholder: 'Please validate API key first',
        send: 'Send',
        enterToSend: '💡 Press Enter to send, Shift+Enter for new line',
        showSources: 'Show',
        hideSources: 'Hide',
        source: 'Source',
        error: 'Error:',
        errorMessage: 'Unable to process your question',
        sendError: 'An error occurred while sending the message. Please try again.',
        suggestedQuestions: [
          'What is the current Vietnamese stock market situation?',
          'How did VN-Index change this week?',
          'Which sectors have good prospects?',
        ],
      },
    },
    
    // Chat page (Oracle)
    oracleChat: {
      headerTitle: 'AI Financial Assistant',
      headerSubtitle: 'RAG-powered Vietnamese market insights',
      statusConnected: 'Connected',
      statusNoKey: 'No API key',
      settingsTitle: 'API Settings',
      clearChat: 'Clear chat',
      apiKeySettingsTitle: 'Gemini API Key',
      closeButton: 'Close',
      apiKeyHint: 'Enter your API key from',
      apiKeyFree: '(free)',
      apiKeyPlaceholder: 'AIzaSy...',
      validateButton: 'Validate',
      validatingButton: 'Checking...',
      validMessage: 'API key is valid! You can start chatting.',
      invalidMessage: 'Invalid API key. Please check and try again.',
      initialMessage: '✨ Hello! I am an AI financial assistant. I can help you analyze the Vietnamese stock market. What would you like to learn?',
      errorMessage: 'Sorry, I encountered an issue processing your question. Please try again later.',
      processingMessage: 'Processing your request...',
      suggestionsLabel: 'Suggested questions:',
      sourcesLabel: 'sources',
      sourceLabel: 'Source',
      relatedLabel: 'related',
      inputPlaceholder: 'Enter your question...',
      inputDisabledPlaceholder: '⚠️ Please configure API key first',
      suggestedQuestionsData: [
        'What is the current Vietnamese stock market situation?',
        'How did VN-Index change this week?',
        'Which sectors have good prospects?',
        'Bank stock analysis today?',
        'What investment trends are emerging?',
        'What news is affecting the market?',
      ],
    },
    
    // Chat Panel (Mini Chat)
    chatPanel: {
      title: 'AI Assistant',
      apiSettingsTitle: 'API Settings',
      getApiKey: 'Get free API key',
      apiKeyPlaceholder: 'AIzaSy...',
      saveButton: 'Save',
      initialMessage: '✨ Hello! I am an AI financial assistant. I can help you analyze the Vietnamese market. What would you like to know?',
      errorMessage: 'Sorry, an error occurred. Please try again.',
      suggestionsLabel: 'Suggested questions:',
      inputPlaceholder: 'Enter your question...',
      inputDisabledPlaceholder: '⚠️ Configure API key',
      suggestedQuestions: [
        'What is the current Vietnamese stock market situation?',
        'How did VN-Index change?',
        'Which sectors have good prospects?',
        'Bank stock analysis?',
        'What investment trends are emerging?',
      ],
    },
    
    // Dashboard page
    dashboard: {
      title: 'Dashboard',
      subtitle: 'Real-time market insights and analytics',
      selectDate: 'Select any date to view historical data',
      refreshButton: 'Refresh',
      refreshData: 'Refresh data',
      timeframes: {
        '1H': '1 Hour',
        '1D': '1 Day',
        '1W': '1 Week',
        '1M': '1 Month',
      },
      metrics: {
        marketChange: 'Market Change',
        advancing: 'Advancing',
        totalVolume: 'Total Volume',
        avgSentiment: 'Avg Sentiment',
        stocksCount: 'stocks',
        decliningCount: 'declining',
        dailyVolume: 'daily volume',
        articles: 'articles',
      },
      chart: {
        title: 'Market Price Trend',
        liveData: 'Live data',
        dataPoints: 'data points',
        updatedEveryMinute: 'Updated every minute',
        noData: 'No chart data available',
      },
      topGainers: {
        title: 'Top Gainers',
        volume: 'Vol:',
        noData: 'No data available',
      },
      insights: {
        title: 'Market Insights',
        noData: 'No data available',
      },
      overview: {
        title: 'Market Overview',
        positiveMessage: 'Market showing positive momentum with',
        advancingStocks: 'advancing stocks vs',
        decliningStocks: 'declining stocks.',
        negativeMessage: 'Market showing mixed signals with',
        decliningStocksMessage: 'declining stocks.',
        sentiment: 'Sentiment score of',
        indicates: 'indicates',
        positive: 'positive',
        negative: 'negative',
        neutral: 'neutral',
        marketSentiment: 'market sentiment based on',
        analyzedArticles: 'analyzed articles.',
        lastUpdated: 'Last updated:',
        notAvailable: 'N/A',
      },
      errors: {
        title: 'Error Loading Data',
        loadingMessage: 'Failed to load dashboard',
      },
      loading: 'Loading Dashboard...',
      marketChangeInsight: 'Market change:',
        sentimentInsight: 'Sentiment:',
        positiveArticles: '% positive articles',
        volumeStrength: 'Volume strength:',
        sharesVolume: 'B shares',
      },

      // Asset Finder / Screener
      screener: {
        title: 'Asset Finder',
        subtitle: 'Discover stocks matching your criteria',
        refreshButton: 'Refresh',
        errors: {
          title: 'Error Loading Data',
        },
        filters: {
          sectionTitle: 'Search & Filter',
          symbolLabel: 'Symbol',
          symbolPlaceholder: 'e.g., VIC, VCB',
          minChangeLabel: 'Min Change %',
          minChangePlaceholder: '-10',
          maxChangeLabel: 'Max Change %',
          maxChangePlaceholder: '10',
          minVolumeLabel: 'Min Volume (M)',
          minVolumePlaceholder: '1',
          applyButton: 'Apply Filters',
          resetButton: 'Reset',
        },
        table: {
          symbol: 'Symbol',
          closePrice: 'Close Price',
          changePercent: 'Change %',
          volume: 'Volume',
          ma20: 'MA20',
          volatility: 'Volatility',
          action: 'Action',
          analyzeButton: 'Analyze',
          showingText: 'Showing',
          ofText: 'of',
          stocksText: 'stocks',
          noStocks: 'No stocks match your filters',
        },
        stats: {
          avgPriceChange: 'Avg Price Change',
          totalVolume: 'Total Volume',
          avgVolatility: 'Avg Volatility',
          gainersVsLosers: 'Gainers vs Losers',
        },
      },
    },
  vi: {
    // Chung
    language: 'Tiếng Việt',
    languageCode: 'vi',
    
    // Trang chủ
    home: {
      title: 'AEGIS LUMINA',
      subtitle: 'Lá Chắn AI Soi Chiếu Dữ Liệu Của Bạn',
      description: 'Được đặt tên theo lá chắn thần thánh của Zeus và Athena kết hợp với ánh sáng của trí tuệ. Một hệ thống AI cấp doanh nghiệp bảo vệ và soi chiếu toàn bộ dữ liệu tài chính của bạn với kiến trúc Lakehouse tiên tiến và chatbot RAG thông minh.',
      startWithMetallica: 'Bắt Đầu với Metallica AI',
      viewDashboard: 'Xem Dashboard',
      productionReady: 'Sản Xuất',
      version: 'Phiên Bản 1.0',
      november2025: 'Tháng 11 2025',
      
      // Tính năng
      aegisProtection: 'Bảo Vệ AEGIS',
      aegisProtectionDesc: 'Lá chắn thần thánh bảo vệ dữ liệu của bạn với kiến trúc Lakehouse của AWS - các lớp Bronze, Silver, Gold đảm bảo chất lượng dữ liệu.',
      aegisStats: '10.950 cổ phiếu • 12.027 tin tức • 18.250 chỉ số',
      
      luminaIntelligence: 'Trí Tuệ LUMINA',
      luminaIntelligenceDesc: 'Những hiểu biết được hỗ trợ bởi AI giúp làm sáng tỏ các mẫu ở thị trường tài chính Việt Nam bằng cách sử dụng công nghệ chatbot RAG nâng cao.',
      luminaStats: '10.585 vector • <10ms tìm kiếm • 768 chiều',
      
      lakehouseArch: 'Kiến Trúc Lakehouse',
      lakehouseArchDesc: 'Nền tảng dữ liệu hiện đại kết hợp tính linh hoạt của data lake với hiệu suất của data warehouse trên AWS S3.',
      lakehouseStats: 'Nén 92% • $6.32/tháng • Truy vấn 0.5-1s',
      
      vietnameseSBERT: 'Vietnamese SBERT',
      vietnameseSBERTDesc: 'Nhúng chuyên biệt cho ngôn ngữ Việt sử dụng mô hình keepitreal/vietnamese-sbert với cơ sở dữ liệu vector FAISS.',
      vietnameseSBERTStats: 'Nhúng 768 chiều • Xử lý theo lô • Thời gian thực',
      
      airflowPipeline: 'Đường Ống ETL Airflow',
      airflowPipelineDesc: 'Đường ống dữ liệu hàng ngày tự động với xử lý PySpark thông qua 7 giai đoạn - từ nạp dữ liệu đến xác thực.',
      airflowStats: '7 giai đoạn • Thời gian hoạt động 99.8% • ~7h mỗi ngày',
      
      awsCloud: 'Hạ Tầng Đám Mây AWS',
      awsCloudDesc: 'Nền tảng đám mây có thể mở rộng với lưu trữ S3, Glue Catalog và các truy vấn Athena để phân tích hiệu suất cao.',
      awsCloudStats: 'S3 • Glue • Athena • Tối ưu hóa chi phí',
      
      // Truy Cập Nhanh
      quickAccess: 'Truy Cập Nhanh',
      
      metallicaAI: 'Chatbot Metallica AI',
      metallicaAIDesc: 'Đặt câu hỏi về thị trường tài chính Việt Nam bằng ngôn ngữ tự nhiên',
      aiPowered: 'Được Hỗ Trợ AI',
      
      analyticsDashboard: 'Dashboard Phân Tích',
      analyticsDashboardDesc: 'Trực quan hóa thời gian thực về cổ phiếu, cảm xúc tin tức và xu hướng thị trường',
      realTime: 'Thời Gian Thực',
      
      assetFinder: 'Công Cụ Tìm Kiếm Tài Sản',
      assetFinderDesc: 'Tìm kiếm và lọc 10.950+ cổ phiếu Việt Nam với các tiêu chí nâng cao',
      stocks: '10.950 cổ phiếu',
      
      aboutAegis: 'Về AEGIS LUMINA',
      aboutAegisDesc: 'Tìm hiểu về kiến trúc Lakehouse, hệ thống RAG và kiến trúc đường ống Airflow của chúng tôi',
      documentation: 'Tài Liệu',
      
      // Hiệu Suất
      systemPerformance: 'Hiệu Suất Hệ Thống',
      costSavings: 'Tiết Kiệm Chi Phí',
      querySpeed: 'Tốc Độ Truy Vấn',
      faster: 'nhanh hơn',
      uptime: 'Thời Gian Hoạt Động',
      compression: 'Nén Dữ Liệu',
      spaceSaved: 'không gian tiết kiệm',
      totalStocks: 'Tổng Số Cổ Phiếu',
      newsArticles: 'Bài Báo Tin Tức',
      vectorsIndexed: 'Vector Được Lập Chỉ Mục',
      monthlyCost: 'Chi Phí Hàng Tháng',
      
      // Lời Kêu Gọi
      readyToExplore: 'Sẵn Sàng Khám Phá?',
      readyToExploreDesc: 'Bắt đầu hành trình của bạn với AEGIS LUMINA. Khám phá hiểu biết, phân tích dữ liệu và đưa ra quyết định sáng suốt với nền tảng phân tích tài chính được hỗ trợ bởi AI của chúng tôi.',
      viewUserGuide: 'Xem Hướng Dẫn Người Dùng',
      learnMore: 'Tìm Hiểu Thêm',
    },
    
    // Trang Chatbot
    chatbot: {
      title: '🤖 Trợ Lý Tài Chính AI',
      description: 'Hỏi đáp về thị trường chứng khoán Việt Nam với công nghệ RAG + Gemini',
      statsBanner: {
        newsArticles: 'tin tức tài chính',
        model: 'Model:',
        vectorDim: 'Chiều vector:',
      },
      apiKeySetup: {
        title: 'Gemini API Key',
        description: 'Để sử dụng chatbot, bạn cần cung cấp API key của Gemini.',
        label: 'API Key',
        placeholder: 'AIzaSy...',
        validate: 'Xác Thực API Key',
        validating: 'Đang kiểm tra...',
        valid: 'API key hợp lệ! Bạn có thể bắt đầu trò chuyện.',
        invalid: 'API key không hợp lệ. Vui lòng kiểm tra lại.',
        tipTitle: 'Lấy API key miễn phí:',
        getApiKey: 'Google AI Studio',
      },
      chat: {
        welcome: '👋 Xin chào! Tôi có thể giúp gì cho bạn?',
        suggestions: 'Câu hỏi gợi ý:',
        placeholder: 'Nhập câu hỏi của bạn...',
        disabledPlaceholder: 'Vui lòng xác thực API key trước',
        send: 'Gửi',
        enterToSend: '💡 Nhấn Enter để gửi, Shift+Enter để xuống dòng',
        showSources: 'Xem',
        hideSources: 'Ẩn',
        source: 'Nguồn',
        error: 'Lỗi:',
        errorMessage: 'Không thể xử lý câu hỏi của bạn',
        sendError: 'Đã xảy ra lỗi khi gửi tin nhắn. Vui lòng thử lại.',
        suggestedQuestions: [
          'Tình hình thị trường chứng khoán Việt Nam hiện tại?',
          'VN-Index biến động như thế nào tuần này?',
          'Các ngành nào đang có triển vọng tốt?',
        ],
      },
    },
    
    // Trang Chat (Oracle)
    oracleChat: {
      headerTitle: 'Trợ Lý Tài Chính AI',
      headerSubtitle: 'RAG-powered Vietnamese market insights',
      statusConnected: 'Kết Nối',
      statusNoKey: 'Chưa có API key',
      settingsTitle: 'Thiết Lập API',
      clearChat: 'Xóa cuộc trò chuyện',
      apiKeySettingsTitle: 'Gemini API Key',
      closeButton: 'Đóng',
      apiKeyHint: 'Nhập API key của bạn từ',
      apiKeyFree: '(miễn phí)',
      apiKeyPlaceholder: 'AIzaSy...',
      validateButton: 'Xác Thực',
      validatingButton: 'Đang kiểm tra...',
      validMessage: 'API key hợp lệ! Bạn có thể bắt đầu trò chuyện.',
      invalidMessage: 'API key không hợp lệ. Vui lòng kiểm tra lại.',
      initialMessage: '✨ Xin chào! Tôi là trợ lý tài chính AI. Tôi có thể giúp bạn phân tích thị trường chứng khoán Việt Nam. Bạn muốn tìm hiểu điều gì?',
      errorMessage: 'Xin lỗi, tôi gặp vấn đề khi xử lý câu hỏi. Vui lòng thử lại sau.',
      processingMessage: 'Đang xử lý yêu cầu của bạn...',
      suggestionsLabel: 'Câu hỏi gợi ý:',
      sourcesLabel: 'nguồn tin',
      sourceLabel: 'Nguồn',
      relatedLabel: 'liên quan',
      inputPlaceholder: 'Nhập câu hỏi của bạn...',
      inputDisabledPlaceholder: '⚠️ Vui lòng cấu hình API key trước',
      suggestedQuestionsData: [
        'Tình hình thị trường chứng khoán Việt Nam hiện tại?',
        'VN-Index biến động như thế nào tuần này?',
        'Các ngành nào đang có triển vọng tốt?',
        'Phân tích cổ phiếu ngân hàng hôm nay?',
        'Xu hướng đầu tư nào đang nổi bật?',
        'Tin tức nào đang ảnh hưởng thị trường?',
      ],
    },
    
    // Chat Panel (Mini Chat)
    chatPanel: {
      title: 'Trợ Lý AI',
      apiSettingsTitle: 'Thiết Lập API',
      getApiKey: 'Lấy API key miễn phí',
      apiKeyPlaceholder: 'AIzaSy...',
      saveButton: 'Lưu',
      initialMessage: '✨ Xin chào! Tôi là trợ lý tài chính AI. Tôi có thể giúp bạn phân tích thị trường Việt Nam. Bạn cần tư vấn gì?',
      errorMessage: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.',
      suggestionsLabel: 'Câu hỏi gợi ý:',
      inputPlaceholder: 'Nhập câu hỏi...',
      inputDisabledPlaceholder: '⚠️ Cấu hình API key',
      suggestedQuestions: [
        'Tình hình thị trường chứng khoán Việt Nam?',
        'VN-Index biến động như thế nào?',
        'Các ngành nào đang triển vọng?',
        'Phân tích cổ phiếu ngân hàng?',
        'Xu hướng đầu tư nổi bật?',
      ],
    },
    
    // Trang Dashboard
    dashboard: {
      title: 'Dashboard',
      subtitle: 'Thông tin thị trường thời gian thực và phân tích',
      selectDate: 'Chọn bất kỳ ngày nào để xem dữ liệu lịch sử',
      refreshButton: 'Làm Mới',
      refreshData: 'Làm mới dữ liệu',
      timeframes: {
        '1H': '1 Giờ',
        '1D': '1 Ngày',
        '1W': '1 Tuần',
        '1M': '1 Tháng',
      },
      metrics: {
        marketChange: 'Biến Động Thị Trường',
        advancing: 'Tăng Giá',
        totalVolume: 'Tổng Giao Dịch',
        avgSentiment: 'Cảm Xúc Trung Bình',
        stocksCount: 'cổ phiếu',
        decliningCount: 'giảm giá',
        dailyVolume: 'giao dịch hàng ngày',
        articles: 'bài viết',
      },
      chart: {
        title: 'Xu Hướng Giá Thị Trường',
        liveData: 'Dữ liệu trực tiếp',
        dataPoints: 'điểm dữ liệu',
        updatedEveryMinute: 'Cập nhật mỗi phút',
        noData: 'Không có dữ liệu biểu đồ',
      },
      topGainers: {
        title: 'Top Cổ Phiếu Tăng Giá',
        volume: 'Khối lượng:',
        noData: 'Không có dữ liệu',
      },
      insights: {
        title: 'Thông Tin Thị Trường',
        noData: 'Không có dữ liệu',
      },
      overview: {
        title: 'Tổng Quan Thị Trường',
        positiveMessage: 'Thị trường có động lực tích cực với',
        advancingStocks: 'cổ phiếu tăng giá so với',
        decliningStocks: 'giảm giá.',
        negativeMessage: 'Thị trường có tín hiệu hỗn hợp với',
        decliningStocksMessage: 'cổ phiếu giảm giá.',
        sentiment: 'Điểm cảm xúc',
        indicates: 'chỉ ra',
        positive: 'tích cực',
        negative: 'tiêu cực',
        neutral: 'trung lập',
        marketSentiment: 'cảm xúc thị trường dựa trên',
        analyzedArticles: 'bài viết được phân tích.',
        lastUpdated: 'Cập nhật lần cuối:',
        notAvailable: 'N/A',
      },
      errors: {
        title: 'Lỗi Tải Dữ Liệu',
        loadingMessage: 'Không thể tải dữ liệu dashboard',
      },
      loading: 'Đang Tải Dashboard...',
      marketChangeInsight: 'Biến động thị trường:',
      sentimentInsight: 'Cảm xúc:',
      positiveArticles: '% bài viết tích cực',
      volumeStrength: 'Sức mạnh giao dịch:',
      sharesVolume: 'tỷ cổ phiếu',
    },

    // Asset Finder / Screener
    screener: {
      title: 'Tìm Kiếm Tài Sản',
      subtitle: 'Khám phá các cổ phiếu phù hợp với tiêu chí của bạn',
      refreshButton: 'Làm Mới',
      errors: {
        title: 'Lỗi Tải Dữ Liệu',
      },
      filters: {
        sectionTitle: 'Tìm Kiếm & Lọc',
        symbolLabel: 'Mã Cổ Phiếu',
        symbolPlaceholder: 'ví dụ: VIC, VCB',
        minChangeLabel: 'Thay Đổi Tối Thiểu %',
        minChangePlaceholder: '-10',
        maxChangeLabel: 'Thay Đổi Tối Đa %',
        maxChangePlaceholder: '10',
        minVolumeLabel: 'Khối Lượng Tối Thiểu (M)',
        minVolumePlaceholder: '1',
        applyButton: 'Áp Dụng Bộ Lọc',
        resetButton: 'Đặt Lại',
      },
      table: {
        symbol: 'Mã Cổ Phiếu',
        closePrice: 'Giá Đóng Cửa',
        changePercent: 'Thay Đổi %',
        volume: 'Khối Lượng',
        ma20: 'MA20',
        volatility: 'Biến Động',
        action: 'Hành Động',
        analyzeButton: 'Phân Tích',
        showingText: 'Hiển Thị',
        ofText: 'của',
        stocksText: 'cổ phiếu',
        noStocks: 'Không có cổ phiếu phù hợp với bộ lọc của bạn',
      },
      stats: {
        avgPriceChange: 'Thay Đổi Giá Trung Bình',
        totalVolume: 'Tổng Khối Lượng',
        avgVolatility: 'Biến Động Trung Bình',
        gainersVsLosers: 'Tăng vs Giảm',
      },
    },
  }
};

/**
 * Thiết lập ngôn ngữ hiện tại
 */
export const setLanguage = (lang: Language) => {
  currentLanguage = lang;
  localStorage.setItem('language', lang);
  document.documentElement.lang = lang;
};

/**
 * Lấy ngôn ngữ hiện tại
 */
export const getLanguage = (): Language => {
  if (typeof window === 'undefined') return 'en';
  
  const stored = localStorage.getItem('language') as Language;
  if (stored && ['en', 'vi'].includes(stored)) {
    currentLanguage = stored;
    return stored;
  }
  
  // Phát hiện ngôn ngữ hệ thống
  const browserLang = navigator.language.split('-')[0];
  if (browserLang === 'vi') {
    setLanguage('vi');
    return 'vi';
  }
  
  return 'en';
};

/**
 * Dịch khóa với hỗ trợ nested keys (ví dụ: 'home.title')
 */
export const t = (key: string): string => {
  const lang = currentLanguage;
  const keys = key.split('.');
  
  let value: any = translations[lang];
  
  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k];
    } else {
      // Fallback to English if key not found
      value = translations['en'];
      for (const fallbackKey of keys) {
        if (value && typeof value === 'object' && fallbackKey in value) {
          value = value[fallbackKey];
        } else {
          return key; // Return key itself if not found
        }
      }
    }
  }
  
  return typeof value === 'string' ? value : key;
};

// Initialize language
export const initI18n = () => {
  getLanguage();
};
