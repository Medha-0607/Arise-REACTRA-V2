import React, { useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import { CheckCircle2, ShieldAlert, Cpu, Lock, Layers, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const { health, isLoading, error, fetchHealth } = useAppStore();

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  const foundationPillars = [
    {
      title: 'Presumptive Boundaries',
      desc: 'Explicit non-definitive match scoring. Invalid captures (blur, glare, misaligned) are rejected prior to classification.',
      icon: ShieldAlert,
      status: 'Enforced',
      color: 'text-amber-400',
    },
    {
      title: 'Offline-First Engine',
      desc: 'Zero external cloud or network dependencies for all core field testing and storage workflows.',
      icon: Cpu,
      status: 'Active',
      color: 'text-emerald-400',
    },
    {
      title: 'Tamper-Evident Records',
      desc: 'Ed25519 cryptographic signing and SHA-256 hash chains provide verifiable audit trails within local trust models.',
      icon: Lock,
      status: 'Configured',
      color: 'text-brand-500',
    },
    {
      title: 'Architectural Layering',
      desc: 'Strict separation of Presentation (React/Vite), API (FastAPI v1), Domain Services, and Authoritative Store (SQLite).',
      icon: Layers,
      status: 'Scaffolded',
      color: 'text-cyan-400',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Hero / Status Header */}
      <div className="bg-surface rounded-xl p-6 tactical-border">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white mb-1 font-mono">
              REACTRA V2 — Engineering Foundation
            </h1>
            <p className="text-sm text-slate-400">
              Phase 0 Foundation Scaffold • SIH26231 • Offline-First Field Testing Architecture
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <div className="px-3.5 py-2 rounded-lg bg-surface-elevated border border-border flex items-center space-x-2.5">
              <span className="relative flex h-2.5 w-2.5">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${health ? 'bg-emerald-400' : 'bg-amber-400'} opacity-75`} />
                <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${health ? 'bg-emerald-500' : 'bg-amber-500'}`} />
              </span>
              <span className="text-xs font-mono font-medium text-slate-300">
                {isLoading ? 'Connecting...' : health ? 'API CONNECTED' : error ? 'OFFLINE' : 'CHECKING'}
              </span>
            </div>
            <Link
              to="/status"
              className="px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-medium font-mono transition-colors flex items-center space-x-1.5"
            >
              <span>Diagnostics</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Core Architectural Pillars */}
      <div>
        <h2 className="text-sm font-semibold tracking-wider uppercase text-slate-400 font-mono mb-4">
          Architectural Boundaries & Safeguards
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {foundationPillars.map((pillar) => {
            const Icon = pillar.icon;
            return (
              <div
                key={pillar.title}
                className="bg-surface rounded-xl p-5 border border-border hover:border-slate-600 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-surface-elevated border border-border text-slate-300">
                      <Icon className="w-5 h-5" />
                    </div>
                    <h3 className="font-semibold text-white text-base">{pillar.title}</h3>
                  </div>
                  <span className={`text-xs font-mono font-medium px-2 py-0.5 rounded bg-surface-elevated ${pillar.color} border border-border`}>
                    {pillar.status}
                  </span>
                </div>
                <p className="text-sm text-slate-400 leading-relaxed">{pillar.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Phase Roadmap Overview */}
      <div className="bg-surface rounded-xl p-6 border border-border">
        <h2 className="text-sm font-semibold tracking-wider uppercase text-slate-400 font-mono mb-4">
          Implementation Roadmap & Current Phase Status
        </h2>
        <div className="space-y-3 font-mono text-xs">
          <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between">
            <div className="flex items-center space-x-2 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              <span className="font-bold">PHASE 0: Foundation & Scaffolding</span>
            </div>
            <span className="text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded">COMPLETE / PASSING</span>
          </div>
          <div className="p-3 rounded-lg bg-surface-elevated border border-border/60 flex items-center justify-between text-slate-400">
            <span>PHASE 1: Core Domain, State Machine & Assay Profiles</span>
            <span className="text-slate-500">PENDING APPROVAL</span>
          </div>
          <div className="p-3 rounded-lg bg-surface-elevated border border-border/60 flex items-center justify-between text-slate-400">
            <span>PHASE 2: Computer Vision & Colorimetric Quality Gating</span>
            <span className="text-slate-500">PLANNED</span>
          </div>
          <div className="p-3 rounded-lg bg-surface-elevated border border-border/60 flex items-center justify-between text-slate-400">
            <span>PHASE 3: Presumptive Classifier & Distance Matching</span>
            <span className="text-slate-500">PLANNED</span>
          </div>
          <div className="p-3 rounded-lg bg-surface-elevated border border-border/60 flex items-center justify-between text-slate-400">
            <span>PHASE 4: Cryptographic Evidence Engine & Chain Verification</span>
            <span className="text-slate-500">PLANNED</span>
          </div>
        </div>
      </div>
    </div>
  );
};
