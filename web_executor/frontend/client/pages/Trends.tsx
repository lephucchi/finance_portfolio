import { useState, useEffect } from "react";
import {
  TrendingUp,
  AlertCircle,
  Loader,
  Award,
  TrendingDown,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { api, getDateRange } from "@/lib/api";
import type { SectorPerformance } from "@/lib/api";

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

function SectorCard({ sector }: { sector: SectorPerformance }) {
  const isPositive = sector.avg_change_pct >= 0;
  const Icon = isPositive ? TrendingUp : TrendingDown;

  return (
    <div className="card-lumina hover:shadow-lg transition-all duration-300">
      <div className="flex items-start justify-between mb-3">
        <h3 className="font-semibold text-foreground text-lg">
          {sector.sector}
        </h3>
        <Icon
          className={cn("w-5 h-5", isPositive ? "text-primary" : "text-accent")}
        />
      </div>

      <p
        className={cn(
          "text-3xl font-bold mb-3",
          isPositive ? "text-primary" : "text-accent",
        )}
      >
        {isPositive ? "+" : ""}
        {sector.avg_change_pct.toFixed(2)}%
      </p>

      <div className="space-y-2 mb-4">
        <p className="text-xs text-muted-foreground">
          {sector.stock_count} stocks • Vol:{" "}
          {(sector.total_volume / 1000000000).toFixed(1)}B
        </p>

        {sector.top_gainers.length > 0 && (
          <div>
            <p className="text-xs font-medium text-primary mb-1">Top Gainers</p>
            <div className="flex gap-1 flex-wrap">
              {sector.top_gainers.slice(0, 3).map((symbol) => (
                <span
                  key={symbol}
                  className="text-xs px-2 py-1 rounded-lg bg-primary/10 text-primary"
                >
                  {symbol}
                </span>
              ))}
            </div>
          </div>
        )}

        {sector.top_losers.length > 0 && (
          <div>
            <p className="text-xs font-medium text-accent mb-1">Top Losers</p>
            <div className="flex gap-1 flex-wrap">
              {sector.top_losers.slice(0, 3).map((symbol) => (
                <span
                  key={symbol}
                  className="text-xs px-2 py-1 rounded-lg bg-accent/10 text-accent"
                >
                  {symbol}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function Trends() {
  const [sectors, setSectors] = useState<SectorPerformance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadSectors() {
      try {
        setLoading(true);
        setError(null);

        const { startDate, endDate } = getDateRange(1);
        const data = await api.getSectorPerformance(startDate, endDate);

        const sortedData = [...data].sort(
          (a, b) => b.avg_change_pct - a.avg_change_pct,
        );
        setSectors(sortedData);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to load sector data";
        setError(message);
        console.error("Trends error:", err);
      } finally {
        setLoading(false);
      }
    }

    loadSectors();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="card-lumina">
          <h1 className="text-3xl font-bold text-foreground">Forecasts</h1>
          <p className="text-sm text-muted-foreground mt-2">
            AI-powered trend analysis and sector predictions
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
          <h1 className="text-3xl font-bold text-foreground">Forecasts</h1>
          <p className="text-sm text-muted-foreground mt-2">
            AI-powered trend analysis and sector predictions
          </p>
        </div>
        <ErrorAlert message={error} />
      </div>
    );
  }

  const topSector = sectors[0];
  const worstSector = sectors[sectors.length - 1];
  const avgChange =
    sectors.reduce((sum, s) => sum + s.avg_change_pct, 0) / sectors.length;

  const gainers = sectors.filter((s) => s.avg_change_pct > 0);
  const losers = sectors.filter((s) => s.avg_change_pct < 0);

  return (
    <div className="space-y-6">
      <div className="card-lumina">
        <h1 className="text-3xl font-bold text-foreground">Forecasts</h1>
        <p className="text-sm text-muted-foreground mt-2">
          AI-powered trend analysis and sector predictions
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card-lumina">
          <p className="text-xs text-muted-foreground font-medium mb-2">
            Market Avg Change
          </p>
          <p
            className={cn(
              "text-2xl font-bold",
              avgChange >= 0 ? "text-primary" : "text-accent",
            )}
          >
            {avgChange >= 0 ? "+" : ""}
            {avgChange.toFixed(2)}%
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            {gainers.length} gainers • {losers.length} losers
          </p>
        </div>

        {topSector && (
          <div className="card-lumina border-l-4 border-primary">
            <p className="text-xs text-muted-foreground font-medium mb-2">
              Best Performing
            </p>
            <p className="text-2xl font-bold text-primary">
              {topSector.sector}
            </p>
            <p className="text-xs text-primary mt-2">
              +{topSector.avg_change_pct.toFixed(2)}%
            </p>
          </div>
        )}

        {worstSector && (
          <div className="card-lumina border-l-4 border-accent">
            <p className="text-xs text-muted-foreground font-medium mb-2">
              Worst Performing
            </p>
            <p className="text-2xl font-bold text-accent">
              {worstSector.sector}
            </p>
            <p className="text-xs text-accent mt-2">
              {worstSector.avg_change_pct.toFixed(2)}%
            </p>
          </div>
        )}
      </div>

      {/* Sector Grid */}
      {sectors.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sectors.map((sector) => (
            <SectorCard key={sector.sector} sector={sector} />
          ))}
        </div>
      ) : (
        <div className="card-lumina py-8 text-center text-muted-foreground">
          No sector data available
        </div>
      )}

      {/* Market Outlook */}
      <div className="card-lumina">
        <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
          <Award className="w-5 h-5 text-primary" />
          Market Outlook
        </h2>
        <div className="space-y-4">
          <div>
            <p className="font-medium text-foreground mb-2">Sector Dynamics</p>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {gainers.length > losers.length
                ? `Market showing positive momentum with ${gainers.length} sectors in green. `
                : `Market showing mixed signals with ${losers.length} sectors declining. `}
              {topSector &&
                `${topSector.sector} sector leading with ${topSector.avg_change_pct.toFixed(2)}% change, `}
              {worstSector &&
                `while ${worstSector.sector} lags with ${worstSector.avg_change_pct.toFixed(2)}% change.`}
            </p>
          </div>

          <div>
            <p className="font-medium text-foreground mb-2">Key Insights</p>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>
                • {sectors.length} sectors analyzed with avg change of{" "}
                {avgChange.toFixed(2)}%
              </li>
              <li>
                • Total trading volume across sectors:{" "}
                {(
                  sectors.reduce((sum, s) => sum + s.total_volume, 0) /
                  1000000000
                ).toFixed(1)}
                B shares
              </li>
              <li>
                • Sector momentum:{" "}
                {gainers.length > losers.length ? "Bullish" : "Bearish"} trend
              </li>
            </ul>
          </div>

          <div>
            <p className="font-medium text-foreground mb-2">
              Investment Strategy
            </p>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Focus on sectors with positive momentum and strong gainers.
              Monitor declining sectors for potential reversal setups. Use
              volume and breadth to confirm trend strength across the market.
            </p>
          </div>
        </div>
      </div>

      {/* Detailed Performance Table */}
      <div className="card-lumina overflow-hidden">
        <h2 className="text-lg font-semibold text-foreground mb-4">
          Detailed Performance
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border/30 bg-secondary/30">
                <th className="px-4 py-3 text-left text-xs font-semibold text-foreground">
                  Sector
                </th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-foreground">
                  Change %
                </th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-foreground">
                  Stocks
                </th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-foreground">
                  Volume
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-foreground">
                  Top Gainers
                </th>
              </tr>
            </thead>
            <tbody>
              {sectors.map((sector) => (
                <tr
                  key={sector.sector}
                  className="border-b border-border/20 hover:bg-secondary/20 transition-colors"
                >
                  <td className="px-4 py-3 font-semibold text-foreground">
                    {sector.sector}
                  </td>
                  <td
                    className={cn(
                      "px-4 py-3 text-right font-semibold",
                      sector.avg_change_pct >= 0
                        ? "text-primary"
                        : "text-accent",
                    )}
                  >
                    {sector.avg_change_pct >= 0 ? "+" : ""}
                    {sector.avg_change_pct.toFixed(2)}%
                  </td>
                  <td className="px-4 py-3 text-right text-sm text-muted-foreground">
                    {sector.stock_count}
                  </td>
                  <td className="px-4 py-3 text-right text-sm text-muted-foreground">
                    {(sector.total_volume / 1000000000).toFixed(1)}B
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1 flex-wrap">
                      {sector.top_gainers.slice(0, 2).map((symbol) => (
                        <span
                          key={symbol}
                          className="text-xs px-2 py-1 rounded-lg bg-primary/10 text-primary font-medium"
                        >
                          {symbol}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
