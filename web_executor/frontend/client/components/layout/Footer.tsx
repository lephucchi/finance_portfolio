export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-border/30 bg-background/50 mt-auto">
      <div className="px-6 py-6">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 mb-6">
          {/* Documentation */}
          <div>
            <h4 className="text-xs font-semibold text-primary mb-3 uppercase tracking-wide">
              Documentation
            </h4>
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li>
                <a href="/about" className="hover:text-primary transition-colors">
                  About Project
                </a>
              </li>
              <li>
                <a href="/guide" className="hover:text-primary transition-colors">
                  User Guide
                </a>
              </li>
              <li>
                <a href="/guide" className="hover:text-primary transition-colors">
                  Developer Guide
                </a>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-xs font-semibold text-primary mb-3 uppercase tracking-wide">
              Features
            </h4>
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li>
                <a href="/" className="hover:text-primary transition-colors">
                  Dashboard
                </a>
              </li>
              <li>
                <a href="/screener" className="hover:text-primary transition-colors">
                  Asset Finder
                </a>
              </li>
              <li>
                <a href="/chat" className="hover:text-primary transition-colors">
                  Metallica Chatbot
                </a>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-xs font-semibold text-primary mb-3 uppercase tracking-wide">
              Legal & Information
            </h4>
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li>
                <a href="/disclaimer" className="hover:text-primary transition-colors">
                  Disclaimer
                </a>
              </li>
              <li>
                <a href="/disclaimer" className="hover:text-primary transition-colors">
                  Terms of Use
                </a>
              </li>
              <li>
                <a href="/guide" className="hover:text-primary transition-colors">
                  Contact & Support
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-border/30 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-muted-foreground">
            © {currentYear} AEGIS LUMINA. All rights reserved.
          </div>
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <span>v1.0.0</span>
            <span className="text-border">•</span>
            <span className="text-primary">Production Ready</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
