import { useNavigate } from "react-router-dom";
import {
  Shield,
  Lightbulb,
  Database,
  Brain,
  MessageSquare,
  BarChart3,
  Search,
  ChevronRight,
  TrendingUp,
  Cloud,
  Activity,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useI18n } from "@/hooks/useI18n";

export default function Homev2() {
  const navigate = useNavigate();
  const { t } = useI18n();

  const features = [
    {
      icon: Shield,
      titleKey: "home.aegisProtection",
      descKey: "home.aegisProtectionDesc",
      statsKey: "home.aegisStats",
      color: "text-blue-500",
      bgColor: "bg-blue-500/10",
    },
    {
      icon: Lightbulb,
      titleKey: "home.luminaIntelligence",
      descKey: "home.luminaIntelligenceDesc",
      statsKey: "home.luminaStats",
      color: "text-yellow-500",
      bgColor: "bg-yellow-500/10",
    },
    {
      icon: Database,
      titleKey: "home.lakehouseArch",
      descKey: "home.lakehouseArchDesc",
      statsKey: "home.lakehouseStats",
      color: "text-purple-500",
      bgColor: "bg-purple-500/10",
    },
    {
      icon: Brain,
      titleKey: "home.vietnameseSBERT",
      descKey: "home.vietnameseSBERTDesc",
      statsKey: "home.vietnameseSBERTStats",
      color: "text-pink-500",
      bgColor: "bg-pink-500/10",
    },
    {
      icon: Cloud,
      titleKey: "home.awsCloud",
      descKey: "home.awsCloudDesc",
      statsKey: "home.awsCloudStats",
      color: "text-cyan-500",
      bgColor: "bg-cyan-500/10",
    },
    {
      icon: TrendingUp,
      titleKey: "home.airflowPipeline",
      descKey: "home.airflowPipelineDesc",
      statsKey: "home.airflowStats",
      color: "text-orange-500",
      bgColor: "bg-orange-500/10",
    },
  ];

  const quickAccess = [
    {
      path: "/chat",
      icon: MessageSquare,
      titleKey: "home.metallicaAI",
      descKey: "home.metallicaAIDesc",
      badgeKey: "home.aiPowered",
    },
    {
      path: "/dashboard",
      icon: BarChart3,
      titleKey: "home.analyticsDashboard",
      descKey: "home.analyticsDashboardDesc",
      badgeKey: "home.realTime",
    },
    {
      path: "/screener",
      icon: Search,
      titleKey: "home.assetFinder",
      descKey: "home.assetFinderDesc",
      badgeKey: "home.stocks",
    },
    {
      path: "/about",
      icon: Shield,
      titleKey: "home.aboutAegis",
      descKey: "home.aboutAegisDesc",
      badgeKey: "home.documentation",
    },
  ];

  const metrics = [
    { labelKey: "home.costSavings", value: "87-94%", color: "text-green-500" },
    {
      labelKey: "home.querySpeed",
      value: "85-90%",
      subtextKey: "home.faster",
      color: "text-blue-500",
    },
    { labelKey: "home.uptime", value: "99.8%", color: "text-purple-500" },
    {
      labelKey: "home.compression",
      value: "92%",
      subtextKey: "home.spaceSaved",
      color: "text-orange-500",
    },
    {
      labelKey: "home.totalStocks",
      value: "10,950",
      color: "text-cyan-500",
    },
    {
      labelKey: "home.newsArticles",
      value: "12,027",
      color: "text-pink-500",
    },
    {
      labelKey: "home.vectorsIndexed",
      value: "10,585",
      color: "text-yellow-500",
    },
    { labelKey: "home.monthlyCost", value: "$6.32", color: "text-green-500" },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="card-lumina bg-gradient-to-br from-primary/10 to-secondary/10">
        <div className="text-center py-10 px-6">
          <div className="flex justify-center mb-6">
            <img
              src="/AEGIS_LUMINA.png"
              alt="AEGIS LUMINA"
              className="w-32 h-32 md:w-40 md:h-40 object-contain"
            />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-3">
            {t("home.title")}
          </h1>
          <p className="text-lg text-primary font-semibold italic mb-4">
            "{t("home.subtitle")}"
          </p>
          <p className="max-w-3xl mx-auto text-muted-foreground mb-6">
            {t("home.description")}
          </p>

          <div className="flex items-center justify-center gap-4">
            <button
              onClick={() => navigate("/chat")}
              className="px-6 py-3 bg-primary text-primary-foreground rounded-md flex items-center gap-2 hover:bg-primary/90 transition"
            >
              <MessageSquare className="w-4 h-4" />
              {t("home.startWithMetallica")}
            </button>
            <button
              onClick={() => navigate("/dashboard")}
              className="px-6 py-3 bg-secondary text-secondary-foreground rounded-md flex items-center gap-2 hover:bg-secondary/90 transition"
            >
              <BarChart3 className="w-4 h-4" />
              {t("home.viewDashboard")}
            </button>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {features.map((feature, idx) => {
          const Icon = feature.icon;
          return (
            <div key={idx} className="card-lumina p-6">
              <div
                className={cn(
                  "w-12 h-12 rounded-lg flex items-center justify-center mb-4",
                  feature.bgColor
                )}
              >
                <Icon className={cn("w-6 h-6", feature.color)} />
              </div>
              <h3 className="text-lg font-semibold mb-2">
                {t(feature.titleKey)}
              </h3>
              <p className="text-sm text-muted-foreground mb-3">
                {t(feature.descKey)}
              </p>
              <div className="text-xs text-primary font-medium bg-primary/10 px-3 py-1.5 rounded-full inline-block">
                {t(feature.statsKey)}
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Access */}
      <div className="card-lumina p-6">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-primary" />
          {t("home.quickAccess")}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {quickAccess.map((item, idx) => {
            const Icon = item.icon;
            return (
              <button
                key={idx}
                onClick={() => navigate(item.path)}
                className="p-4 rounded-lg border bg-secondary/20 text-left hover:bg-secondary/40 transition"
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold">{t(item.titleKey)}</h3>
                      <ChevronRight className="w-4 h-4 text-muted-foreground" />
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {t(item.descKey)}
                    </p>
                    <span className="text-xs bg-primary/20 text-primary px-2 py-1 rounded-full inline-block">
                      {t(item.badgeKey)}
                    </span>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* System Performance */}
      <div className="card-lumina p-6">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary" />
          {t("home.systemPerformance")}
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {metrics.map((metric, idx) => (
            <div key={idx} className="p-4 rounded-lg bg-background/50 text-center">
              <div className={cn("text-2xl font-bold mb-1", metric.color)}>
                {metric.value}
              </div>
              <div className="text-xs text-muted-foreground uppercase tracking-wide">
                {t(metric.labelKey)}
              </div>
              {metric.subtextKey && (
                <div className="text-xs text-muted-foreground italic mt-1">
                  {t(metric.subtextKey)}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Call to Action */}
      <div className="card-lumina p-6 text-center">
        <h2 className="text-2xl font-bold mb-3">{t("home.readyToExplore")}</h2>
        <p className="text-muted-foreground mb-4">
          {t("home.readyToExploreDesc")}
        </p>
        <div className="flex items-center justify-center gap-3">
          <button
            onClick={() => navigate("/guide")}
            className="px-5 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition"
          >
            {t("home.viewUserGuide")}
          </button>
          <button
            onClick={() => navigate("/about")}
            className="px-5 py-2 border-2 border-primary text-primary rounded-md hover:bg-primary/10 transition"
          >
            {t("home.learnMore")}
          </button>
        </div>
      </div>
    </div>
  );
}
