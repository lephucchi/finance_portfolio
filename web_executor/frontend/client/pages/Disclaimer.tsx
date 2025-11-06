import { 
  AlertTriangle, 
  Shield, 
  FileText, 
  Database, 
  Mail,
  ExternalLink,
  Info
} from "lucide-react";

export default function Disclaimer() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card-lumina border-l-4 border-yellow-500">
        <div className="flex items-center gap-3 mb-2">
          <AlertTriangle className="w-8 h-8 text-yellow-600" />
          <h1 className="text-4xl font-bold text-foreground">Important Disclaimer</h1>
        </div>
        <p className="text-muted-foreground">
          Please read this disclaimer carefully before using this platform
        </p>
      </div>

      {/* Educational Purpose */}
      <div className="card-lumina bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-500">
        <div className="flex items-start gap-4">
          <Info className="w-8 h-8 text-yellow-600 flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-3">
              Educational & Research Purpose Only
            </h2>
            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                This platform was developed as a <strong>graduation thesis project</strong> for 
                educational and research purposes. It is designed to demonstrate the capabilities 
                of modern data engineering, machine learning, and cloud architecture techniques 
                applied to financial data analytics.
              </p>
              <p>
                The system is intended for <strong>academic demonstration</strong>, technical 
                learning, and portfolio presentation purposes only. It is not a commercial product 
                and should not be used as the sole basis for making investment decisions.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Not Financial Advice */}
      <div className="card-lumina bg-red-50 dark:bg-red-900/20 border-2 border-red-500">
        <div className="flex items-start gap-4">
          <AlertTriangle className="w-8 h-8 text-red-600 flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-3">
              Not Financial Advice
            </h2>
            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                <strong>THIS IS NOT FINANCIAL, INVESTMENT, OR TRADING ADVICE.</strong>
              </p>
              <p>
                All information, analysis, predictions, and insights provided by this platform are 
                for informational and educational purposes only. They do not constitute professional 
                financial advice, investment recommendations, or trading signals.
              </p>
              <p>
                You should <strong>always conduct your own research</strong> and consult with 
                qualified financial advisors before making any investment decisions. Past performance 
                does not guarantee future results.
              </p>
              <div className="p-4 bg-red-100 dark:bg-red-900/30 rounded-lg mt-4">
                <p className="text-sm font-semibold text-red-900 dark:text-red-200">
                  ⚠️ INVESTMENT WARNING: Trading stocks and financial instruments involves substantial 
                  risk of loss. You could lose all or more than your initial investment. Never invest 
                  money you cannot afford to lose.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Data Accuracy & Limitations */}
      <div className="card-lumina">
        <div className="flex items-start gap-4">
          <Database className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-3">
              Data Accuracy & Limitations
            </h2>
            <div className="space-y-3">
              <div className="p-4 bg-secondary/20 rounded-lg">
                <h3 className="font-semibold text-foreground mb-2">Data Sources</h3>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>
                      <strong>Stock Data:</strong> Sourced from third-party APIs (VNStock). 
                      We do not guarantee the accuracy, completeness, or timeliness of this data.
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>
                      <strong>News Articles:</strong> Collected via Google Custom Search Engine. 
                      Content accuracy depends on original publishers.
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>
                      <strong>Economic Indicators:</strong> Aggregated from multiple public sources. 
                      May have delays or discrepancies.
                    </span>
                  </li>
                </ul>
              </div>

              <div className="p-4 bg-secondary/20 rounded-lg">
                <h3 className="font-semibold text-foreground mb-2">Known Limitations</h3>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>Data may have a delay of 5-15 minutes from real-time market conditions</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>Some features display mock/demo data as indicated by "🚧 DEMO" badges</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>AI chatbot responses are generated by Google Gemini and may contain inaccuracies</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>Historical data completeness varies by symbol and date range</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>System performance and availability are not guaranteed (best-effort basis)</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Third-Party Services */}
      <div className="card-lumina">
        <div className="flex items-start gap-4">
          <ExternalLink className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-3">
              Third-Party Services
            </h2>
            <div className="space-y-3 text-muted-foreground">
              <p>
                This platform relies on several third-party services and APIs. We do not control 
                or guarantee the availability, accuracy, or performance of these services:
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-secondary/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-2">AWS Services</h4>
                  <ul className="text-sm space-y-1">
                    <li>• Amazon S3 (Data Storage)</li>
                    <li>• AWS Glue (Data Catalog)</li>
                    <li>• AWS Athena (Query Engine)</li>
                    <li>• Amazon EC2 (Compute)</li>
                  </ul>
                </div>

                <div className="p-4 bg-secondary/20 rounded-lg">
                  <h4 className="font-semibold text-foreground mb-2">AI & Data APIs</h4>
                  <ul className="text-sm space-y-1">
                    <li>• Google Gemini API (Chatbot)</li>
                    <li>• VNStock API (Market Data)</li>
                    <li>• Google Custom Search (News)</li>
                    <li>• Economic Data APIs</li>
                  </ul>
                </div>
              </div>

              <p className="text-sm italic">
                You are responsible for obtaining and managing your own API keys (e.g., Gemini API key) 
                and complying with the terms of service of these third-party providers.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* No Warranty */}
      <div className="card-lumina">
        <div className="flex items-start gap-4">
          <Shield className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-3">
              No Warranty & Limitation of Liability
            </h2>
            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                This platform is provided <strong>"AS IS"</strong> and <strong>"AS AVAILABLE"</strong> without 
                any warranties of any kind, either express or implied, including but not limited to:
              </p>
              <ul className="space-y-2 text-sm ml-6">
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">→</span>
                  <span>Warranties of merchantability or fitness for a particular purpose</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">→</span>
                  <span>Accuracy, reliability, or completeness of data</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">→</span>
                  <span>Uninterrupted or error-free operation</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">→</span>
                  <span>Security against unauthorized access or data breaches</span>
                </li>
              </ul>
              <p className="font-semibold text-foreground">
                The developers, contributors, and affiliated parties shall not be liable for any 
                direct, indirect, incidental, consequential, or punitive damages arising from your 
                use of this platform, including but not limited to financial losses from investment 
                decisions made based on information provided here.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* License & Open Source */}
      <div className="card-lumina">
        <div className="flex items-start gap-4">
          <FileText className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-3">
              License & Usage Rights
            </h2>
            <div className="space-y-3 text-muted-foreground">
              <p>
                This project is developed as open-source software for educational purposes. 
                By using this platform, you agree to:
              </p>
              <ul className="space-y-2 text-sm ml-6">
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span>Use the platform for non-commercial, educational purposes</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span>Not redistribute or commercialize the platform without permission</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span>Attribute the original creators when referencing or forking the project</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">✓</span>
                  <span>Comply with all applicable laws and third-party terms of service</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Contact Information */}
      <div className="card-lumina border-l-4 border-primary">
        <div className="flex items-start gap-4">
          <Mail className="w-8 h-8 text-primary flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-3">
              Questions or Concerns?
            </h2>
            <div className="space-y-3 text-muted-foreground">
              <p>
                If you have questions about this disclaimer, the platform's functionality, 
                or wish to report issues, please refer to the <a href="/guide" className="text-primary hover:underline">Guide</a> page 
                for contact information and contribution guidelines.
              </p>
              <p className="text-sm">
                <strong>Last Updated:</strong> November 2025<br/>
                <strong>Version:</strong> 1.0<br/>
                <strong>Institution:</strong> University of Economics and Law (UEL)
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Acceptance */}
      <div className="card-lumina bg-primary/10 border-2 border-primary">
        <div className="text-center py-4">
          <p className="text-foreground font-semibold mb-2">
            By using this platform, you acknowledge that you have read, understood, 
            and agree to this disclaimer.
          </p>
          <p className="text-sm text-muted-foreground">
            If you do not agree with any part of this disclaimer, please discontinue use immediately.
          </p>
        </div>
      </div>
    </div>
  );
}
