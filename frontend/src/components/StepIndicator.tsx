import React from 'react';
import { WorkflowStep } from '../types/workflow';
import { cn } from '../lib/utils';
import {
  FileText,
  Camera,
  ShieldCheck,
  Activity,
  CheckSquare,
  Lock,
  QrCode,
  FileCheck2,
} from 'lucide-react';
import { Link } from 'react-router-dom';

interface StepIndicatorProps {
  currentStep: WorkflowStep;
  className?: string;
}

const steps: { id: WorkflowStep; label: string; path: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: 'setup', label: '1. Setup', path: '/setup', icon: FileText },
  { id: 'capture', label: '2. Capture', path: '/capture', icon: Camera },
  { id: 'check', label: '3. Quality Check', path: '/check', icon: ShieldCheck },
  { id: 'analysis', label: '4. Analysis', path: '/analysis', icon: Activity },
  { id: 'result', label: '5. Result', path: '/result', icon: CheckSquare },
  { id: 'evidence', label: '6. Evidence', path: '/evidence', icon: Lock },
  { id: 'referral', label: '7. Referral & QR', path: '/referral', icon: QrCode },
  { id: 'verify', label: '8. Verify & Timeline', path: '/verify', icon: FileCheck2 },
];

const stepOrder: Record<WorkflowStep, number> = {
  home: -1,
  setup: 0,
  capture: 1,
  check: 2,
  analysis: 3,
  result: 4,
  evidence: 5,
  referral: 6,
  verify: 7,
  timeline: 7,
};

export const StepIndicator: React.FC<StepIndicatorProps> = ({ currentStep, className }) => {
  const currentIndex = stepOrder[currentStep] ?? -1;

  return (
    <nav aria-label="Field Workflow Progress" className={cn('w-full bg-surface border border-border rounded-xl p-3 overflow-x-auto', className)}>
      <ol className="flex items-center min-w-max md:min-w-0 justify-between gap-1.5 sm:gap-2">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          const isActive = step.id === currentStep || (step.id === 'verify' && currentStep === 'timeline');
          const isCompleted = currentIndex > idx;

          return (
            <li key={step.id} className="flex items-center">
              <Link
                to={step.path}
                className={cn(
                  'flex items-center space-x-1.5 sm:space-x-2 px-2.5 sm:px-3 py-1.5 rounded-lg text-[11px] sm:text-xs font-mono font-medium transition-colors',
                  isActive
                    ? 'bg-brand-600/25 text-brand-400 border border-brand-500/40'
                    : isCompleted
                    ? 'text-emerald-400 hover:bg-surface-elevated'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-surface-elevated'
                )}
              >
                <div
                  className={cn(
                    'w-5 h-5 rounded flex items-center justify-center text-[10px]',
                    isActive
                      ? 'bg-brand-600 text-white'
                      : isCompleted
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-surface-elevated text-slate-400 border border-slate-700'
                  )}
                >
                  <Icon className="w-3 h-3" />
                </div>
                <span>{step.label}</span>
              </Link>
              {idx < steps.length - 1 && (
                <div className="h-px w-2 sm:w-3 bg-border mx-0.5 sm:mx-1 hidden lg:block" />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
