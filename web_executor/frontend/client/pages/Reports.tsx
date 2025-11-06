import { Zap, Download, Share2, Plus, Construction, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

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
            This Reports feature is currently under development. All reports, analysis, 
            and AI-generated insights shown below are simulated for demonstration purposes 
            and do not reflect actual market analysis.
          </p>
        </div>
      </div>
    </div>
  );
}

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
      {/* Header */}
      <div className="card-lumina flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-foreground">Reports</h1>
            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-semibold rounded-full border border-yellow-300">
              🚧 DEMO
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-2">
            AI-generated market analysis reports (Demo Version)
          </p>
        </div>
        <button className="btn-lumina-primary px-4 py-2 flex items-center gap-2" disabled>
          <Plus className="w-4 h-4" />
          Generate
        </button>
      </div>

      {/* Development Warning */}
      <DevelopmentWarning />

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
                <button 
                  className="p-2 rounded-lg hover:bg-secondary/50 transition-colors"
                  disabled
                  title="Demo feature - not functional"
                >
                  <Download className="w-4 h-4 text-muted-foreground" />
                </button>
                <button 
                  className="p-2 rounded-lg hover:bg-secondary/50 transition-colors"
                  disabled
                  title="Demo feature - not functional"
                >
                  <Share2 className="w-4 h-4 text-muted-foreground" />
                </button>
                <button 
                  className="btn-lumina px-4 py-2"
                  disabled
                  title="Demo feature - not functional"
                >
                  View
                </button>
              </div>
            </div>
          </div>
        ))}
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
              <strong>Important:</strong> This Reports feature is currently in development. 
              All reports, confidence scores, and AI-generated insights displayed above are 
              simulated data for demonstration purposes only.
            </p>
            <ul className="text-xs text-yellow-700 space-y-1 list-disc list-inside">
              <li>No actual AI analysis is being performed</li>
              <li>Reports cannot be downloaded or shared</li>
              <li>Confidence scores are randomly generated</li>
              <li>Do not use this information for investment decisions</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
