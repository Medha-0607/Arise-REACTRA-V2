import React from 'react';
import { Inbox } from 'lucide-react';
import { cn } from '../lib/utils';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: React.ComponentType<{ className?: string }>;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon: Icon = Inbox,
  action,
  className,
}) => {
  return (
    <div
      className={cn(
        'p-10 rounded-xl bg-surface border border-dashed border-border text-center flex flex-col items-center justify-center font-mono',
        className
      )}
    >
      <div className="p-3.5 rounded-xl bg-surface-elevated text-slate-400 border border-slate-700 mb-3.5">
        <Icon className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-semibold text-white mb-1">{title}</h3>
      <p className="text-xs text-slate-400 max-w-sm mb-5 leading-relaxed">{description}</p>
      {action}
    </div>
  );
};
