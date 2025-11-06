import { useState, useEffect } from "react";
import { FileText, TrendingUp, AlertCircle, Loader, RefreshCw, Construction } from "lucide-react";
import { cn } from "@/lib/utils";

// Mock data for demo
const MOCK_SENTIMENT_DATA = {
  summary: [
    {
      date: "2025-10-17",
      total_articles: 45,
      avg_sentiment: 0.42,
      positive_pct: 58.5,
      negative_pct: 23.2,
      neutral_pct: 18.3,
      positive_count: 26,
      negative_count: 11,
      neutral_count: 8
    },
    {
      date: "2025-10-16",
      total_articles: 52,
      avg_sentiment: 0.35,
      positive_pct: 54.2,
      negative_pct: 28.1,
      neutral_pct: 17.7,
      positive_count: 28,
      negative_count: 15,
      neutral_count: 9
    },
    {
      date: "2025-10-15",
      total_articles: 38,
      avg_sentiment: -0.15,
      positive_pct: 35.8,
      negative_pct: 42.5,
      neutral_pct: 21.7,
      positive_count: 14,
      negative_count: 16,
      neutral_count: 8
    },
    {
      date: "2025-10-14",
      total_articles: 41,
      avg_sentiment: 0.28,
      positive_pct: 51.3,
      negative_pct: 31.2,
      neutral_pct: 17.5,
      positive_count: 21,
      negative_count: 13,
      neutral_count: 7
    },
    {
      date: "2025-10-13",
      total_articles: 49,
      avg_sentiment: 0.48,
      positive_pct: 62.1,
      negative_pct: 20.3,
      neutral_pct: 17.6,
      positive_count: 30,
      negative_count: 10,
      neutral_count: 9
    },
  ],
  overall: {
    total_articles: 225,
    avg_sentiment: 0.33,
    positive_pct: 52.4,
    negative_pct: 29.1,
    neutral_pct: 18.5
  }
};

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

function DevelopmentWarning() {
  return (
    <div className="card-lumina border-l-4 border-yellow-500 bg-yellow-50">
      <div className="flex gap-3">
        <Construction className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="font-semibold text-yellow-900 flex items-center gap-2">
            🚧 Under Development - Demo Data Only
          </h3>
          <p className="text-sm text-yellow-800 mt-1">
            This feature is currently under development. All data shown below is simulated for demonstration purposes and does not reflect real market sentiment or news analysis.
          </p>
        </div>
      </div>
    </div>
  );
}

function SentimentBadge({ sentiment }: { sentiment: number }) {
  let color = "bg-muted/50 text-muted-foreground";
  let label = "Neutral";

  if (sentiment >= 0.3) {
    color = "bg-primary/20 text-primary";
    label = "Positive";
  } else if (sentiment <= -0.3) {
    color = "bg-accent/20 text-accent";
    label = "Negative";
  }

  return (
    <span className={cn("text-xs px-2 py-1 rounded-full font-medium", color)}>
      {label}
    </span>
  );
}

export default function News() {
  const [sentimentSummary, setSentimentSummary] = useState<any[]>([]);
  const [sentimentOverall, setSentimentOverall] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadSentiment = async () => {
    try {
      setLoading(true);

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 800));

      // Load mock data
      setSentimentSummary(MOCK_SENTIMENT_DATA.summary);
      setSentimentOverall(MOCK_SENTIMENT_DATA.overall);
    } catch (err) {
      console.error("Error loading mock data:", err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    loadSentiment();
  };

  useEffect(() => {
    loadSentiment();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="card-lumina">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">
                Market Insights
              </h1>
              <p className="text-sm text-muted-foreground mt-2">
                News sentiment analysis and financial intelligence
              </p>
            </div>
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className={cn(
                "px-4 py-2 rounded-lg transition-all duration-300 text-sm font-medium flex items-center gap-2",
                "bg-secondary/50 text-foreground hover:bg-secondary",
                isRefreshing && "opacity-50 cursor-not-allowed"
              )}
            >
              <RefreshCw className={cn("h-4 w-4", isRefreshing && "animate-spin")} />
              Refresh
            </button>
          </div>
        </div>
        <LoadingSpinner />
      </div>
    );
  }

  const recentSentiment = sentimentSummary && sentimentSummary.length > 0 
    ? sentimentSummary[sentimentSummary.length - 1] 
    : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card-lumina">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold text-foreground">
                Market Insights
              </h1>
              <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-semibold rounded-full border border-yellow-300">
                🚧 DEMO
              </span>
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              News sentiment analysis and financial intelligence (Demo Version)
            </p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className={cn(
              "px-4 py-2 rounded-lg transition-all duration-300 text-sm font-medium flex items-center gap-2",
              "bg-secondary/50 text-foreground hover:bg-secondary",
              isRefreshing && "opacity-50 cursor-not-allowed"
            )}
          >
            <RefreshCw className={cn("h-4 w-4", isRefreshing && "animate-spin")} />
            Refresh
          </button>
        </div>
      </div>

      {/* Development Warning */}
      <DevelopmentWarning />

      {/* Stats */}
      {sentimentOverall && sentimentSummary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card-lumina">
            <p className="text-xs text-muted-foreground font-medium mb-2">
              Total Articles
            </p>
            <p className="text-2xl font-bold text-foreground">
              {sentimentOverall.total_articles}
            </p>
            <p className="text-xs text-primary mt-2">
              {sentimentSummary.length} days analyzed
            </p>
          </div>

          <div className="card-lumina">
            <p className="text-xs text-muted-foreground font-medium mb-2">
              Overall Sentiment
            </p>
            <p className="text-2xl font-bold text-foreground">
              {sentimentOverall.avg_sentiment.toFixed(2)}
            </p>
            <p className="text-xs text-primary mt-2">
              {sentimentOverall.dominant_sentiment === "positive"
                ? "Bullish"
                : sentimentOverall.dominant_sentiment === "negative"
                  ? "Bearish"
                  : "Neutral"}
            </p>
          </div>

          {recentSentiment && (
            <div className="card-lumina">
              <p className="text-xs text-muted-foreground font-medium mb-2">
                Latest Update ({recentSentiment.date})
              </p>
              <p className="text-2xl font-bold text-foreground">
                {recentSentiment.positive_pct.toFixed(0)}%
              </p>
              <p className="text-xs text-primary mt-2">Positive Sentiment</p>
            </div>
          )}
        </div>
      )}

      {/* Daily Sentiment Trend */}
      <div className="card-lumina">
        <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-primary" />
          Daily Sentiment Breakdown
        </h2>
        {sentimentSummary.length > 0 ? (
          <div className="space-y-3">
            {sentimentSummary
              .slice()
              .reverse()
              .map((day) => (
                <div
                  key={day.date}
                  className="p-4 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-all duration-300"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-foreground">
                        {new Date(day.date).toLocaleDateString("en-US", {
                          weekday: "long",
                          month: "short",
                          day: "numeric",
                        })}
                      </h3>
                      <p className="text-xs text-muted-foreground">
                        {day.total_articles} articles analyzed
                      </p>
                    </div>
                    <SentimentBadge sentiment={day.avg_sentiment} />
                  </div>

                  <div className="flex gap-4 mb-3">
                    <div className="flex items-center gap-2">
                      <div className="w-12 h-2 rounded bg-primary/20 relative overflow-hidden">
                        <div
                          className="h-full bg-primary"
                          style={{
                            width: `${Math.min(day.positive_pct, 100)}%`,
                          }}
                        />
                      </div>
                      <span className="text-xs text-primary font-medium">
                        👍 {day.positive_pct.toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-12 h-2 rounded bg-accent/20 relative overflow-hidden">
                        <div
                          className="h-full bg-accent"
                          style={{
                            width: `${Math.min(day.negative_pct, 100)}%`,
                          }}
                        />
                      </div>
                      <span className="text-xs text-accent font-medium">
                        👎 {day.negative_pct.toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-12 h-2 rounded bg-muted/20 relative overflow-hidden">
                        <div
                          className="h-full bg-muted-foreground"
                          style={{
                            width: `${Math.min(day.neutral_pct, 100)}%`,
                          }}
                        />
                      </div>
                      <span className="text-xs text-muted-foreground font-medium">
                        😐 {day.neutral_pct.toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <span className="text-xs px-2 py-1 rounded-lg bg-primary/10 text-primary">
                      Positive: {day.positive_count}
                    </span>
                    <span className="text-xs px-2 py-1 rounded-lg bg-accent/10 text-accent">
                      Negative: {day.negative_count}
                    </span>
                    <span className="text-xs px-2 py-1 rounded-lg bg-muted/10 text-muted-foreground">
                      Neutral: {day.neutral_count}
                    </span>
                  </div>
                </div>
              ))}
          </div>
        ) : (
          <div className="py-8 text-center text-muted-foreground">
            No sentiment data available
          </div>
        )}
      </div>

      {/* Sentiment Interpretation Guide */}
      <div className="card-lumina">
        <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
          <TrendingUp className="w-4 h-4" />
          Sentiment Interpretation
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="p-3 rounded-lg bg-primary/10 border border-primary/20">
            <p className="text-xs font-medium text-primary mb-1">
              Positive (≥ 0.3)
            </p>
            <p className="text-xs text-muted-foreground">
              Bullish sentiment with strong positive coverage
            </p>
          </div>
          <div className="p-3 rounded-lg bg-muted/10 border border-muted/20">
            <p className="text-xs font-medium text-muted-foreground mb-1">
              Neutral (-0.3 to 0.3)
            </p>
            <p className="text-xs text-muted-foreground">
              Mixed or balanced market sentiment
            </p>
          </div>
          <div className="p-3 rounded-lg bg-accent/10 border border-accent/20">
            <p className="text-xs font-medium text-accent mb-1">
              Negative (≤ -0.3)
            </p>
            <p className="text-xs text-muted-foreground">
              Bearish sentiment with negative coverage
            </p>
          </div>
        </div>
      </div>

      {/* Demo Disclaimer Footer */}
      <div className="card-lumina border-2 border-yellow-300 bg-yellow-50/50">
        <div className="flex gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-yellow-900 mb-2">
              📊 Demo Data Notice
            </h3>
            <p className="text-sm text-yellow-800 mb-2">
              <strong>Important:</strong> This Market Insights feature is currently in development. 
              All sentiment scores, article counts, and trends displayed above are simulated data 
              for demonstration purposes only.
            </p>
            <ul className="text-xs text-yellow-700 space-y-1 list-disc list-inside">
              <li>No real news sources are being analyzed</li>
              <li>Sentiment scores are randomly generated</li>
              <li>Data does not reflect actual market conditions</li>
              <li>Do not use this information for investment decisions</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
