import { useState, useEffect } from "react";
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Zap,
  AlertCircle,
  Loader,
  Calendar,
  RefreshCw,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useI18n } from "@/hooks/useI18n";
import {
  api,
  formatCurrency,
  formatPercent,
} from "@/lib/api";
import type { DashboardSummary, StockData } from "@/lib/api";

function SmoothLineChart({ data }: { data: StockData[] }) {
  if (!data || data.length === 0) return null;

  const padding = 40;
  const width = 600;
  const chartHeight = 300 - padding * 2;

  const prices = data.map((d) => d.close);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice || 1;

  const points = data
    .map((d, i) => {
      const x = padding + (i / (data.length - 1)) * (width - padding * 2);
      const y = padding + ((maxPrice - d.close) / priceRange) * chartHeight;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg
      width="100%"
      height={300}
      viewBox={`0 0 ${width} 300`}
      preserveAspectRatio="xMidYMid meet"
      style={{ maxWidth: "100%" }}
    >
      {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => (
        <line
          key={`grid-${i}`}
          x1={padding}
          y1={padding + ratio * chartHeight}
          x2={width - padding}
          y2={padding + ratio * chartHeight}
          stroke="currentColor"
          strokeDasharray="3 3"
          opacity="0.1"
          strokeWidth="1"
        />
      ))}

      <defs>
        <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity="0.3" />
          <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity="0" />
        </linearGradient>
      </defs>

      <polyline
        points={points}
        fill="none"
        stroke="hsl(var(--primary))"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      <line
        x1={padding}
        y1={padding}
        x2={padding}
        y2={300 - padding}
        stroke="currentColor"
        strokeWidth="1"
        opacity="0.2"
      />
      <line
        x1={padding}
        y1={300 - padding}
        x2={width - padding}
        y2={300 - padding}
        stroke="currentColor"
        strokeWidth="1"
        opacity="0.2"
      />

      {data.map((d, i) => (
        <text
          key={`label-${i}`}
          x={padding + (i / (data.length - 1)) * (width - padding * 2)}
          y={300 - padding + 20}
          textAnchor="middle"
          fontSize="12"
          fill="currentColor"
          opacity="0.5"
        >
          {d.data_date.slice(-2)}
        </text>
      ))}
    </svg>
  );
}

function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-8">
      <Loader className="w-6 h-6 animate-spin text-primary" />
    </div>
  );
}

function ErrorAlert({ message, title }: { message: string; title: string }) {
  return (
    <div className="card-lumina border-l-4 border-accent bg-accent/10">
      <div className="flex gap-3">
        <AlertCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="font-semibold text-foreground">{title}</h3>
          <p className="text-sm text-muted-foreground mt-1">{message}</p>
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { t, language } = useI18n();
  const [timeFrame, setTimeFrame] = useState("1d");
  const [selectedDate, setSelectedDate] = useState("2025-10-17"); // Latest available date
  const [dashboardData, setDashboardData] = useState<DashboardSummary | null>(
    null,
  );
  const [stocksData, setStocksData] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);

      // Calculate date range for chart (5 days before selected date)
      const selectedDateObj = new Date(selectedDate);
      const startDateObj = new Date(selectedDateObj);
      startDateObj.setDate(startDateObj.getDate() - 5);
      
      const startDate = startDateObj.toISOString().split('T')[0];
      const endDate = selectedDate;

      const [dashboard, stocks] = await Promise.all([
        api.getDashboardSummary(selectedDate),
        api.getStocks(startDate, endDate),
      ]);

      setDashboardData(dashboard);
      setStocksData(stocks);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to load dashboard data";
      setError(message);
      console.error("Dashboard error:", err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    loadDashboard();
  };

  useEffect(() => {
    loadDashboard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedDate]); // Only reload when date changes, NOT on mount

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="card-lumina">
          <h1 className="text-3xl font-bold text-foreground">{t('dashboard.title')}</h1>
          <p className="text-sm text-muted-foreground mt-2">
            {t('dashboard.subtitle')}
          </p>
        </div>
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="card-lumina">
          <h1 className="text-3xl font-bold text-foreground">{t('dashboard.title')}</h1>
          <p className="text-sm text-muted-foreground mt-2">
            {t('dashboard.subtitle')}
          </p>
        </div>
        <ErrorAlert message={error} title={t('dashboard.errors.title') as string} />
      </div>
    );
  }

  const topGainers = dashboardData?.top_gainers || [];
  const topLosers = dashboardData?.top_losers || [];

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="card-lumina">
        <div className="flex flex-col gap-4">
          {/* Title and Controls Row */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-foreground">{t('dashboard.title')}</h1>
              <p className="text-sm text-muted-foreground mt-2">
                {t('dashboard.subtitle')}
              </p>
            </div>

            <div className="flex gap-2 items-center flex-wrap">
              {/* Date Picker */}
              <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg shadow-sm border border-gray-200">
                <Calendar className="h-4 w-4 text-gray-500" />
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="text-sm font-medium text-gray-700 border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
                  title={t('dashboard.selectDate') as string}
                />
              </div>

              {/* Refresh Button */}
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className={cn(
                  "px-4 py-2 rounded-lg transition-all duration-300 text-sm font-medium flex items-center gap-2",
                  "bg-secondary/50 text-foreground hover:bg-secondary",
                  isRefreshing && "opacity-50 cursor-not-allowed"
                )}
                title={t('dashboard.refreshData') as string}
              >
                <RefreshCw className={cn("h-4 w-4", isRefreshing && "animate-spin")} />
                {t('dashboard.refreshButton')}
              </button>
            </div>
          </div>

          {/* Time Frame Buttons Row */}
          <div className="flex gap-2">
            {["1H", "1D", "1W", "1M"].map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeFrame(tf)}
                className={cn(
                  "px-4 py-2 rounded-lg transition-all duration-300 text-sm font-medium",
                  timeFrame === tf
                    ? "bg-primary text-primary-foreground shadow-md"
                    : "bg-secondary/50 text-foreground hover:bg-secondary",
                )}
              >
                {t(`dashboard.timeframes.${tf}` as any)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      {dashboardData?.market && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            {
              label: t('dashboard.metrics.marketChange'),
              value: formatPercent(dashboardData.market.market_change_pct ?? 0),
              change: `${dashboardData.market.total_stocks ?? 0} ${t('dashboard.metrics.stocksCount')}`,
              positive: (dashboardData.market.market_change_pct ?? 0) >= 0,
            },
            {
              label: t('dashboard.metrics.advancing'),
              value: (dashboardData.market.advancing ?? 0).toString(),
              change: `${dashboardData.market.declining ?? 0} ${t('dashboard.metrics.decliningCount')}`,
              positive: true,
            },
            {
              label: t('dashboard.metrics.totalVolume'),
              value: `${((dashboardData.market.total_volume ?? 0) / 1000000).toFixed(0)}M`,
              change: t('dashboard.metrics.dailyVolume'),
              positive: true,
            },
            {
              label: t('dashboard.metrics.avgSentiment'),
              value: (dashboardData.sentiment?.avg_score ?? 0).toFixed(2),
              change: `${dashboardData.sentiment?.total_articles ?? 0} ${t('dashboard.metrics.articles')}`,
              positive: (dashboardData.sentiment?.avg_score ?? 0) >= 0.3,
            },
          ].map((metric, idx) => {
            const Icon = metric.positive ? TrendingUp : TrendingDown;
            return (
              <div key={metric.label} className="card-lumina hover:shadow-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-muted-foreground font-medium mb-2">
                      {metric.label}
                    </p>
                    <p className="text-2xl font-bold text-foreground">
                      {metric.value}
                    </p>
                  </div>
                  <Icon
                    className={cn(
                      "w-5 h-5",
                      metric.positive ? "text-primary" : "text-accent",
                    )}
                  />
                </div>
                <p
                  className={cn(
                    "text-sm font-medium mt-3",
                    metric.positive ? "text-primary" : "text-accent",
                  )}
                >
                  {metric.change}
                </p>
              </div>
            );
          })}
        </div>
      )}

      {/* Main Chart */}
      <div className="card-lumina lg:col-span-2">
        <h2 className="text-lg font-semibold text-foreground mb-4">
          {t('dashboard.chart.title')}
        </h2>
        {stocksData.length > 0 ? (
          <>
            <div className="overflow-x-auto">
              <SmoothLineChart data={stocksData} />
            </div>
            <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
              <Zap className="w-3 h-3" />
              {t('dashboard.chart.liveData')} • {stocksData.length} {t('dashboard.chart.dataPoints')} • {t('dashboard.chart.updatedEveryMinute')}
            </div>
          </>
        ) : (
          <div className="py-8 text-center text-muted-foreground">
            {t('dashboard.chart.noData')}
          </div>
        )}
      </div>

      {/* Top Assets */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Gainers */}
        <div className="card-lumina">
          <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            {t('dashboard.topGainers.title')}
          </h2>
          {topGainers.length > 0 ? (
            <div className="space-y-3">
              {topGainers.slice(0, 5).map((asset) => (
                <div
                  key={asset.symbol}
                  className="p-3 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-all duration-300 cursor-pointer"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-foreground">
                        {asset.symbol}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {t('dashboard.topGainers.volume')} {(asset.volume / 1000000).toFixed(1)}M
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-foreground">
                        {formatCurrency(asset.close)}
                      </p>
                      <p className="text-sm text-primary font-medium">
                        {formatPercent(asset.price_change_pct)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-4 text-center text-muted-foreground">
              {t('dashboard.topGainers.noData')}
            </div>
          )}
        </div>

        {/* Insights */}
        <div className="card-lumina">
          <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-accent" />
            {t('dashboard.insights.title')}
          </h2>
          <div className="space-y-3">
            {dashboardData?.market && dashboardData?.sentiment &&
              [
                `${t('dashboard.marketChangeInsight')} ${formatPercent(dashboardData.market.market_change_pct ?? 0)}`,
                `${t('dashboard.sentimentInsight')} ${(dashboardData.sentiment.positive_pct ?? 0).toFixed(1)}% ${t('dashboard.positiveArticles')}`,
                `${t('dashboard.volumeStrength')} ${((dashboardData.market.total_volume ?? 0) / 1000000000).toFixed(1)} ${t('dashboard.sharesVolume')}`,
              ].map((insight, i) => (
                <div
                  key={`insight-${i}`}
                  className="p-3 rounded-lg bg-secondary/30 border-l-2 border-primary/50"
                >
                  <p className="text-xs text-foreground leading-relaxed">
                    {insight}
                  </p>
                </div>
              ))}
          </div>
        </div>
      </div>

      {/* Strategic Summary */}
      {dashboardData?.market && dashboardData?.sentiment && (
        <div className="card-lumina border-l-4 border-primary">
          <h3 className="font-semibold text-primary mb-2">{t('dashboard.overview.title')}</h3>
          <p className="text-sm text-foreground leading-relaxed">
            {(dashboardData.market.advancing ?? 0) > (dashboardData.market.declining ?? 0)
              ? `${t('dashboard.overview.positiveMessage')} ${dashboardData.market.advancing} ${t('dashboard.overview.advancingStocks')} ${dashboardData.market.declining} ${t('dashboard.overview.decliningStocks')} `
              : `${t('dashboard.overview.negativeMessage')} ${dashboardData.market.declining} ${t('dashboard.overview.decliningStocksMessage')} `}
            {t('dashboard.overview.sentiment')} {(dashboardData.sentiment.avg_score ?? 0).toFixed(2)}{" "}
            {t('dashboard.overview.indicates')}{" "}
            {(dashboardData.sentiment.avg_score ?? 0) >= 0.3
              ? t('dashboard.overview.positive')
              : (dashboardData.sentiment.avg_score ?? 0) <= -0.3
                ? t('dashboard.overview.negative')
                : t('dashboard.overview.neutral')}{" "}
            {t('dashboard.overview.marketSentiment')} {dashboardData.sentiment.total_articles ?? 0}{" "}
            {t('dashboard.overview.analyzedArticles')}
          </p>
          <p className="text-xs text-muted-foreground mt-3">
            {t('dashboard.overview.lastUpdated')}{" "}
            {dashboardData.latest_update ? new Date(dashboardData.latest_update).toLocaleString(language === 'vi' ? 'vi-VN' : 'en-US') : t('dashboard.overview.notAvailable')}
          </p>
        </div>
      )}
    </div>
  );
}
