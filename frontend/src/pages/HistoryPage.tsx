import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { FieldCard } from '../components/FieldCard';
import { StatusBadge } from '../components/StatusBadge';
import { PresumptiveWarning } from '../components/PresumptiveWarning';
import { apiClient } from '../services/apiClient';
import { SessionSummaryResponse } from '../types/api';
import { useWorkflowStore } from '../stores/useWorkflowStore';
import {
  History,
  Search,
  Filter,
  Lock,
  ArrowRight,
  Sparkles,
  Calendar,
  User,
  Database,
} from 'lucide-react';

interface HistoryRecord {
  id: string;
  caseId: string;
  timestamp: string;
  operator: string;
  profile: string;
  status?: string;
  result: 'PRESUMPTIVE_POSITIVE' | 'PRESUMPTIVE_NEGATIVE' | 'INCONCLUSIVE' | 'INVALID_CAPTURE';
  isSealed: boolean;
  isAuthoritative?: boolean;
}

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const { setActiveSession, setIsLoading } = useWorkflowStore();
  const [search, setSearch] = useState('');
  const [filterResult, setFilterResult] = useState<string>('ALL');
  const [authoritativeSessions, setAuthoritativeSessions] = useState<SessionSummaryResponse[]>([]);

  const fetchSessions = useCallback(async (caseQuery?: string) => {
    try {
      const sessions = await apiClient.listSessions(caseQuery ? { case_id: caseQuery } : undefined);
      if (Array.isArray(sessions)) {
        setAuthoritativeSessions(sessions);
      }
    } catch {
      // offline or no backend
    }
  }, []);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const handleInspect = async (record: HistoryRecord) => {
    if (record.isAuthoritative) {
      setIsLoading(true);
      try {
        const detail = await apiClient.getSession(record.id);
        setActiveSession(detail);
        navigate(record.isSealed ? '/evidence' : '/setup');
      } catch {
        navigate('/evidence');
      } finally {
        setIsLoading(false);
      }
    } else {
      navigate('/evidence');
    }
  };

  const demoRecords: HistoryRecord[] = [
    {
      id: 'SES-2026-0922-001',
      caseId: 'CAS-METRO-492',
      timestamp: '2026-09-22 22:45 UTC',
      operator: 'OFC-8492',
      profile: 'Marquis Reagent Profile',
      result: 'PRESUMPTIVE_POSITIVE',
      isSealed: true,
      isAuthoritative: false,
    },
    {
      id: 'SES-2026-0922-002',
      caseId: 'CAS-HIGHWAY-109',
      timestamp: '2026-09-22 21:12 UTC',
      operator: 'DET-1044',
      profile: 'Scott Reagent Profile',
      result: 'PRESUMPTIVE_NEGATIVE',
      isSealed: true,
      isAuthoritative: false,
    },
    {
      id: 'SES-2026-0922-003',
      caseId: 'CAS-PORT-881',
      timestamp: '2026-09-22 18:30 UTC',
      operator: 'OFC-3921',
      profile: 'Duquenois-Levine Profile',
      result: 'INCONCLUSIVE',
      isSealed: true,
      isAuthoritative: false,
    },
    {
      id: 'SES-2026-0921-004',
      caseId: 'CAS-AIRPORT-302',
      timestamp: '2026-09-21 14:05 UTC',
      operator: 'AGT-9011',
      profile: 'Mecke Reagent Profile',
      result: 'INVALID_CAPTURE',
      isSealed: false,
      isAuthoritative: false,
    },
  ];

  // Map real sessions to records
  const mappedAuthRecords: HistoryRecord[] = authoritativeSessions.map((s) => ({
    id: s.id,
    caseId: s.case_id || s.id.slice(0, 16),
    timestamp: new Date(s.created_at_utc).toUTCString(),
    operator: s.operator_id || 'LOCAL-OPERATOR',
    profile: s.assay_profile_id || 'Standard Profile',
    result: (s.status === 'SEALED' || s.status === 'CLASSIFIED'
      ? 'PRESUMPTIVE_POSITIVE'
      : s.status === 'REJECTED'
      ? 'INVALID_CAPTURE'
      : 'INCONCLUSIVE') as HistoryRecord['result'],
    isSealed: s.status === 'SEALED',
    isAuthoritative: true,
  }));

  const allRecords = mappedAuthRecords.length > 0 ? [...mappedAuthRecords, ...demoRecords] : demoRecords;

  const filtered = allRecords.filter((rec) => {
    const matchesSearch =
      rec.caseId.toLowerCase().includes(search.toLowerCase()) ||
      rec.operator.toLowerCase().includes(search.toLowerCase()) ||
      rec.profile.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filterResult === 'ALL' || rec.result === filterResult;
    return matchesSearch && matchesFilter;
  });

  const getResultBadge = (res: HistoryRecord['result']) => {
    switch (res) {
      case 'PRESUMPTIVE_POSITIVE':
        return <StatusBadge label="PRESUMPTIVE POSITIVE" variant="success" />;
      case 'PRESUMPTIVE_NEGATIVE':
        return <StatusBadge label="PRESUMPTIVE NEGATIVE" variant="info" />;
      case 'INCONCLUSIVE':
        return <StatusBadge label="INCONCLUSIVE" variant="warning" />;
      case 'INVALID_CAPTURE':
        return <StatusBadge label="INVALID CAPTURE" variant="danger" />;
    }
  };

  const hasAuthoritative = mappedAuthRecords.length > 0;

  return (
    <div className="space-y-6 font-mono">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            Field Test History & Local Archive
          </h1>
          <p className="text-xs text-slate-400">
            Searchable log of offline presumptive test records and sealed cryptographic envelopes.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          {hasAuthoritative ? (
            <span className="px-2.5 py-1 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-500/30 flex items-center space-x-1 font-bold">
              <Database className="w-3 h-3" />
              <span>LOCAL SQLITE DATABASE ACTIVE</span>
            </span>
          ) : (
            <span className="px-2.5 py-1 rounded bg-purple-950/60 text-purple-300 border border-purple-500/30 flex items-center space-x-1 font-bold">
              <Sparkles className="w-3 h-3" />
              <span>DEMO RECORDS ONLY</span>
            </span>
          )}
        </div>
      </div>

      <PresumptiveWarning variant="banner" className="rounded-lg" />

      {/* Filter & Search Bar */}
      <div className="p-4 rounded-xl bg-surface border border-border flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 text-xs">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by Case ID, Operator, or Assay Profile..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-surface-elevated border border-border rounded-lg pl-9 pr-3.5 py-2 text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-brand-500 text-xs"
          />
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400 flex-shrink-0" />
          <select
            value={filterResult}
            onChange={(e) => setFilterResult(e.target.value)}
            className="bg-surface-elevated border border-border rounded-lg px-3 py-2 text-slate-200 text-xs focus:outline-none focus:border-brand-500"
          >
            <option value="ALL">All Outcomes</option>
            <option value="PRESUMPTIVE_POSITIVE">Presumptive Positive</option>
            <option value="PRESUMPTIVE_NEGATIVE">Presumptive Negative</option>
            <option value="INCONCLUSIVE">Inconclusive</option>
            <option value="INVALID_CAPTURE">Invalid / Rejected</option>
          </select>
        </div>
      </div>

      {/* History Records Table / Card List */}
      <FieldCard
        title={`Archived Test Sessions (${filtered.length})`}
        subtitle="Immutable Local Records"
        icon={History}
      >
        <div className="space-y-3">
          {filtered.map((record) => (
            <div
              key={record.id}
              className="p-4 rounded-xl bg-surface-elevated/70 border border-border hover:border-slate-600 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4 text-xs"
            >
              <div className="space-y-1.5">
                <div className="flex items-center space-x-3">
                  <span className="font-bold text-white text-sm">{record.caseId}</span>
                  {getResultBadge(record.result)}
                  {record.isAuthoritative ? (
                    <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[9px] font-bold">
                      LOCAL DB
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/30 text-[9px] font-bold">
                      DEMO
                    </span>
                  )}
                </div>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-slate-400">
                  <span className="flex items-center space-x-1">
                    <Calendar className="w-3 h-3 text-slate-500" />
                    <span>{record.timestamp}</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <User className="w-3 h-3 text-slate-500" />
                    <span>{record.operator}</span>
                  </span>
                  <span className="text-slate-300 font-semibold">{record.profile}</span>
                </div>
              </div>

              <div className="flex items-center space-x-3 self-end md:self-center">
                {record.isSealed ? (
                  <span className="flex items-center space-x-1 text-emerald-400 text-[11px]">
                    <Lock className="w-3.5 h-3.5" />
                    <span>Sealed</span>
                  </span>
                ) : (
                  <span className="text-rose-400 text-[11px]">Unsealed</span>
                )}
                <button
                  type="button"
                  onClick={() => handleInspect(record)}
                  className="px-3 py-1.5 rounded-lg bg-surface hover:bg-slate-700 text-slate-300 hover:text-white border border-border text-xs flex items-center space-x-1 transition-colors"
                >
                  <span>Inspect</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          ))}

          {filtered.length === 0 && (
            <div className="py-8 text-center text-slate-500 text-xs">
              No archived records match the search filter.
            </div>
          )}
        </div>
      </FieldCard>
    </div>
  );
};
