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

      // Market Insights / News
      news: {
        title: 'Market Insights',
        subtitle: 'News sentiment analysis and financial intelligence',
        subtitleDemo: 'News sentiment analysis and financial intelligence (Demo Version)',
        refreshButton: 'Refresh',
        developmentWarning: '🚧 Under Development - Demo Data Only',
        developmentWarningText: 'This feature is currently under development. All data shown below is simulated for demonstration purposes and does not reflect real market sentiment or news analysis.',
        demoTag: '🚧 DEMO',
        stats: {
          totalArticles: 'Total Articles',
          daysAnalyzed: 'days analyzed',
          overallSentiment: 'Overall Sentiment',
          latestUpdate: 'Latest Update',
          positiveArticles: 'Positive Sentiment',
        },
        sentiment: {
          positive: 'Positive',
          negative: 'Negative',
          neutral: 'Neutral',
          bullish: 'Bullish',
          bearish: 'Bearish',
        },
        dailyBreakdown: 'Daily Sentiment Breakdown',
        articlesAnalyzed: 'articles analyzed',
          positiveLabel: '👍',
          negativeLabel: '👎',
          neutralLabel: '😐',
          positiveCount: 'Positive:',
          negativeCount: 'Negative:',
          neutralCount: 'Neutral:',
          noData: 'No sentiment data available',
        interpretation: {
          title: 'Sentiment Interpretation',
          positive: 'Positive (≥ 0.3)',
          positiveDesc: 'Bullish sentiment with strong positive coverage',
          neutral: 'Neutral (-0.3 to 0.3)',
          neutralDesc: 'Mixed or balanced market sentiment',
          negative: 'Negative (≤ -0.3)',
          negativeDesc: 'Bearish sentiment with negative coverage',
        },
      disclaimer: {
        title: '📊 Demo Data Notice',
        important: 'Important:',
        message: 'This Market Insights feature is currently in development. All sentiment scores, article counts, and trends displayed above are simulated data for demonstration purposes only.',
        bulletPoints: [
          'No real news sources are being analyzed',
          'Sentiment scores are randomly generated',
          'Data does not reflect actual market conditions',
          'Do not use this information for investment decisions',
        ],
      },
    },

    // Forecasts / Trends
    trends: {
      title: 'Forecasts',
      subtitle: 'AI-powered trend analysis and sector predictions',
      subtitleDemo: 'AI-powered trend analysis and sector predictions (Demo Version)',
      demoTag: '🚧 DEMO',
      refreshButton: 'Refresh',
      developmentWarning: '🚧 Under Development - Demo Data Only',
      developmentWarningText: 'This Forecasts feature is currently under development. All sector performance data, predictions, and analytics shown below are simulated for demonstration purposes and do not reflect actual market conditions.',
      stats: {
        marketAvgChange: 'Market Avg Change',
        gainersLosers: 'gainers • ',
        bestPerforming: 'Best Performing',
        worstPerforming: 'Worst Performing',
      },
      sectorCard: {
        stocks: 'stocks • Vol:',
        topGainers: 'Top Gainers',
        topLosers: 'Top Losers',
        noData: 'No sector data available',
      },
      marketOutlook: {
        title: 'Market Outlook',
        sectorDynamics: 'Sector Dynamics',
        keyInsights: 'Key Insights',
        investmentStrategy: 'Investment Strategy',
        positiveMessage: 'Market showing positive momentum with',
        sectorsInGreen: 'sectors in green.',
        mixedMessage: 'Market showing mixed signals with',
        sectorsDeclining: 'sectors declining.',
        sectorLeading: 'sector leading with',
        sectorLagging: 'while',
        change: 'change',
        avgChange: 'avg change of',
        totalVolume: 'Total trading volume across sectors:',
        sectorAnalyzed: 'sectors analyzed with',
        sectorMomentum: 'Sector momentum:',
        bullishTrend: 'Bullish trend',
        bearishTrend: 'Bearish trend',
        strategyText: 'Focus on sectors with positive momentum and strong gainers. Monitor declining sectors for potential reversal setups. Use volume and breadth to confirm trend strength across the market.',
        sharesLabel: 'B shares',
      },
      table: {
        title: 'Detailed Performance',
        sector: 'Sector',
        changePercent: 'Change %',
        stocks: 'Stocks',
        volume: 'Volume',
        topGainers: 'Top Gainers',
      },
      disclaimer: {
        title: '📊 Demo Data Notice',
        important: 'Important:',
        message: 'This Forecasts feature is currently in development. All sector performance data, trends, and analytics displayed above are simulated data for demonstration purposes only.',
        bulletPoints: [
          'Sector performance metrics are randomly generated',
          'Stock symbols and volumes do not reflect real market data',
          'Predictions and trends are for UI demonstration only',
          'Do not use this information for investment decisions',
        ],
      },
    },

    // About
    about: {
      tagline: 'The AI Shield That Illuminates Your Data',
      description: 'Named after the divine shield of Zeus and Athena (AEGIS) combined with the light of wisdom (LUMINA) – An AI system that protects and illuminates all your financial data, like the watchful eye of Athena upon her legendary shield.',
      version: 'Version 1.0',
      productionReady: 'Production Ready',
      november2025: 'November 2025',
      
      // Tabs
      overview: 'Overview',
      lakehouse: 'Lakehouse',
      ragChatbot: 'RAG Chatbot',
      airflowEtl: 'Airflow ETL',
      
      // Overview Section
      missionStatement: 'Mission Statement',
      missionText: 'We build a comprehensive financial data analytics platform that enables extraction of insights from Vietnam stock market data, news, and economic indicators using modern Lakehouse architecture combined with AI/ML capabilities.',
      costSavings: 'Cost savings vs traditional RDS',
      fasterQuerySpeed: 'Faster query speed',
      systemUptime: 'System uptime',
      
      projectOverview: 'Project Overview',
      keySolutions: 'Key Solutions',
      dataProcessed: 'Data Processed',
      stocks: 'Stocks',
      news: 'News',
      indicators: 'Indicators',
      symbols: 'Symbols',
      systemPerformance: 'System Performance',
      queryLatencyP50: 'Query Latency (P50)',
      queryLatencyP99: 'Query Latency (P99)',
      dataFreshness: 'Data Freshness',
      vectorSearchLatency: 'Vector Search',
      target: 'Target',
      actual: 'Actual',
      
      technologyStack: 'Technology Stack',
      cloudInfrastructure: 'Cloud Infrastructure',
      dataProcessing: 'Data Processing',
      backendApi: 'Backend & API',
      aiMlNlp: 'AI/ML & NLP',
      frontendStack: 'Frontend Stack',
      
      futureVision: 'Future Vision',
      phase1Immediate: 'Phase 1: Immediate',
      phase2ShortTerm: 'Phase 2: Short-term',
      phase3MediumTerm: 'Phase 3: Medium-term',
      phase4LongTerm: 'Phase 4: Long-term',
      week1_2: 'Week 1-2',
      month1_2: 'Month 1-2',
      month3_6: 'Month 3-6',
      month6_12: 'Month 6-12',
      
      developmentTeam: 'Development Team',
      teamDescription: 'This project is developed by a team of engineers passionate about Data Engineering, Machine Learning, and Financial Analytics.',
      dataEngineering: 'Data Engineering',
      dataEngineeringDesc: 'Lakehouse architecture, ETL pipelines, Data quality',
      aiMlDevelopment: 'AI/ML Development',
      aiMlDevelopmentDesc: 'RAG system, Embeddings, NLP processing',
      fullStackDevelopment: 'Full-stack Development',
      fullStackDevelopmentDesc: 'Backend API, Frontend UI, DevOps',
      
      openForCollaboration: 'Open for Collaboration:',
      collaborationText: 'We welcome contributions from the community. If you\'re interested in the project, check out the Guide section to learn how to contribute code or ideas!',
      
      // BE-FE & MCP Section
      backendFrontendMcp: 'Backend, Frontend & MCP Architecture',
      systemArchitectureDesc: 'The RAG chatbot system consists of three main components: FastAPI backend with RAG service, React frontend with Metallica personality, and optional MCP server for tool integration.',
      systemArchitecture: 'System Architecture',
      frontendLayer: 'Frontend Layer',
      frontendLayerDesc: 'React application with Metallica AI personality',
      backendLayer: 'Backend Layer (FastAPI)',
      backendLayerDesc: 'Core RAG service with Gemini integration',
      dataLayer: 'Data & Model Layer (AWS S3)',
      dataLayerDesc: 'Vector indices, embeddings, and metadata',
      
      // Backend Details
      backendFastapi: 'Backend (FastAPI + RAG Service)',
      coreComponents: 'Core Components',
      ragService: 'RAG Service',
      ragServiceItems: ['Query embedding (Vietnamese-SBERT)', 'FAISS vector search', 'Cross-encoder reranking', 'Context building with full text', 'Gemini LLM integration'],
      apiEndpoints: 'API Endpoints',
      apiEndpointsList: ['POST /api/v1/rag/validate-key', 'POST /api/v1/rag/query', 'GET /api/v1/rag/history', 'DELETE /api/v1/rag/history', 'GET /health'],
      keyFeatures: 'Key Features',
      asyncProcessing: 'Async Processing',
      asyncProcessingDesc: 'Non-blocking request handling with Python async/await',
      errorHandling: 'Error Handling',
      errorHandlingDesc: 'Graceful fallback for API failures',
      loggingFeature: 'Logging',
      loggingDesc: 'Structured JSON logs for debugging',
      cachingFeature: 'Caching',
      cachingDesc: 'Supabase + Redis for response caching',
      rateLimiting: 'Rate Limiting',
      rateLimitingDesc: 'Token-based API key management',
      corsEnabled: 'CORS Enabled',
      corsEnabledDesc: 'Cross-origin requests from frontend',
      
      // Frontend Details
      frontendReact: 'Frontend (React + TypeScript)',
      metallicaPersonality: 'Metallica AI Personality',
      visualIdentity: 'Visual Identity',
      visualIdentityItems: ['🎨 Metallica Avatar (3 locations)', '⚡ Lumina color scheme (primary/secondary)', '🎭 Glassmorphism UI design', '✨ Smooth animations & transitions'],
      personalityTraits: 'Personality',
      personalityItems: ['🎯 AEGIS Lumina messenger', '💬 Structured response format', '📚 Source citations with links', '🌐 Vietnamese-first language'],
      responseFormatNote: 'Response Format:',
      responseFormatDesc: 'Markdown-formatted answers with source citations, relevance scores, and keyword highlighting for financial analysis.',
      keyPagesFeatures: 'Key Pages & Features',
      chatPage: '💬 Chat Page',
      chatPageDesc: 'RAG chatbot interface with Metallica avatar, message history, source citations',
      dashboardPage: '📊 Dashboard',
      dashboardPageDesc: 'Real-time stock data visualization, technical indicators, market overview',
      assetFinder: '🔍 Asset Finder',
      assetFinderDesc: 'Advanced screening with filters for stock selection',
      
      // MCP Server
      mcpServer: 'MCP Server (Model Context Protocol)',
      mcpServerDesc: 'Optional Model Context Protocol server for LLM tool integration and advanced AI capabilities.',
      availableTools: 'Available Tools',
      stockAnalyzerTool: 'Stock Analyzer Tool',
      stockAnalyzerDesc: 'Query stock data, technical indicators, price history',
      newsFetcherTool: 'News Fetcher Tool',
      newsFetcherDesc: 'Retrieve latest news, sentiment analysis, trending topics',
      marketIntelligenceTool: 'Market Intelligence Tool',
      marketIntelligenceDesc: 'Macro indicators, economic events, market sentiment',
      portfolioAnalyzerTool: 'Portfolio Analyzer Tool',
      portfolioAnalyzerDesc: 'Portfolio optimization, risk assessment, rebalancing',
      integrationBenefits: 'Integration Benefits',
      extendedCapabilities: 'Extended Capabilities:',
      extendedCapabilitiesDesc: 'Gemini AI can use RAG tools for enhanced financial analysis',
      realtimeDataAccess: 'Real-time Data Access:',
      realtimeDataAccessDesc: 'Live stock prices, market data, news feeds',
      contextAwareness: 'Context Awareness:',
      contextAwarenessDesc: 'Tools provide rich context for LLM decision-making',
      autonomousWorkflows: 'Autonomous Workflows:',
      autonomousWorkflowsDesc: 'Multi-step analysis without user intervention',
      
      // End-to-End Flow
      endToEndDataFlow: 'End-to-End Data Flow',
      dataFlow1: 'User enters query in Chat interface → Frontend validates input & stores in state',
      dataFlow2: 'Frontend sends API request to backend → Backend receives query + API key + history',
      dataFlow3: 'RAG Service embeds query → Vietnamese-SBERT generates 768-dim vector',
      dataFlow4: 'FAISS vector search in S3 → Returns top-7 most similar documents (IndexFlatIP)',
      dataFlow5: 'Cross-encoder reranking → Reorders results by relevance score',
      dataFlow6: 'Context building with full text → Loads 2000 chars per doc from CSV cache (~6,988 chars total)',
      dataFlow7: 'Gemini LLM generation → Generates answer with Metallica personality (~800ms)',
      dataFlow8: 'Response formatting & source extraction → Markdown + source citations [{source, link}]',
      dataFlow9: 'Frontend receives response → Displays with Metallica avatar, sources, citations',
      totalResponseTime2: 'Total Response Time:',
      endToEndTime: '~2-5 seconds (end-to-end)',
      
      // Performance Metrics
      performanceMetrics: 'Performance Metrics',
      queryEmbeddingTime: '~50ms',
      queryEmbeddingLabel: 'Query Embedding',
      faissSearchTime: '<10ms',
      faissSearchLabel: 'FAISS Search',
      rerankingTime: '~100ms',
      rerankingLabel: 'Reranking',
      llmGenerationTime: '~800ms',
      llmGenerationLabel: 'LLM Generation',
      uptime: '99.8%',
      uptimeLabel: 'Uptime',
      indexedVectorsCount: '328K+',
      indexedVectorsLabel: 'Indexed Vectors',
      newsArticlesCount: '12K+',
      newsArticlesLabel: 'News Articles',
      retrievedDocsCount: '7',
      retrievedDocsLabel: 'Retrieved Docs',
      
      // Lakehouse Section
      lakehouseArchitecture: 'Lakehouse Architecture',
      lakehouseDescription: 'A modern data architecture that combines the best of Data Lakes and Data Warehouses, providing scalable storage with high-performance analytics capabilities.',
      medallionArchitecture: 'Medallion Architecture (Bronze-Silver-Gold)',
      
      bronzeLayer: 'Bronze Layer',
      bronzeLayerDesc: 'Raw data ingestion from sources',
      silverLayer: 'Silver Layer',
      silverLayerDesc: 'Cleaned & standardized data',
      goldLayer: 'Gold Layer',
      goldLayerDesc: 'Business-ready aggregates',
      
      dataSources: 'Data Sources',
      stockData: '📈 Stock Data',
      stockDataDesc: 'Source: VNStock API v3 • Symbols: 30 major stocks • Records: 10,950+ • Period: 365 days • Update: Real-time (2-5 min delay)',
      newsData: '📰 News Data',
      newsDataDesc: 'Source: Google Custom Search • Articles: 12,027 • Language: Vietnamese • Coverage: 1-3 years • Topics: Finance, Banking, Markets',
      macroData: '📊 Macro Data',
      macroDataDesc: 'Source: Economic APIs • Indicators: 50+ • Records: 18,250 • Period: 6 years (2020-2025) • Update: Daily/Weekly',
      
      performanceCostEfficiency: 'Performance & Cost Efficiency',
      costSavingsVsRds: 'Cost Savings vs RDS',
      queryLatency: 'Query Latency (P50)',
      dataCompression: 'Data Compression',
      monthlyQueryCost: 'Monthly Query Cost',
      
      awsInfrastructure: 'AWS Infrastructure',
      amazonS3: 'Amazon S3',
      amazonS3Desc: 'Data Lake storage with 3 layers (Bronze, Silver, Gold)',
      awsGlue: 'AWS Glue',
      awsGlueDesc: 'Data Catalog with 9 tables across 2 databases',
      awsAthena: 'AWS Athena',
      awsAthenaDesc: 'Serverless SQL queries on S3 data',
      
      // RAG Section
      ragChatbotSystem: 'RAG Chatbot System',
      ragDescription: 'Retrieval-Augmented Generation (RAG) chatbot that provides accurate, grounded answers about Vietnamese financial markets using real news data and advanced AI technology.',
      
      howRagWorks: 'How RAG Works',
      queryEmbedding: 'Query Embedding',
      queryEmbeddingDesc: 'Convert user question to 768-dim vector using Vietnamese-SBERT',
      vectorSearch: 'Vector Search',
      vectorSearchDesc: 'Search 10,585 indexed articles using FAISS for top-5 relevant docs',
      reranking: 'Reranking',
      rerankingDesc: 'Cross-encoder reranks results for better relevance',
      contextPreparation: 'Context Preparation',
      contextPreparationDesc: 'Format top-3 articles as context with sources and metadata',
      llmGeneration: 'LLM Generation',
      llmGenerationDesc: 'Google Gemini generates natural response based on context',
      responseFormatting: 'Response Formatting',
      responseFormattingDesc: 'Return answer with sources, scores, and confidence',
      totalResponseTime: 'Total Response Time:',
      
      ragTechnologyStack: 'Technology Stack',
      embeddingSearch: 'Embedding & Search',
      generationStorage: 'Generation & Storage',
      
      ragKeyFeatures: 'Key Features',
      noHallucination: 'No Hallucination',
      noHallucinationDesc: 'Answers grounded in real news articles with source citations',
      vietnameseSupport: 'Vietnamese Support',
      vietnameseSupportDesc: 'Optimized for Vietnamese language queries and responses',
      fastAccurate: 'Fast & Accurate',
      fastAccurateDesc: 'Sub-second vector search with high relevance scores',
      
      ragSystemStatistics: 'System Statistics',
      indexedVectors: 'Indexed Vectors',
      newsArticles: 'News Articles',
      vectorSearchTime: 'Vector Search Time',
      embeddingDimensions: 'Embedding Dimensions',
      
      initialRagTraining: 'Initial RAG Training (Kaggle)',
      trainingProcess: 'Training Process',
      technicalSpecifications: 'Technical Specifications',
      
      // Airflow Section
      airflowEtlPipeline: 'Apache Airflow ETL Pipeline',
      airflowDescription: 'Fully automated ETL pipeline orchestrated by Apache Airflow, processing data from multiple sources through Bronze-Silver-Gold layers using PySpark for distributed computing.',
      
      etlPipelineStages: 'ETL Pipeline Stages',
      bronzeLayerStage: 'Bronze Layer (08:00-09:30 UTC)',
      bronzeLayerStageDesc: 'Data collection from APIs',
      silverLayerStage: 'Silver Layer (10:00-11:30 UTC)',
      silverLayerStageDesc: 'Data cleaning & standardization',
      goldLayerStage: 'Gold Layer (13:00-14:30 UTC)',
      goldLayerStageDesc: 'Feature engineering & aggregation',
      ragPipelineStage: 'RAG Pipeline (14:30-15:00 UTC)',
      ragPipelineStageDesc: 'Vector database update for chatbot',
      qualityCheckStage: 'Quality Check (15:00-15:15 UTC)',
      qualityCheckStageDesc: 'Data validation & monitoring',
      glueCatalogStage: 'Glue Catalog Update (15:30-15:45 UTC)',
      glueCatalogStageDesc: 'Metadata synchronization',
      notificationStage: 'Notification (15:45-16:00 UTC)',
      notificationStageDesc: 'Status reporting',
      
      totalPipelineDuration: 'Total Pipeline Duration:',
      dailyAt: 'Daily at 09:00 UTC',
      
      pipelineTechnologyStack: 'Technology Stack',
      orchestration: 'Orchestration',
      processing: 'Processing',
      ragPipeline: 'RAG Pipeline',
      
      pysparkDistributed: 'PySpark Distributed Processing',
      pysparkDesc: 'PySpark enables distributed data processing across multiple nodes, handling large-scale data transformations efficiently with parallel computing.',
      clusterConfiguration: 'Cluster Configuration',
      keyOperations: 'Key Operations',
      
      pipelineFeatures: 'Key Features',
      fullyAutomated: 'Fully Automated',
      fullyAutomatedDesc: 'Runs daily without manual intervention, with automatic retry on failure',
      parallelProcessing: 'Parallel Processing',
      parallelProcessingDesc: 'PySpark distributes workload across multiple nodes for faster processing',
      qualityMonitoring: 'Quality Monitoring',
      qualityMonitoringDesc: 'Built-in data quality checks and alerts for anomaly detection',
      
      pipelineStatistics: 'Pipeline Statistics',
      dailyRunsYear: 'Daily Runs/Year',
      successRate: 'Success Rate',
      averageDuration: 'Average Duration',
      dataLayersProcessed: 'Data Layers Processed',
      
      infrastructure: 'Infrastructure',
      airflowDeployment: 'Airflow Deployment',
      sparkCluster: 'Spark Cluster',
    },

    // Reports
    reports: {
      title: 'Reports',
      subtitle: 'AI-Generated Market Analysis Reports (Demo Version)',
      demoTag: '🚧 DEMO',
      generateButton: 'Generate Report',
      developmentWarning: '🚧 Under Development - Demo Data Only',
      developmentWarningText: 'This Reports feature is currently under development. All reports, analyses and insights generated by AI displayed below are simulated for demonstration purposes and do not reflect actual market analysis.',
      analysisInProgress: 'Analysis In Progress',
      processingMessage: 'Processing market data and generating insights...',
      eta: 'ETA:',
      minutes: 'minutes',
      created: 'Created At',
      status: 'Status',
      confidence: 'Confidence:',
      download: 'Download',
      share: 'Share',
      view: 'View',
      demoFeatureNotFunctional: 'Demo feature - not functional',
      disclaimer: {
        title: '📊 Demo Data Notice',
        important: 'Important:',
        message: 'This Reports feature is currently under development. All reports, confidence scores and insights generated by AI shown above are simulated data for demonstration purposes only.',
        bulletPoints: [
          'No actual AI analysis is being performed',
          'Reports cannot be downloaded or shared',
          'Confidence scores are randomly generated',
          'Do not use this information for investment decisions',
        ],
      },
    },

    // Guide
    guide: {
      header: 'User Guide',
      headerDescription: 'Complete instructions for using the platform and contributing to the project',
      
      // Tab names
      forUsers: 'For Users',
      forDevelopers: 'For Developers',
      
      // User Guide Section
      // Dashboard
      dashboard: {
        title: 'Dashboard',
        description: 'The Dashboard is your central hub for monitoring Vietnam stock market performance and key metrics.',
        features: 'Features:',
        
        datePicker: {
          title: 'Date Picker',
          description: 'Select any date to view historical market data. Click the date button in the top section, choose a date from the calendar, and the dashboard will update automatically. No date restrictions - explore data from any available period.',
        },
        
        refreshButton: {
          title: 'Refresh Button',
          description: 'Click the refresh icon to manually reload data. The dashboard no longer auto-refreshes to prevent unnecessary API calls. Use this when you need updated information.',
        },
        
        timeRangeFilters: {
          title: 'Time Range Filters',
          description: 'Use the 1D, 1W, 1M, 3M, 1Y buttons to quickly jump to common time ranges. These buttons are located on a separate row below the date picker and refresh button for easy access.',
        },
      },
      
      // Asset Finder / Screener
      assetFinder: {
        title: 'Asset Finder (Screener)',
        description: 'Screen and filter Vietnamese stocks based on various criteria to find investment opportunities.',
        howToUse: 'How to Use:',
        tip1: 'Use the search bar to filter stocks by symbol or name',
        tip2: 'Apply filters for price range, volume, market cap, and performance',
        tip3: 'Sort results by clicking column headers',
        tip4: 'Click refresh to get the latest stock data',
      },
      
      // Metallica Chatbot
      metallicaChatbot: {
        title: 'Metallica Chatbot',
        description: 'Ask questions about Vietnamese financial news and get AI-powered insights using our RAG (Retrieval-Augmented Generation) system.',
        setup: 'Setup:',
        requiredGeminiKey: 'Required: Gemini API Key',
        setupStep1: 'Visit Google AI Studio',
        setupStep2: 'Create a free Gemini API key',
        setupStep3: 'Enter the key in the chatbot interface',
        setupStep4: 'Click "Validate" to activate the chatbot',
        googleAIStudio: 'Google AI Studio',
        
        tipsForBestResults: 'Tips for Best Results:',
        tip1: 'Ask specific questions about Vietnamese stocks, sectors, or companies',
        tip2: 'Questions can be in English or Vietnamese',
        tip3: 'The system searches 12,000+ indexed news articles for context',
        tip4: 'Response time is typically under 2 seconds',
      },
      
      // Demo Features
      demoFeatures: {
        title: 'Demo Features',
        description: 'The following features are currently in demo mode with mock data:',
        
        marketInsights: {
          title: 'Market Insights',
          description: 'Shows sample sentiment analysis data for demonstration purposes.',
        },
        
        forecasts: {
          title: 'Forecasts',
          description: 'Displays mock Vietnam sector performance data (Banking, Real Estate, etc.).',
        },
        
        reports: {
          title: 'Reports',
          description: 'Shows sample reports with disabled generation features.',
        },
        
        footer: 'These features are marked with a 🚧 DEMO badge and include development warnings. They will be activated with real data in future releases.',
      },
      
      // Developer Guide Section
      // Project Setup
      projectSetup: {
        title: 'Project Setup',
        
        prerequisites: 'Prerequisites',
        frontend: 'Frontend',
        frontendReq: 'Node.js 18+, npm/yarn',
        backend: 'Backend',
        backendReq: 'Python 3.9+, pip',
        awsAccount: 'AWS Account',
        awsReq: 'S3, Glue, Athena access',
        geminiKey: 'Gemini API Key',
        geminiKeyReq: 'For chatbot functionality',
        
        installationSteps: 'Installation Steps',
        cloneRepository: 'Clone Repository',
        frontendSetup: 'Frontend Setup',
        backendSetup: 'Backend Setup',
        configureAWS: 'Configure AWS',
      },
      
      // Architecture Overview
      architectureOverview: {
        title: 'Architecture Overview',
        description: 'Understanding the system architecture is crucial for contributing effectively.',
        
        bronzeLayer: {
          title: 'Bronze Layer',
          description: 'Raw data ingestion',
        },
        bronze1: 'VNStock API data',
        bronze2: 'Google CSE news',
        bronze3: 'Economic indicators',
        
        silverLayer: {
          title: 'Silver Layer',
          description: 'Cleaned & enriched',
        },
        silver1: 'Data validation',
        silver2: 'Schema normalization',
        silver3: 'Quality checks',
        
        goldLayer: {
          title: 'Gold Layer',
          description: 'Query-optimized',
        },
        gold1: 'Aggregated metrics',
        gold2: 'Business views',
        gold3: 'Performance indexes',
        
        keyComponents: 'Key Components',
        airflowDAGs: 'Airflow DAGs: Daily ETL orchestration (09:00 UTC)',
        pysparkJobs: 'PySpark Jobs: Distributed data processing',
        awsGlue: 'AWS Glue: Metadata catalog with 9 tables',
        athena: 'Athena: SQL-on-S3 query engine',
        faiss: 'FAISS: Vector search for RAG chatbot',
      },
      
      // Development Workflow
      developmentWorkflow: {
        title: 'Development Workflow',
        
        branchingStrategy: 'Branching Strategy',
        main: 'main - Production-ready code',
        develop: 'develop - Integration branch for features',
        feature: 'feature/* - New features or enhancements',
        bugfix: 'bugfix/* - Bug fixes',
        
        testingRequirements: 'Testing Requirements',
        test1: 'Write unit tests for all new features',
        test2: 'Ensure integration tests pass before PR',
        test3: 'Test locally with sample data',
        test4: 'Verify TypeScript types (no any types)',
      },
      
      // How to Contribute
      howToContribute: {
        title: 'How to Contribute',
        
        step1: {
          title: 'Fork & Clone',
          description: 'Fork the repository and clone it to your local machine',
        },
        
        step2: {
          title: 'Create Branch',
          description: 'Create a new branch following naming conventions: feature/your-feature-name',
        },
        
        step3: {
          title: 'Make Changes',
          description: 'Implement your feature with clean, documented code',
        },
        
        step4: {
          title: 'Test Thoroughly',
          description: 'Write and run tests to ensure everything works',
        },
        
        step5: {
          title: 'Submit PR',
          description: 'Create a pull request with a clear description of changes',
        },
        
        codeStyleGuidelines: 'Code Style Guidelines',
        guideline1: 'Follow TypeScript/Python best practices',
        guideline2: 'Use meaningful variable and function names',
        guideline3: 'Add comments for complex logic',
        guideline4: 'Keep functions small and focused',
        guideline5: 'Run linters before committing (ESLint, Black)',
      },
      
      // Useful Resources
      usefulResources: {
        title: 'Useful Resources',
        
        projectDocumentation: {
          title: 'Project Documentation',
          description: 'Learn about the project architecture and goals',
        },
        
        awsAthenaDocs: {
          title: 'AWS Athena Docs',
          description: 'Query language and optimization guides',
        },
        
        pysparkAPI: {
          title: 'PySpark API',
          description: 'Reference for data processing jobs',
        },
        
        reactDocumentation: {
          title: 'React Documentation',
          description: 'Frontend framework reference',
        },
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

    // Market Insights / News
    news: {
      title: 'Thông Tin Thị Trường',
      subtitle: 'Phân tích cảm xúc tin tức và trí tuệ tài chính',
      subtitleDemo: 'Phân tích cảm xúc tin tức và trí tuệ tài chính (Phiên Bản Demo)',
      refreshButton: 'Làm Mới',
      developmentWarning: '🚧 Đang Phát Triển - Chỉ Dữ Liệu Demo',
      developmentWarningText: 'Tính năng này hiện đang được phát triển. Tất cả dữ liệu được hiển thị dưới đây được mô phỏng cho mục đích trình diễn và không phản ánh cảm xúc thị trường hoặc phân tích tin tức thực tế.',
      demoTag: '🚧 DEMO',
      stats: {
        totalArticles: 'Tổng Số Bài Viết',
        daysAnalyzed: 'ngày được phân tích',
        overallSentiment: 'Cảm Xúc Tổng Thể',
        latestUpdate: 'Cập Nhật Mới Nhất',
        positiveArticles: 'Cảm Xúc Tích Cực',
      },
      sentiment: {
        positive: 'Tích Cực',
        negative: 'Tiêu Cực',
        neutral: 'Trung Lập',
        bullish: 'Lạc Quan',
        bearish: 'Bi Quan',
      },
      dailyBreakdown: 'Phân Tích Cảm Xúc Hàng Ngày',
      articlesAnalyzed: 'bài viết được phân tích',
      positiveLabel: '👍',
      negativeLabel: '👎',
      neutralLabel: '😐',
      positiveCount: 'Tích Cực:',
      negativeCount: 'Tiêu Cực:',
      neutralCount: 'Trung Lập:',
      noData: 'Không có dữ liệu cảm xúc',
      interpretation: {
        title: 'Giải Thích Cảm Xúc',
        positive: 'Tích Cực (≥ 0.3)',
        positiveDesc: 'Cảm xúc lạc quan với lưu lượng tích cực mạnh',
        neutral: 'Trung Lập (-0.3 đến 0.3)',
        neutralDesc: 'Cảm xúc thị trường hỗn hợp hoặc cân bằng',
        negative: 'Tiêu Cực (≤ -0.3)',
        negativeDesc: 'Cảm xúc bi quan với lưu lượng tiêu cực',
      },
      disclaimer: {
        title: '📊 Thông Báo Dữ Liệu Demo',
        important: 'Quan Trọng:',
        message: 'Tính năng Market Insights này hiện đang được phát triển. Tất cả các điểm cảm xúc, số lượng bài viết và xu hướng được hiển thị ở trên là dữ liệu mô phỏng chỉ cho mục đích trình diễn.',
        bulletPoints: [
          'Không có nguồn tin tức thực tế nào được phân tích',
          'Điểm cảm xúc được tạo ngẫu nhiên',
          'Dữ liệu không phản ánh điều kiện thị trường thực tế',
          'Không sử dụng thông tin này để quyết định đầu tư',
        ],
      },
    },

    // Forecasts / Trends
    trends: {
      title: 'Dự Báo',
      subtitle: 'Phân tích xu hướng do AI hỗ trợ và dự đoán ngành',
      subtitleDemo: 'Phân tích xu hướng do AI hỗ trợ và dự đoán ngành (Phiên Bản Demo)',
      demoTag: '🚧 DEMO',
      refreshButton: 'Làm Mới',
      developmentWarning: '🚧 Đang Phát Triển - Chỉ Dữ Liệu Demo',
      developmentWarningText: 'Tính năng Dự Báo này hiện đang được phát triển. Tất cả dữ liệu hiệu suất ngành, dự đoán và phân tích được hiển thị dưới đây được mô phỏng cho mục đích trình diễn và không phản ánh điều kiện thị trường thực tế.',
      stats: {
        marketAvgChange: 'Thay Đổi Trung Bình Thị Trường',
        gainersLosers: 'tăng • ',
        bestPerforming: 'Hiệu Suất Tốt Nhất',
        worstPerforming: 'Hiệu Suất Tồi Tệ Nhất',
      },
      sectorCard: {
        stocks: 'cổ phiếu • Khối lượng:',
        topGainers: 'Top Tăng Giá',
        topLosers: 'Top Giảm Giá',
        noData: 'Không có dữ liệu ngành',
      },
      marketOutlook: {
        title: 'Triển Vọng Thị Trường',
        sectorDynamics: 'Động Lực Ngành',
        keyInsights: 'Những Hiểu Biết Chính',
        investmentStrategy: 'Chiến Lược Đầu Tư',
        positiveMessage: 'Thị trường có động lực tích cực với',
        sectorsInGreen: 'ngành xanh.',
        mixedMessage: 'Thị trường có tín hiệu hỗn hợp với',
        sectorsDeclining: 'ngành giảm.',
        sectorLeading: 'ngành dẫn đầu với',
        sectorLagging: 'trong khi',
        change: 'thay đổi',
        avgChange: 'thay đổi trung bình của',
        totalVolume: 'Tổng khối lượng giao dịch trên các ngành:',
        sectorAnalyzed: 'ngành được phân tích với',
        sectorMomentum: 'Động lực ngành:',
        bullishTrend: 'xu hướng Lạc Quan',
        bearishTrend: 'xu hướng Bi Quan',
        strategyText: 'Tập trung vào các ngành có động lực tích cực và những người tăng giá mạnh. Giám sát các ngành đang suy giảm để tìm kiếm các cơ hội đảo chiều tiềm năng. Sử dụng khối lượng và chiều rộng để xác nhận sức mạnh xu hướng trên toàn thị trường.',
        sharesLabel: 'tỷ cổ phiếu',
      },
      table: {
        title: 'Hiệu Suất Chi Tiết',
        sector: 'Ngành',
        changePercent: 'Thay Đổi %',
        stocks: 'Cổ Phiếu',
        volume: 'Khối Lượng',
        topGainers: 'Top Tăng Giá',
      },
      disclaimer: {
        title: '📊 Thông Báo Dữ Liệu Demo',
        important: 'Quan Trọng:',
        message: 'Tính năng Dự Báo này hiện đang được phát triển. Tất cả dữ liệu hiệu suất ngành, xu hướng và phân tích được hiển thị ở trên là dữ liệu mô phỏng chỉ cho mục đích trình diễn.',
        bulletPoints: [
          'Các số liệu hiệu suất ngành được tạo ngẫu nhiên',
          'Các ký hiệu cổ phiếu và khối lượng không phản ánh dữ liệu thị trường thực tế',
          'Dự đoán và xu hướng chỉ cho mục đích trình diễn giao diện',
          'Không sử dụng thông tin này để quyết định đầu tư',
        ],
      },
    },

    // Reports
    reports: {
      title: 'Báo Cáo',
      subtitle: 'Báo cáo phân tích thị trường được tạo bởi AI (Phiên Bản Demo)',
      demoTag: '🚧 DEMO',
      generateButton: 'Tạo Báo Cáo',
      developmentWarning: '🚧 Đang Phát Triển - Chỉ Dữ Liệu Demo',
      developmentWarningText: 'Tính năng Reports này hiện đang được phát triển. Tất cả báo cáo, phân tích và những hiểu biết được tạo bởi AI được hiển thị dưới đây được mô phỏng cho mục đích trình diễn và không phản ánh phân tích thị trường thực tế.',
      analysisInProgress: 'Phân Tích Đang Tiến Hành',
      processingMessage: 'Xử lý dữ liệu thị trường và tạo hiểu biết...',
      eta: 'Dự Kiến:',
      minutes: 'phút',
      created: 'Tạo Lúc',
      status: 'Trạng Thái',
      confidence: 'Độ Tin Cây:',
      download: 'Tải Xuống',
      share: 'Chia Sẻ',
      view: 'Xem',
      demoFeatureNotFunctional: 'Tính năng demo - không hoạt động',
      disclaimer: {
        title: '📊 Thông Báo Dữ Liệu Demo',
        important: 'Quan Trọng:',
        message: 'Tính năng Reports này hiện đang được phát triển. Tất cả báo cáo, điểm độ tin cây và những hiểu biết được tạo bởi AI được hiển thị ở trên là dữ liệu mô phỏng chỉ cho mục đích trình diễn.',
        bulletPoints: [
          'Không có phân tích AI thực tế nào được thực hiện',
          'Báo cáo không thể tải xuống hoặc chia sẻ',
          'Điểm độ tin cây được tạo ngẫu nhiên',
          'Không sử dụng thông tin này để quyết định đầu tư',
        ],
      },
    },

    // Guide Vietnamese
    guide: {
      header: 'Hướng Dẫn Người Dùng',
      headerDescription: 'Hướng dẫn hoàn chỉnh để sử dụng nền tảng và đóng góp cho dự án',
      
      // Tab names
      forUsers: 'Dành cho Người Dùng',
      forDevelopers: 'Dành cho Nhà Phát Triển',
      
      // User Guide Section
      // Dashboard
      dashboard: {
        title: 'Bảng Điều Khiển',
        description: 'Bảng Điều Khiển là trung tâm của bạn để giám sát hiệu suất thị trường chứng khoán Việt Nam và các chỉ số chính.',
        features: 'Tính Năng:',
        
        datePicker: {
          title: 'Chọn Ngày',
          description: 'Chọn bất kỳ ngày nào để xem dữ liệu thị trường lịch sử. Nhấp vào nút ngày ở phần trên cùng, chọn ngày từ lịch, và bảng điều khiển sẽ cập nhật tự động. Không có hạn chế về ngày - khám phá dữ liệu từ bất kỳ thời kỳ nào có sẵn.',
        },
        
        refreshButton: {
          title: 'Nút Làm Mới',
          description: 'Nhấp vào biểu tượng làm mới để tải lại dữ liệu theo cách thủ công. Bảng điều khiển không còn tự động làm mới để ngăn chặn các cuộc gọi API không cần thiết. Sử dụng điều này khi bạn cần thông tin cập nhật.',
        },
        
        timeRangeFilters: {
          title: 'Bộ Lọc Khoảng Thời Gian',
          description: 'Sử dụng các nút 1D, 1W, 1M, 3M, 1Y để nhanh chóng chuyển đến các khoảng thời gian phổ biến. Các nút này được đặt trên một hàng riêng biệt bên dưới nút chọn ngày và nút làm mới để dễ dàng truy cập.',
        },
      },
      
      // Asset Finder / Screener
      assetFinder: {
        title: 'Công Cụ Tìm Tài Sản (Screener)',
        description: 'Lọc và tìm kiếm các cổ phiếu Việt Nam dựa trên nhiều tiêu chí khác nhau để tìm kiếm cơ hội đầu tư.',
        howToUse: 'Cách Sử Dụng:',
        tip1: 'Sử dụng thanh tìm kiếm để lọc cổ phiếu theo ký hiệu hoặc tên',
        tip2: 'Áp dụng các bộ lọc cho phạm vi giá, khối lượng, vốn hóa thị trường và hiệu suất',
        tip3: 'Sắp xếp kết quả bằng cách nhấp vào tiêu đề cột',
        tip4: 'Nhấp vào làm mới để nhận dữ liệu chứng khoán mới nhất',
      },
      
      // Metallica Chatbot
      metallicaChatbot: {
        title: 'Chatbot Metallica',
        description: 'Đặt câu hỏi về tin tức tài chính Việt Nam và nhận thông tin chi tiết được hỗ trợ bởi AI bằng cách sử dụng hệ thống RAG (Retrieval-Augmented Generation) của chúng tôi.',
        setup: 'Cài Đặt:',
        requiredGeminiKey: 'Bắt Buộc: Khóa API Gemini',
        setupStep1: 'Truy cập Google AI Studio',
        setupStep2: 'Tạo khóa API Gemini miễn phí',
        setupStep3: 'Nhập khóa trong giao diện chatbot',
        setupStep4: 'Nhấp vào "Xác Thực" để kích hoạt chatbot',
        googleAIStudio: 'Google AI Studio',
        
        tipsForBestResults: 'Mẹo Cho Kết Quả Tốt Nhất:',
        tip1: 'Đặt những câu hỏi cụ thể về cổ phiếu, ngành hoặc công ty Việt Nam',
        tip2: 'Câu hỏi có thể bằng tiếng Anh hoặc tiếng Việt',
        tip3: 'Hệ thống tìm kiếm hơn 12.000 bài báo tin tức được lập chỉ mục',
        tip4: 'Thời gian phản ứng thường dưới 2 giây',
      },
      
      // Demo Features
      demoFeatures: {
        title: 'Tính Năng Demo',
        description: 'Các tính năng sau đây hiện đang ở chế độ demo với dữ liệu giả:',
        
        marketInsights: {
          title: 'Thông Tin Thị Trường',
          description: 'Hiển thị dữ liệu phân tích tình cảm mẫu cho mục đích trình diễn.',
        },
        
        forecasts: {
          title: 'Dự Báo',
          description: 'Hiển thị dữ liệu hiệu suất ngành Việt Nam giả (Ngân Hàng, Bất Động Sản, v.v.).',
        },
        
        reports: {
          title: 'Báo Cáo',
          description: 'Hiển thị các báo cáo mẫu với các tính năng tạo bị vô hiệu hóa.',
        },
        
        footer: 'Các tính năng này được đánh dấu bằng huy hiệu 🚧 DEMO và bao gồm các cảnh báo phát triển. Chúng sẽ được kích hoạt với dữ liệu thực trong các phiên bản tương lai.',
      },
      
      // Developer Guide Section
      // Project Setup
      projectSetup: {
        title: 'Cài Đặt Dự Án',
        
        prerequisites: 'Yêu Cầu Trước',
        frontend: 'Frontend',
        frontendReq: 'Node.js 18+, npm/yarn',
        backend: 'Backend',
        backendReq: 'Python 3.9+, pip',
        awsAccount: 'Tài Khoản AWS',
        awsReq: 'Truy cập S3, Glue, Athena',
        geminiKey: 'Khóa API Gemini',
        geminiKeyReq: 'Cho chức năng chatbot',
        
        installationSteps: 'Các Bước Cài Đặt',
        cloneRepository: 'Nhân Bản Kho Lưu Trữ',
        frontendSetup: 'Cài Đặt Frontend',
        backendSetup: 'Cài Đặt Backend',
        configureAWS: 'Cấu Hình AWS',
      },
      
      // Architecture Overview
      architectureOverview: {
        title: 'Tổng Quan Kiến Trúc',
        description: 'Hiểu rõ kiến trúc hệ thống là rất quan trọng để đóng góp hiệu quả.',
        
        bronzeLayer: {
          title: 'Lớp Bronze',
          description: 'Nạp dữ liệu thô',
        },
        bronze1: 'Dữ liệu API VNStock',
        bronze2: 'Tin tức Google CSE',
        bronze3: 'Chỉ số kinh tế',
        
        silverLayer: {
          title: 'Lớp Silver',
          description: 'Dữ liệu đã làm sạch & làm phong phú',
        },
        silver1: 'Xác thực dữ liệu',
        silver2: 'Chuẩn hóa lược đồ',
        silver3: 'Kiểm tra chất lượng',
        
        goldLayer: {
          title: 'Lớp Gold',
          description: 'Tối ưu hóa cho truy vấn',
        },
        gold1: 'Chỉ số tổng hợp',
        gold2: 'Chế độ xem kinh doanh',
        gold3: 'Chỉ số hiệu suất',
        
        keyComponents: 'Các Thành Phần Chính',
        airflowDAGs: 'Airflow DAGs: Sắp xếp ETL hàng ngày (09:00 UTC)',
        pysparkJobs: 'PySpark Jobs: Xử lý dữ liệu phân tán',
        awsGlue: 'AWS Glue: Danh mục siêu dữ liệu với 9 bảng',
        athena: 'Athena: Công cụ truy vấn SQL-on-S3',
        faiss: 'FAISS: Tìm kiếm vectơ cho chatbot RAG',
      },
      
      // Development Workflow
      developmentWorkflow: {
        title: 'Quy Trình Phát Triển',
        
        branchingStrategy: 'Chiến Lược Nhánh',
        main: 'main - Mã sẵn sàng cho sản xuất',
        develop: 'develop - Nhánh tích hợp cho các tính năng',
        feature: 'feature/* - Các tính năng hoặc cải tiến mới',
        bugfix: 'bugfix/* - Sửa lỗi',
        
        testingRequirements: 'Yêu Cầu Kiểm Tra',
        test1: 'Viết các bài kiểm tra đơn vị cho tất cả các tính năng mới',
        test2: 'Đảm bảo các bài kiểm tra tích hợp vượt qua trước PR',
        test3: 'Kiểm tra cục bộ với dữ liệu mẫu',
        test4: 'Xác minh các loại TypeScript (không có loại bất kỳ)',
      },
      
      // How to Contribute
      howToContribute: {
        title: 'Cách Đóng Góp',
        
        step1: {
          title: 'Fork & Nhân Bản',
          description: 'Fork kho lưu trữ và nhân bản nó vào máy cục bộ của bạn',
        },
        
        step2: {
          title: 'Tạo Nhánh',
          description: 'Tạo nhánh mới theo quy ước đặt tên: feature/your-feature-name',
        },
        
        step3: {
          title: 'Thực Hiện Thay Đổi',
          description: 'Triển khai tính năng của bạn với mã sạch, được ghi chép',
        },
        
        step4: {
          title: 'Kiểm Tra Kỹ Lưỡng',
          description: 'Viết và chạy các bài kiểm tra để đảm bảo mọi thứ hoạt động',
        },
        
        step5: {
          title: 'Gửi PR',
          description: 'Tạo yêu cầu kéo với mô tả rõ ràng về các thay đổi',
        },
        
        codeStyleGuidelines: 'Hướng Dẫn Phong Cách Mã',
        guideline1: 'Tuân theo các thực tiễn tốt nhất của TypeScript/Python',
        guideline2: 'Sử dụng các tên biến và hàm có ý nghĩa',
        guideline3: 'Thêm bình luận cho logic phức tạp',
        guideline4: 'Giữ các hàm nhỏ và tập trung',
        guideline5: 'Chạy linters trước khi xác nhận (ESLint, Black)',
      },
      
      // Useful Resources
      usefulResources: {
        title: 'Các Tài Nguyên Hữu Ích',
        
        projectDocumentation: {
          title: 'Tài Liệu Dự Án',
          description: 'Tìm hiểu về kiến trúc và mục tiêu dự án',
        },
        
        awsAthenaDocs: {
          title: 'Tài Liệu AWS Athena',
          description: 'Ngôn ngữ truy vấn và hướng dẫn tối ưu hóa',
        },
        
        pysparkAPI: {
          title: 'API PySpark',
          description: 'Tham khảo cho các công việc xử lý dữ liệu',
        },
        
        reactDocumentation: {
          title: 'Tài Liệu React',
          description: 'Tham khảo khung công tác frontend',
        },
      },
    },

    // About Vietnamese
    about: {
      tagline: 'Lá Chắn AI Soi Chiếu Dữ Liệu Của Bạn',
      description: 'Được đặt tên theo lá chắn thần thánh của Zeus và Athena (AEGIS) kết hợp với ánh sáng của trí tuệ (LUMINA) – Một hệ thống AI bảo vệ và soi chiếu toàn bộ dữ liệu tài chính của bạn, như ánh mắt canh chừng của Athena trên lá chắn huyền thoại của cô.',
      version: 'Phiên Bản 1.0',
      productionReady: 'Sản Xuất',
      november2025: 'Tháng 11 2025',
      
      // Tabs
      overview: 'Tổng Quan',
      lakehouse: 'Lakehouse',
      ragChatbot: 'RAG Chatbot',
      airflowEtl: 'Airflow ETL',
      
      // Overview Section
      missionStatement: 'Tuyên Bố Sứ Mệnh',
      missionText: 'Chúng tôi xây dựng một nền tảng phân tích dữ liệu tài chính toàn diện cho phép trích xuất hiểu biết từ dữ liệu thị trường chứng khoán Việt Nam, tin tức và chỉ số kinh tế bằng cách sử dụng kiến trúc Lakehouse hiện đại kết hợp với khả năng AI/ML.',
      costSavings: 'Tiết kiệm chi phí so với RDS truyền thống',
      fasterQuerySpeed: 'Tốc độ truy vấn nhanh hơn',
      systemUptime: 'Thời gian hoạt động hệ thống',
      
      projectOverview: 'Tổng Quan Dự Án',
      keySolutions: 'Các Giải Pháp Chính',
      dataProcessed: 'Dữ Liệu Được Xử Lý',
      stocks: 'Cổ Phiếu',
      news: 'Tin Tức',
      indicators: 'Chỉ Số',
      symbols: 'Ký Hiệu',
      systemPerformance: 'Hiệu Suất Hệ Thống',
      queryLatencyP50: 'Độ Trễ Truy Vấn (P50)',
      queryLatencyP99: 'Độ Trễ Truy Vấn (P99)',
      dataFreshness: 'Tính Mới Của Dữ Liệu',
      vectorSearchLatency: 'Tìm Kiếm Vector',
      target: 'Mục Tiêu',
      actual: 'Thực Tế',
      
      technologyStack: 'Stack Công Nghệ',
      cloudInfrastructure: 'Hạ Tầng Đám Mây',
      dataProcessing: 'Xử Lý Dữ Liệu',
      backendApi: 'Backend & API',
      aiMlNlp: 'AI/ML & NLP',
      frontendStack: 'Stack Frontend',
      
      futureVision: 'Tầm Nhìn Tương Lai',
      phase1Immediate: 'Giai Đoạn 1: Ngay Lập Tức',
      phase2ShortTerm: 'Giai Đoạn 2: Ngắn Hạn',
      phase3MediumTerm: 'Giai Đoạn 3: Trung Hạn',
      phase4LongTerm: 'Giai Đoạn 4: Dài Hạn',
      week1_2: 'Tuần 1-2',
      month1_2: 'Tháng 1-2',
      month3_6: 'Tháng 3-6',
      month6_12: 'Tháng 6-12',
      
      developmentTeam: 'Đội Phát Triển',
      teamDescription: 'Dự án này được phát triển bởi một nhóm kỹ sư đam mê về Kỹ Thuật Dữ Liệu, Học Máy và Phân Tích Tài Chính.',
      dataEngineering: 'Kỹ Thuật Dữ Liệu',
      dataEngineeringDesc: 'Kiến trúc Lakehouse, pipeline ETL, chất lượng dữ liệu',
      aiMlDevelopment: 'Phát Triển AI/ML',
      aiMlDevelopmentDesc: 'Hệ thống RAG, nhúng, xử lý NLP',
      fullStackDevelopment: 'Phát Triển Full-stack',
      fullStackDevelopmentDesc: 'Backend API, giao diện người dùng Frontend, DevOps',
      
      openForCollaboration: 'Mở Cho Cộng Tác:',
      collaborationText: 'Chúng tôi hoan nghênh những đóng góp từ cộng đồng. Nếu bạn quan tâm đến dự án, hãy xem phần Hướng Dẫn để tìm hiểu cách đóng góp code hoặc ý tưởng!',
      
      // BE-FE & MCP Section (Vietnamese)
      backendFrontendMcp: 'Kiến Trúc Backend, Frontend & MCP',
      systemArchitectureDesc: 'Hệ thống chatbot RAG bao gồm ba thành phần chính: Backend FastAPI với dịch vụ RAG, Frontend React với tính cách Metallica, và máy chủ MCP tùy chọn để tích hợp công cụ.',
      systemArchitecture: 'Kiến Trúc Hệ Thống',
      frontendLayer: 'Lớp Frontend',
      frontendLayerDesc: 'Ứng dụng React với tính cách AI Metallica',
      backendLayer: 'Lớp Backend (FastAPI)',
      backendLayerDesc: 'Dịch vụ RAG cốt lõi với tích hợp Gemini',
      dataLayer: 'Lớp Dữ Liệu & Mô Hình (AWS S3)',
      dataLayerDesc: 'Chỉ số vectơ, nhúng, và siêu dữ liệu',
      
      // Backend Details (Vietnamese)
      backendFastapi: 'Backend (FastAPI + Dịch Vụ RAG)',
      coreComponents: 'Thành Phần Cốt Lõi',
      ragService: 'Dịch Vụ RAG',
      apiEndpoints: 'Điểm Cuối API',
      keyFeatures: 'Các Tính Năng Chính',
      asyncProcessing: 'Xử Lý Không Đồng Bộ',
      asyncProcessingDesc: 'Xử lý yêu cầu không chặn với Python async/await',
      errorHandling: 'Xử Lý Lỗi',
      errorHandlingDesc: 'Quay lui nhẹ nhàng cho các sự cố API',
      loggingFeature: 'Ghi Nhật Ký',
      loggingDesc: 'Nhật ký JSON có cấu trúc để gỡ lỗi',
      cachingFeature: 'Bộ Nhớ Đệm',
      cachingDesc: 'Supabase + Redis để bộ nhớ đệm phản hồi',
      rateLimiting: 'Giới Hạn Tốc Độ',
      rateLimitingDesc: 'Quản lý khóa API dựa trên token',
      corsEnabled: 'CORS Được Bật',
      corsEnabledDesc: 'Yêu cầu từ nguồn chéo từ frontend',
      
      // Frontend Details (Vietnamese)
      frontendReact: 'Frontend (React + TypeScript)',
      metallicaPersonality: 'Tính Cách AI Metallica',
      visualIdentity: 'Nhận Dạng Trực Quan',
      personalityTraits: 'Tính Cách',
      responseFormatNote: 'Định Dạng Phản Hồi:',
      responseFormatDesc: 'Các câu trả lời được định dạng Markdown với trích dẫn từ nguồn, điểm liên quan, và tô sáng từ khóa để phân tích tài chính.',
      keyPagesFeatures: 'Trang Chính & Tính Năng',
      chatPage: '💬 Trang Trò Chuyện',
      chatPageDesc: 'Giao diện chatbot RAG với avatar Metallica, lịch sử tin nhắn, trích dẫn từ nguồn',
      dashboardPage: '📊 Bảng Điều Khiển',
      dashboardPageDesc: 'Trực quan hóa dữ liệu cổ phiếu thời gian thực, chỉ số kỹ thuật, tổng quan thị trường',
      assetFinder: '🔍 Công Cụ Tìm Kiếm Tài Sản',
      assetFinderDesc: 'Sàng lọc nâng cao với bộ lọc để lựa chọn cổ phiếu',
      
      // MCP Server (Vietnamese)
      mcpServer: 'Máy Chủ MCP (Giao Thức Ngữ Cảnh Mô Hình)',
      mcpServerDesc: 'Máy chủ Giao Thức Ngữ Cảnh Mô Hình tùy chọn để tích hợp công cụ LLM và khả năng AI nâng cao.',
      availableTools: 'Công Cụ Có Sẵn',
      stockAnalyzerTool: 'Công Cụ Phân Tích Cổ Phiếu',
      stockAnalyzerDesc: 'Truy vấn dữ liệu cổ phiếu, chỉ số kỹ thuật, lịch sử giá',
      newsFetcherTool: 'Công Cụ Lấy Tin Tức',
      newsFetcherDesc: 'Lấy tin tức mới nhất, phân tích cảm xúc, chủ đề xu hướng',
      marketIntelligenceTool: 'Công Cụ Thông Tin Thị Trường',
      marketIntelligenceDesc: 'Chỉ số vĩ mô, sự kiện kinh tế, cảm xúc thị trường',
      portfolioAnalyzerTool: 'Công Cụ Phân Tích Danh Mục',
      portfolioAnalyzerDesc: 'Tối ưu hóa danh mục, đánh giá rủi ro, cân bằng lại',
      integrationBenefits: 'Lợi Ích Tích Hợp',
      extendedCapabilities: 'Khả Năng Mở Rộng:',
      extendedCapabilitiesDesc: 'AI Gemini có thể sử dụng các công cụ RAG để phân tích tài chính nâng cao',
      realtimeDataAccess: 'Truy Cập Dữ Liệu Thời Gian Thực:',
      realtimeDataAccessDesc: 'Giá cổ phiếu trực tiếp, dữ liệu thị trường, luồng tin tức',
      contextAwareness: 'Nhận Thức Ngữ Cảnh:',
      contextAwarenessDesc: 'Các công cụ cung cấp ngữ cảnh phong phú để ra quyết định LLM',
      autonomousWorkflows: 'Quy Trình Làm Việc Tự Động:',
      autonomousWorkflowsDesc: 'Phân tích nhiều bước mà không cần sự can thiệp của người dùng',
      
      // End-to-End Flow (Vietnamese)
      endToEndDataFlow: 'Luồng Dữ Liệu Từ Đầu Đến Cuối',
      dataFlow1: 'Người dùng nhập truy vấn trong giao diện Trò chuyện → Frontend xác thực đầu vào & lưu vào trạng thái',
      dataFlow2: 'Frontend gửi yêu cầu API tới backend → Backend nhận truy vấn + khóa API + lịch sử',
      dataFlow3: 'Dịch vụ RAG nhúng truy vấn → Vietnamese-SBERT tạo vectơ 768 chiều',
      dataFlow4: 'Tìm kiếm vectơ FAISS trong S3 → Trả về 7 tài liệu giống nhất (IndexFlatIP)',
      dataFlow5: 'Xếp hạng lại cross-encoder → Sắp xếp lại kết quả theo điểm liên quan',
      dataFlow6: 'Xây dựng ngữ cảnh với toàn bộ văn bản → Tải 2000 ký tự mỗi tài liệu từ bộ nhớ đệm CSV (~6,988 ký tự tổng cộng)',
      dataFlow7: 'Tạo Gemini LLM → Tạo câu trả lời với tính cách Metallica (~800ms)',
      dataFlow8: 'Định dạng phản hồi & trích xuất nguồn → Markdown + trích dẫn từ nguồn [{source, link}]',
      dataFlow9: 'Frontend nhận phản hồi → Hiển thị với avatar Metallica, nguồn, trích dẫn',
      totalResponseTime2: 'Tổng Thời Gian Phản Hồi:',
      endToEndTime: '~2-5 giây (từ đầu đến cuối)',
      
      // Performance Metrics (Vietnamese)
      performanceMetrics: 'Số Liệu Hiệu Suất',
      queryEmbeddingTime: '~50ms',
      queryEmbeddingLabel: 'Nhúng Truy Vấn',
      faissSearchTime: '<10ms',
      faissSearchLabel: 'Tìm Kiếm FAISS',
      rerankingTime: '~100ms',
      rerankingLabel: 'Xếp Hạng Lại',
      llmGenerationTime: '~800ms',
      llmGenerationLabel: 'Tạo LLM',
      uptime: '99.8%',
      uptimeLabel: 'Thời Gian Hoạt Động',
      indexedVectorsCount: '328K+',
      indexedVectorsLabel: 'Vectơ Được Lập Chỉ Mục',
      newsArticlesCount: '12K+',
      newsArticlesLabel: 'Bài Viết Tin Tức',
      retrievedDocsCount: '7',
      retrievedDocsLabel: 'Tài Liệu Được Lấy',
      
      // Lakehouse Section (Vietnamese)
      lakehouseArchitecture: 'Kiến Trúc Lakehouse',
      lakehouseDescription: 'Một kiến trúc dữ liệu hiện đại kết hợp những điểm tốt nhất của Data Lakes và Data Warehouses, cung cấp lưu trữ có khả năng mở rộng với khả năng phân tích hiệu suất cao.',
      medallionArchitecture: 'Kiến Trúc Medallion (Bronze-Silver-Gold)',
      
      bronzeLayer: 'Lớp Bronze',
      bronzeLayerDesc: 'Nạp dữ liệu thô từ các nguồn',
      silverLayer: 'Lớp Silver',
      silverLayerDesc: 'Dữ liệu được làm sạch & chuẩn hóa',
      goldLayer: 'Lớp Gold',
      goldLayerDesc: 'Tập hợp sẵn sàng kinh doanh',
      
      dataSources: 'Nguồn Dữ Liệu',
      stockData: '📈 Dữ Liệu Cổ Phiếu',
      stockDataDesc: 'Nguồn: VNStock API v3 • Ký hiệu: 30 cổ phiếu chính • Bản ghi: 10,950+ • Giai đoạn: 365 ngày • Cập nhật: Thời gian thực (2-5 phút trễ)',
      newsData: '📰 Dữ Liệu Tin Tức',
      newsDataDesc: 'Nguồn: Google Custom Search • Bài viết: 12,027 • Ngôn ngữ: Tiếng Việt • Phạm vi: 1-3 năm • Chủ đề: Tài chính, Ngân hàng, Thị trường',
      macroData: '📊 Dữ Liệu Vĩ Mô',
      macroDataDesc: 'Nguồn: API Kinh tế • Chỉ số: 50+ • Bản ghi: 18,250 • Giai đoạn: 6 năm (2020-2025) • Cập nhật: Hàng ngày/Hàng tuần',
      
      performanceCostEfficiency: 'Hiệu Suất & Hiệu Quả Chi Phí',
      costSavingsVsRds: 'Tiết Kiệm Chi Phí So Với RDS',
      queryLatency: 'Độ Trễ Truy Vấn (P50)',
      dataCompression: 'Nén Dữ Liệu',
      monthlyQueryCost: 'Chi Phí Truy Vấn Hàng Tháng',
      
      awsInfrastructure: 'Hạ Tầng AWS',
      amazonS3: 'Amazon S3',
      amazonS3Desc: 'Lưu trữ Data Lake với 3 lớp (Bronze, Silver, Gold)',
      awsGlue: 'AWS Glue',
      awsGlueDesc: 'Danh mục dữ liệu với 9 bảng trên 2 cơ sở dữ liệu',
      awsAthena: 'AWS Athena',
      awsAthenaDesc: 'Truy vấn SQL không máy chủ trên dữ liệu S3',
      
      // RAG Section
      ragChatbotSystem: 'Hệ Thống RAG Chatbot',
      ragDescription: 'Chatbot Retrieval-Augmented Generation (RAG) cung cấp câu trả lời chính xác, được dựa trên sự hiểu biết về thị trường tài chính Việt Nam bằng cách sử dụng dữ liệu tin tức thực tế và công nghệ AI nâng cao.',
      
      howRagWorks: 'RAG Hoạt Động Như Thế Nào',
      queryEmbedding: 'Nhúng Truy Vấn',
      queryEmbeddingDesc: 'Chuyển câu hỏi của người dùng thành vector 768 chiều bằng cách sử dụng Vietnamese-SBERT',
      vectorSearch: 'Tìm Kiếm Vector',
      vectorSearchDesc: 'Tìm kiếm 10,585 bài viết được lập chỉ mục bằng FAISS để có 5 tài liệu liên quan hàng đầu',
      reranking: 'Sắp Xếp Lại',
      rerankingDesc: 'Cross-encoder sắp xếp lại kết quả để có độ liên quan tốt hơn',
      contextPreparation: 'Chuẩn Bị Bối Cảnh',
      contextPreparationDesc: 'Định dạng 3 bài viết hàng đầu làm bối cảnh có nguồn và siêu dữ liệu',
      llmGeneration: 'Tạo LLM',
      llmGenerationDesc: 'Google Gemini tạo phản hồi tự nhiên dựa trên bối cảnh',
      responseFormatting: 'Định Dạng Phản Hồi',
      responseFormattingDesc: 'Trả về câu trả lời có nguồn, điểm và mức độ tin cậy',
      totalResponseTime: 'Tổng Thời Gian Phản Hồi:',
      
      ragTechnologyStack: 'Stack Công Nghệ',
      embeddingSearch: 'Tìm Kiếm & Nhúng',
      generationStorage: 'Lưu Trữ & Tạo',
      
      ragKeyFeatures: 'Các Tính Năng Chính',
      noHallucination: 'Không Ảo Giác',
      noHallucinationDesc: 'Câu trả lời được dựa trên các bài viết tin tức thực tế có trích dẫn nguồn',
      vietnameseSupport: 'Hỗ Trợ Tiếng Việt',
      vietnameseSupportDesc: 'Tối ưu hóa cho các truy vấn và phản hồi trong tiếng Việt',
      fastAccurate: 'Nhanh & Chính Xác',
      fastAccurateDesc: 'Tìm kiếm vector dưới một giây với điểm độ liên quan cao',
      
      ragSystemStatistics: 'Thống Kê Hệ Thống',
      indexedVectors: 'Vector Được Lập Chỉ Mục',
      newsArticles: 'Bài Viết Tin Tức',
      vectorSearchTime: 'Thời Gian Tìm Kiếm Vector',
      embeddingDimensions: 'Kích Thước Nhúng',
      
      initialRagTraining: 'Đào Tạo RAG Ban Đầu (Kaggle)',
      trainingProcess: 'Quá Trình Đào Tạo',
      technicalSpecifications: 'Thông Số Kỹ Thuật',
      
      // Airflow Section
      airflowEtlPipeline: 'Pipeline ETL Apache Airflow',
      airflowDescription: 'Pipeline ETL được tự động hóa hoàn toàn được điều phối bởi Apache Airflow, xử lý dữ liệu từ nhiều nguồn thông qua các lớp Bronze-Silver-Gold bằng cách sử dụng PySpark để tính toán phân tán.',
      
      etlPipelineStages: 'Các Giai Đoạn Pipeline ETL',
      bronzeLayerStage: 'Lớp Bronze (08:00-09:30 UTC)',
      bronzeLayerStageDesc: 'Thu thập dữ liệu từ API',
      silverLayerStage: 'Lớp Silver (10:00-11:30 UTC)',
      silverLayerStageDesc: 'Làm sạch & chuẩn hóa dữ liệu',
      goldLayerStage: 'Lớp Gold (13:00-14:30 UTC)',
      goldLayerStageDesc: 'Kỹ thuật tính năng & tổng hợp',
      ragPipelineStage: 'Pipeline RAG (14:30-15:00 UTC)',
      ragPipelineStageDesc: 'Cập nhật cơ sở dữ liệu vector cho chatbot',
      qualityCheckStage: 'Kiểm Tra Chất Lượng (15:00-15:15 UTC)',
      qualityCheckStageDesc: 'Xác thực & giám sát dữ liệu',
      glueCatalogStage: 'Cập Nhật Danh Mục Glue (15:30-15:45 UTC)',
      glueCatalogStageDesc: 'Đồng bộ hóa siêu dữ liệu',
      notificationStage: 'Thông Báo (15:45-16:00 UTC)',
      notificationStageDesc: 'Báo cáo trạng thái',
      
      totalPipelineDuration: 'Tổng Thời Lượng Pipeline:',
      dailyAt: 'Hàng ngày lúc 09:00 UTC',
      
      pipelineTechnologyStack: 'Stack Công Nghệ',
      orchestration: 'Điều Phối',
      processing: 'Xử Lý',
      ragPipeline: 'Pipeline RAG',
      
      pysparkDistributed: 'Xử Lý Phân Tán PySpark',
      pysparkDesc: 'PySpark cho phép xử lý dữ liệu phân tán trên nhiều nút, xử lý các phép biến đổi dữ liệu quy mô lớn một cách hiệu quả với tính toán song song.',
      clusterConfiguration: 'Cấu Hình Cụm',
      keyOperations: 'Các Hoạt Động Chính',
      
      pipelineFeatures: 'Các Tính Năng Chính',
      fullyAutomated: 'Được Tự Động Hóa Hoàn Toàn',
      fullyAutomatedDesc: 'Chạy hàng ngày mà không cần can thiệp thủ công, với khả năng thử lại tự động khi thất bại',
      parallelProcessing: 'Xử Lý Song Song',
      parallelProcessingDesc: 'PySpark phân phối khối lượng công việc trên nhiều nút để xử lý nhanh hơn',
      qualityMonitoring: 'Giám Sát Chất Lượng',
      qualityMonitoringDesc: 'Kiểm tra chất lượng dữ liệu tích hợp và cảnh báo phát hiện bất thường',
      
      pipelineStatistics: 'Thống Kê Pipeline',
      dailyRunsYear: 'Chạy Hàng Ngày/Năm',
      successRate: 'Tỷ Lệ Thành Công',
      averageDuration: 'Thời Lượng Trung Bình',
      dataLayersProcessed: 'Lớp Dữ Liệu Được Xử Lý',
      
      infrastructure: 'Hạ Tầng',
      airflowDeployment: 'Triển Khai Airflow',
      sparkCluster: 'Cụm Spark',
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

// Get translation value (can return string, string[], or object)
export const tValue = (key: string): TranslationValue => {
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
  
  return value || key;
};

// Initialize language
export const initI18n = () => {
  getLanguage();
};
