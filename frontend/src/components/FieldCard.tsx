import React from 'react';
import { cn } from '../lib/utils';

interface FieldCardProps {
  title?: string;
  subtitle?: string;
  badge?: React.ReactNode;
  icon?: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
  className?: string;
  headerAction?: React.ReactNode;
}

export const FieldCard: React.FC<FieldCardProps> = ({
  title,
  subtitle,
  badge,
  icon: Icon,
  children,
  className,
  headerAction,
}) => {
  return (
    <div className={cn('bg-surface rounded-xl border border-border overflow-hidden', className)}>
      {(title || Icon || headerAction || badge) && (
        <div className="px-5 py-3.5 border-b border-border/80 flex items-center justify-between bg-surface/50">
          <div className="flex items-center space-x-2.5">
            {Icon && (
              <div className="p-1.5 rounded-md bg-surface-elevated text-brand-400 border border-slate-700">
                <Icon className="w-4 h-4" />
              </div>
            )}
            <div>
              {title && <h3 className="text-sm font-semibold text-white font-mono tracking-tight">{title}</h3>}
              {subtitle && <p className="text-xs text-slate-400 font-mono">{subtitle}</p>}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {badge}
            {headerAction}
          </div>
        </div>
      )}
      <div className="p-5">{children}</div>
    </div>
  );
};
