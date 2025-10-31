import { useState, useEffect } from "react";
import { BarChart2, Zap, AlertCircle, Loader } from "lucide-react";
import { cn } from "@/lib/utils";
import { api, getDateRange, formatCurrency, formatPercent } from "@/lib/api";
import type { StockData } from "@/lib/api";

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

export default function Screener() {
  const [stocks, setStocks] = useState<StockData[]>([]);
  const [filteredStocks, setFilteredStocks] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    searchSymbol: "",
    minChange: "",
    maxChange: "",
    minVolume: "",
  });

  useEffect(() => {
    async function loadStocks() {
      try {
        setLoading(true);
        setError(null);

        const { startDate, endDate } = getDateRange(1);
        const data = await api.getStocks(startDate, endDate);

        setStocks(data);
        setFilteredStocks(data);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to load stock data";
        setError(message);
        console.error("Screener error:", err);
      } finally {
        setLoading(false);
      }
    }

    loadStocks();
  }, []);

  useEffect(() => {
    let filtered = stocks;

    if (filters.searchSymbol) {
      filtered = filtered.filter((s) =>
        s.symbol.toLowerCase().includes(filters.searchSymbol.toLowerCase()),
      );
    }

    if (filters.minChange) {
      const minVal = parseFloat(filters.minChange);
      filtered = filtered.filter((s) => s.price_change_pct >= minVal);
    }

    if (filters.maxChange) {
      const maxVal = parseFloat(filters.maxChange);
      filtered = filtered.filter((s) => s.price_change_pct <= maxVal);
    }

    if (filters.minVolume) {
      const minVol = parseFloat(filters.minVolume) * 1000000;
      filtered = filtered.filter((s) => s.volume >= minVol);
    }

    setFilteredStocks(filtered);
  }, [filters, stocks]);

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const resetFilters = () => {
    setFilters({
      searchSymbol: "",
      minChange: "",
      maxChange: "",
      minVolume: "",
    });
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="card-lumina">
          <h1 className="text-3xl font-bold text-foreground">Asset Finder</h1>
          <p className="text-sm text-muted-foreground mt-2">
            Discover stocks matching your criteria
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
          <h1 className="text-3xl font-bold text-foreground">Asset Finder</h1>
          <p className="text-sm text-muted-foreground mt-2">
            Discover stocks matching your criteria
          </p>
        </div>
        <ErrorAlert message={error} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="card-lumina">
        <h1 className="text-3xl font-bold text-foreground">Asset Finder</h1>
        <p className="text-sm text-muted-foreground mt-2">
          Discover stocks matching your criteria
        </p>
      </div>

      {/* Filters */}
      <div className="card-lumina">
        <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-primary" />
          Search & Filter
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="text-xs font-medium text-muted-foreground block mb-2">
              Symbol
            </label>
            <input
              type="text"
              placeholder="e.g., VIC, VCB"
              className="input-lumina w-full"
              value={filters.searchSymbol}
              onChange={(e) =>
                handleFilterChange("searchSymbol", e.target.value)
              }
            />
          </div>
          <div>
            <label className="text-xs font-medium text-muted-foreground block mb-2">
              Min Change %
            </label>
            <input
              type="number"
              placeholder="-10"
              className="input-lumina w-full"
              value={filters.minChange}
              onChange={(e) => handleFilterChange("minChange", e.target.value)}
            />
          </div>
          <div>
            <label className="text-xs font-medium text-muted-foreground block mb-2">
              Max Change %
            </label>
            <input
              type="number"
              placeholder="10"
              className="input-lumina w-full"
              value={filters.maxChange}
              onChange={(e) => handleFilterChange("maxChange", e.target.value)}
            />
          </div>
          <div>
            <label className="text-xs font-medium text-muted-foreground block mb-2">
              Min Volume (M)
            </label>
            <input
              type="number"
              placeholder="1"
              className="input-lumina w-full"
              value={filters.minVolume}
              onChange={(e) => handleFilterChange("minVolume", e.target.value)}
            />
          </div>
        </div>
        <div className="flex gap-2">
          <button className="btn-lumina-primary px-6 py-2">
            Apply Filters
          </button>
          <button
            onClick={resetFilters}
            className="px-6 py-2 rounded-lg bg-secondary/50 text-foreground hover:bg-secondary transition-all duration-300"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Results Table */}
      <div className="card-lumina overflow-hidden">
        <div className="mb-4 text-sm text-muted-foreground">
          Showing {filteredStocks.length} of {stocks.length} stocks
        </div>
        {filteredStocks.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border/30 bg-secondary/30">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-foreground">
                    Symbol
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-foreground">
                    Close Price
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-foreground">
                    Change %
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-foreground">
                    Volume
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-foreground">
                    MA20
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-foreground">
                    Volatility
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-foreground">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredStocks.slice(0, 20).map((stock) => (
                  <tr
                    key={`${stock.symbol}-${stock.data_date}`}
                    className="border-b border-border/20 hover:bg-secondary/20 transition-colors"
                  >
                    <td className="px-4 py-3">
                      <p className="font-semibold text-foreground">
                        {stock.symbol}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {stock.data_date}
                      </p>
                    </td>
                    <td className="px-4 py-3 text-right font-semibold text-foreground">
                      {formatCurrency(stock.close)}
                    </td>
                    <td
                      className={cn(
                        "px-4 py-3 text-right font-semibold",
                        stock.price_change_pct > 0
                          ? "text-primary"
                          : "text-accent",
                      )}
                    >
                      {formatPercent(stock.price_change_pct)}
                    </td>
                    <td className="px-4 py-3 text-right text-sm text-muted-foreground">
                      {(stock.volume / 1000000).toFixed(1)}M
                    </td>
                    <td className="px-4 py-3 text-right text-sm text-muted-foreground">
                      {formatCurrency(stock.ma_20)}
                    </td>
                    <td className="px-4 py-3 text-right text-sm font-medium">
                      <span
                        className={cn(
                          "px-2 py-1 rounded-lg",
                          stock.volatility_7d > 0.05
                            ? "bg-accent/20 text-accent"
                            : "bg-primary/20 text-primary",
                        )}
                      >
                        {(stock.volatility_7d * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button className="text-xs px-3 py-1 rounded-lg bg-primary/10 text-primary hover:bg-primary/20 transition-colors">
                        Analyze
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-8 text-center text-muted-foreground">
            No stocks match your filters
          </div>
        )}
      </div>

      {/* Summary Stats */}
      {filteredStocks.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card-lumina">
            <p className="text-xs text-muted-foreground font-medium mb-2">
              Avg Price Change
            </p>
            <p
              className={cn(
                "text-2xl font-bold",
                filteredStocks.reduce((sum, s) => sum + s.price_change_pct, 0) /
                  filteredStocks.length >
                  0
                  ? "text-primary"
                  : "text-accent",
              )}
            >
              {(
                filteredStocks.reduce((sum, s) => sum + s.price_change_pct, 0) /
                filteredStocks.length
              ).toFixed(2)}
              %
            </p>
          </div>

          <div className="card-lumina">
            <p className="text-xs text-muted-foreground font-medium mb-2">
              Total Volume
            </p>
            <p className="text-2xl font-bold text-foreground">
              {(
                filteredStocks.reduce((sum, s) => sum + s.volume, 0) / 1000000
              ).toFixed(0)}
              M
            </p>
          </div>

          <div className="card-lumina">
            <p className="text-xs text-muted-foreground font-medium mb-2">
              Avg Volatility
            </p>
            <p className="text-2xl font-bold text-foreground">
              {(
                (filteredStocks.reduce((sum, s) => sum + s.volatility_7d, 0) /
                  filteredStocks.length) *
                100
              ).toFixed(2)}
              %
            </p>
          </div>

          <div className="card-lumina">
            <p className="text-xs text-muted-foreground font-medium mb-2">
              Gainers vs Losers
            </p>
            <p className="text-2xl font-bold text-foreground">
              {filteredStocks.filter((s) => s.price_change_pct > 0).length} /{" "}
              {filteredStocks.filter((s) => s.price_change_pct < 0).length}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
