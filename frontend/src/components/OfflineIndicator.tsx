import React from 'react';
import { WifiOff } from 'lucide-react';
import { cn } from '../lib/utils';

interface OfflineIndicatorProps {
  className?: string;
}

export const OfflineIndicator: React.FC<OfflineIndicatorProps> = ({ className }) => {
  return (
    <div
      className={cn(
        'flex items-center space-x-1.5 text-xs font-mono px-2.5 py-1 rounded bg-surface-elevated text-emerald-400 border border-emerald-500/30',
        className
      )}
      title="Application operates fully offline without cloud dependencies"
    >
      <WifiOff className="w-3.5 h-3.5" aria-hidden="true" />
      <span className="font-medium tracking-tight">OFFLINE READY</span>
    </div>
  );
};
