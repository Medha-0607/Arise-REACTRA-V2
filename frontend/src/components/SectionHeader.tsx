import React from 'react';
import { cn } from '../lib/utils';

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  badge?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  subtitle,
  badge,
  action,
  className,
}) => {
  return (
    <div className={cn('flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-border/60', className)}>
      <div>
        <div className="flex items-center space-x-2.5">
          <h2 className="text-lg font-bold tracking-tight text-white font-mono">{title}</h2>
          {badge}
        </div>
        {subtitle && <p className="text-xs text-slate-400 font-mono mt-0.5">{subtitle}</p>}
      </div>
      {action && <div className="flex items-center space-x-2">{action}</div>}
    </div>
  );
};
