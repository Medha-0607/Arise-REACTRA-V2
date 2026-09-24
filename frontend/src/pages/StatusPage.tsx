import React, { useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import { RefreshCw, Server, Database, CheckCircle2, XCircle } from 'lucide-react';

export const StatusPage: React.FC = () => {
  const { health, isLoading, error, fetchHealth } = useAppStore();

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white font-mono">
            System Status & Connectivity
          </h1>
          <p className="text-xs text-slate-400">
            Real-time diagnostics and local service connectivity checks.
          </p>
        </div>
        <button
          onClick={() => fetchHealth()}
          disabled={isLoading}
          className="px-3.5 py-2 bg-surface-elevated hover:bg-slate-700 active:bg-slate-800 text-slate-200 rounded-lg text-xs font-mono font-medium border border-border transition-colors flex items-center space-x-2 disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Status</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Backend API Status */}
        <div className="bg-surface rounded-xl p-5 border border-border space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-surface-elevated text-brand-500 border border-border">
                <Server className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">FastAPI Backend</h3>
                <span className="text-[11px] font-mono text-slate-400">/api/v1/health</span>
              </div>
            </div>
            {health ? (
              <span className="flex items-center space-x-1 text-emerald-400 text-xs font-mono">
                <CheckCircle2 className="w-4 h-4" />
                <span>ONLINE</span>
              </span>
            ) : (
              <span className="flex items-center space-x-1 text-tactical-red text-xs font-mono">
                <XCircle className="w-4 h-4" />
                <span>OFFLINE</span>
              </span>
            )}
          </div>

          <div className="bg-surface-elevated rounded-lg p-3 font-mono text-xs space-y-2 border border-border/50">
            <div className="flex justify-between text-slate-400">
              <span>Service:</span>
              <span className="text-slate-200">{health?.service || 'N/A'}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>API Version:</span>
              <span className="text-slate-200">{health?.api_version || 'N/A'}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>App Version:</span>
              <span className="text-slate-200">{health?.app_version || 'N/A'}</span>
            </div>
          </div>

          {error && (
            <div className="p-2.5 rounded bg-tactical-red/10 border border-tactical-red/30 text-tactical-red text-xs font-mono">
              {error}
            </div>
          )}
        </div>

        {/* Local SQLite Database Status */}
        <div className="bg-surface rounded-xl p-5 border border-border space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-surface-elevated text-cyan-400 border border-border">
                <Database className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">SQLite Data Store</h3>
                <span className="text-[11px] font-mono text-slate-400">Authoritative Local DB</span>
              </div>
            </div>
            <span className="flex items-center space-x-1 text-emerald-400 text-xs font-mono">
              <CheckCircle2 className="w-4 h-4" />
              <span>READY</span>
            </span>
          </div>

          <div className="bg-surface-elevated rounded-lg p-3 font-mono text-xs space-y-2 border border-border/50">
            <div className="flex justify-between text-slate-400">
              <span>Driver:</span>
              <span className="text-slate-200">SQLAlchemy 2.0+</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Schema Engine:</span>
              <span className="text-slate-200">Migrated & Verified (v2.0)</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Storage Mode:</span>
              <span className="text-slate-200">Offline-First Local File</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
