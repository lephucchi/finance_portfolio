import { useState } from "react";
import { 
  Book, 
  User, 
  Code, 
  Calendar, 
  RefreshCw, 
  Search, 
  MessageSquare,
  Key,
  Filter,
  Database,
  GitBranch,
  Terminal,
  PlayCircle,
  CheckCircle,
  AlertCircle
} from "lucide-react";
import { cn } from "@/lib/utils";

type TabType = "user" | "developer";

export default function Guide() {
  const [activeTab, setActiveTab] = useState<TabType>("user");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card-lumina">
        <div className="flex items-center gap-3 mb-2">
          <Book className="w-8 h-8 text-primary" />
          <h1 className="text-4xl font-bold text-foreground">User Guide</h1>
        </div>
        <p className="text-muted-foreground">
          Complete instructions for using the platform and contributing to the project
        </p>
      </div>

      {/* Tab Switcher */}
      <div className="card-lumina">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab("user")}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg transition-all",
              activeTab === "user"
                ? "bg-primary text-primary-foreground"
                : "bg-secondary/30 text-muted-foreground hover:bg-secondary/50"
            )}
          >
            <User className="w-4 h-4" />
            For Users
          </button>
          <button
            onClick={() => setActiveTab("developer")}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg transition-all",
              activeTab === "developer"
                ? "bg-primary text-primary-foreground"
                : "bg-secondary/30 text-muted-foreground hover:bg-secondary/50"
            )}
          >
            <Code className="w-4 h-4" />
            For Developers
          </button>
        </div>
      </div>

      {/* User Guide */}
      {activeTab === "user" && (
        <div className="space-y-6">
          {/* Dashboard */}
          <div className="card-lumina">
            <div className="flex items-center gap-3 mb-4">
              <Calendar className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">Dashboard</h2>
            </div>
            
            <div className="space-y-4">
              <p className="text-muted-foreground">
                The Dashboard is your central hub for monitoring Vietnam stock market performance
                and key metrics.
              </p>

              <div className="space-y-3">
                <h3 className="font-semibold text-foreground">Features:</h3>
                
                <div className="p-4 bg-secondary/20 rounded-lg">
                  <div className="flex items-start gap-3">
                    <Calendar className="w-5 h-5 text-primary mt-0.5" />
                    <div>
                      <h4 className="font-medium text-foreground mb-1">Date Picker</h4>
                      <p className="text-sm text-muted-foreground">
                        Select any date to view historical market data. Click the date button in the
                        top section, choose a date from the calendar, and the dashboard will update
                        automatically. No date restrictions - explore data from any available period.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-secondary/20 rounded-lg">
                  <div className="flex items-start gap-3">
                    <RefreshCw className="w-5 h-5 text-primary mt-0.5" />
                    <div>
                      <h4 className="font-medium text-foreground mb-1">Refresh Button</h4>
                      <p className="text-sm text-muted-foreground">
                        Click the refresh icon to manually reload data. The dashboard no longer
                        auto-refreshes to prevent unnecessary API calls. Use this when you need
                        updated information.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-secondary/20 rounded-lg">
                  <div className="flex items-start gap-3">
                    <Filter className="w-5 h-5 text-primary mt-0.5" />
                    <div>
                      <h4 className="font-medium text-foreground mb-1">Time Range Filters</h4>
                      <p className="text-sm text-muted-foreground">
                        Use the 1D, 1W, 1M, 3M, 1Y buttons to quickly jump to common time ranges.
                        These buttons are located on a separate row below the date picker and refresh
                        button for easy access.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Asset Finder */}
          <div className="card-lumina">
            <div className="flex items-center gap-3 mb-4">
              <Search className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">Asset Finder (Screener)</h2>
            </div>
            
            <div className="space-y-4">
              <p className="text-muted-foreground">
                Screen and filter Vietnamese stocks based on various criteria to find investment
                opportunities.
              </p>

              <div className="space-y-3">
                <h3 className="font-semibold text-foreground">How to Use:</h3>
                
                <div className="space-y-2 text-sm text-muted-foreground">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Use the search bar to filter stocks by symbol or name</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Apply filters for price range, volume, market cap, and performance</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Sort results by clicking column headers</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Click refresh to get the latest stock data</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Metallica Chatbot */}
          <div className="card-lumina">
            <div className="flex items-center gap-3 mb-4">
              <MessageSquare className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">Metallica Chatbot</h2>
            </div>  
            
            <div className="space-y-4">
              <p className="text-muted-foreground">
                Ask questions about Vietnamese financial news and get AI-powered insights using
                our RAG (Retrieval-Augmented Generation) system.
              </p>

              <div className="space-y-3">
                <h3 className="font-semibold text-foreground">Setup:</h3>
                
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-500 rounded-lg">
                  <div className="flex items-start gap-3">
                    <Key className="w-5 h-5 text-yellow-600 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-foreground mb-2">Required: Gemini API Key</h4>
                      <ol className="text-sm text-muted-foreground space-y-2 list-decimal list-inside">
                        <li>Visit <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Google AI Studio</a></li>
                        <li>Create a free Gemini API key</li>
                        <li>Enter the key in the chatbot interface</li>
                        <li>Click "Validate" to activate the chatbot</li>
                      </ol>
                    </div>
                  </div>
                </div>

                <h3 className="font-semibold text-foreground mt-4">Tips for Best Results:</h3>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Ask specific questions about Vietnamese stocks, sectors, or companies</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Questions can be in English or Vietnamese</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>The system searches 12,000+ indexed news articles for context</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Response time is typically under 2 seconds</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Demo Features */}
          <div className="card-lumina border-l-4 border-yellow-500">
            <div className="flex items-center gap-3 mb-4">
              <AlertCircle className="w-6 h-6 text-yellow-600" />
              <h2 className="text-2xl font-bold text-foreground">Demo Features</h2>
            </div>
            
            <div className="space-y-4">
              <p className="text-muted-foreground">
                The following features are currently in demo mode with mock data:
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-2">Market Insights</h4>
                  <p className="text-sm text-muted-foreground">
                    Shows sample sentiment analysis data for demonstration purposes.
                  </p>
                </div>

                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-2">Forecasts</h4>
                  <p className="text-sm text-muted-foreground">
                    Displays mock Vietnam sector performance data (Banking, Real Estate, etc.).
                  </p>
                </div>

                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-2">Reports</h4>
                  <p className="text-sm text-muted-foreground">
                    Shows sample reports with disabled generation features.
                  </p>
                </div>
              </div>

              <p className="text-sm text-muted-foreground italic">
                These features are marked with a 🚧 DEMO badge and include development warnings.
                They will be activated with real data in future releases.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Developer Guide */}
      {activeTab === "developer" && (
        <div className="space-y-6">
          {/* Project Setup */}
          <div className="card-lumina">
            <div className="flex items-center gap-3 mb-4">
              <Terminal className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">Project Setup</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-foreground mb-3">Prerequisites</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="p-3 bg-secondary/20 rounded-lg text-sm">
                    <div className="font-medium text-foreground">Frontend</div>
                    <div className="text-muted-foreground">Node.js 18+, npm/yarn</div>
                  </div>
                  <div className="p-3 bg-secondary/20 rounded-lg text-sm">
                    <div className="font-medium text-foreground">Backend</div>
                    <div className="text-muted-foreground">Python 3.9+, pip</div>
                  </div>
                  <div className="p-3 bg-secondary/20 rounded-lg text-sm">
                    <div className="font-medium text-foreground">AWS Account</div>
                    <div className="text-muted-foreground">S3, Glue, Athena access</div>
                  </div>
                  <div className="p-3 bg-secondary/20 rounded-lg text-sm">
                    <div className="font-medium text-foreground">Gemini API Key</div>
                    <div className="text-muted-foreground">For chatbot functionality</div>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-foreground mb-3">Installation Steps</h3>
                <div className="space-y-3">
                  <div className="p-4 bg-secondary/10 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm font-bold">1</span>
                      <span className="font-medium text-foreground">Clone Repository</span>
                    </div>
                    <code className="block p-2 bg-secondary/30 rounded text-sm text-muted-foreground font-mono">
                      git clone &lt;repository-url&gt;<br/>
                      cd finance_portfolio
                    </code>
                  </div>

                  <div className="p-4 bg-secondary/10 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm font-bold">2</span>
                      <span className="font-medium text-foreground">Frontend Setup</span>
                    </div>
                    <code className="block p-2 bg-secondary/30 rounded text-sm text-muted-foreground font-mono">
                      cd web_executor/frontend<br/>
                      npm install<br/>
                      npm run dev
                    </code>
                  </div>

                  <div className="p-4 bg-secondary/10 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm font-bold">3</span>
                      <span className="font-medium text-foreground">Backend Setup</span>
                    </div>
                    <code className="block p-2 bg-secondary/30 rounded text-sm text-muted-foreground font-mono">
                      cd web_executor/backend<br/>
                      pip install -r requirements.txt<br/>
                      uvicorn main:app --reload
                    </code>
                  </div>

                  <div className="p-4 bg-secondary/10 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm font-bold">4</span>
                      <span className="font-medium text-foreground">Configure AWS</span>
                    </div>
                    <code className="block p-2 bg-secondary/30 rounded text-sm text-muted-foreground font-mono">
                      # Set environment variables<br/>
                      AWS_ACCESS_KEY_ID=your_key<br/>
                      AWS_SECRET_ACCESS_KEY=your_secret<br/>
                      AWS_REGION=ap-southeast-1
                    </code>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Architecture Overview */}
          <div className="card-lumina">
            <div className="flex items-center gap-3 mb-4">
              <Database className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">Architecture Overview</h2>
            </div>
            
            <div className="space-y-4">
              <p className="text-muted-foreground">
                Understanding the system architecture is crucial for contributing effectively.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-secondary/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-2">Bronze Layer</h4>
                  <p className="text-sm text-muted-foreground mb-2">Raw data ingestion</p>
                  <ul className="text-xs text-muted-foreground space-y-1">
                    <li>• VNStock API data</li>
                    <li>• Google CSE news</li>
                    <li>• Economic indicators</li>
                  </ul>
                </div>

                <div className="p-4 bg-secondary/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-2">Silver Layer</h4>
                  <p className="text-sm text-muted-foreground mb-2">Cleaned & enriched</p>
                  <ul className="text-xs text-muted-foreground space-y-1">
                    <li>• Data validation</li>
                    <li>• Schema normalization</li>
                    <li>• Quality checks</li>
                  </ul>
                </div>

                <div className="p-4 bg-secondary/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-2">Gold Layer</h4>
                  <p className="text-sm text-muted-foreground mb-2">Query-optimized</p>
                  <ul className="text-xs text-muted-foreground space-y-1">
                    <li>• Aggregated metrics</li>
                    <li>• Business views</li>
                    <li>• Performance indexes</li>
                  </ul>
                </div>
              </div>

              <div className="p-4 bg-primary/10 rounded-lg border-l-4 border-primary">
                <h4 className="font-semibold text-foreground mb-2">Key Components</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• <strong>Airflow DAGs:</strong> Daily ETL orchestration (09:00 UTC)</li>
                  <li>• <strong>PySpark Jobs:</strong> Distributed data processing</li>
                  <li>• <strong>AWS Glue:</strong> Metadata catalog with 9 tables</li>
                  <li>• <strong>Athena:</strong> SQL-on-S3 query engine</li>
                  <li>• <strong>FAISS:</strong> Vector search for RAG chatbot</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Development Workflow */}
          <div className="card-lumina">
            <div className="flex items-center gap-3 mb-4">
              <GitBranch className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">Development Workflow</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-foreground mb-3">Branching Strategy</h3>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <div className="flex items-start gap-2">
                    <Code className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><code className="text-primary">main</code> - Production-ready code</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Code className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><code className="text-primary">develop</code> - Integration branch for features</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Code className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><code className="text-primary">feature/*</code> - New features or enhancements</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Code className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><code className="text-primary">bugfix/*</code> - Bug fixes</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-foreground mb-3">Testing Requirements</h3>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Write unit tests for all new features</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Ensure integration tests pass before PR</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Test locally with sample data</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>Verify TypeScript types (no <code>any</code> types)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Contribution Guidelines */}
          <div className="card-lumina border-l-4 border-primary">
            <div className="flex items-center gap-3 mb-4">
              <PlayCircle className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">How to Contribute</h2>
            </div>
            
            <div className="space-y-4">
              <ol className="space-y-3 text-muted-foreground">
                <li className="flex items-start gap-3">
                  <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold flex-shrink-0">1</span>
                  <div>
                    <div className="font-medium text-foreground">Fork & Clone</div>
                    <div className="text-sm">Fork the repository and clone it to your local machine</div>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold flex-shrink-0">2</span>
                  <div>
                    <div className="font-medium text-foreground">Create Branch</div>
                    <div className="text-sm">Create a new branch following naming conventions: <code className="text-primary">feature/your-feature-name</code></div>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold flex-shrink-0">3</span>
                  <div>
                    <div className="font-medium text-foreground">Make Changes</div>
                    <div className="text-sm">Implement your feature with clean, documented code</div>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold flex-shrink-0">4</span>
                  <div>
                    <div className="font-medium text-foreground">Test Thoroughly</div>
                    <div className="text-sm">Write and run tests to ensure everything works</div>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold flex-shrink-0">5</span>
                  <div>
                    <div className="font-medium text-foreground">Submit PR</div>
                    <div className="text-sm">Create a pull request with a clear description of changes</div>
                  </div>
                </li>
              </ol>

              <div className="p-4 bg-primary/10 rounded-lg mt-4">
                <h4 className="font-semibold text-foreground mb-2">Code Style Guidelines</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Follow TypeScript/Python best practices</li>
                  <li>• Use meaningful variable and function names</li>
                  <li>• Add comments for complex logic</li>
                  <li>• Keep functions small and focused</li>
                  <li>• Run linters before committing (ESLint, Black)</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Useful Resources */}
          <div className="card-lumina">
            <div className="flex items-center gap-3 mb-4">
              <Book className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">Useful Resources</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <a href="/about" className="p-4 bg-secondary/20 rounded-lg hover:bg-secondary/30 transition-colors">
                <h4 className="font-semibold text-foreground mb-1">Project Documentation</h4>
                <p className="text-sm text-muted-foreground">Learn about the project architecture and goals</p>
              </a>
              
              <a href="https://docs.aws.amazon.com/athena/" target="_blank" rel="noopener noreferrer" className="p-4 bg-secondary/20 rounded-lg hover:bg-secondary/30 transition-colors">
                <h4 className="font-semibold text-foreground mb-1">AWS Athena Docs</h4>
                <p className="text-sm text-muted-foreground">Query language and optimization guides</p>
              </a>
              
              <a href="https://spark.apache.org/docs/latest/api/python/" target="_blank" rel="noopener noreferrer" className="p-4 bg-secondary/20 rounded-lg hover:bg-secondary/30 transition-colors">
                <h4 className="font-semibold text-foreground mb-1">PySpark API</h4>
                <p className="text-sm text-muted-foreground">Reference for data processing jobs</p>
              </a>
              
              <a href="https://react.dev/" target="_blank" rel="noopener noreferrer" className="p-4 bg-secondary/20 rounded-lg hover:bg-secondary/30 transition-colors">
                <h4 className="font-semibold text-foreground mb-1">React Documentation</h4>
                <p className="text-sm text-muted-foreground">Frontend framework reference</p>
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
