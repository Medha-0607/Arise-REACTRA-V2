import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';

interface LoadingStateProps {
  label?: string;
  sublabel?: string;
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  label = 'Processing...',
  sublabel = 'Executing deterministic workflow routines',
  className,
}) => {
  return (
    <div
      className={cn(
        'p-8 rounded-xl bg-surface border border-border text-center flex flex-col items-center justify-center font-mono',
        className
      )}
    >
      <Loader2 className="w-8 h-8 text-brand-500 animate-spin mb-3" />
      <h3 className="text-sm font-semibold text-white mb-1">{label}</h3>
      <p className="text-xs text-slate-400">{sublabel}</p>
    </div>
  );
};
