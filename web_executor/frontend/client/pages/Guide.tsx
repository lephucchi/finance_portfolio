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
import { useI18n } from "@/hooks/useI18n";

type TabType = "user" | "developer";

export default function Guide() {
  const [activeTab, setActiveTab] = useState<TabType>("user");
  const { t } = useI18n();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card-lumina">
        <div className="flex items-center gap-3 mb-2">
          <Book className="w-8 h-8 text-primary" />
          <h1 className="text-4xl font-bold text-foreground">{t('guide.header')}</h1>
        </div>
        <p className="text-muted-foreground">
          {t('guide.headerDescription')}
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
            {t('guide.forUsers')}
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
            {t('guide.forDevelopers')}
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
              <h2 className="text-2xl font-bold text-foreground">{t('guide.dashboard.title')}</h2>
            </div>
            
            <div className="space-y-4">
              <p className="text-muted-foreground">
                {t('guide.dashboard.description')}
              </p>

              <div className="space-y-3">
                <h3 className="font-semibold text-foreground">{t('guide.dashboard.features')}</h3>
                
                <div className="p-4 bg-secondary/20 rounded-lg">
                  <div className="flex items-start gap-3">
                    <Calendar className="w-5 h-5 text-primary mt-0.5" />
                    <div>
                      <h4 className="font-medium text-foreground mb-1">{t('guide.dashboard.datePicker.title')}</h4>
                      <p className="text-sm text-muted-foreground">
                        {t('guide.dashboard.datePicker.description')}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-secondary/20 rounded-lg">
                  <div className="flex items-start gap-3">
                    <RefreshCw className="w-5 h-5 text-primary mt-0.5" />
                    <div>
                      <h4 className="font-medium text-foreground mb-1">{t('guide.dashboard.refreshButton.title')}</h4>
                      <p className="text-sm text-muted-foreground">
                        {t('guide.dashboard.refreshButton.description')}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-secondary/20 rounded-lg">
                  <div className="flex items-start gap-3">
                    <Filter className="w-5 h-5 text-primary mt-0.5" />
                    <div>
                      <h4 className="font-medium text-foreground mb-1">{t('guide.dashboard.timeRangeFilters.title')}</h4>
                      <p className="text-sm text-muted-foreground">
                        {t('guide.dashboard.timeRangeFilters.description')}
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
              <h2 className="text-2xl font-bold text-foreground">{t('guide.assetFinder.title')}</h2>
            </div>
            
            <div className="space-y-4">
              <p className="text-muted-foreground">
                {t('guide.assetFinder.description')}
              </p>

              <div className="space-y-3">
                <h3 className="font-semibold text-foreground">{t('guide.assetFinder.howToUse')}</h3>
                
                <div className="space-y-2 text-sm text-muted-foreground">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.assetFinder.tip1')}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.assetFinder.tip2')}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.assetFinder.tip3')}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.assetFinder.tip4')}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Metallica Chatbot */}
          <div className="card-lumina">
            <div className="flex items-center gap-3 mb-4">
              <MessageSquare className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">{t('guide.metallicaChatbot.title')}</h2>
            </div>  
            
            <div className="space-y-4">
              <p className="text-muted-foreground">
                {t('guide.metallicaChatbot.description')}
              </p>

              <div className="space-y-3">
                <h3 className="font-semibold text-foreground">{t('guide.metallicaChatbot.setup')}</h3>
                
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-500 rounded-lg">
                  <div className="flex items-start gap-3">
                    <Key className="w-5 h-5 text-yellow-600 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-foreground mb-2">{t('guide.metallicaChatbot.requiredGeminiKey')}</h4>
                      <ol className="text-sm text-muted-foreground space-y-2 list-decimal list-inside">
                        <li>{t('guide.metallicaChatbot.setupStep1')} <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">{t('guide.metallicaChatbot.googleAIStudio')}</a></li>
                        <li>{t('guide.metallicaChatbot.setupStep2')}</li>
                        <li>{t('guide.metallicaChatbot.setupStep3')}</li>
                        <li>{t('guide.metallicaChatbot.setupStep4')}</li>
                      </ol>
                    </div>
                  </div>
                </div>

                <h3 className="font-semibold text-foreground mt-4">{t('guide.metallicaChatbot.tipsForBestResults')}</h3>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.metallicaChatbot.tip1')}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.metallicaChatbot.tip2')}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.metallicaChatbot.tip3')}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.metallicaChatbot.tip4')}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Demo Features */}
          <div className="card-lumina border-l-4 border-yellow-500">
            <div className="flex items-center gap-3 mb-4">
              <AlertCircle className="w-6 h-6 text-yellow-600" />
              <h2 className="text-2xl font-bold text-foreground">{t('guide.demoFeatures.title')}</h2>
            </div>
            
            <div className="space-y-4">
              <p className="text-muted-foreground">
                {t('guide.demoFeatures.description')}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-2">{t('guide.demoFeatures.marketInsights.title')}</h4>
                  <p className="text-sm text-muted-foreground">
                    {t('guide.demoFeatures.marketInsights.description')}
                  </p>
                </div>

                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-2">{t('guide.demoFeatures.forecasts.title')}</h4>
                  <p className="text-sm text-muted-foreground">
                    {t('guide.demoFeatures.forecasts.description')}
                  </p>
                </div>

                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-2">{t('guide.demoFeatures.reports.title')}</h4>
                  <p className="text-sm text-muted-foreground">
                    {t('guide.demoFeatures.reports.description')}
                  </p>
                </div>
              </div>

              <p className="text-sm text-muted-foreground italic">
                {t('guide.demoFeatures.footer')}
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
              <h2 className="text-2xl font-bold text-foreground">{t('guide.projectSetup.title')}</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-foreground mb-3">{t('guide.projectSetup.prerequisites')}</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="p-3 bg-secondary/20 rounded-lg text-sm">
                    <div className="font-medium text-foreground">{t('guide.projectSetup.frontend')}</div>
                    <div className="text-muted-foreground">{t('guide.projectSetup.frontendReq')}</div>
                  </div>
                  <div className="p-3 bg-secondary/20 rounded-lg text-sm">
                    <div className="font-medium text-foreground">{t('guide.projectSetup.backend')}</div>
                    <div className="text-muted-foreground">{t('guide.projectSetup.backendReq')}</div>
                  </div>
                  <div className="p-3 bg-secondary/20 rounded-lg text-sm">
                    <div className="font-medium text-foreground">{t('guide.projectSetup.awsAccount')}</div>
                    <div className="text-muted-foreground">{t('guide.projectSetup.awsReq')}</div>
                  </div>
                  <div className="p-3 bg-secondary/20 rounded-lg text-sm">
                    <div className="font-medium text-foreground">{t('guide.projectSetup.geminiKey')}</div>
                    <div className="text-muted-foreground">{t('guide.projectSetup.geminiKeyReq')}</div>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-foreground mb-3">{t('guide.projectSetup.installationSteps')}</h3>
                <div className="space-y-3">
                  <div className="p-4 bg-secondary/10 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm font-bold">1</span>
                      <span className="font-medium text-foreground">{t('guide.projectSetup.cloneRepository')}</span>
                    </div>
                    <code className="block p-2 bg-secondary/30 rounded text-sm text-muted-foreground font-mono">
                      git clone &lt;repository-url&gt;<br/>
                      cd finance_portfolio
                    </code>
                  </div>

                  <div className="p-4 bg-secondary/10 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm font-bold">2</span>
                      <span className="font-medium text-foreground">{t('guide.projectSetup.frontendSetup')}</span>
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
                      <span className="font-medium text-foreground">{t('guide.projectSetup.backendSetup')}</span>
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
                      <span className="font-medium text-foreground">{t('guide.projectSetup.configureAWS')}</span>
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
              <h2 className="text-2xl font-bold text-foreground">{t('guide.architectureOverview.title')}</h2>
            </div>
            
            <div className="space-y-4">
              <p className="text-muted-foreground">
                {t('guide.architectureOverview.description')}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-secondary/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-2">{t('guide.architectureOverview.bronzeLayer.title')}</h4>
                  <p className="text-sm text-muted-foreground mb-2">{t('guide.architectureOverview.bronzeLayer.description')}</p>
                  <ul className="text-xs text-muted-foreground space-y-1">
                    <li>• {t('guide.architectureOverview.bronze1')}</li>
                    <li>• {t('guide.architectureOverview.bronze2')}</li>
                    <li>• {t('guide.architectureOverview.bronze3')}</li>
                  </ul>
                </div>

                <div className="p-4 bg-secondary/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-2">{t('guide.architectureOverview.silverLayer.title')}</h4>
                  <p className="text-sm text-muted-foreground mb-2">{t('guide.architectureOverview.silverLayer.description')}</p>
                  <ul className="text-xs text-muted-foreground space-y-1">
                    <li>• {t('guide.architectureOverview.silver1')}</li>
                    <li>• {t('guide.architectureOverview.silver2')}</li>
                    <li>• {t('guide.architectureOverview.silver3')}</li>
                  </ul>
                </div>

                <div className="p-4 bg-secondary/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-2">{t('guide.architectureOverview.goldLayer.title')}</h4>
                  <p className="text-sm text-muted-foreground mb-2">{t('guide.architectureOverview.goldLayer.description')}</p>
                  <ul className="text-xs text-muted-foreground space-y-1">
                    <li>• {t('guide.architectureOverview.gold1')}</li>
                    <li>• {t('guide.architectureOverview.gold2')}</li>
                    <li>• {t('guide.architectureOverview.gold3')}</li>
                  </ul>
                </div>
              </div>

              <div className="p-4 bg-primary/10 rounded-lg border-l-4 border-primary">
                <h4 className="font-semibold text-foreground mb-2">{t('guide.architectureOverview.keyComponents')}</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• {t('guide.architectureOverview.airflowDAGs')}</li>
                  <li>• {t('guide.architectureOverview.pysparkJobs')}</li>
                  <li>• {t('guide.architectureOverview.awsGlue')}</li>
                  <li>• {t('guide.architectureOverview.athena')}</li>
                  <li>• {t('guide.architectureOverview.faiss')}</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Development Workflow */}
          <div className="card-lumina">
            <div className="flex items-center gap-3 mb-4">
              <GitBranch className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">{t('guide.developmentWorkflow.title')}</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-foreground mb-3">{t('guide.developmentWorkflow.branchingStrategy')}</h3>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <div className="flex items-start gap-2">
                    <Code className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.developmentWorkflow.main')}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Code className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.developmentWorkflow.develop')}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Code className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.developmentWorkflow.feature')}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Code className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.developmentWorkflow.bugfix')}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-foreground mb-3">{t('guide.developmentWorkflow.testingRequirements')}</h3>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.developmentWorkflow.test1')}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.developmentWorkflow.test2')}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.developmentWorkflow.test3')}</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                    <span>{t('guide.developmentWorkflow.test4')}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Contribution Guidelines */}
          <div className="card-lumina border-l-4 border-primary">
            <div className="flex items-center gap-3 mb-4">
              <PlayCircle className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">{t('guide.howToContribute.title')}</h2>
            </div>
            
            <div className="space-y-4">
              <ol className="space-y-3 text-muted-foreground">
                <li className="flex items-start gap-3">
                  <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold flex-shrink-0">1</span>
                  <div>
                    <div className="font-medium text-foreground">{t('guide.howToContribute.step1.title')}</div>
                    <div className="text-sm">{t('guide.howToContribute.step1.description')}</div>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold flex-shrink-0">2</span>
                  <div>
                    <div className="font-medium text-foreground">{t('guide.howToContribute.step2.title')}</div>
                    <div className="text-sm">{t('guide.howToContribute.step2.description')}</div>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold flex-shrink-0">3</span>
                  <div>
                    <div className="font-medium text-foreground">{t('guide.howToContribute.step3.title')}</div>
                    <div className="text-sm">{t('guide.howToContribute.step3.description')}</div>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold flex-shrink-0">4</span>
                  <div>
                    <div className="font-medium text-foreground">{t('guide.howToContribute.step4.title')}</div>
                    <div className="text-sm">{t('guide.howToContribute.step4.description')}</div>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold flex-shrink-0">5</span>
                  <div>
                    <div className="font-medium text-foreground">{t('guide.howToContribute.step5.title')}</div>
                    <div className="text-sm">{t('guide.howToContribute.step5.description')}</div>
                  </div>
                </li>
              </ol>

              <div className="p-4 bg-primary/10 rounded-lg mt-4">
                <h4 className="font-semibold text-foreground mb-2">{t('guide.howToContribute.codeStyleGuidelines')}</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• {t('guide.howToContribute.guideline1')}</li>
                  <li>• {t('guide.howToContribute.guideline2')}</li>
                  <li>• {t('guide.howToContribute.guideline3')}</li>
                  <li>• {t('guide.howToContribute.guideline4')}</li>
                  <li>• {t('guide.howToContribute.guideline5')}</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Useful Resources */}
          <div className="card-lumina">
            <div className="flex items-center gap-3 mb-4">
              <Book className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold text-foreground">{t('guide.usefulResources.title')}</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <a href="/about" className="p-4 bg-secondary/20 rounded-lg hover:bg-secondary/30 transition-colors">
                <h4 className="font-semibold text-foreground mb-1">{t('guide.usefulResources.projectDocumentation.title')}</h4>
                <p className="text-sm text-muted-foreground">{t('guide.usefulResources.projectDocumentation.description')}</p>
              </a>
              
              <a href="https://docs.aws.amazon.com/athena/" target="_blank" rel="noopener noreferrer" className="p-4 bg-secondary/20 rounded-lg hover:bg-secondary/30 transition-colors">
                <h4 className="font-semibold text-foreground mb-1">{t('guide.usefulResources.awsAthenaDocs.title')}</h4>
                <p className="text-sm text-muted-foreground">{t('guide.usefulResources.awsAthenaDocs.description')}</p>
              </a>
              
              <a href="https://spark.apache.org/docs/latest/api/python/" target="_blank" rel="noopener noreferrer" className="p-4 bg-secondary/20 rounded-lg hover:bg-secondary/30 transition-colors">
                <h4 className="font-semibold text-foreground mb-1">{t('guide.usefulResources.pysparkAPI.title')}</h4>
                <p className="text-sm text-muted-foreground">{t('guide.usefulResources.pysparkAPI.description')}</p>
              </a>
              
              <a href="https://react.dev/" target="_blank" rel="noopener noreferrer" className="p-4 bg-secondary/20 rounded-lg hover:bg-secondary/30 transition-colors">
                <h4 className="font-semibold text-foreground mb-1">{t('guide.usefulResources.reactDocumentation.title')}</h4>
                <p className="text-sm text-muted-foreground">{t('guide.usefulResources.reactDocumentation.description')}</p>
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
