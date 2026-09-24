import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { FieldCard } from '../components/FieldCard';
import { StepIndicator } from '../components/StepIndicator';
import { PrimaryAction } from '../components/PrimaryAction';
import { PresumptiveWarning } from '../components/PresumptiveWarning';
import { AuthenticatedQRCode } from '../components/AuthenticatedQRCode';
import { CustodyHandoffCard } from '../components/CustodyHandoffCard';
import { useWorkflowStore } from '../stores/useWorkflowStore';
import { apiClient } from '../services/apiClient';
import {
  ReferralExportResponse,
  CustodyEventResponse,
  ReferralSummaryResponse,
} from '../types/api';
import {
  FileCode,
  Printer,
  ShieldCheck,
  Sparkles,
  Database,
  Tag,
  Loader2,
  Download,
  AlertCircle,
  ArrowRight,
} from 'lucide-react';

export const ReferralPage: React.FC = () => {
  const navigate = useNavigate();
  const { setup, activeSessionId, isSimulatedMode, resultType, setStep } = useWorkflowStore();
  const [referralSummary, setReferralSummary] = useState<ReferralSummaryResponse | null>(null);
  const [referralExport, setReferralExport] = useState<ReferralExportResponse | null>(null);
  const [custodyHistory, setCustodyHistory] = useState<CustodyEventResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!activeSessionId || isSimulatedMode) return;
    setLoading(true);
    setExportError(null);
    try {
      const summary = await apiClient.getReferralSummary(activeSessionId);
      setReferralSummary(summary);

      if (summary.status === 'EVIDENCE_SEALED' || summary.status === 'ARCHIVED') {
        try {
          const exp = await apiClient.getReferralExport(activeSessionId);
          setReferralExport(exp);
        } catch (e: unknown) {
          console.warn('Referral export not available yet:', e);
        }

        try {
          const cust = await apiClient.getCustodyHistory(activeSessionId);
          setCustodyHistory(cust);
        } catch (e: unknown) {
          console.warn('Custody history load error:', e);
        }
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load referral data';
      setExportError(msg);
    } finally {
      setLoading(false);
    }
  }, [activeSessionId, isSimulatedMode]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleDownloadJson = () => {
    if (!referralExport) return;
    const blob = new Blob([JSON.stringify(referralExport.referral_data, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = referralExport.json_filename || `REACTRA_REFERRAL_${activeSessionId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadHtml = () => {
    if (!referralExport) return;
    const blob = new Blob([referralExport.html_document], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = referralExport.html_filename || `REACTRA_REFERRAL_${activeSessionId}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrintHtml = () => {
    if (!referralExport) return;
    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(referralExport.html_document);
      printWindow.document.close();
      printWindow.focus();
      setTimeout(() => {
        printWindow.print();
      }, 500);
    }
  };

  const handleCustodyRecorded = (event: CustodyEventResponse) => {
    setCustodyHistory((prev) => [...prev, event]);
    // Reload export package so it includes latest custody event
    loadData();
  };

  const isSealed =
    referralSummary?.status === 'EVIDENCE_SEALED' || referralSummary?.status === 'ARCHIVED';

  return (
    <div className="space-y-6 font-mono">
      <StepIndicator currentStep="referral" />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            7. Formal Forensic Science Laboratory (FSL) Referral Package
          </h1>
          <p className="text-xs text-slate-400">
            Authoritative field triage export, verifiable attestation QR, and chain-of-custody transfer records.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          {referralExport ? (
            <span className="px-2.5 py-1 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-500/30 flex items-center space-x-1 font-bold">
              <Database className="w-3 h-3" />
              <span>FORMAL REFERRAL PACKAGE READY</span>
            </span>
          ) : isSealed ? (
            <span className="px-2.5 py-1 rounded bg-blue-950/60 text-blue-300 border border-blue-500/30 flex items-center space-x-1 font-bold">
              <ShieldCheck className="w-3 h-3" />
              <span>EVIDENCE SEALED</span>
            </span>
          ) : (
            <span className="px-2.5 py-1 rounded bg-purple-950/60 text-purple-300 border border-purple-500/30 flex items-center space-x-1 font-bold">
              <Sparkles className="w-3 h-3" />
              <span>UNSEALED / PRE-EXPORT</span>
            </span>
          )}
        </div>
      </div>

      <PresumptiveWarning variant="banner" className="rounded-lg" />

      {exportError && (
        <div className="p-3 rounded-lg bg-red-950/70 border border-red-500/40 text-red-300 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{exportError}</span>
        </div>
      )}

      {/* Formal Referral Export Actions Banner */}
      {isSealed && referralExport && (
        <div className="p-4 rounded-xl bg-surface-elevated border border-brand-500/40 shadow-lg space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/60 pb-3">
            <div>
              <div className="font-bold text-white text-sm flex items-center space-x-2">
                <FileCode className="w-4 h-4 text-brand-400" />
                <span>Authoritative Referral Exports Ready</span>
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">
                Target Artifacts: <code className="text-slate-200">{referralExport.json_filename}</code> &{' '}
                <code className="text-slate-200">{referralExport.html_filename}</code>
              </div>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <button
                onClick={handleDownloadJson}
                className="py-1.5 px-3 rounded bg-surface hover:bg-surface-highlight border border-border text-slate-200 text-xs flex items-center space-x-1.5 font-bold transition-colors"
              >
                <Download className="w-3.5 h-3.5 text-brand-400" />
                <span>Export JSON</span>
              </button>
              <button
                onClick={handleDownloadHtml}
                className="py-1.5 px-3 rounded bg-surface hover:bg-surface-highlight border border-border text-slate-200 text-xs flex items-center space-x-1.5 font-bold transition-colors"
              >
                <Download className="w-3.5 h-3.5 text-emerald-400" />
                <span>Export HTML</span>
              </button>
              <button
                onClick={handlePrintHtml}
                className="py-1.5 px-3 rounded bg-brand-600 hover:bg-brand-500 text-white text-xs flex items-center space-x-1.5 font-bold transition-colors"
              >
                <Printer className="w-3.5 h-3.5" />
                <span>Print / Save PDF</span>
              </button>
            </div>
          </div>
          <div className="text-[10px] text-slate-400 flex items-center space-x-2">
            <span className="font-bold text-slate-300">Print Pipeline:</span>
            <span>Canonical HTML includes <code className="text-slate-200">@media print</code> styling formatted for standard A4 court/FSL docket output.</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Referral Content (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Authoritative Field-Test Triage Card */}
          <FieldCard
            title="Authoritative Field-Test Triage Data"
            subtitle="PRD §29 Authoritative Referral Data Binding"
            icon={ShieldCheck}
          >
            {loading ? (
              <div className="py-8 flex items-center justify-center space-x-2 text-slate-400 text-xs">
                <Loader2 className="w-4 h-4 animate-spin text-brand-400" />
                <span>Fetching authoritative referral records...</span>
              </div>
            ) : referralSummary ? (
              <div className="space-y-4 text-xs">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="p-3 rounded-lg bg-surface-elevated border border-border/70 space-y-1">
                    <span className="text-slate-400 block text-[11px]">Case ID</span>
                    <strong className="text-white text-sm">{referralSummary.case_id}</strong>
                  </div>
                  <div className="p-3 rounded-lg bg-surface-elevated border border-border/70 space-y-1">
                    <span className="text-slate-400 block text-[11px]">Session Identifier</span>
                    <span className="text-brand-300 font-mono">{referralSummary.session_id}</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="p-2.5 rounded bg-surface-elevated border border-border/60">
                    <span className="text-slate-400 block text-[10px]">PRESUMPTIVE OUTCOME</span>
                    <span className="font-bold text-amber-400">
                      {referralSummary.presumptive_outcome?.replace(/_/g, ' ') || 'PRESUMPTIVE POSITIVE'}
                    </span>
                  </div>
                  <div className="p-2.5 rounded bg-surface-elevated border border-border/60">
                    <span className="text-slate-400 block text-[10px]">TARGET ANALYTE</span>
                    <span className="text-slate-200 font-semibold">
                      {referralSummary.target_analyte_name || referralSummary.assay_profile_id || 'Standard Reagent'}
                    </span>
                  </div>
                  <div className="p-2.5 rounded bg-surface-elevated border border-border/60">
                    <span className="text-slate-400 block text-[10px]">OPERATOR BADGE</span>
                    <span className="text-slate-200">{referralSummary.operator_id}</span>
                  </div>
                </div>

                {/* Procedural References Grid */}
                <div className="p-3.5 rounded-lg bg-surface-elevated/70 border border-border space-y-2.5">
                  <span className="font-bold text-slate-200 block text-xs">
                    Recorded Statutory Safeguards & Physical Identifiers
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2 text-[11px]">
                    <div className="flex justify-between border-b border-border/40 pb-1">
                      <span className="text-slate-400">Seizure Memo / Panchnama:</span>
                      <span className="text-slate-200 font-mono">
                        {referralSummary.panchnama_memo_ref_no || 'Recorded'}
                      </span>
                    </div>
                    <div className="flex justify-between border-b border-border/40 pb-1">
                      <span className="text-slate-400">Sample Seal Identifier:</span>
                      <span className="text-slate-200 font-mono">
                        {referralSummary.sample_seal_identifier || 'Recorded'}
                      </span>
                    </div>
                    <div className="flex justify-between border-b border-border/40 pb-1">
                      <span className="text-slate-400">Representative Sample ID:</span>
                      <span className="text-slate-200 font-mono">
                        {referralSummary.representative_sample_id || 'Recorded'}
                      </span>
                    </div>
                    <div className="flex justify-between border-b border-border/40 pb-1">
                      <span className="text-slate-400">Independent Witnesses:</span>
                      <span className="text-slate-200">
                        {referralSummary.witnesses_recorded} Observer(s) Logged
                      </span>
                    </div>
                    <div className="flex justify-between border-b border-border/40 pb-1">
                      <span className="text-slate-400">NDPS §50 Safeguard:</span>
                      <span className="text-brand-300 font-semibold">{referralSummary.section_50_status}</span>
                    </div>
                    <div className="flex justify-between border-b border-border/40 pb-1">
                      <span className="text-slate-400">NDPS §52A Inventory:</span>
                      <span className="text-brand-300 font-semibold">{referralSummary.section_52a_status}</span>
                    </div>
                  </div>
                </div>

                {/* Hash Chain & Integrity Data */}
                {referralExport?.referral_data.integrity && (
                  <div className="p-3 rounded-lg bg-surface border border-border text-[11px] space-y-1.5">
                    <span className="font-bold text-slate-300 block">Cryptographic Envelope Integrity</span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[10px]">
                      <div>
                        <span className="text-slate-400">Record Digest: </span>
                        <code className="text-slate-200 font-mono">
                          {referralExport.referral_data.integrity.record_digest.slice(0, 16)}...
                        </code>
                      </div>
                      <div>
                        <span className="text-slate-400">Previous Hash: </span>
                        <code className="text-slate-200 font-mono">
                          {referralExport.referral_data.integrity.previous_record_hash
                            ? `${referralExport.referral_data.integrity.previous_record_hash.slice(0, 16)}...`
                            : 'GENESIS (None)'}
                        </code>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px]">
                Demo mode active. In live field mode, referral data is populated from backend sealed session.
              </div>
            )}
          </FieldCard>

          {/* Multi-Party Custody Handoff Card */}
          <CustodyHandoffCard
            sessionId={activeSessionId || ''}
            isSealed={isSealed}
            operatorId={referralSummary?.operator_id || setup.operatorBadge || 'OFC-OFFLINE'}
            history={custodyHistory}
            onHandoffRecorded={handleCustodyRecorded}
          />
        </div>

        {/* Sidebar: QR Attestation & Export Summary (1 col) */}
        <div className="space-y-6">
          {/* Authenticated QR Attestation */}
          {referralExport ? (
            <AuthenticatedQRCode
              payload={referralExport.qr_payload}
              testId={referralExport.test_id}
              evidenceId={referralExport.referral_data.integrity.evidence_id}
            />
          ) : (
            <FieldCard
              title="Attestation QR"
              subtitle="Requires Sealed Evidence"
              icon={Tag}
            >
              <div className="p-4 rounded-lg bg-surface text-slate-400 text-xs text-center space-y-2">
                <Tag className="w-8 h-8 text-slate-600 mx-auto" />
                <p>Complete evidence sealing to generate cryptographically bound QR attestation.</p>
              </div>
            </FieldCard>
          )}

          {/* Presumptive Overview Card */}
          <FieldCard
            title="Presumptive Triage Overview"
            subtitle="Field Result vs. Lab Role"
            icon={Tag}
          >
            <div className="space-y-3 text-xs text-slate-300">
              <div className="flex justify-between p-2 rounded bg-surface-elevated">
                <span className="text-slate-400">Field Finding:</span>
                <span className="font-bold text-amber-400">
                  {referralSummary?.presumptive_outcome?.replace(/_/g, ' ') || resultType.replace('_', ' ')}
                </span>
              </div>
              <div className="flex justify-between p-2 rounded bg-surface-elevated">
                <span className="text-slate-400">Target Analyte:</span>
                <span className="text-slate-200">
                  {referralSummary?.target_analyte_name || setup.testProfileId}
                </span>
              </div>
              <div className="flex justify-between p-2 rounded bg-surface-elevated">
                <span className="text-slate-400">Evidence Status:</span>
                <span className="text-emerald-400 font-bold">
                  {referralSummary ? referralSummary.status : 'SEALED ENVELOPE'}
                </span>
              </div>
              <div className="flex justify-between p-2 rounded bg-surface-elevated">
                <span className="text-slate-400">Custody Transfers:</span>
                <span className="text-slate-200 font-bold">{custodyHistory.length} Event(s)</span>
              </div>

              <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px] font-sans leading-relaxed">
                <span className="font-bold font-mono block mb-1">Presumptive Triage Notice</span>
                Forensic laboratories execute formal confirmatory testing (GC-MS / HPLC). REACTRA's field findings are submitted strictly as presumptive investigative triage data.
              </div>
            </div>
          </FieldCard>
        </div>
      </div>

      {/* Navigation Controls */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-surface border border-border">
        <button
          type="button"
          onClick={() => {
            setStep('evidence');
            navigate('/evidence');
          }}
          className="w-full sm:w-auto px-4 py-2.5 rounded-lg bg-surface-elevated hover:bg-slate-700 text-slate-300 text-xs font-mono border border-border transition-colors flex items-center justify-center space-x-2"
        >
          <span>Back to Evidence</span>
        </button>

        <PrimaryAction
          label="Proceed to Cryptographic Verification"
          icon={ArrowRight}
          onClick={() => {
            setStep('verify');
            navigate('/verify');
          }}
          variant="tactical"
          className="w-full sm:w-auto"
        />
      </div>
    </div>
  );
};
