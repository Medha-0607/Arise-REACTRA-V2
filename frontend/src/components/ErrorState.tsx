import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { cn } from '../lib/utils';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Operation Interrupted',
  message = 'An unexpected error prevented completion of the request.',
  onRetry,
  className,
}) => {
  return (
    <div
      className={cn(
        'p-8 rounded-xl bg-surface border border-tactical-red/30 text-center flex flex-col items-center justify-center font-mono',
        className
      )}
    >
      <div className="p-3.5 rounded-xl bg-tactical-red/10 text-tactical-red border border-tactical-red/30 mb-3.5">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-semibold text-white mb-1">{title}</h3>
      <p className="text-xs text-slate-400 max-w-sm mb-5 leading-relaxed">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-surface-elevated hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-mono font-medium border border-border transition-colors flex items-center space-x-2"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Operation</span>
        </button>
      )}
    </div>
  );
};
