import { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error caught by REACTRA ErrorBoundary:', error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-background flex items-center justify-center p-6 text-slate-100">
          <div className="max-w-md w-full bg-surface border border-tactical-red/30 rounded-xl p-6 shadow-2xl">
            <div className="flex items-center space-x-3 text-tactical-red mb-4">
              <AlertTriangle className="w-8 h-8 flex-shrink-0" />
              <h2 className="text-xl font-bold">System Runtime Exception</h2>
            </div>
            <p className="text-sm text-slate-400 mb-4">
              An unexpected error occurred in the presentation shell. The local state remains isolated.
            </p>
            {this.state.error && (
              <pre className="bg-background/80 p-3 rounded text-xs font-mono text-tactical-red/90 overflow-x-auto mb-6 border border-slate-800">
                {this.state.error.message}
              </pre>
            )}
            <button
              onClick={this.handleReload}
              className="w-full py-2.5 px-4 bg-brand-600 hover:bg-brand-500 active:bg-brand-700 text-white rounded-lg font-medium text-sm transition-colors flex items-center justify-center space-x-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Reload Application</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
