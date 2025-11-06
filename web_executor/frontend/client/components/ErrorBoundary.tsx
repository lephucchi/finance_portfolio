import React, { ReactNode } from "react";
import { AlertCircle } from "lucide-react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Error Boundary Component
 * Catches React errors and displays user-friendly error messages
 * Prevents entire app from crashing due to component errors
 */
export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to console for debugging
    console.error("Error caught by boundary:", error);
    console.error("Error info:", errorInfo);

    // You can also log the error to an error reporting service here
    // Example: logErrorToService(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="p-6 min-h-screen flex items-center justify-center bg-background">
            <div className="max-w-md w-full">
              <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6">
                <div className="flex items-center gap-3 mb-4">
                  <AlertCircle className="w-6 h-6 text-destructive flex-shrink-0" />
                  <h1 className="text-lg font-semibold text-foreground">
                    Something went wrong
                  </h1>
                </div>
                <p className="text-sm text-muted-foreground mb-4">
                  {this.state.error?.message ||
                    "An unexpected error occurred. Please try refreshing the page."}
                </p>
                <button
                  onClick={() => window.location.reload()}
                  className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors text-sm font-medium"
                >
                  Refresh Page
                </button>
                {process.env.NODE_ENV === "development" && (
                  <details className="mt-4 p-3 bg-muted rounded-md text-xs font-mono">
                    <summary className="cursor-pointer font-semibold mb-2">
                      Error Details (Dev Only)
                    </summary>
                    <p className="text-red-600 whitespace-pre-wrap overflow-auto">
                      {this.state.error?.toString()}
                    </p>
                  </details>
                )}
              </div>
            </div>
          </div>
        )
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
