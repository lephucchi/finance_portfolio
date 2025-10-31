import { Zap, Download, Share2, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

const REPORTS = [
  {
    id: 1,
    title: "Q4 2024 Market Overview",
    created: "2024-01-15",
    status: "COMPLETE",
    confidence: 94,
  },
  {
    id: 2,
    title: "Banking Sector Analysis",
    created: "2024-01-14",
    status: "COMPLETE",
    confidence: 91,
  },
  {
    id: 3,
    title: "Technology Stock Insights",
    created: "2024-01-13",
    status: "COMPLETE",
    confidence: 87,
  },
];

export default function Reports() {
  return (
    <div className="space-y-6">
      <div className="card-lumina flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Reports</h1>
          <p className="text-sm text-muted-foreground mt-2">
            AI-generated market analysis reports
          </p>
        </div>
        <button className="btn-lumina-primary px-4 py-2 flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Generate
        </button>
      </div>

      {/* Generation Status */}
      <div className="card-lumina border-l-4 border-primary">
        <div className="flex items-start gap-4">
          <Zap className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
          <div className="flex-1">
            <h3 className="font-semibold text-primary mb-2">
              Analysis in Progress
            </h3>
            <p className="text-sm text-foreground mb-3">
              Processing market data and generating insights...
            </p>
            <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: "68%" }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              68% • ETA: 2 minutes
            </p>
          </div>
        </div>
      </div>

      {/* Reports List */}
      <div className="space-y-3">
        {REPORTS.map((report) => (
          <div key={report.id} className="card-lumina">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex-1">
                <h3 className="font-semibold text-foreground">
                  {report.title}
                </h3>
                <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-muted-foreground">
                  <span>{new Date(report.created).toLocaleDateString()}</span>
                  <span>•</span>
                  <span
                    className={cn(
                      "px-2 py-1 rounded-full",
                      "bg-primary/20 text-primary",
                    )}
                  >
                    {report.status}
                  </span>
                  <span>•</span>
                  <span>Confidence: {report.confidence}%</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button className="p-2 rounded-lg hover:bg-secondary/50 transition-colors">
                  <Download className="w-4 h-4" />
                </button>
                <button className="p-2 rounded-lg hover:bg-secondary/50 transition-colors">
                  <Share2 className="w-4 h-4" />
                </button>
                <button className="btn-lumina px-4 py-2">View</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
