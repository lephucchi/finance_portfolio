import { useState, useEffect } from "react";
import { FileText, TrendingUp, AlertCircle, Loader } from "lucide-react";
import { cn } from "@/lib/utils";
import { api, getDateRange, DATA_START_DATE, DATA_END_DATE } from "@/lib/api";
import type { SentimentSummary, SentimentOverall } from "@/lib/api";

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
  const [sentimentSummary, setSentimentSummary] = useState<SentimentSummary[]>(
    [],
  );
  const [sentimentOverall, setSentimentOverall] =
    useState<SentimentOverall | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadSentiment() {
      try {
        setLoading(true);
        setError(null);

        // Use available data range: Oct 18-30, 2025 (13 days)
        const result = await api.getSentimentSummary(DATA_START_DATE, DATA_END_DATE);

        setSentimentSummary(result.summary);
        setSentimentOverall(result.overall);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to load sentiment data";
        setError(message);
        console.error("Sentiment error:", err);
      } finally {
        setLoading(false);
      }
    }

    loadSentiment();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="card-lumina">
          <h1 className="text-3xl font-bold text-foreground">
            Market Insights
          </h1>
          <p className="text-sm text-muted-foreground mt-2">
            News sentiment analysis and financial intelligence
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
          <h1 className="text-3xl font-bold text-foreground">
            Market Insights
          </h1>
          <p className="text-sm text-muted-foreground mt-2">
            News sentiment analysis and financial intelligence
          </p>
        </div>
        <ErrorAlert message={error} />
      </div>
    );
  }

  const recentSentiment = sentimentSummary[sentimentSummary.length - 1];

  return (
    <div className="space-y-6">
      <div className="card-lumina">
        <h1 className="text-3xl font-bold text-foreground">Market Insights</h1>
        <p className="text-sm text-muted-foreground mt-2">
          News sentiment analysis and financial intelligence
        </p>
      </div>

      {/* Stats */}
      {sentimentOverall && (
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
    </div>
  );
}
