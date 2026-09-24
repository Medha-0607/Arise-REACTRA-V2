import React from 'react';
import { AlertTriangle, Info } from 'lucide-react';
import { cn } from '../lib/utils';

interface PresumptiveWarningProps {
  variant?: 'banner' | 'card' | 'inline';
  className?: string;
}

export const PresumptiveWarning: React.FC<PresumptiveWarningProps> = ({
  variant = 'banner',
  className,
}) => {
  if (variant === 'banner') {
    return (
      <aside
        aria-label="Presumptive Testing Notice"
        className={cn(
          'bg-tactical-amber/10 border-b border-tactical-amber/30 px-4 py-2 text-xs font-mono text-tactical-amber flex items-center justify-center space-x-2',
          className
        )}
      >
        <AlertTriangle className="w-4 h-4 flex-shrink-0 text-tactical-amber" aria-hidden="true" />
        <span className="font-semibold tracking-wide uppercase text-center">
          Presumptive Field Testing Companion — Not a Confirmatory Laboratory Analysis
        </span>
      </aside>
    );
  }

  if (variant === 'card') {
    return (
      <div
        className={cn(
          'bg-surface border border-tactical-amber/40 rounded-xl p-4 text-xs font-mono text-slate-300 space-y-2',
          className
        )}
      >
        <div className="flex items-center space-x-2 text-tactical-amber font-semibold uppercase tracking-wider">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>Non-Negotiable Presumptive Boundary</span>
        </div>
        <p className="text-slate-400 leading-relaxed">
          REACTRA provides preliminary colorimetric interpretation to assist field triage.
          It does <strong className="text-slate-200">NOT</strong> establish final chemical identity,
          forensic laboratory confirmation, statutory guilt, or legal possession status.
        </p>
      </div>
    );
  }

  return (
    <div className={cn('flex items-center space-x-2 text-xs font-mono text-tactical-amber/90', className)}>
      <Info className="w-3.5 h-3.5 flex-shrink-0" />
      <span>Presumptive Interpretation Only</span>
    </div>
  );
};
