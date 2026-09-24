import React from 'react';
import { ResultType } from '../types/workflow';
import { CheckCircle2, HelpCircle, XCircle, ShieldAlert, Sparkles, Lock } from 'lucide-react';
import { cn } from '../lib/utils';
import { PresumptiveWarning } from './PresumptiveWarning';

interface ResultStateProps {
  resultType: ResultType;
  profileName?: string;
  profileVersion?: string;
  isSimulated?: boolean;
  className?: string;
}

export const ResultState: React.FC<ResultStateProps> = ({
  resultType,
  profileName = 'Marquis Reagent Profile',
  profileVersion = 'v1.0.0',
  isSimulated = false,
  className,
}) => {
  const configs = {
    PRESUMPTIVE_POSITIVE: {
      title: 'PRESUMPTIVE POSITIVE INDICATION',
      badgeText: 'PRESUMPTIVE MATCH',
      badgeColor: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/40',
      bannerBg: 'bg-emerald-950/30 border-emerald-500/40',
      icon: CheckCircle2,
      textColor: 'text-emerald-400',
      measurementSummary: 'Observed colorimetric shift aligns with reference profile reaction criteria.',
      interpretationSummary:
        'Preliminary indication consistent with target analyte class. Confirmatory laboratory testing (GC-MS / HPLC) is required for definitive forensic proof.',
    },
    PRESUMPTIVE_NEGATIVE: {
      title: 'PRESUMPTIVE NEGATIVE INDICATION',
      badgeText: 'NO REACTION MATCH',
      badgeColor: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/40',
      bannerBg: 'bg-cyan-950/30 border-cyan-500/40',
      icon: CheckCircle2,
      textColor: 'text-cyan-400',
      measurementSummary: 'No significant colorimetric transition observed within reaction time window.',
      interpretationSummary:
        'Target analyte not detected at presumptive sensitivity threshold. Does not preclude presence of other chemical compounds.',
    },
    INCONCLUSIVE: {
      title: 'INCONCLUSIVE REACTION PROFILE',
      badgeText: 'INCONCLUSIVE',
      badgeColor: 'bg-amber-500/15 text-amber-400 border-amber-500/40',
      bannerBg: 'bg-amber-950/30 border-amber-500/40',
      icon: HelpCircle,
      textColor: 'text-amber-400',
      measurementSummary: 'Reaction hue or chroma gradient fell within indeterminate decision margin.',
      interpretationSummary:
        'Color response could not be decisively matched to known profile curves. Retest with fresh reagent or submit for laboratory confirmation.',
    },
    INVALID_CAPTURE: {
      title: 'INVALID MEASUREMENT — REJECTED',
      badgeText: 'QUALITY FAILURE',
      badgeColor: 'bg-rose-500/15 text-rose-400 border-rose-500/40',
      bannerBg: 'bg-rose-950/30 border-rose-500/40',
      icon: XCircle,
      textColor: 'text-rose-400',
      measurementSummary: 'Capture quality failed validation thresholds (blur, glare, or misalignment).',
      interpretationSummary:
        'Deterministic quality guard prevented classification. Measurement was rejected prior to classifier invocation.',
    },
  };

  const config = configs[resultType];
  const Icon = config.icon;

  return (
    <div className={cn('space-y-6', className)}>
      {isSimulated && (
        <div className="p-3 rounded-lg bg-purple-950/40 border border-purple-500/30 text-purple-300 text-xs font-mono flex items-center space-x-2">
          <Sparkles className="w-4 h-4 flex-shrink-0 text-purple-400" />
          <span>
            <strong>DEMO / SIMULATION:</strong> This result demonstrates UI state presentation only. No physical specimen was measured.
          </span>
        </div>
      )}

      {/* Primary Result Banner */}
      <div className={cn('p-6 rounded-xl border', config.bannerBg)}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div className="flex items-center space-x-3.5">
            <div className={cn('p-3 rounded-xl bg-surface-elevated border border-slate-700', config.textColor)}>
              <Icon className="w-7 h-7" />
            </div>
            <div>
              <span className="text-[11px] font-mono text-slate-400 tracking-wider uppercase">
                Field Result Classification
              </span>
              <h2 className="text-xl font-bold font-mono tracking-tight text-white">{config.title}</h2>
            </div>
          </div>
          <span className={cn('self-start sm:self-center px-3 py-1 rounded-md text-xs font-mono font-bold border', config.badgeColor)}>
            {config.badgeText}
          </span>
        </div>

        {/* Presumptive Disclaimer Component */}
        <PresumptiveWarning variant="card" className="mt-4" />
      </div>

      {/* Two-Column Measurement vs Interpretation Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
        {/* Measurement Box */}
        <div className="bg-surface rounded-xl p-5 border border-border space-y-3">
          <div className="flex items-center space-x-2 text-slate-200 font-semibold uppercase tracking-wider">
            <ShieldAlert className="w-4 h-4 text-brand-400" />
            <span>1. Objective Measurement</span>
          </div>
          <p className="text-slate-400 leading-relaxed">{config.measurementSummary}</p>
          <div className="pt-2 border-t border-border/60 space-y-1.5 text-[11px] text-slate-400">
            <div className="flex justify-between">
              <span>Assay Profile:</span>
              <span className="text-slate-200">{profileName}</span>
            </div>
            <div className="flex justify-between">
              <span>Profile Schema:</span>
              <span className="text-slate-200">{profileVersion}</span>
            </div>
          </div>
        </div>

        {/* Interpretation Box */}
        <div className="bg-surface rounded-xl p-5 border border-border space-y-3">
          <div className="flex items-center space-x-2 text-slate-200 font-semibold uppercase tracking-wider">
            <Lock className="w-4 h-4 text-emerald-400" />
            <span>2. Presumptive Interpretation</span>
          </div>
          <p className="text-slate-400 leading-relaxed">{config.interpretationSummary}</p>
          <div className="pt-2 border-t border-border/60 space-y-1.5 text-[11px] text-slate-400">
            <div className="flex justify-between">
              <span>Confirmation Level:</span>
              <span className="text-amber-400 font-semibold">PRESUMPTIVE ONLY</span>
            </div>
            <div className="flex justify-between">
              <span>Evidence Envelope:</span>
              <span className="text-slate-200">Tamper-Evident Sealed</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
