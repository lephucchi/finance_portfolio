import { useNavigate } from "react-router-dom";
import { 
  Shield, 
  Lightbulb, 
  Database, 
  Brain, 
  MessageSquare, 
  BarChart3, 
  Search, 
  Zap,
  ChevronRight,
  CheckCircle2,
  TrendingUp,
  Cloud,
  Activity
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="card-lumina bg-gradient-to-br from-primary/20 via-primary/10 to-secondary/20 border-2 border-primary/20">
        <div className="text-center py-12 px-6">
          <div className="flex justify-center mb-6">
            <img 
              src="/AEGIS_LUMINA.png" 
              alt="AEGIS LUMINA Logo" 
              className="w-32 h-32 md:w-40 md:h-40 object-contain animate-soft-glow"
            />
          </div>
          
          <h1 className="text-4xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            AEGIS LUMINA
          </h1>
          
          <p className="text-xl md:text-2xl text-primary font-semibold mb-4 italic">
            "The AI Shield That Illuminates Your Data"
          </p>
          
          <p className="text-base md:text-lg text-muted-foreground max-w-3xl mx-auto mb-8 leading-relaxed">
            Named after the divine shield of Zeus and Athena combined with the light of wisdom. 
            An enterprise-grade AI system that <strong className="text-foreground">protects</strong> and <strong className="text-foreground">illuminates</strong> all 
            your financial data with cutting-edge Lakehouse architecture and intelligent RAG chatbot.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={() => navigate("/chat")}
              className="px-8 py-4 bg-primary text-primary-foreground rounded-lg font-semibold text-lg hover:bg-primary/90 transition-all duration-300 shadow-lg hover:shadow-xl flex items-center gap-2"
            >
              <MessageSquare className="w-5 h-5" />
              Start with Metallica AI
            </button>
            <button
              onClick={() => navigate("/dashboard")}
              className="px-8 py-4 bg-secondary text-secondary-foreground rounded-lg font-semibold text-lg hover:bg-secondary/90 transition-all duration-300 shadow-md flex items-center gap-2"
            >
              <BarChart3 className="w-5 h-5" />
              View Dashboard
            </button>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-6 mt-8 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <span>Production Ready</span>
            </div>
            <span>•</span>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <span>Version 1.0</span>
            </div>
            <span>•</span>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <span>November 2025</span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          {
            icon: Shield,
            title: "AEGIS Protection",
            description: "Divine shield protecting your data with AWS Lakehouse architecture - Bronze, Silver, Gold layers ensuring data quality.",
            color: "text-blue-500",
            bgColor: "bg-blue-500/10",
            stats: "10,950 stocks • 12,027 news • 18,250 indicators"
          },
          {
            icon: Lightbulb,
            title: "LUMINA Intelligence",
            description: "AI-powered insights that illuminate patterns in Vietnamese financial markets using advanced RAG chatbot technology.",
            color: "text-yellow-500",
            bgColor: "bg-yellow-500/10",
            stats: "10,585 vectors • <10ms search • 768 dimensions"
          },
          {
            icon: Database,
            title: "Lakehouse Architecture",
            description: "Modern data platform combining data lake flexibility with data warehouse performance on AWS S3.",
            color: "text-purple-500",
            bgColor: "bg-purple-500/10",
            stats: "92% compression • $6.32/month • 0.5-1s queries"
          },
          {
            icon: Brain,
            title: "Vietnamese SBERT",
            description: "Specialized embeddings for Vietnamese language using keepitreal/vietnamese-sbert model with FAISS vector database.",
            color: "text-pink-500",
            bgColor: "bg-pink-500/10",
            stats: "768-dim embeddings • Batch processing • Real-time"
          },
          {
            icon: Zap,
            title: "Airflow ETL Pipeline",
            description: "Automated daily data pipeline with PySpark processing through 7 stages - from ingestion to validation.",
            color: "text-orange-500",
            bgColor: "bg-orange-500/10",
            stats: "7 stages • 99.8% uptime • ~7h daily cycle"
          },
          {
            icon: Cloud,
            title: "AWS Cloud Infrastructure",
            description: "Scalable cloud platform with S3 storage, Glue Catalog, and Athena queries for high performance analytics.",
            color: "text-cyan-500",
            bgColor: "bg-cyan-500/10",
            stats: "S3 • Glue • Athena • Cost-optimized"
          }
        ].map((feature, idx) => {
          const Icon = feature.icon;
          return (
            <div
              key={idx}
              className="card-lumina hover:shadow-xl transition-all duration-300 group cursor-pointer"
            >
              <div className={cn("w-12 h-12 rounded-lg flex items-center justify-center mb-4", feature.bgColor)}>
                <Icon className={cn("w-6 h-6", feature.color)} />
              </div>
              <h3 className="text-lg font-bold text-foreground mb-2 group-hover:text-primary transition-colors">
                {feature.title}
              </h3>
              <p className="text-sm text-muted-foreground mb-3 leading-relaxed">
                {feature.description}
              </p>
              <div className="text-xs text-primary font-medium bg-primary/10 px-3 py-1.5 rounded-full inline-block">
                {feature.stats}
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Access Navigation */}
      <div className="card-lumina">
        <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
          <Activity className="w-6 h-6 text-primary" />
          Quick Access
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            {
              path: "/chat",
              icon: MessageSquare,
              title: "Metallica AI Chatbot",
              description: "Ask questions about Vietnamese financial markets in natural language",
              badge: "AI-Powered"
            },
            {
              path: "/dashboard",
              icon: BarChart3,
              title: "Analytics Dashboard",
              description: "Real-time visualization of stocks, news sentiment, and market trends",
              badge: "Real-time"
            },
            {
              path: "/screener",
              icon: Search,
              title: "Asset Finder",
              description: "Search and filter 10,950+ Vietnamese stocks with advanced criteria",
              badge: "10,950 stocks"
            },
            {
              path: "/about",
              icon: Shield,
              title: "About AEGIS LUMINA",
              description: "Learn about our Lakehouse, RAG system, and Airflow pipeline architecture",
              badge: "Documentation"
            }
          ].map((item, idx) => {
            const Icon = item.icon;
            return (
              <button
                key={idx}
                onClick={() => navigate(item.path)}
                className="p-6 rounded-lg border border-border/30 bg-secondary/20 hover:bg-secondary/40 hover:border-primary/50 transition-all duration-300 text-left group"
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 group-hover:bg-primary/20 transition-colors">
                    <Icon className="w-6 h-6 text-primary" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                        {item.title}
                      </h3>
                      <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {item.description}
                    </p>
                    <span className="text-xs bg-primary/20 text-primary px-2 py-1 rounded-full font-medium">
                      {item.badge}
                    </span>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Call to Action */}
      <div className="card-lumina bg-gradient-to-r from-primary/10 to-primary/5 border-2 border-primary/20">
        <div className="text-center py-8">
          <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-4">
            Ready to Explore?
          </h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            Start your journey with AEGIS LUMINA. Discover insights, analyze data, and make informed decisions 
            with our AI-powered financial analytics platform.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={() => navigate("/guide")}
              className="px-6 py-3 bg-secondary text-secondary-foreground rounded-lg font-semibold hover:bg-secondary/90 transition-all duration-300 shadow-md flex items-center gap-2"
            >
              View User Guide
              <ChevronRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => navigate("/about")}
              className="px-6 py-3 border-2 border-primary text-primary rounded-lg font-semibold hover:bg-primary/10 transition-all duration-300 flex items-center gap-2"
            >
              Learn More
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
