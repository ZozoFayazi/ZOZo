import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-card border border-border rounded-xl p-8 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-destructive/10 rounded-full mb-4">
              <AlertTriangle className="h-8 w-8 text-destructive" />
            </div>
            
            <h2 className="text-2xl font-bold mb-2">Etwas ist schiefgelaufen</h2>
            <p className="text-muted-foreground mb-6">
              Es ist ein unerwarteter Fehler aufgetreten. Bitte laden Sie die Seite neu.
            </p>
            
            {this.state.error && (
              <div className="mb-6 p-4 bg-destructive/5 rounded-lg text-left">
                <p className="text-xs text-muted-foreground font-mono break-all">
                  {this.state.error.toString()}
                </p>
              </div>
            )}
            
            <button
              onClick={this.handleReload}
              className="btn-primary flex items-center gap-2 mx-auto"
            >
              <RefreshCw className="h-4 w-4" />
              Seite neu laden
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
