import { useState } from "react";
import { Target, TrendingUp, Zap, Users, Code, Database, Cloud, Brain, Layers, MessageSquare, GitBranch, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { useI18n } from "@/hooks/useI18n";

type Section = "overview" | "lakehouse" | "rag" | "airflow" | "architecture";

export default function About() {
  const [activeSection, setActiveSection] = useState<Section>("overview");
  const { t } = useI18n();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card-lumina bg-gradient-to-br from-primary/10 to-secondary/10">
        <div className="text-center py-8">
          <div className="flex justify-center mb-4">
            <img 
              src="/AEGIS_LUMINA.png" 
              alt="AEGIS LUMINA Logo" 
              className="w-48 h-48 md:w-56 md:h-56 object-contain"
            />
          </div>
          <p className="text-lg text-primary font-semibold mb-3 italic">
            "{t('about.tagline')}"
          </p>
          <p className="text-base text-muted-foreground mb-4 max-w-3xl mx-auto px-4">
            {t('about.description')}
          </p>
          <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
            <span className="px-3 py-1 bg-primary/20 text-primary rounded-full font-medium">
              {t('about.version')}
            </span>
            <span>•</span>
            <span>{t('about.productionReady')}</span>
            <span>•</span>
            <span>{t('about.november2025')}</span>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="card-lumina">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <button
            onClick={() => setActiveSection("overview")}
            className={cn(
              "flex items-center gap-2 px-4 py-3 rounded-lg transition-all",
              activeSection === "overview"
                ? "bg-primary text-primary-foreground shadow-lg"
                : "bg-secondary/30 text-muted-foreground hover:bg-secondary/50"
            )}
          >
            <Target className="w-5 h-5" />
            <span className="font-medium">{t('about.overview')}</span>
          </button>
          <button
            onClick={() => setActiveSection("lakehouse")}
            className={cn(
              "flex items-center gap-2 px-4 py-3 rounded-lg transition-all",
              activeSection === "lakehouse"
                ? "bg-primary text-primary-foreground shadow-lg"
                : "bg-secondary/30 text-muted-foreground hover:bg-secondary/50"
            )}
          >
            <Layers className="w-5 h-5" />
            <span className="font-medium">{t('about.lakehouse')}</span>
          </button>
          <button
            onClick={() => setActiveSection("rag")}
            className={cn(
              "flex items-center gap-2 px-4 py-3 rounded-lg transition-all",
              activeSection === "rag"
                ? "bg-primary text-primary-foreground shadow-lg"
                : "bg-secondary/30 text-muted-foreground hover:bg-secondary/50"
            )}
          >
            <MessageSquare className="w-5 h-5" />
            <span className="font-medium">{t('about.ragChatbot')}</span>
          </button>
          <button
            onClick={() => setActiveSection("airflow")}
            className={cn(
              "flex items-center gap-2 px-4 py-3 rounded-lg transition-all",
              activeSection === "airflow"
                ? "bg-primary text-primary-foreground shadow-lg"
                : "bg-secondary/30 text-muted-foreground hover:bg-secondary/50"
            )}
          >
            <GitBranch className="w-5 h-5" />
            <span className="font-medium">{t('about.airflowEtl')}</span>
          </button>
          <button
            onClick={() => setActiveSection("architecture")}
            className={cn(
              "flex items-center gap-2 px-4 py-3 rounded-lg transition-all",
              activeSection === "architecture"
                ? "bg-primary text-primary-foreground shadow-lg"
                : "bg-secondary/30 text-muted-foreground hover:bg-secondary/50"
            )}
          >
            <Code className="w-5 h-5" />
            <span className="font-medium">{t('about.backendFrontendMcp')}</span>
          </button>
        </div>
      </div>

      {/* OVERVIEW SECTION */}
      {activeSection === "overview" && (
        <>
      {/* Mission Statement */}
      <div className="card-lumina">
        <div className="flex items-start gap-4">
          <Target className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-3">
              {t('about.missionStatement')}
            </h2>
            <div className="prose prose-sm max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                {t('about.missionText')}
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                <div className="p-4 bg-primary/5 rounded-lg">
                  <div className="text-3xl font-bold text-primary mb-2">87-94%</div>
                  <div className="text-sm text-muted-foreground">{t('about.costSavings')}</div>
                </div>
                <div className="p-4 bg-primary/5 rounded-lg">
                  <div className="text-3xl font-bold text-primary mb-2">85-90%</div>
                  <div className="text-sm text-muted-foreground">{t('about.fasterQuerySpeed')}</div>
                </div>
                <div className="p-4 bg-primary/5 rounded-lg">
                  <div className="text-3xl font-bold text-primary mb-2">99.8%</div>
                  <div className="text-sm text-muted-foreground">{t('about.systemUptime')}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Project Overview */}
      <div className="card-lumina">
        <div className="flex items-start gap-4 mb-6">
          <TrendingUp className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-3">
              {t('about.projectOverview')}
            </h2>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column */}
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                {t('about.keySolutions')}
              </h3>
              <ul className="space-y-2">
                {[
                  "Lakehouse Architecture (Medallion: Bronze-Silver-Gold)",
                  "Cloud-Native Stack (AWS S3, Glue, Athena)",
                  "Automated ETL Pipeline (Airflow + PySpark)",
                  "RAG Chatbot (FAISS + Gemini API)",
                  "Real-time API (FastAPI)",
                  "Modern Web UI (React + TypeScript)"
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                    <span className="text-primary mt-1">✓</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                {t('about.dataProcessed')}
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-secondary/30 rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">{t('about.stocks')}</div>
                  <div className="text-lg font-bold text-foreground">10,950+</div>
                </div>
                <div className="p-3 bg-secondary/30 rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">{t('about.news')}</div>
                  <div className="text-lg font-bold text-foreground">12,027</div>
                </div>
                <div className="p-3 bg-secondary/30 rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">{t('about.indicators')}</div>
                  <div className="text-lg font-bold text-foreground">18,250</div>
                </div>
                <div className="p-3 bg-secondary/30 rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">{t('about.symbols')}</div>
                  <div className="text-lg font-bold text-foreground">30</div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                {t('about.systemPerformance')}
              </h3>
              <div className="space-y-3">
                {[
                  { label: t('about.queryLatencyP50'), target: "< 2s", actual: "0.8s", status: "✅" },
                  { label: t('about.queryLatencyP99'), target: "< 5s", actual: "2.1s", status: "✅" },
                  { label: t('about.dataFreshness'), target: "< 30min", actual: "5-15min", status: "✅" },
                  { label: t('about.vectorSearchLatency'), target: "< 50ms", actual: "12ms", status: "✅" },
                  { label: t('about.systemUptime'), target: "> 99%", actual: "99.8%", status: "✅" }
                ].map((metric, i) => (
                  <div key={i} className="flex items-center justify-between p-2 bg-secondary/20 rounded">
                    <span className="text-sm text-muted-foreground">{metric.label}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">{t('about.target')}: {metric.target}</span>
                      <span className="text-sm font-semibold text-primary">{t('about.actual')}: {metric.actual}</span>
                      <span>{metric.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Technology Stack */}
      <div className="card-lumina">
        <div className="flex items-start gap-4 mb-6">
          <Code className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-3">
              {t('about.technologyStack')}
            </h2>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {/* Cloud Infrastructure */}
          <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg">
            <Cloud className="w-6 h-6 text-blue-600 mb-3" />
            <h3 className="font-semibold text-foreground mb-2">{t('about.cloudInfrastructure')}</h3>
            <ul className="space-y-1 text-sm text-muted-foreground">
              <li>• AWS S3</li>
              <li>• AWS Glue</li>
              <li>• AWS Athena</li>
              <li>• EC2 & EMR</li>
            </ul>
          </div>

          {/* Data Processing */}
          <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg">
            <Database className="w-6 h-6 text-green-600 mb-3" />
            <h3 className="font-semibold text-foreground mb-2">{t('about.dataProcessing')}</h3>
            <ul className="space-y-1 text-sm text-muted-foreground">
              <li>• Apache Airflow</li>
              <li>• Apache Spark</li>
              <li>• PySpark</li>
              <li>• Pandas</li>
            </ul>
          </div>

          {/* Backend & API */}
          <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg">
            <Zap className="w-6 h-6 text-purple-600 mb-3" />
            <h3 className="font-semibold text-foreground mb-2">{t('about.backendApi')}</h3>
            <ul className="space-y-1 text-sm text-muted-foreground">
              <li>• FastAPI</li>
              <li>• Python Async</li>
              <li>• Supabase</li>
              <li>• Redis Cache</li>
            </ul>
          </div>

          {/* AI/ML */}
          <div className="p-4 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-lg">
            <Brain className="w-6 h-6 text-orange-600 mb-3" />
            <h3 className="font-semibold text-foreground mb-2">{t('about.aiMlNlp')}</h3>
            <ul className="space-y-1 text-sm text-muted-foreground">
              <li>• FAISS Vector DB</li>
              <li>• Vietnamese SBERT</li>
              <li>• Google Gemini</li>
              <li>• HuggingFace</li>
            </ul>
          </div>

          {/* Frontend */}
          <div className="p-4 bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-indigo-900/20 dark:to-indigo-800/20 rounded-lg">
            <Code className="w-6 h-6 text-indigo-600 mb-3" />
            <h3 className="font-semibold text-foreground mb-2">{t('about.frontendStack')}</h3>
            <ul className="space-y-1 text-sm text-muted-foreground">
              <li>• React 18.2.0</li>
              <li>• TypeScript 5.2</li>
              <li>• Vite 4.4.0</li>
              <li>• TailwindCSS 3.3</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Future Vision */}
      <div className="card-lumina">
        <div className="flex items-start gap-4 mb-6">
          <TrendingUp className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-3">
              {t('about.futureVision')}
            </h2>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[
            {
              phase: t('about.phase1Immediate'),
              time: t('about.week1_2'),
              items: [
                "Production monitoring & alerting",
                "User authentication system",
                "Rate limiting enforcement",
                "Performance optimization"
              ]
            },
            {
              phase: t('about.phase2ShortTerm'),
              time: t('about.month1_2'),
              items: [
                "Query reformulation",
                "Multi-turn conversations",
                "Advanced filters & search",
                "Horizontal scaling"
              ]
            },
            {
              phase: t('about.phase3MediumTerm'),
              time: t('about.month3_6'),
              items: [
                "BI Dashboards integration",
                "Predictive models",
                "Real-time analytics",
                "Named entity recognition"
              ]
            },
            {
              phase: t('about.phase4LongTerm'),
              time: t('about.month6_12'),
              items: [
                "Real-time streaming (Kafka)",
                "Multi-language support",
                "Mobile applications",
                "Enterprise features"
              ]
            }
          ].map((phase, i) => (
            <div key={i} className="p-4 bg-secondary/20 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-foreground">{phase.phase}</h3>
                <span className="text-xs text-muted-foreground bg-primary/10 px-2 py-1 rounded">
                  {phase.time}
                </span>
              </div>
              <ul className="space-y-2">
                {phase.items.map((item, j) => (
                  <li key={j} className="flex items-start gap-2 text-sm text-muted-foreground">
                    <span className="text-primary mt-0.5">→</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Team */}
      <div className="card-lumina">
        <div className="flex items-start gap-4 mb-6">
          <Users className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-3">
              {t('about.developmentTeam')}
            </h2>
            <p className="text-muted-foreground">
              {t('about.teamDescription')}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            {
              role: t('about.dataEngineering'),
              desc: t('about.dataEngineeringDesc')
            },
            {
              role: t('about.aiMlDevelopment'),
              desc: t('about.aiMlDevelopmentDesc')
            },
            {
              role: t('about.fullStackDevelopment'),
              desc: t('about.fullStackDevelopmentDesc')
            }
          ].map((team, i) => (
            <div key={i} className="p-4 bg-gradient-to-br from-primary/5 to-secondary/5 rounded-lg">
              <h3 className="font-semibold text-foreground mb-2">{team.role}</h3>
              <p className="text-sm text-muted-foreground">{team.desc}</p>
            </div>
          ))}
        </div>

        <div className="mt-6 p-4 bg-primary/5 rounded-lg border-l-4 border-primary">
          <p className="text-sm text-foreground">
            <strong>{t('about.openForCollaboration')}</strong> {t('about.collaborationText')}
          </p>
        </div>
      </div>
        </>
      )}

      {/* LAKEHOUSE SECTION */}
      {activeSection === "lakehouse" && (
        <>
          {/* Lakehouse Overview */}
          <div className="card-lumina">
            <div className="flex items-start gap-4">
              <Layers className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-foreground mb-3">
                  {t('about.lakehouseArchitecture')}
                </h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                  {t('about.lakehouseDescription')}
                </p>
              </div>
            </div>
          </div>

          {/* Medallion Architecture */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.medallionArchitecture')}</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Bronze Layer */}
              <div className="p-4 bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-900/20 dark:to-amber-800/20 rounded-lg border-2 border-amber-200 dark:border-amber-800">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-3 h-3 rounded-full bg-amber-600"></div>
                  <h4 className="font-bold text-foreground">{t('about.bronzeLayer')}</h4>
                </div>
                <p className="text-sm text-muted-foreground mb-3">{t('about.bronzeLayerDesc')}</p>
                <ul className="text-xs text-muted-foreground space-y-1">
                  <li>• Original format (JSON, CSV)</li>
                  <li>• No data cleaning</li>
                  <li>• All source columns</li>
                  <li>• Size: ~875 MB</li>
                  <li>• Use: Audit trail, recovery</li>
                </ul>
              </div>

              {/* Silver Layer */}
              <div className="p-4 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/20 dark:to-gray-800/20 rounded-lg border-2 border-gray-300 dark:border-gray-700">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-3 h-3 rounded-full bg-gray-400"></div>
                  <h4 className="font-bold text-foreground">{t('about.silverLayer')}</h4>
                </div>
                <p className="text-sm text-muted-foreground mb-3">{t('about.silverLayerDesc')}</p>
                <ul className="text-xs text-muted-foreground space-y-1">
                  <li>• Parquet format (Snappy)</li>
                  <li>• Removed duplicates & nulls</li>
                  <li>• Standardized schema</li>
                  <li>• Size: ~68 MB (92% compression)</li>
                  <li>• Use: Analytics, ML training</li>
                </ul>
              </div>

              {/* Gold Layer */}
              <div className="p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 rounded-lg border-2 border-yellow-300 dark:border-yellow-700">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-3 h-3 rounded-full bg-yellow-600"></div>
                  <h4 className="font-bold text-foreground">{t('about.goldLayer')}</h4>
                </div>
                <p className="text-sm text-muted-foreground mb-3">{t('about.goldLayerDesc')}</p>
                <ul className="text-xs text-muted-foreground space-y-1">
                  <li>• Optimized for queries</li>
                  <li>• Aggregated metrics</li>
                  <li>• Feature engineering</li>
                  <li>• Size: ~99 MB</li>
                  <li>• Use: Dashboards, APIs</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Data Sources */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.dataSources')}</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-2">{t('about.stockData')}</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Source: VNStock API v3</li>
                  <li>• Symbols: 30 major stocks</li>
                  <li>• Records: 10,950+</li>
                  <li>• Period: 365 days</li>
                  <li>• Update: Real-time (2-5 min delay)</li>
                </ul>
              </div>

              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-2">{t('about.newsData')}</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Source: Google Custom Search</li>
                  <li>• Articles: 12,027</li>
                  <li>• Language: Vietnamese</li>
                  <li>• Coverage: 1-3 years</li>
                  <li>• Topics: Finance, Banking, Markets</li>
                </ul>
              </div>

              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-2">{t('about.macroData')}</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Source: Economic APIs</li>
                  <li>• Indicators: 50+</li>
                  <li>• Records: 18,250</li>
                  <li>• Period: 6 years (2020-2025)</li>
                  <li>• Update: Daily/Weekly</li>
                </ul>
              </div>
            </div>
          </div>

          {/* AWS Stack */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.awsInfrastructure')}</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <Cloud className="w-6 h-6 text-blue-600 mb-2" />
                <h4 className="font-semibold text-foreground mb-2">{t('about.amazonS3')}</h4>
                <p className="text-sm text-muted-foreground">{t('about.amazonS3Desc')}</p>
              </div>
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <Database className="w-6 h-6 text-green-600 mb-2" />
                <h4 className="font-semibold text-foreground mb-2">{t('about.awsGlue')}</h4>
                <p className="text-sm text-muted-foreground">{t('about.awsGlueDesc')}</p>
              </div>
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <Zap className="w-6 h-6 text-purple-600 mb-2" />
                <h4 className="font-semibold text-foreground mb-2">{t('about.awsAthena')}</h4>
                <p className="text-sm text-muted-foreground">{t('about.awsAthenaDesc')}</p>
              </div>
            </div>
          </div>
        </>
      )}

      {/* RAG SECTION */}
      {activeSection === "rag" && (
        <>
          {/* RAG Overview */}
          <div className="card-lumina">
            <div className="flex items-start gap-4">
              <MessageSquare className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-foreground mb-3">
                  {t('about.ragChatbotSystem')}
                </h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                  {t('about.ragDescription')}
                </p>
              </div>
            </div>
          </div>

          {/* RAG Pipeline */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.howRagWorks')}</h3>
            <div className="space-y-4">
              {[
                {
                  step: 1,
                  title: t('about.queryEmbedding'),
                  desc: t('about.queryEmbeddingDesc'),
                  time: "~50ms"
                },
                {
                  step: 2,
                  title: t('about.vectorSearch'),
                  desc: t('about.vectorSearchDesc'),
                  time: "<10ms"
                },
                {
                  step: 3,
                  title: t('about.reranking'),
                  desc: t('about.rerankingDesc'),
                  time: "~100ms"
                },
                {
                  step: 4,
                  title: t('about.contextPreparation'),
                  desc: t('about.contextPreparationDesc'),
                  time: "~10ms"
                },
                {
                  step: 5,
                  title: t('about.llmGeneration'),
                  desc: t('about.llmGenerationDesc'),
                  time: "~800ms"
                },
                {
                  step: 6,
                  title: t('about.responseFormatting'),
                  desc: t('about.responseFormattingDesc'),
                  time: "~10ms"
                }
              ].map((item) => (
                <div key={item.step} className="flex items-start gap-4 p-4 bg-secondary/20 rounded-lg">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground font-bold flex-shrink-0">
                    {item.step}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-semibold text-foreground">{item.title}</h4>
                      <span className="text-xs text-primary font-mono">{item.time}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">{item.desc}</p>
                  </div>
                  {item.step < 6 && <ChevronRight className="w-5 h-5 text-muted-foreground mt-1" />}
                </div>
              ))}
            </div>
            <div className="mt-4 p-3 bg-primary/10 rounded-lg text-center">
              <span className="text-sm font-semibold text-foreground">{t('about.totalResponseTime')} </span>
              <span className="text-lg font-bold text-primary">~5 second</span>
            </div>
          </div>

          {/* RAG Technology */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.ragTechnologyStack')}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-3">{t('about.embeddingSearch')}</h4>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span><strong>Vietnamese-SBERT:</strong> 768-dim embeddings optimized for Vietnamese text</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span><strong>FAISS:</strong> Facebook's vector similarity search (IndexFlatIP)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span><strong>Cosine Similarity:</strong> Measure relevance between query and documents</span>
                  </li>
                </ul>
              </div>

              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-3">{t('about.generationStorage')}</h4>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span><strong>Google Gemini 2.0 Flash:</strong> Fast, cost-effective LLM ($0.075 per 1M tokens)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span><strong>Supabase PostgreSQL:</strong> Chat history and user management</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span><strong>AWS S3:</strong> Vector database storage and backups</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* RAG Features */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.ragKeyFeatures')}</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="text-2xl mb-2">✅</div>
                <h4 className="font-semibold text-foreground mb-2">{t('about.noHallucination')}</h4>
                <p className="text-sm text-muted-foreground">
                  {t('about.noHallucinationDesc')}
                </p>
              </div>
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="text-2xl mb-2">🇻🇳</div>
                <h4 className="font-semibold text-foreground mb-2">{t('about.vietnameseSupport')}</h4>
                <p className="text-sm text-muted-foreground">
                  {t('about.vietnameseSupportDesc')}
                </p>
              </div>
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <div className="text-2xl mb-2">⚡</div>
                <h4 className="font-semibold text-foreground mb-2">{t('about.fastAccurate')}</h4>
                <p className="text-sm text-muted-foreground">
                  {t('about.fastAccurateDesc')}
                </p>
              </div>
            </div>
          </div>

          {/* RAG Stats */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.ragSystemStatistics')}</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">10,585</div>
                <div className="text-xs text-muted-foreground">{t('about.indexedVectors')}</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">12,027</div>
                <div className="text-xs text-muted-foreground">{t('about.newsArticles')}</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">&lt;10ms</div>
                <div className="text-xs text-muted-foreground">{t('about.vectorSearchTime')}</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">768</div>
                <div className="text-xs text-muted-foreground">{t('about.embeddingDimensions')}</div>
              </div>
            </div>
          </div>

          {/* Initial Training (Kaggle) */}
          <div className="card-lumina border-l-4 border-blue-500">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.initialRagTraining')}</h3>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                The initial vector database was created using Kaggle notebooks with GPU acceleration for faster embedding generation.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-3">{t('about.trainingProcess')}</h4>
                  <ol className="text-sm text-muted-foreground space-y-2">
                    <li className="flex items-start gap-2">
                      <span className="font-bold text-primary">1.</span>
                      <span>Load news dataset (combined_text, title, source, link)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-bold text-primary">2.</span>
                      <span>Clean data: remove nulls, empty content, duplicates</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-bold text-primary">3.</span>
                      <span>Chunk text: 500 characters with 100 overlap</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-bold text-primary">4.</span>
                      <span>Generate embeddings using multilingual-e5-large</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-bold text-primary">5.</span>
                      <span>Create FAISS IndexFlatIP and save to files</span>
                    </li>
                  </ol>
                </div>

                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-3">Technical Specifications</h4>
                  <ul className="text-sm text-muted-foreground space-y-2">
                    <li className="flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span><strong>Model:</strong> intfloat/multilingual-e5-large</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span><strong>Batch Size:</strong> 64 documents per batch</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span><strong>Normalization:</strong> L2 normalized embeddings</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span><strong>Output:</strong> vector_index.faiss, embeddings.npy, metadata.parquet</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span><strong>Device:</strong> Kaggle GPU (CUDA acceleration)</span>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <p className="text-sm text-foreground">
                  <strong>Note:</strong> After initial training on Kaggle, the vector database is deployed to AWS S3 
                  and maintained by the daily Airflow RAG pipeline with incremental updates using Vietnamese-SBERT for consistency.
                </p>
              </div>
            </div>
          </div>
        </>
      )}

      {/* AIRFLOW SECTION */}
      {activeSection === "airflow" && (
        <>
          {/* Airflow Overview */}
          <div className="card-lumina">
            <div className="flex items-start gap-4">
              <GitBranch className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-foreground mb-3">
                  {t('about.airflowEtlPipeline')}
                </h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                  {t('about.airflowDescription')}
                </p>
              </div>
            </div>
          </div>

          {/* Pipeline Stages */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.etlPipelineStages')}</h3>
            <div className="space-y-4">
              {[
                {
                  step: 1,
                  title: t('about.bronzeLayerStage'),
                  desc: t('about.bronzeLayerStageDesc'),
                  tasks: ["Fetch 30 stock symbols", "Crawl 12K+ news articles", "Collect 50+ macro indicators"],
                  duration: "1.5 hours"
                },
                {
                  step: 2,
                  title: t('about.silverLayerStage'),
                  desc: t('about.silverLayerStageDesc'),
                  tasks: ["Remove duplicates & nulls", "Validate schemas", "Parquet conversion with Snappy"],
                  duration: "1.5 hours"
                },
                {
                  step: 3,
                  title: t('about.goldLayerStage'),
                  desc: t('about.goldLayerStageDesc'),
                  tasks: ["Calculate technical indicators", "Aggregate sentiment scores", "Compute market metrics"],
                  duration: "1.5 hours"
                },
                {
                  step: 4,
                  title: t('about.ragPipelineStage'),
                  desc: t('about.ragPipelineStageDesc'),
                  tasks: ["Extract news from Silver layer", "Generate Vietnamese SBERT embeddings", "Update FAISS index with deduplication"],
                  duration: "30 minutes"
                },
                {
                  step: 5,
                  title: t('about.qualityCheckStage'),
                  desc: t('about.qualityCheckStageDesc'),
                  tasks: ["Validate row counts", "Check schema consistency", "Compare with baseline"],
                  duration: "15 minutes"
                },
                {
                  step: 6,
                  title: t('about.glueCatalogStage'),
                  desc: t('about.glueCatalogStageDesc'),
                  tasks: ["Update partition metadata", "Refresh statistics", "Enable Athena queries"],
                  duration: "15 minutes"
                },
                {
                  step: 7,
                  title: t('about.notificationStage'),
                  desc: t('about.notificationStageDesc'),
                  tasks: ["Send summary email", "Slack notification", "Log to CloudWatch"],
                  duration: "15 minutes"
                }
              ].map((stage) => (
                <div key={stage.step} className="p-4 bg-secondary/20 rounded-lg">
                  <div className="flex items-start gap-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary text-primary-foreground font-bold flex-shrink-0">
                      {stage.step}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-foreground">{stage.title}</h4>
                        <span className="text-xs text-primary font-medium px-2 py-1 bg-primary/10 rounded">
                          {stage.duration}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">{stage.desc}</p>
                      <ul className="text-xs text-muted-foreground space-y-1">
                        {stage.tasks.map((task, idx) => (
                          <li key={idx} className="flex items-center gap-2">
                            <span className="text-primary">→</span>
                            {task}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 p-3 bg-primary/10 rounded-lg text-center">
              <span className="text-sm font-semibold text-foreground">{t('about.totalPipelineDuration')} </span>
              <span className="text-lg font-bold text-primary">~7 hours</span>
              <span className="text-sm text-muted-foreground ml-2">{t('about.dailyAt')}</span>
            </div>
          </div>

          {/* Technology Stack */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.pipelineTechnologyStack')}</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-3">{t('about.orchestration')}</h4>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span><strong>Apache Airflow 2.7.0:</strong> Workflow orchestration and scheduling</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span><strong>DAGs:</strong> Directed Acyclic Graphs for pipeline definition</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span><strong>Web UI:</strong> Real-time monitoring and logs</span>
                  </li>
                </ul>
              </div>

              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-3">{t('about.processing')}</h4>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span><strong>Apache Spark 3.3.0:</strong> Distributed data processing</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span><strong>PySpark:</strong> Python API for Spark jobs with 5 workers</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span><strong>Pandas:</strong> Data manipulation and analysis</span>
                  </li>
                </ul>
              </div>

              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-3">{t('about.ragPipeline')}</h4>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span><strong>Vietnamese SBERT:</strong> keepitreal/vietnamese-sbert</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span><strong>FAISS:</strong> IndexFlatIP for vector similarity</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span><strong>Text Chunking:</strong> 500 chars with 100 overlap</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* PySpark Details */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.pysparkDistributed')}</h3>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                {t('about.pysparkDesc')}
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-secondary/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-3">{t('about.clusterConfiguration')}</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• 5 worker nodes (parallel processing)</li>
                    <li>• 4 cores per node (20 cores total)</li>
                    <li>• 50 GB total memory allocation</li>
                    <li>• Standalone cluster mode</li>
                    <li>• Local SSD for shuffle operations</li>
                  </ul>
                </div>

                <div className="p-4 bg-secondary/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-3">{t('about.keyOperations')}</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Data cleaning & deduplication</li>
                    <li>• Schema validation & standardization</li>
                    <li>• Window functions for time series</li>
                    <li>• Aggregations & feature engineering</li>
                    <li>• Parquet conversion with Snappy compression</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Pipeline Features */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.pipelineFeatures')}</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="text-2xl mb-2">🤖</div>
                <h4 className="font-semibold text-foreground mb-2">{t('about.fullyAutomated')}</h4>
                <p className="text-sm text-muted-foreground">
                  {t('about.fullyAutomatedDesc')}
                </p>
              </div>
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="text-2xl mb-2">📊</div>
                <h4 className="font-semibold text-foreground mb-2">{t('about.parallelProcessing')}</h4>
                <p className="text-sm text-muted-foreground">
                  {t('about.parallelProcessingDesc')}
                </p>
              </div>
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <div className="text-2xl mb-2">🔍</div>
                <h4 className="font-semibold text-foreground mb-2">{t('about.qualityMonitoring')}</h4>
                <p className="text-sm text-muted-foreground">
                  {t('about.qualityMonitoringDesc')}
                </p>
              </div>
            </div>
          </div>

          {/* Pipeline Stats */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.pipelineStatistics')}</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">365</div>
                <div className="text-xs text-muted-foreground">{t('about.dailyRunsYear')}</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">90%</div>
                <div className="text-xs text-muted-foreground">{t('about.successRate')}</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">7h</div>
                <div className="text-xs text-muted-foreground">{t('about.averageDuration')}</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">3</div>
                <div className="text-xs text-muted-foreground">{t('about.dataLayersProcessed')}</div>
              </div>
            </div>
          </div>

          {/* Infrastructure */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.infrastructure')}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-3">{t('about.airflowDeployment')}</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Docker Compose (development)</li>
                  <li>• Docker Compose (production)</li>
                  <li>• PostgreSQL metadata database</li>
                  <li>• Redis for task queuing</li>
                  <li>• CloudWatch for logging</li>
                </ul>
              </div>

              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-3">{t('about.sparkCluster')}</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Standalone cluster mode</li>
                  <li>• 5 worker nodes</li>
                  <li>• 4 cores per node</li>
                  <li>• 50 GB total memory</li>
                  <li>• S3 for input/output</li>
                </ul>
              </div>
            </div>
          </div>
        </>
      )}

      {/* ARCHITECTURE SECTION: BE-FE & MCP */}
      {activeSection === "architecture" && (
        <>
          {/* Overview */}
          <div className="card-lumina">
            <div className="flex items-start gap-4">
              <Code className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-foreground mb-3">
                  {t('about.backendFrontendMcp')}
                </h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                  {t('about.systemArchitectureDesc')}
                </p>
              </div>
            </div>
          </div>

          {/* System Architecture Diagram */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.systemArchitecture')}</h3>
            <div className="bg-secondary/10 p-6 rounded-lg">
              <div className="space-y-6">
                {/* Frontend Layer */}
                <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border-2 border-indigo-300 dark:border-indigo-700">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-2xl">🖥️</span>
                    <h4 className="font-bold text-foreground">{t('about.frontendLayer')}</h4>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{t('about.frontendLayerDesc')}</p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                    <div className="text-xs bg-white dark:bg-slate-900 p-2 rounded">📱 Chat Interface</div>
                    <div className="text-xs bg-white dark:bg-slate-900 p-2 rounded">🔑 API Key Manager</div>
                    <div className="text-xs bg-white dark:bg-slate-900 p-2 rounded">📊 Dashboard</div>
                  </div>
                </div>

                {/* Arrow down */}
                <div className="text-center text-primary">↓ HTTPS REST API ↓</div>

                {/* Backend Layer */}
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border-2 border-purple-300 dark:border-purple-700">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-2xl">⚙️</span>
                    <h4 className="font-bold text-foreground">{t('about.backendLayer')}</h4>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{t('about.backendLayerDesc')}</p>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-2">
                    <div className="text-xs bg-white dark:bg-slate-900 p-2 rounded">🔍 RAG Service</div>
                    <div className="text-xs bg-white dark:bg-slate-900 p-2 rounded">🤖 LLM (Gemini)</div>
                    <div className="text-xs bg-white dark:bg-slate-900 p-2 rounded">📦 Vector DB (FAISS)</div>
                    <div className="text-xs bg-white dark:bg-slate-900 p-2 rounded">💾 Supabase</div>
                  </div>
                </div>

                {/* Arrow down */}
                <div className="text-center text-primary">↓ Data & Model Access ↓</div>

                {/* Data Layer */}
                <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border-2 border-green-300 dark:border-green-700">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-2xl">💾</span>
                    <h4 className="font-bold text-foreground">{t('about.dataLayer')}</h4>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{t('about.dataLayerDesc')}</p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                    <div className="text-xs bg-white dark:bg-slate-900 p-2 rounded">📈 FAISS Index (328K vectors)</div>
                    <div className="text-xs bg-white dark:bg-slate-900 p-2 rounded">🧠 Embeddings (768-dim)</div>
                    <div className="text-xs bg-white dark:bg-slate-900 p-2 rounded">📋 Metadata (Parquet)</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Backend Details */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">{t('about.backendFastapi')}</h3>
            <div className="space-y-4">
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-3">{t('about.coreComponents')}</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h5 className="font-medium text-foreground mb-2">{t('about.ragService')}</h5>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Query embedding (Vietnamese-SBERT)</li>
                      <li>• FAISS vector search</li>
                      <li>• Cross-encoder reranking</li>
                      <li>• Context building with full text</li>
                      <li>• Gemini LLM integration</li>
                    </ul>
                  </div>
                  <div>
                    <h5 className="font-medium text-foreground mb-2">{t('about.apiEndpoints')}</h5>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• POST /api/v1/rag/validate-key</li>
                      <li>• POST /api/v1/rag/query</li>
                      <li>• GET /api/v1/rag/history</li>
                      <li>• DELETE /api/v1/rag/history</li>
                      <li>• GET /health</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <h5 className="font-medium text-foreground mb-3">Key Features</h5>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="flex items-start gap-2">
                    <span className="text-primary mt-1">✓</span>
                    <div>
                      <div className="font-medium text-foreground text-sm">Async Processing</div>
                      <div className="text-xs text-muted-foreground">Non-blocking request handling with Python async/await</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-primary mt-1">✓</span>
                    <div>
                      <div className="font-medium text-foreground text-sm">Error Handling</div>
                      <div className="text-xs text-muted-foreground">Graceful fallback for API failures</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-primary mt-1">✓</span>
                    <div>
                      <div className="font-medium text-foreground text-sm">Logging</div>
                      <div className="text-xs text-muted-foreground">Structured JSON logs for debugging</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-primary mt-1">✓</span>
                    <div>
                      <div className="font-medium text-foreground text-sm">Caching</div>
                      <div className="text-xs text-muted-foreground">Supabase + Redis for response caching</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-primary mt-1">✓</span>
                    <div>
                      <div className="font-medium text-foreground text-sm">Rate Limiting</div>
                      <div className="text-xs text-muted-foreground">Token-based API key management</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-primary mt-1">✓</span>
                    <div>
                      <div className="font-medium text-foreground text-sm">CORS Enabled</div>
                      <div className="text-xs text-muted-foreground">Cross-origin requests from frontend</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Frontend Details */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">Frontend (React + TypeScript)</h3>
            <div className="space-y-4">
              <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-3">Metallica AI Personality</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                  <div>
                    <h5 className="font-medium text-foreground mb-2">Visual Identity</h5>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>🎨 Metallica Avatar (3 locations)</li>
                      <li>⚡ Lumina color scheme (primary/secondary)</li>
                      <li>🎭 Glassmorphism UI design</li>
                      <li>✨ Smooth animations & transitions</li>
                    </ul>
                  </div>
                  <div>
                    <h5 className="font-medium text-foreground mb-2">Personality</h5>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>🎯 AEGIS Lumina messenger</li>
                      <li>💬 Structured response format</li>
                      <li>📚 Source citations with links</li>
                      <li>🌐 Vietnamese-first language</li>
                    </ul>
                  </div>
                </div>
                <div className="p-3 bg-indigo-100 dark:bg-indigo-900/30 rounded text-sm text-foreground">
                  <strong>Response Format:</strong> Markdown-formatted answers with source citations, relevance scores, 
                  and keyword highlighting for financial analysis.
                </div>
              </div>

              <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                <h5 className="font-medium text-foreground mb-3">Key Pages & Features</h5>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="text-sm">
                    <div className="font-medium text-foreground mb-1">💬 Chat Page</div>
                    <div className="text-muted-foreground text-xs">RAG chatbot interface with Metallica avatar, message history, source citations</div>
                  </div>
                  <div className="text-sm">
                    <div className="font-medium text-foreground mb-1">📊 Dashboard</div>
                    <div className="text-muted-foreground text-xs">Real-time stock data visualization, technical indicators, market overview</div>
                  </div>
                  <div className="text-sm">
                    <div className="font-medium text-foreground mb-1">🔍 Asset Finder</div>
                    <div className="text-muted-foreground text-xs">Advanced screening with filters for stock selection</div>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                <h5 className="font-medium text-foreground mb-3">Technology Stack</h5>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs">
                  <div className="bg-white dark:bg-slate-900 p-2 rounded">React 18.2.0</div>
                  <div className="bg-white dark:bg-slate-900 p-2 rounded">TypeScript 5.2</div>
                  <div className="bg-white dark:bg-slate-900 p-2 rounded">Vite 4.4.0</div>
                  <div className="bg-white dark:bg-slate-900 p-2 rounded">TailwindCSS 3.3</div>
                  <div className="bg-white dark:bg-slate-900 p-2 rounded">React Query</div>
                  <div className="bg-white dark:bg-slate-900 p-2 rounded">React Router</div>
                </div>
              </div>
            </div>
          </div>

          {/* MCP Server */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">MCP Server (Model Context Protocol)</h3>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Optional Model Context Protocol server for LLM tool integration and advanced AI capabilities.
              </p>

              <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-3">Available Tools</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="flex items-start gap-2">
                    <span className="text-primary font-bold">1</span>
                    <div>
                      <div className="font-medium text-foreground text-sm">Stock Analyzer Tool</div>
                      <div className="text-xs text-muted-foreground">Query stock data, technical indicators, price history</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-primary font-bold">2</span>
                    <div>
                      <div className="font-medium text-foreground text-sm">News Fetcher Tool</div>
                      <div className="text-xs text-muted-foreground">Retrieve latest news, sentiment analysis, trending topics</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-primary font-bold">3</span>
                    <div>
                      <div className="font-medium text-foreground text-sm">Market Intelligence Tool</div>
                      <div className="text-xs text-muted-foreground">Macro indicators, economic events, market sentiment</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-primary font-bold">4</span>
                    <div>
                      <div className="font-medium text-foreground text-sm">Portfolio Analyzer Tool</div>
                      <div className="text-xs text-muted-foreground">Portfolio optimization, risk assessment, rebalancing</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-3">Integration Benefits</h4>
                <div className="space-y-2">
                  <div className="flex items-start gap-2 text-sm">
                    <span className="text-primary">✓</span>
                    <span className="text-muted-foreground"><strong>Extended Capabilities:</strong> Gemini AI can use RAG tools for enhanced financial analysis</span>
                  </div>
                  <div className="flex items-start gap-2 text-sm">
                    <span className="text-primary">✓</span>
                    <span className="text-muted-foreground"><strong>Real-time Data Access:</strong> Live stock prices, market data, news feeds</span>
                  </div>
                  <div className="flex items-start gap-2 text-sm">
                    <span className="text-primary">✓</span>
                    <span className="text-muted-foreground"><strong>Context Awareness:</strong> Tools provide rich context for LLM decision-making</span>
                  </div>
                  <div className="flex items-start gap-2 text-sm">
                    <span className="text-primary">✓</span>
                    <span className="text-muted-foreground"><strong>Autonomous Workflows:</strong> Multi-step analysis without user intervention</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Data Flow */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">End-to-End Data Flow</h3>
            <div className="space-y-3">
              {[
                {
                  step: 1,
                  user: "User enters query in Chat interface",
                  system: "Frontend validates input & stores in state"
                },
                {
                  step: 2,
                  user: "Frontend sends API request to backend",
                  system: "Backend receives query + API key + history"
                },
                {
                  step: 3,
                  user: "RAG Service embeds query",
                  system: "Vietnamese-SBERT generates 768-dim vector"
                },
                {
                  step: 4,
                  user: "FAISS vector search in S3",
                  system: "Returns top-7 most similar documents (IndexFlatIP)"
                },
                {
                  step: 5,
                  user: "Cross-encoder reranking",
                  system: "Reorders results by relevance score"
                },
                {
                  step: 6,
                  user: "Context building with full text",
                  system: "Loads 2000 chars per doc from CSV cache (~6,988 chars total)"
                },
                {
                  step: 7,
                  user: "Gemini LLM generation",
                  system: "Generates answer with Metallica personality (~800ms)"
                },
                {
                  step: 8,
                  user: "Response formatting & source extraction",
                  system: "Markdown + source citations [{source, link}]"
                },
                {
                  step: 9,
                  user: "Frontend receives response",
                  system: "Displays with Metallica avatar, sources, citations"
                }
              ].map((flow) => (
                <div key={flow.step} className="p-3 bg-secondary/20 rounded-lg">
                  <div className="flex items-start gap-3">
                    <div className="flex items-center justify-center w-7 h-7 rounded-full bg-primary text-primary-foreground font-bold flex-shrink-0 text-xs">
                      {flow.step}
                    </div>
                    <div className="flex-1">
                      <div className="text-sm"><span className="font-medium text-foreground">{flow.user}</span></div>
                      <div className="text-xs text-muted-foreground">→ {flow.system}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 p-3 bg-primary/10 rounded-lg text-center">
              <span className="text-sm font-semibold text-foreground">{t('about.totalResponseTime')} </span>
              <span className="text-lg font-bold text-primary">~2-5 seconds (end-to-end)</span>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">Performance Metrics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-3 bg-primary/10 rounded-lg text-center">
                <div className="text-2xl font-bold text-primary mb-1">~50ms</div>
                <div className="text-xs text-muted-foreground">Query Embedding</div>
              </div>
              <div className="p-3 bg-primary/10 rounded-lg text-center">
                <div className="text-2xl font-bold text-primary mb-1">&lt;10ms</div>
                <div className="text-xs text-muted-foreground">FAISS Search</div>
              </div>
              <div className="p-3 bg-primary/10 rounded-lg text-center">
                <div className="text-2xl font-bold text-primary mb-1">~100ms</div>
                <div className="text-xs text-muted-foreground">Reranking</div>
              </div>
              <div className="p-3 bg-primary/10 rounded-lg text-center">
                <div className="text-2xl font-bold text-primary mb-1">~800ms</div>
                <div className="text-xs text-muted-foreground">LLM Generation</div>
              </div>
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg text-center">
                <div className="text-2xl font-bold text-green-600 mb-1">99.8%</div>
                <div className="text-xs text-muted-foreground">Uptime</div>
              </div>
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg text-center">
                <div className="text-2xl font-bold text-green-600 mb-1">328K+</div>
                <div className="text-xs text-muted-foreground">Indexed Vectors</div>
              </div>
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg text-center">
                <div className="text-2xl font-bold text-green-600 mb-1">12K+</div>
                <div className="text-xs text-muted-foreground">News Articles</div>
              </div>
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg text-center">
                <div className="text-2xl font-bold text-green-600 mb-1">7</div>
                <div className="text-xs text-muted-foreground">Retrieved Docs</div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
