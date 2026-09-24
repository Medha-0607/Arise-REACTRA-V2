import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkflowStore } from '../stores/useWorkflowStore';
import { apiClient } from '../services/apiClient';
import { StepIndicator } from '../components/StepIndicator';
import { PrimaryAction } from '../components/PrimaryAction';
import { EvidenceStatus } from '../components/EvidenceStatus';
import { PresumptiveWarning } from '../components/PresumptiveWarning';
import { ReliabilityPassport } from '../components/ReliabilityPassport';
import {
  Lock,
  ArrowRight,
  Download,
  ShieldCheck,
  RefreshCw,
  AlertTriangle,
} from 'lucide-react';

export const EvidencePage: React.FC = () => {
  const navigate = useNavigate();
  const {
    setup,
    resultType,
    setStep,
    isSimulatedMode,
    activeSessionId,
    latestMeasurementOutcome,
    latestClassificationOutcome,
    latestEvidenceOutcome,
    setLatestEvidenceOutcome,
  } = useWorkflowStore();

  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Authoritative Backend Sealing Trigger
  useEffect(() => {
    if (isSimulatedMode) {
      return;
    }

    if (!activeSessionId) {
      return;
    }

    if (latestEvidenceOutcome && latestEvidenceOutcome.session_id === activeSessionId) {
      return;
    }

    let isMounted = true;
    const runSealing = async () => {
      setLoading(true);
      setErrorMsg(null);
      try {
        const resp = await apiClient.sealSession(activeSessionId);
        if (isMounted) {
          setLatestEvidenceOutcome(resp);
        }
      } catch (err: unknown) {
        if (isMounted) {
          const message = err instanceof Error ? err.message : 'Evidence sealing failed';
          setErrorMsg(message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    runSealing();

    return () => {
      isMounted = false;
    };
  }, [activeSessionId, isSimulatedMode, latestEvidenceOutcome, setLatestEvidenceOutcome]);

  const handleProceedToTimeline = () => {
    setStep('timeline');
    navigate('/timeline');
  };

  const handleProceedToVerify = () => {
    navigate('/verify');
  };

  const handleExportJSON = () => {
    const jsonStr = latestEvidenceOutcome?.canonical_record_json || JSON.stringify({
      session_id: activeSessionId || 'SIM-SESSION',
      evidence_id: latestEvidenceOutcome?.evidence_id || 'ENV-2026-SIM-99482A',
      result: resultType,
      sealed_at: new Date().toISOString(),
    }, null, 2);

    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `REACTRA-EVIDENCE-${latestEvidenceOutcome?.evidence_id || 'ENVELOPE'}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const dynamicEvidenceId =
    latestEvidenceOutcome?.evidence_id ||
    (isSimulatedMode ? 'ENV-2026-SIM-99482A' : 'ENV-PENDING-SEAL');

  return (
    <div className="space-y-6 font-mono">
      <StepIndicator currentStep="evidence" />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            6. Verifiable Evidence Reliability Passport
          </h1>
          <p className="text-xs text-slate-400">
            Immutable cryptographic envelope packaging field capture, normalized measurement, and presumptive interpretation.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400">Status:</span>
          <span className="px-3 py-1 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 text-xs font-bold flex items-center space-x-1.5">
            <Lock className="w-3 h-3" />
            <span>{latestEvidenceOutcome?.integrity_status || (isSimulatedMode ? 'ENVELOPE SEALED' : 'SEALING...')}</span>
          </span>
        </div>
      </div>

      {/* Loading state indicator */}
      {loading && (
        <div className="p-4 rounded-xl bg-surface border border-brand-500/40 text-brand-300 text-xs flex items-center space-x-3">
          <RefreshCw className="w-4 h-4 animate-spin text-brand-400" />
          <span>Computing canonical JSON digest & generating local Ed25519 digital seal...</span>
        </div>
      )}

      {/* Error state indicator */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs flex items-center space-x-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 text-rose-400" />
          <div>
            <div className="font-bold text-rose-200">Evidence Sealing Error</div>
            <div className="text-rose-400/90">{errorMsg}</div>
          </div>
        </div>
      )}

      <PresumptiveWarning variant="banner" className="rounded-lg" />

      {/* Cryptographic Trust Envelope Header */}
      <EvidenceStatus
        envelopeId={dynamicEvidenceId}
        hashAlgorithm="SHA-256 (Canonical Formatted JSON)"
        signatureAlgorithm="Ed25519 Elliptic Curve Signature (Local Key)"
        isSealed={true}
      />

      {/* Hash Chain Linkage Banner */}
      {latestEvidenceOutcome && (
        <div className="p-3.5 rounded-xl bg-surface-elevated border border-border text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="space-y-1">
            <span className="text-slate-400 text-[10px] block font-bold">DEVICE EVIDENCE HASH CHAIN</span>
            <div className="flex items-center space-x-2 text-[11px]">
              <span className="text-slate-400">Previous Record Hash:</span>
              <code className="text-brand-300 font-mono">
                {latestEvidenceOutcome.previous_record_hash
                  ? `${latestEvidenceOutcome.previous_record_hash.slice(0, 24)}...`
                  : 'GENESIS RECORD (None — Chain Root)'}
              </code>
            </div>
          </div>
          <span className="px-2.5 py-1 rounded bg-surface border border-border/80 text-[10px] text-slate-300 font-mono">
            Device: {latestEvidenceOutcome.device_enrollment_id}
          </span>
        </div>
      )}

      {/* Reliability Passport (Four Quadrants) */}
      <ReliabilityPassport
        setup={setup}
        resultType={resultType}
        measurementOutcome={latestMeasurementOutcome}
        classificationOutcome={latestClassificationOutcome}
        evidenceOutcome={latestEvidenceOutcome}
        isSimulated={isSimulatedMode}
        envelopeId={dynamicEvidenceId}
        isSealed={true}
      />

      {/* Export & Navigation Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-surface border border-border">
        <div className="flex items-center space-x-3 w-full sm:w-auto flex-wrap gap-y-2">
          <button
            type="button"
            onClick={handleExportJSON}
            className="flex-1 sm:flex-initial px-4 py-2.5 rounded-lg bg-surface-elevated hover:bg-slate-700 text-slate-300 text-xs font-mono border border-border transition-colors flex items-center justify-center space-x-2"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Envelope JSON</span>
          </button>
          <button
            type="button"
            onClick={handleProceedToVerify}
            className="flex-1 sm:flex-initial px-4 py-2.5 rounded-lg bg-surface-elevated hover:bg-slate-700 text-brand-300 text-xs font-mono border border-brand-500/40 transition-colors flex items-center justify-center space-x-2"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-brand-400" />
            <span>Verify Chain & Envelope</span>
          </button>
          <button
            type="button"
            onClick={handleProceedToTimeline}
            className="flex-1 sm:flex-initial px-4 py-2.5 rounded-lg bg-surface-elevated hover:bg-slate-700 text-slate-400 hover:text-slate-200 text-xs font-mono border border-border transition-colors flex items-center justify-center space-x-2"
          >
            <span>Timeline</span>
          </button>
        </div>

        <PrimaryAction
          label="Proceed to Referral & QR"
          icon={ArrowRight}
          onClick={() => {
            setStep('referral');
            navigate('/referral');
          }}
          variant="primary"
          className="w-full sm:w-auto"
        />
      </div>
    </div>
  );
};
