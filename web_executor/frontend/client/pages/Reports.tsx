import { Zap, Download, Share2, Plus, Construction, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { useI18n } from "@/hooks/useI18n";

function DevelopmentWarning({ title, message }: { title?: string; message?: string }) {
  return (
    <div className="card-lumina border-l-4 border-yellow-500 bg-yellow-50">
      <div className="flex gap-3">
        <Construction className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="font-semibold text-yellow-900 flex items-center gap-2">
            {title || "🚧 Under Development - Demo Data Only"}
          </h3>
          <p className="text-sm text-yellow-800 mt-1">
            {message || "This Reports feature is currently under development. All reports, analysis, and AI-generated insights shown below are simulated for demonstration purposes and do not reflect actual market analysis."}
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
  const { t, language } = useI18n();
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card-lumina flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-foreground">{t('reports.title')}</h1>
            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-semibold rounded-full border border-yellow-300">
              {t('reports.demoTag')}
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-2">
            {t('reports.subtitle')}
          </p>
        </div>
        <button className="btn-lumina-primary px-4 py-2 flex items-center gap-2" disabled>
          <Plus className="w-4 h-4" />
          {t('reports.generateButton')}
        </button>
      </div>

      {/* Development Warning */}
      <DevelopmentWarning 
        title={t('reports.developmentWarning')}
        message={t('reports.developmentWarningText')}
      />

      {/* Generation Status */}
      <div className="card-lumina border-l-4 border-primary">
        <div className="flex items-start gap-4">
          <Zap className="w-5 h-5 text-primary flex-shrink-0 mt-1" />
          <div className="flex-1">
            <h3 className="font-semibold text-primary mb-2">
              {t('reports.analysisInProgress')}
            </h3>
            <p className="text-sm text-foreground mb-3">
              {t('reports.processingMessage')}
            </p>
            <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: "68%" }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              68% • {t('reports.eta')} 2 {t('reports.minutes')}
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
                  <span>{t('reports.created')}: {new Date(report.created).toLocaleDateString(language === 'vi' ? 'vi-VN' : 'en-US')}</span>
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
                  <span>{t('reports.confidence')} {report.confidence}%</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button 
                  className="p-2 rounded-lg hover:bg-secondary/50 transition-colors"
                  disabled
                  title={t('reports.demoFeatureNotFunctional')}
                >
                  <Download className="w-4 h-4 text-muted-foreground" />
                </button>
                <button 
                  className="p-2 rounded-lg hover:bg-secondary/50 transition-colors"
                  disabled
                  title={t('reports.demoFeatureNotFunctional')}
                >
                  <Share2 className="w-4 h-4 text-muted-foreground" />
                </button>
                <button 
                  className="btn-lumina px-4 py-2"
                  disabled
                  title={t('reports.demoFeatureNotFunctional')}
                >
                  {t('reports.view')}
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
              {t('reports.disclaimer.title')}
            </h3>
            <p className="text-sm text-yellow-800 mb-2">
              <strong>{t('reports.disclaimer.important')}</strong> {t('reports.disclaimer.message')}
            </p>
            <ul className="text-xs text-yellow-700 space-y-1 list-disc list-inside">
              {(language === 'vi'
                ? [
                    'Không có phân tích AI thực tế nào được thực hiện',
                    'Báo cáo không thể tải xuống hoặc chia sẻ',
                    'Điểm độ tin cây được tạo ngẫu nhiên',
                    'Không sử dụng thông tin này để quyết định đầu tư',
                  ]
                : [
                    'No actual AI analysis is being performed',
                    'Reports cannot be downloaded or shared',
                    'Confidence scores are randomly generated',
                    'Do not use this information for investment decisions',
                  ]
              ).map((point, index) => (
                <li key={index}>{point}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
