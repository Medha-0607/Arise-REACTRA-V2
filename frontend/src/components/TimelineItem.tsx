import React from 'react';
import { cn } from '../lib/utils';
import { CheckCircle2, Clock, AlertCircle } from 'lucide-react';

export type TimelineEventStatus = 'COMPLETED' | 'PENDING' | 'SKIPPED' | 'FAILED';

interface TimelineItemProps {
  timestamp: string;
  title: string;
  description: string;
  status: TimelineEventStatus;
  isLast?: boolean;
  actor?: string;
  className?: string;
}

export const TimelineItem: React.FC<TimelineItemProps> = ({
  timestamp,
  title,
  description,
  status,
  isLast = false,
  actor,
  className,
}) => {
  const statusConfigs = {
    COMPLETED: {
      icon: CheckCircle2,
      iconClass: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
      lineClass: 'bg-emerald-500/30',
    },
    PENDING: {
      icon: Clock,
      iconClass: 'text-slate-400 bg-surface-elevated border-slate-700',
      lineClass: 'bg-border',
    },
    SKIPPED: {
      icon: AlertCircle,
      iconClass: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
      lineClass: 'bg-border',
    },
    FAILED: {
      icon: AlertCircle,
      iconClass: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
      lineClass: 'bg-rose-500/30',
    },
  };

  const config = statusConfigs[status];
  const Icon = config.icon;

  return (
    <div className={cn('relative flex items-start space-x-4 font-mono text-xs', className)}>
      {/* Vertical Connecting Line */}
      {!isLast && (
        <div
          className={cn('absolute left-4 top-8 -bottom-4 w-0.5', config.lineClass)}
          aria-hidden="true"
        />
      )}

      {/* Node Icon */}
      <div
        className={cn(
          'w-8 h-8 rounded-lg flex items-center justify-center border flex-shrink-0 z-10',
          config.iconClass
        )}
      >
        <Icon className="w-4 h-4" />
      </div>

      {/* Event Details */}
      <div className="flex-1 bg-surface-elevated/60 border border-border/80 rounded-xl p-4 mb-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-1.5">
          <h4 className="font-semibold text-white text-sm">{title}</h4>
          <span className="text-[11px] text-slate-400">{timestamp}</span>
        </div>
        <p className="text-slate-300 leading-relaxed text-[11px] mb-2">{description}</p>
        {actor && (
          <div className="text-[10px] text-slate-400 flex items-center space-x-1">
            <span>Logged By:</span>
            <span className="text-slate-200">{actor}</span>
          </div>
        )}
      </div>
    </div>
  );
};
