import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Shield,
  Home,
  PlusCircle,
  FileCheck,
  History,
  FlaskConical,
  Sparkles,
  Menu,
  X,
  Database,
} from 'lucide-react';
import { OfflineIndicator } from './OfflineIndicator';
import { cn } from '../lib/utils';
import { useWorkflowStore } from '../stores/useWorkflowStore';

export const TopBar: React.FC = () => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isSimulatedMode } = useWorkflowStore();

  const primaryNav = [
    { label: 'Home', path: '/home', icon: Home },
    { label: 'Start Test', path: '/setup', icon: PlusCircle },
    { label: 'History', path: '/history', icon: History },
    { label: 'Verify', path: '/verify', icon: FileCheck },
    { label: 'Lab Referral', path: '/referral', icon: FlaskConical },
  ];

  const secondaryNav = [
    { label: 'QA Lab', path: '/qa', icon: Sparkles, badge: isSimulatedMode ? 'ACTIVE' : undefined },
    { label: 'Diagnostics', path: '/status', icon: Database },
  ];

  return (
    <header className="bg-surface border-b border-border/80 px-4 sm:px-6 py-3 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand & Identity */}
        <Link to="/home" className="flex items-center space-x-3 group">
          <div className="w-8 h-8 rounded-lg bg-brand-600/20 border border-brand-500/40 flex items-center justify-center text-brand-500 group-hover:border-brand-500/80 transition-colors">
            <Shield className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold tracking-tight text-base sm:text-lg text-white font-mono">
                REACTRA
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-elevated text-slate-400 border border-slate-700">
                V2.0
              </span>
            </div>
            <p className="text-[10px] text-slate-400 hidden sm:block">
              Field Testing & Verifiable Evidence
            </p>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden lg:flex items-center space-x-4">
          <nav className="flex items-center space-x-1">
            {primaryNav.map((item) => {
              const Icon = item.icon;
              const isActive =
                location.pathname === item.path ||
                (item.path === '/home' && location.pathname === '/');

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    'flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg text-xs font-mono font-medium transition-colors',
                    isActive
                      ? 'bg-brand-600/20 text-brand-400 border border-brand-500/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-surface-elevated'
                  )}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="h-4 w-px bg-border hidden lg:block" />

          {/* Secondary Support Utilities */}
          <nav className="flex items-center space-x-1">
            {secondaryNav.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    'flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-mono transition-colors',
                    isActive
                      ? 'bg-purple-950/50 text-purple-300 border border-purple-500/40'
                      : 'text-slate-500 hover:text-slate-300'
                  )}
                >
                  <Icon className="w-3 h-3" />
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="px-1 py-0.2 bg-purple-600 text-white rounded text-[8px] font-bold ml-0.5">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>

          <div className="h-4 w-px bg-border hidden lg:block" />

          <OfflineIndicator />
        </div>

        {/* Mobile / Tablet Menu Button */}
        <div className="flex items-center space-x-2 lg:hidden">
          <OfflineIndicator />
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg bg-surface-elevated border border-border text-slate-300 hover:text-white"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Nav Dropdown */}
      {mobileMenuOpen && (
        <div className="lg:hidden mt-3 pt-3 border-t border-border grid grid-cols-2 gap-1.5">
          {primaryNav.map((item) => {
            const Icon = item.icon;
            const isActive =
              location.pathname === item.path ||
              (item.path === '/home' && location.pathname === '/');

            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileMenuOpen(false)}
                className={cn(
                  'flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-mono font-medium transition-colors',
                  isActive
                    ? 'bg-brand-600/20 text-brand-400 border border-brand-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-surface-elevated'
                )}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      )}
    </header>
  );
};
