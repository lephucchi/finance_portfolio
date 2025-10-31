export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-border/30 bg-background/50 mt-auto">
      <div className="px-6 py-6">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 mb-6">
          {/* Documentation */}
          <div>
            <h4 className="text-xs font-semibold text-primary mb-3 uppercase tracking-wide">
              Docs
            </h4>
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li>
                <a href="#" className="hover:text-primary transition-colors">
                  API Reference
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary transition-colors">
                  Data Schema
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary transition-colors">
                  Getting Started
                </a>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-xs font-semibold text-primary mb-3 uppercase tracking-wide">
              Resources
            </h4>
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li>
                <a href="#" className="hover:text-primary transition-colors">
                  Guides
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary transition-colors">
                  Blog
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary transition-colors">
                  Support
                </a>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-xs font-semibold text-primary mb-3 uppercase tracking-wide">
              Legal
            </h4>
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li>
                <a href="#" className="hover:text-primary transition-colors">
                  Privacy
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary transition-colors">
                  Terms
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary transition-colors">
                  Contact
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-border/30 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-muted-foreground">
            © {currentYear} AEGIS: Lumina. All rights reserved.
          </div>
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <span>v2.1.0</span>
            <span className="text-border">•</span>
            <span className="text-primary">Ready to Analyze</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
