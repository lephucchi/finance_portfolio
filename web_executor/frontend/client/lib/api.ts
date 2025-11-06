import { env } from './env';

// Use environment variables for configuration
const API_BASE_URL = env.apiBaseUrl;

// Available data range from environment
export const DATA_START_DATE = env.dataStartDate;
export const DATA_END_DATE = env.dataEndDate;

// Pagination defaults from environment
export const DEFAULT_PAGE_SIZE = env.defaultPageSize;
export const MAX_PAGE_SIZE = env.maxPageSize;

export interface StockData {
  symbol: string;
  data_date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  ma_20: number;
  ma_50: number;
  price_change_pct: number;
  volatility_7d: number;
}

export interface TechnicalIndicator {
  date: string;
  ma_20: number;
  ma_50: number;
  rsi_14: number;
  macd: number;
  macd_signal: number;
  bollinger_upper: number;
  bollinger_middle: number;
  bollinger_lower: number;
  volatility_7d: number;
  volume_ma_20: number;
}

export interface SectorPerformance {
  sector: string;
  avg_change_pct: number;
  total_volume: number;
  stock_count: number;
  top_gainers: string[];
  top_losers: string[];
}

export interface SentimentSummary {
  date: string;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  avg_sentiment: number;
  total_articles: number;
  positive_pct: number;
  negative_pct: number;
  neutral_pct: number;
}

export interface SentimentOverall {
  total_articles: number;
  avg_sentiment: number;
  dominant_sentiment: string;
}

export interface SentimentTrend {
  period: string;
  avg_sentiment: number;
  article_count: number;
  positive_pct: number;
  negative_pct: number;
  neutral_pct: number;
}

export interface MacroIndicator {
  date: string;
  indicator_name: string;
  indicator_value: number;
  value_change_pct: number;
  ma_7: number;
  ma_30: number;
}

export interface ForexRate {
  date: string;
  currency_pair: string;
  rate: number;
  change_pct: number;
  ma_7: number;
  ma_30: number;
}

export interface DashboardSummary {
  date: string;
  market: {
    total_stocks: number;
    market_change_pct: number;
    avg_sentiment: number;
    total_volume: number;
    advancing: number;
    declining: number;
    unchanged: number;
  };
  top_gainers: Array<{
    symbol: string;
    price_change_pct: number;
    close: number;
    volume: number;
  }>;
  top_losers: Array<{
    symbol: string;
    price_change_pct: number;
    close: number;
    volume: number;
  }>;
  sentiment: {
    avg_score: number;
    positive_pct: number;
    total_articles: number;
  };
  macro: {
    cpi: number;
    usd_vnd: number;
  };
  latest_update: string;
}

async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const result = await response.json();

  if (!result.success) {
    throw new Error(result.detail || result.message || "API request failed");
  }

  return result.data;
}

export const api = {
  // Market Data APIs
  async getStocks(
    startDate: string,
    endDate: string,
    symbols?: string[],
  ): Promise<StockData[]> {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });

    if (symbols && symbols.length > 0) {
      params.append("symbols", symbols.join(","));
    }

    const response = await fetch(`${API_BASE_URL}/market/stocks?${params}`);
    return handleApiResponse<StockData[]>(response);
  },

  async getTechnicalIndicators(
    symbol: string,
    startDate: string,
    endDate: string,
  ): Promise<TechnicalIndicator[]> {
    const params = new URLSearchParams({
      symbol,
      start_date: startDate,
      end_date: endDate,
    });

    const response = await fetch(
      `${API_BASE_URL}/market/technical-indicators?${params}`,
    );
    const data = await handleApiResponse<{
      symbol: string;
      indicators: TechnicalIndicator[];
    }>(response);
    return data.indicators;
  },

  async getSectorPerformance(
    startDate: string,
    endDate: string,
  ): Promise<SectorPerformance[]> {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });

    const response = await fetch(
      `${API_BASE_URL}/market/sector-performance?${params}`,
    );
    return handleApiResponse<SectorPerformance[]>(response);
  },

  // Sentiment APIs
  async getSentimentSummary(
    startDate: string,
    endDate: string,
  ): Promise<{
    summary: SentimentSummary[];
    overall: SentimentOverall;
  }> {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });

    const response = await fetch(`${API_BASE_URL}/sentiment/summary?${params}`);
    return handleApiResponse<{
      summary: SentimentSummary[];
      overall: SentimentOverall;
    }>(response);
  },

  async getSentimentTrend(
    startDate: string,
    endDate: string,
    interval: "daily" | "weekly" | "monthly" = "daily",
  ): Promise<SentimentTrend[]> {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
      interval,
    });

    const response = await fetch(`${API_BASE_URL}/sentiment/trend?${params}`);
    const data = await handleApiResponse<{
      interval: string;
      trend: SentimentTrend[];
    }>(response);
    return data.trend;
  },

  // Macro Economics APIs
  async getMacroIndicators(
    startDate: string,
    endDate: string,
    indicators?: string[],
  ): Promise<MacroIndicator[]> {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });

    if (indicators && indicators.length > 0) {
      params.append("indicators", indicators.join(","));
    }

    const response = await fetch(`${API_BASE_URL}/macro/indicators?${params}`);
    return handleApiResponse<MacroIndicator[]>(response);
  },

  async getForexRates(
    startDate: string,
    endDate: string,
  ): Promise<ForexRate[]> {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });

    const response = await fetch(`${API_BASE_URL}/macro/forex?${params}`);
    return handleApiResponse<ForexRate[]>(response);
  },

  // Dashboard APIs
  async getDashboardSummary(date?: string): Promise<DashboardSummary> {
    const params = new URLSearchParams();
    if (date) {
      params.append("date_", date);
    }

    const response = await fetch(`${API_BASE_URL}/dashboard/summary?${params}`);
    return handleApiResponse<DashboardSummary>(response);
  },

  async getCorrelationAnalysis(
    startDate: string,
    endDate: string,
  ): Promise<{
    period: { start: string; end: string };
    data: Array<{
      data_date: string;
      symbol: string;
      price_change_pct: number;
      avg_sentiment: number;
      indicator_value: number;
    }>;
    correlations: {
      sentiment_vs_market: number;
      macro_vs_market: number;
    };
  }> {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });

    const response = await fetch(
      `${API_BASE_URL}/dashboard/correlation?${params}`,
    );
    return handleApiResponse<{
      period: { start: string; end: string };
      data: Array<{
        data_date: string;
        symbol: string;
        price_change_pct: number;
        avg_sentiment: number;
        indicator_value: number;
      }>;
      correlations: {
        sentiment_vs_market: number;
        macro_vs_market: number;
      };
    }>(response);
  },
};

export function getDateRange(days: number = 5): {
  startDate: string;
  endDate: string;
} {
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  return {
    startDate: startDate.toISOString().split("T")[0],
    endDate: endDate.toISOString().split("T")[0],
  };
}

export function formatCurrency(value: number): string {
  return value.toLocaleString("vi-VN", {
    style: "currency",
    currency: "VND",
    minimumFractionDigits: 0,
  });
}

export function formatPercent(value: number): string {
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
}
