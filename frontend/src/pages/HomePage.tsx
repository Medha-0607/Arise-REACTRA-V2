import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  PlusCircle,
  History,
  FileCheck,
  FlaskConical,
  Sparkles,
  ShieldCheck,
  Activity,
  Lock,
  ArrowRight,
  WifiOff,
  Database,
} from 'lucide-react';
import { PrimaryAction } from '../components/PrimaryAction';
import { FieldCard } from '../components/FieldCard';
import { PresumptiveWarning } from '../components/PresumptiveWarning';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const workflowPillars = [
    {
      step: '01',
      title: 'MEASURE',
      tagline: 'Deterministic Pre-Gating',
      desc: 'Adaptive Capture Guard validates blur, specular glare, exposure, and card alignment before measurement sampling occurs.',
      icon: Activity,
      color: 'text-brand-400',
    },
    {
      step: '02',
      title: 'EXPLAIN',
      tagline: 'Presumptive Distance Matching',
      desc: 'Calibrated colorimetric hue/chroma vector comparison against registered assay profiles with explicit decision margins.',
      icon: ShieldCheck,
      color: 'text-amber-400',
    },
    {
      step: '03',
      title: 'PRESERVE',
      tagline: 'Tamper-Evident Reliability',
      desc: 'Ed25519 digital signing and SHA-256 canonical hash chains create verifiable chain-of-custody audit envelopes.',
      icon: Lock,
      color: 'text-emerald-400',
    },
  ];

  return (
    <div className="space-y-8 font-mono">
      {/* Hero Operational Console Header */}
      <div className="bg-surface rounded-2xl p-6 sm:p-8 border border-border tactical-border">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="flex items-center space-x-2 text-xs text-brand-400">
              <span className="h-2 w-2 rounded-full bg-brand-500 animate-pulse" />
              <span>OFFLINE FIELD TESTING READY</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
              Reaction-Aware Field Testing & Evidence Companion
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 leading-relaxed font-sans">
              Preliminary colorimetric reagent interpretation with adaptive quality gating and cryptographic evidence sealing.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row lg:flex-col gap-3 flex-shrink-0">
            <PrimaryAction
              label="Start Field Test"
              icon={PlusCircle}
              variant="primary"
              onClick={() => navigate('/setup')}
              className="w-full sm:w-auto text-sm"
            />
            <Link
              to="/qa"
              className="px-4 py-2.5 rounded-lg bg-surface-elevated hover:bg-slate-700 text-slate-300 text-xs font-mono border border-border flex items-center justify-center space-x-2 transition-colors"
            >
              <Sparkles className="w-4 h-4 text-purple-400" />
              <span>QA Simulation Lab</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Presumptive Product Scope Card */}
      <PresumptiveWarning variant="card" />

      {/* Product Model: MEASURE • EXPLAIN • PRESERVE */}
      <div>
        <h2 className="text-xs font-semibold tracking-wider uppercase text-slate-400 mb-4 flex items-center space-x-2">
          <span>Operational Architecture Pipeline</span>
          <span className="h-px flex-1 bg-border/60" />
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {workflowPillars.map((pillar) => {
            const Icon = pillar.icon;
            return (
              <div
                key={pillar.title}
                className="bg-surface rounded-xl p-5 border border-border hover:border-slate-600 transition-colors space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-500">{pillar.step}</span>
                  <div className="p-2 rounded-lg bg-surface-elevated border border-border">
                    <Icon className={`w-4 h-4 ${pillar.color}`} />
                  </div>
                </div>
                <div>
                  <h3 className="text-base font-bold text-white tracking-tight">{pillar.title}</h3>
                  <span className="text-[11px] text-slate-400 block">{pillar.tagline}</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed font-sans">{pillar.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Secondary Operations Grid */}
      <div>
        <h2 className="text-xs font-semibold tracking-wider uppercase text-slate-400 mb-4 flex items-center space-x-2">
          <span>Field Records & Verification Operations</span>
          <span className="h-px flex-1 bg-border/60" />
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            to="/history"
            className="p-4 rounded-xl bg-surface border border-border hover:border-slate-600 transition-colors flex flex-col justify-between group"
          >
            <div className="flex items-center space-x-3 mb-3">
              <div className="p-2 rounded-lg bg-surface-elevated text-brand-400 border border-slate-700">
                <History className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-semibold text-white group-hover:text-brand-400 transition-colors">
                Test History
              </h3>
            </div>
            <p className="text-[11px] text-slate-400 font-sans mb-3">
              Search and inspect local presumptive test records and sealed envelopes.
            </p>
            <span className="text-xs text-brand-400 flex items-center space-x-1">
              <span>Access Records</span>
              <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
            </span>
          </Link>

          <Link
            to="/verify"
            className="p-4 rounded-xl bg-surface border border-border hover:border-slate-600 transition-colors flex flex-col justify-between group"
          >
            <div className="flex items-center space-x-3 mb-3">
              <div className="p-2 rounded-lg bg-surface-elevated text-emerald-400 border border-slate-700">
                <FileCheck className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-semibold text-white group-hover:text-emerald-400 transition-colors">
                Verify Evidence
              </h3>
            </div>
            <p className="text-[11px] text-slate-400 font-sans mb-3">
              Validate Ed25519 signatures and SHA-256 hash chains of exported evidence envelopes.
            </p>
            <span className="text-xs text-emerald-400 flex items-center space-x-1">
              <span>Inspect Envelope</span>
              <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
            </span>
          </Link>

          <Link
            to="/referral"
            className="p-4 rounded-xl bg-surface border border-border hover:border-slate-600 transition-colors flex flex-col justify-between group"
          >
            <div className="flex items-center space-x-3 mb-3">
              <div className="p-2 rounded-lg bg-surface-elevated text-cyan-400 border border-slate-700">
                <FlaskConical className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-semibold text-white group-hover:text-cyan-400 transition-colors">
                Lab Referral
              </h3>
            </div>
            <p className="text-[11px] text-slate-400 font-sans mb-3">
              Prepare confirmatory laboratory referral packages and custody transfer metadata.
            </p>
            <span className="text-xs text-cyan-400 flex items-center space-x-1">
              <span>Prepare Referral</span>
              <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
            </span>
          </Link>

          <Link
            to="/status"
            className="p-4 rounded-xl bg-surface border border-border hover:border-slate-600 transition-colors flex flex-col justify-between group"
          >
            <div className="flex items-center space-x-3 mb-3">
              <div className="p-2 rounded-lg bg-surface-elevated text-purple-400 border border-slate-700">
                <Database className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-semibold text-white group-hover:text-purple-400 transition-colors">
                Diagnostics
              </h3>
            </div>
            <p className="text-[11px] text-slate-400 font-sans mb-3">
              Inspect backend API status, SQLite database connectivity, and engine versioning.
            </p>
            <span className="text-xs text-purple-400 flex items-center space-x-1">
              <span>System Health</span>
              <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
            </span>
          </Link>
        </div>
      </div>

      {/* Operational Field Status Summary */}
      <FieldCard
        title="Local Field Operational Status"
        subtitle="Hardware & Environment Constraints"
        icon={WifiOff}
      >
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-3 rounded-lg bg-surface-elevated border border-border/50 space-y-1">
            <span className="text-slate-400 block text-[11px]">Network State</span>
            <span className="text-emerald-400 font-bold">100% OFFLINE ISOLATION</span>
          </div>
          <div className="p-3 rounded-lg bg-surface-elevated border border-border/50 space-y-1">
            <span className="text-slate-400 block text-[11px]">Cryptographic Device Key</span>
            <span className="text-slate-200 font-bold">DEVICE_KEY_ED25519 (BOUND)</span>
          </div>
          <div className="p-3 rounded-lg bg-surface-elevated border border-border/50 space-y-1">
            <span className="text-slate-400 block text-[11px]">Assay Schema Version</span>
            <span className="text-slate-200 font-bold">PROFILE_V1 (REGISTERED)</span>
          </div>
        </div>
      </FieldCard>
    </div>
  );
};
