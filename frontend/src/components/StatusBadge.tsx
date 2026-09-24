import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Clock, HelpCircle } from 'lucide-react';
import { cn } from '../lib/utils';

export type BadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'neutral';

interface StatusBadgeProps {
  label: string;
  variant?: BadgeVariant;
  icon?: React.ComponentType<{ className?: string }>;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  label,
  variant = 'neutral',
  icon: CustomIcon,
  className,
}) => {
  const variantStyles = {
    success: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    warning: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    danger: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
    info: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30',
    neutral: 'bg-surface-elevated text-slate-300 border-slate-700',
  };

  const DefaultIcon = () => {
    switch (variant) {
      case 'success':
        return <CheckCircle2 className="w-3.5 h-3.5" />;
      case 'warning':
        return <AlertTriangle className="w-3.5 h-3.5" />;
      case 'danger':
        return <XCircle className="w-3.5 h-3.5" />;
      case 'info':
        return <Clock className="w-3.5 h-3.5" />;
      default:
        return <HelpCircle className="w-3.5 h-3.5" />;
    }
  };

  return (
    <span
      className={cn(
        'inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs font-mono font-medium border',
        variantStyles[variant],
        className
      )}
    >
      {CustomIcon ? <CustomIcon className="w-3.5 h-3.5" /> : <DefaultIcon />}
      <span>{label}</span>
    </span>
  );
};
