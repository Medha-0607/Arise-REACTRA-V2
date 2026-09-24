import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';

export type MetricState = 'PASS' | 'WARN' | 'FAIL' | 'CHECKING';

interface QualityCheckRowProps {
  label: string;
  description: string;
  state: MetricState;
  scoreText?: string;
  className?: string;
}

export const QualityCheckRow: React.FC<QualityCheckRowProps> = ({
  label,
  description,
  state,
  scoreText,
  className,
}) => {
  const configs = {
    PASS: {
      badge: 'PASS',
      badgeClass: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
      icon: CheckCircle2,
      iconClass: 'text-emerald-400',
    },
    WARN: {
      badge: 'MARGINAL',
      badgeClass: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
      icon: AlertTriangle,
      iconClass: 'text-amber-400',
    },
    FAIL: {
      badge: 'REJECTED',
      badgeClass: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
      icon: XCircle,
      iconClass: 'text-rose-400',
    },
    CHECKING: {
      badge: 'EVALUATING',
      badgeClass: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30',
      icon: Loader2,
      iconClass: 'text-cyan-400 animate-spin',
    },
  };

  const current = configs[state];
  const Icon = current.icon;

  return (
    <div
      className={cn(
        'p-3.5 rounded-lg bg-surface-elevated/70 border border-border flex items-center justify-between gap-4 font-mono text-xs',
        className
      )}
    >
      <div className="flex items-center space-x-3">
        <Icon className={cn('w-4 h-4 flex-shrink-0', current.iconClass)} />
        <div>
          <span className="font-semibold text-white block">{label}</span>
          <span className="text-[11px] text-slate-400">{description}</span>
        </div>
      </div>

      <div className="flex items-center space-x-3 flex-shrink-0">
        {scoreText && <span className="text-slate-400 text-[11px]">{scoreText}</span>}
        <span className={cn('px-2.5 py-0.5 rounded text-[10px] font-bold border', current.badgeClass)}>
          {current.badge}
        </span>
      </div>
    </div>
  );
};
