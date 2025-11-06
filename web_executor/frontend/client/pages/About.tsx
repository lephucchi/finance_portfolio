import { useState } from "react";
import { Target, TrendingUp, Zap, Users, Code, Database, Cloud, Brain, Layers, MessageSquare, GitBranch, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

type Section = "overview" | "lakehouse" | "rag" | "airflow";

export default function About() {
  const [activeSection, setActiveSection] = useState<Section>("overview");

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
            "The AI Shield That Illuminates Your Data"
          </p>
          <p className="text-base text-muted-foreground mb-4 max-w-3xl mx-auto px-4">
            Named after the divine shield of Zeus and Athena (AEGIS) combined with the light of wisdom (LUMINA) – 
            An AI system that protects and illuminates all your financial data, 
            like the watchful eye of Athena upon her legendary shield.
          </p>
          <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
            <span className="px-3 py-1 bg-primary/20 text-primary rounded-full font-medium">
              Version 1.0
            </span>
            <span>•</span>
            <span>Production Ready</span>
            <span>•</span>
            <span>November 2025</span>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="card-lumina">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
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
            <span className="font-medium">Overview</span>
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
            <span className="font-medium">Lakehouse</span>
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
            <span className="font-medium">RAG Chatbot</span>
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
            <span className="font-medium">Airflow ETL</span>
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
              Mission Statement
            </h2>
            <div className="prose prose-sm max-w-none">
              <p className="text-foreground leading-relaxed mb-4">
                We build a <strong>comprehensive financial data analytics platform</strong> that 
                enables extraction of insights from Vietnam stock market data, news, and economic 
                indicators using <strong>modern Lakehouse architecture</strong> combined with 
                <strong> AI/ML capabilities</strong>.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                <div className="p-4 bg-primary/5 rounded-lg">
                  <div className="text-3xl font-bold text-primary mb-2">87-94%</div>
                  <div className="text-sm text-muted-foreground">Cost savings vs traditional RDS</div>
                </div>
                <div className="p-4 bg-primary/5 rounded-lg">
                  <div className="text-3xl font-bold text-primary mb-2">85-90%</div>
                  <div className="text-sm text-muted-foreground">Faster query speed</div>
                </div>
                <div className="p-4 bg-primary/5 rounded-lg">
                  <div className="text-3xl font-bold text-primary mb-2">99.8%</div>
                  <div className="text-sm text-muted-foreground">System uptime</div>
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
              Project Overview
            </h2>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column */}
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                Key Solutions
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
                Data Processed
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-secondary/30 rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">Stocks</div>
                  <div className="text-lg font-bold text-foreground">10,950+</div>
                </div>
                <div className="p-3 bg-secondary/30 rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">News</div>
                  <div className="text-lg font-bold text-foreground">12,027</div>
                </div>
                <div className="p-3 bg-secondary/30 rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">Indicators</div>
                  <div className="text-lg font-bold text-foreground">18,250</div>
                </div>
                <div className="p-3 bg-secondary/30 rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">Symbols</div>
                  <div className="text-lg font-bold text-foreground">30</div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-2">
                System Performance
              </h3>
              <div className="space-y-3">
                {[
                  { label: "Query Latency (P50)", target: "< 2s", actual: "0.8s", status: "✅" },
                  { label: "Query Latency (P99)", target: "< 5s", actual: "2.1s", status: "✅" },
                  { label: "Data Freshness", target: "< 30min", actual: "5-15min", status: "✅" },
                  { label: "Vector Search", target: "< 50ms", actual: "12ms", status: "✅" },
                  { label: "System Uptime", target: "> 99%", actual: "99.8%", status: "✅" }
                ].map((metric, i) => (
                  <div key={i} className="flex items-center justify-between p-2 bg-secondary/20 rounded">
                    <span className="text-sm text-muted-foreground">{metric.label}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">{metric.target}</span>
                      <span className="text-sm font-semibold text-primary">{metric.actual}</span>
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
              Technology Stack
            </h2>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {/* Cloud Infrastructure */}
          <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg">
            <Cloud className="w-6 h-6 text-blue-600 mb-3" />
            <h3 className="font-semibold text-foreground mb-2">Cloud Infrastructure</h3>
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
            <h3 className="font-semibold text-foreground mb-2">Data Processing</h3>
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
            <h3 className="font-semibold text-foreground mb-2">Backend & API</h3>
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
            <h3 className="font-semibold text-foreground mb-2">AI/ML & NLP</h3>
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
            <h3 className="font-semibold text-foreground mb-2">Frontend Stack</h3>
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
              Future Vision
            </h2>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[
            {
              phase: "Phase 1: Immediate",
              time: "Week 1-2",
              items: [
                "Production monitoring & alerting",
                "User authentication system",
                "Rate limiting enforcement",
                "Performance optimization"
              ]
            },
            {
              phase: "Phase 2: Short-term",
              time: "Month 1-2",
              items: [
                "Query reformulation",
                "Multi-turn conversations",
                "Advanced filters & search",
                "Horizontal scaling"
              ]
            },
            {
              phase: "Phase 3: Medium-term",
              time: "Month 3-6",
              items: [
                "BI Dashboards integration",
                "Predictive models",
                "Real-time analytics",
                "Named entity recognition"
              ]
            },
            {
              phase: "Phase 4: Long-term",
              time: "Month 6-12",
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
              Development Team
            </h2>
            <p className="text-muted-foreground">
              This project is developed by a team of engineers passionate about Data Engineering, 
              Machine Learning, and Financial Analytics.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            {
              role: "Data Engineering",
              desc: "Lakehouse architecture, ETL pipelines, Data quality"
            },
            {
              role: "AI/ML Development",
              desc: "RAG system, Embeddings, NLP processing"
            },
            {
              role: "Full-stack Development",
              desc: "Backend API, Frontend UI, DevOps"
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
            <strong>Open for Collaboration:</strong> We welcome contributions from the community. 
            If you're interested in the project, check out the <strong>Guide</strong> section to 
            learn how to contribute code or ideas!
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
                  Lakehouse Architecture
                </h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                  A modern data architecture that combines the best of Data Lakes and Data Warehouses,
                  providing scalable storage with high-performance analytics capabilities.
                </p>
              </div>
            </div>
          </div>

          {/* Medallion Architecture */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">Medallion Architecture (Bronze-Silver-Gold)</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Bronze Layer */}
              <div className="p-4 bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-900/20 dark:to-amber-800/20 rounded-lg border-2 border-amber-200 dark:border-amber-800">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-3 h-3 rounded-full bg-amber-600"></div>
                  <h4 className="font-bold text-foreground">Bronze Layer</h4>
                </div>
                <p className="text-sm text-muted-foreground mb-3">Raw data ingestion from sources</p>
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
                  <h4 className="font-bold text-foreground">Silver Layer</h4>
                </div>
                <p className="text-sm text-muted-foreground mb-3">Cleaned & standardized data</p>
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
                  <h4 className="font-bold text-foreground">Gold Layer</h4>
                </div>
                <p className="text-sm text-muted-foreground mb-3">Business-ready aggregates</p>
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
            <h3 className="text-xl font-bold text-foreground mb-4">Data Sources</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-2">📈 Stock Data</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Source: VNStock API v3</li>
                  <li>• Symbols: 30 major stocks</li>
                  <li>• Records: 10,950+</li>
                  <li>• Period: 365 days</li>
                  <li>• Update: Real-time (2-5 min delay)</li>
                </ul>
              </div>

              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-2">📰 News Data</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Source: Google Custom Search</li>
                  <li>• Articles: 12,027</li>
                  <li>• Language: Vietnamese</li>
                  <li>• Coverage: 1-3 years</li>
                  <li>• Topics: Finance, Banking, Markets</li>
                </ul>
              </div>

              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-2">📊 Macro Data</h4>
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

          {/* Performance Metrics */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">Performance & Cost Efficiency</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">87-94%</div>
                <div className="text-xs text-muted-foreground">Cost Savings vs RDS</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">0.5-1s</div>
                <div className="text-xs text-muted-foreground">Query Latency (P50)</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">92%</div>
                <div className="text-xs text-muted-foreground">Data Compression</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">$6.32</div>
                <div className="text-xs text-muted-foreground">Monthly Query Cost</div>
              </div>
            </div>
          </div>

          {/* AWS Stack */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">AWS Infrastructure</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <Cloud className="w-6 h-6 text-blue-600 mb-2" />
                <h4 className="font-semibold text-foreground mb-2">Amazon S3</h4>
                <p className="text-sm text-muted-foreground">Data Lake storage with 3 layers (Bronze, Silver, Gold)</p>
              </div>
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <Database className="w-6 h-6 text-green-600 mb-2" />
                <h4 className="font-semibold text-foreground mb-2">AWS Glue</h4>
                <p className="text-sm text-muted-foreground">Data Catalog with 9 tables across 2 databases</p>
              </div>
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <Zap className="w-6 h-6 text-purple-600 mb-2" />
                <h4 className="font-semibold text-foreground mb-2">AWS Athena</h4>
                <p className="text-sm text-muted-foreground">Serverless SQL queries on S3 data</p>
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
                  RAG Chatbot System
                </h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                  Retrieval-Augmented Generation (RAG) chatbot that provides accurate, 
                  grounded answers about Vietnamese financial markets using real news data 
                  and advanced AI technology.
                </p>
              </div>
            </div>
          </div>

          {/* RAG Pipeline */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">How RAG Works</h3>
            <div className="space-y-4">
              {[
                {
                  step: 1,
                  title: "Query Embedding",
                  desc: "Convert user question to 768-dim vector using Vietnamese-SBERT",
                  time: "~50ms"
                },
                {
                  step: 2,
                  title: "Vector Search",
                  desc: "Search 10,585 indexed articles using FAISS for top-5 relevant docs",
                  time: "<10ms"
                },
                {
                  step: 3,
                  title: "Reranking",
                  desc: "Cross-encoder reranks results for better relevance",
                  time: "~100ms"
                },
                {
                  step: 4,
                  title: "Context Preparation",
                  desc: "Format top-3 articles as context with sources and metadata",
                  time: "~10ms"
                },
                {
                  step: 5,
                  title: "LLM Generation",
                  desc: "Google Gemini generates natural response based on context",
                  time: "~800ms"
                },
                {
                  step: 6,
                  title: "Response Formatting",
                  desc: "Return answer with sources, scores, and confidence",
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
              <span className="text-sm font-semibold text-foreground">Total Response Time: </span>
              <span className="text-lg font-bold text-primary">~5 second</span>
            </div>
          </div>

          {/* RAG Technology */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">Technology Stack</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-3">Embedding & Search</h4>
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
                <h4 className="font-semibold text-foreground mb-3">Generation & Storage</h4>
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
            <h3 className="text-xl font-bold text-foreground mb-4">Key Features</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="text-2xl mb-2">✅</div>
                <h4 className="font-semibold text-foreground mb-2">No Hallucination</h4>
                <p className="text-sm text-muted-foreground">
                  Answers grounded in real news articles with source citations
                </p>
              </div>
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="text-2xl mb-2">🇻🇳</div>
                <h4 className="font-semibold text-foreground mb-2">Vietnamese Support</h4>
                <p className="text-sm text-muted-foreground">
                  Optimized for Vietnamese language queries and responses
                </p>
              </div>
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <div className="text-2xl mb-2">⚡</div>
                <h4 className="font-semibold text-foreground mb-2">Fast & Accurate</h4>
                <p className="text-sm text-muted-foreground">
                  Sub-second vector search with high relevance scores
                </p>
              </div>
            </div>
          </div>

          {/* RAG Stats */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">System Statistics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">10,585</div>
                <div className="text-xs text-muted-foreground">Indexed Vectors</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">12,027</div>
                <div className="text-xs text-muted-foreground">News Articles</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">&lt;10ms</div>
                <div className="text-xs text-muted-foreground">Vector Search Time</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">768</div>
                <div className="text-xs text-muted-foreground">Embedding Dimensions</div>
              </div>
            </div>
          </div>

          {/* Initial Training (Kaggle) */}
          <div className="card-lumina border-l-4 border-blue-500">
            <h3 className="text-xl font-bold text-foreground mb-4">Initial RAG Training (Kaggle)</h3>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                The initial vector database was created using Kaggle notebooks with GPU acceleration for faster embedding generation.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-3">Training Process</h4>
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
                  Apache Airflow ETL Pipeline
                </h2>
                <p className="text-muted-foreground leading-relaxed mb-4">
                  Fully automated ETL pipeline orchestrated by Apache Airflow, processing data 
                  from multiple sources through Bronze-Silver-Gold layers using PySpark for 
                  distributed computing.
                </p>
              </div>
            </div>
          </div>

          {/* Pipeline Stages */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">ETL Pipeline Stages</h3>
            <div className="space-y-4">
              {[
                {
                  step: 1,
                  title: "Bronze Layer (08:00-09:30 UTC)",
                  desc: "Data collection from APIs",
                  tasks: ["Fetch 30 stock symbols", "Crawl 12K+ news articles", "Collect 50+ macro indicators"],
                  duration: "1.5 hours"
                },
                {
                  step: 2,
                  title: "Silver Layer (10:00-11:30 UTC)",
                  desc: "Data cleaning & standardization",
                  tasks: ["Remove duplicates & nulls", "Validate schemas", "Parquet conversion with Snappy"],
                  duration: "1.5 hours"
                },
                {
                  step: 3,
                  title: "Gold Layer (13:00-14:30 UTC)",
                  desc: "Feature engineering & aggregation",
                  tasks: ["Calculate technical indicators", "Aggregate sentiment scores", "Compute market metrics"],
                  duration: "1.5 hours"
                },
                {
                  step: 4,
                  title: "RAG Pipeline (14:30-15:00 UTC)",
                  desc: "Vector database update for chatbot",
                  tasks: ["Extract news from Silver layer", "Generate Vietnamese SBERT embeddings", "Update FAISS index with deduplication"],
                  duration: "30 minutes"
                },
                {
                  step: 5,
                  title: "Quality Check (15:00-15:15 UTC)",
                  desc: "Data validation & monitoring",
                  tasks: ["Validate row counts", "Check schema consistency", "Compare with baseline"],
                  duration: "15 minutes"
                },
                {
                  step: 6,
                  title: "Glue Catalog Update (15:30-15:45 UTC)",
                  desc: "Metadata synchronization",
                  tasks: ["Update partition metadata", "Refresh statistics", "Enable Athena queries"],
                  duration: "15 minutes"
                },
                {
                  step: 7,
                  title: "Notification (15:45-16:00 UTC)",
                  desc: "Status reporting",
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
              <span className="text-sm font-semibold text-foreground">Total Pipeline Duration: </span>
              <span className="text-lg font-bold text-primary">~7 hours</span>
              <span className="text-sm text-muted-foreground ml-2">(Daily at 09:00 UTC)</span>
            </div>
          </div>

          {/* Technology Stack */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">Technology Stack</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-3">Orchestration</h4>
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
                <h4 className="font-semibold text-foreground mb-3">Processing</h4>
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
                <h4 className="font-semibold text-foreground mb-3">RAG Pipeline</h4>
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
            <h3 className="text-xl font-bold text-foreground mb-4">PySpark Distributed Processing</h3>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                PySpark enables distributed data processing across multiple nodes, handling large-scale data transformations 
                efficiently with parallel computing.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-secondary/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-3">Cluster Configuration</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• 5 worker nodes (parallel processing)</li>
                    <li>• 4 cores per node (20 cores total)</li>
                    <li>• 50 GB total memory allocation</li>
                    <li>• Standalone cluster mode</li>
                    <li>• Local SSD for shuffle operations</li>
                  </ul>
                </div>

                <div className="p-4 bg-secondary/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-3">Key Operations</h4>
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
            <h3 className="text-xl font-bold text-foreground mb-4">Key Features</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="text-2xl mb-2">🤖</div>
                <h4 className="font-semibold text-foreground mb-2">Fully Automated</h4>
                <p className="text-sm text-muted-foreground">
                  Runs daily without manual intervention, with automatic retry on failure
                </p>
              </div>
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="text-2xl mb-2">📊</div>
                <h4 className="font-semibold text-foreground mb-2">Parallel Processing</h4>
                <p className="text-sm text-muted-foreground">
                  PySpark distributes workload across multiple nodes for faster processing
                </p>
              </div>
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <div className="text-2xl mb-2">🔍</div>
                <h4 className="font-semibold text-foreground mb-2">Quality Monitoring</h4>
                <p className="text-sm text-muted-foreground">
                  Built-in data quality checks and alerts for anomaly detection
                </p>
              </div>
            </div>
          </div>

          {/* Pipeline Stats */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">Pipeline Statistics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">365</div>
                <div className="text-xs text-muted-foreground">Daily Runs/Year</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">90%</div>
                <div className="text-xs text-muted-foreground">Success Rate</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">7h</div>
                <div className="text-xs text-muted-foreground">Average Duration</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary mb-1">3</div>
                <div className="text-xs text-muted-foreground">Data Layers Processed</div>
              </div>
            </div>
          </div>

          {/* Infrastructure */}
          <div className="card-lumina">
            <h3 className="text-xl font-bold text-foreground mb-4">Infrastructure</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-3">Airflow Deployment</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Docker Compose (development)</li>
                  <li>• Docker Compose (production)</li>
                  <li>• PostgreSQL metadata database</li>
                  <li>• Redis for task queuing</li>
                  <li>• CloudWatch for logging</li>
                </ul>
              </div>

              <div className="p-4 bg-secondary/20 rounded-lg">
                <h4 className="font-semibold text-foreground mb-3">Spark Cluster</h4>
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
    </div>
  );
}
