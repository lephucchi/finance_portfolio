import { useState, useEffect } from "react";
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Zap,
  AlertCircle,
  Loader,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { api, getDateRange, formatCurrency, formatPercent, DATA_END_DATE } from "@/lib/api";
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

function ErrorAlert({ message }: { message: string }) {
  return (
    <div className="card-lumina border-l-4 border-accent bg-accent/10">
      <div className="flex gap-3">
        <AlertCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="font-semibold text-foreground">Error Loading Data</h3>
          <p className="text-sm text-muted-foreground mt-1">{message}</p>
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [timeFrame, setTimeFrame] = useState("1d");
  const [dashboardData, setDashboardData] = useState<DashboardSummary | null>(
    null,
  );
  const [stocksData, setStocksData] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        // Use latest available data (Oct 30, 2025)
        const { startDate, endDate } = getDateRange(5);

        const [dashboard, stocks] = await Promise.all([
          api.getDashboardSummary(DATA_END_DATE),
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
      }
    }

    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="card-lumina">
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-2">
            Real-time market insights and analytics
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
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-2">
            Real-time market insights and analytics
          </p>
        </div>
        <ErrorAlert message={error} />
      </div>
    );
  }

  const topGainers = dashboardData?.top_gainers || [];
  const topLosers = dashboardData?.top_losers || [];

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="card-lumina">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
            <p className="text-sm text-muted-foreground mt-2">
              Real-time market insights and analytics
            </p>
          </div>

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
                {tf}
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
              label: "Market Change",
              value: formatPercent(dashboardData.market.market_change_pct ?? 0),
              change: `${dashboardData.market.total_stocks ?? 0} stocks`,
              positive: (dashboardData.market.market_change_pct ?? 0) >= 0,
            },
            {
              label: "Advancing",
              value: (dashboardData.market.advancing ?? 0).toString(),
              change: `${dashboardData.market.declining ?? 0} declining`,
              positive: true,
            },
            {
              label: "Total Volume",
              value: `${((dashboardData.market.total_volume ?? 0) / 1000000).toFixed(0)}M`,
              change: "daily volume",
              positive: true,
            },
            {
              label: "Avg Sentiment",
              value: (dashboardData.sentiment?.avg_score ?? 0).toFixed(2),
              change: `${dashboardData.sentiment?.total_articles ?? 0} articles`,
              positive: (dashboardData.sentiment?.avg_score ?? 0) >= 0.3,
            },
          ].map((metric, idx) => {
            const Icon = metric.positive ? TrendingUp : TrendingDown;
            return (
              <div key={idx} className="card-lumina hover:shadow-lg">
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
          Market Price Trend
        </h2>
        {stocksData.length > 0 ? (
          <>
            <div className="overflow-x-auto">
              <SmoothLineChart data={stocksData} />
            </div>
            <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
              <Zap className="w-3 h-3" />
              Live data • {stocksData.length} data points • Updated every minute
            </div>
          </>
        ) : (
          <div className="py-8 text-center text-muted-foreground">
            No chart data available
          </div>
        )}
      </div>

      {/* Top Assets */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Gainers */}
        <div className="card-lumina">
          <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            Top Gainers
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
                        Vol: {(asset.volume / 1000000).toFixed(1)}M
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
              No data available
            </div>
          )}
        </div>

        {/* Insights */}
        <div className="card-lumina">
          <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-accent" />
            Market Insights
          </h2>
          <div className="space-y-3">
            {dashboardData?.market && dashboardData?.sentiment &&
              [
                `Market change: ${formatPercent(dashboardData.market.market_change_pct ?? 0)}`,
                `Sentiment: ${(dashboardData.sentiment.positive_pct ?? 0).toFixed(1)}% positive articles`,
                `Volume strength: ${((dashboardData.market.total_volume ?? 0) / 1000000000).toFixed(1)}B shares`,
              ].map((insight, i) => (
                <div
                  key={i}
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
          <h3 className="font-semibold text-primary mb-2">Market Overview</h3>
          <p className="text-sm text-foreground leading-relaxed">
            {(dashboardData.market.advancing ?? 0) > (dashboardData.market.declining ?? 0)
              ? `Market showing positive momentum with ${dashboardData.market.advancing} advancing stocks vs ${dashboardData.market.declining} declining. `
              : `Market showing mixed signals with ${dashboardData.market.declining} declining stocks. `}
            Sentiment score of {(dashboardData.sentiment.avg_score ?? 0).toFixed(2)}{" "}
            indicates{" "}
            {(dashboardData.sentiment.avg_score ?? 0) >= 0.3
              ? "positive"
              : (dashboardData.sentiment.avg_score ?? 0) <= -0.3
                ? "negative"
                : "neutral"}{" "}
            market sentiment based on {dashboardData.sentiment.total_articles ?? 0}{" "}
            analyzed articles.
          </p>
          <p className="text-xs text-muted-foreground mt-3">
            Last updated:{" "}
            {dashboardData.latest_update ? new Date(dashboardData.latest_update).toLocaleString() : "N/A"}
          </p>
        </div>
      )}
    </div>
  );
}
