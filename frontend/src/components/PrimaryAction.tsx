import React from 'react';
import { cn } from '../lib/utils';
import { Loader2 } from 'lucide-react';

interface PrimaryActionProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  label: string;
  icon?: React.ComponentType<{ className?: string }>;
  variant?: 'primary' | 'secondary' | 'danger' | 'tactical';
  isLoading?: boolean;
}

export const PrimaryAction: React.FC<PrimaryActionProps> = ({
  label,
  icon: Icon,
  variant = 'primary',
  isLoading = false,
  className,
  disabled,
  ...props
}) => {
  const variantStyles = {
    primary:
      'bg-brand-600 hover:bg-brand-500 active:bg-brand-700 text-white border-brand-500/50 shadow-lg shadow-brand-600/20 focus:ring-brand-500',
    secondary:
      'bg-surface-elevated hover:bg-slate-700 active:bg-slate-800 text-slate-200 border-border hover:border-slate-500 focus:ring-slate-400',
    danger:
      'bg-tactical-red/20 hover:bg-tactical-red/30 active:bg-tactical-red/40 text-tactical-red border-tactical-red/40 focus:ring-tactical-red',
    tactical:
      'bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white border-emerald-500/50 shadow-lg shadow-emerald-600/20 focus:ring-emerald-500',
  };

  return (
    <button
      type="button"
      disabled={disabled || isLoading}
      className={cn(
        'min-h-[48px] px-6 py-3 rounded-lg font-mono text-sm font-semibold tracking-wide uppercase border',
        'flex items-center justify-center space-x-2.5 transition-all duration-150',
        'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background',
        'disabled:opacity-45 disabled:cursor-not-allowed disabled:hover:bg-inherit',
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin flex-shrink-0" />
      ) : (
        Icon && <Icon className="w-4 h-4 flex-shrink-0" />
      )}
      <span>{label}</span>
    </button>
  );
};
