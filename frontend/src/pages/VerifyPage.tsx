import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkflowStore } from '../stores/useWorkflowStore';
import { apiClient } from '../services/apiClient';
import { StepIndicator } from '../components/StepIndicator';
import { FieldCard } from '../components/FieldCard';
import { PrimaryAction } from '../components/PrimaryAction';
import { PresumptiveWarning } from '../components/PresumptiveWarning';
import {
  EvidenceVerifyResponse,
  ChainVerificationResponse,
} from '../types/api';
import {
  FileCheck,
  Upload,
  CheckCircle2,
  AlertTriangle,
  Lock,
  ShieldAlert,
  Link,
  Loader2,
  RefreshCw,
  ArrowRight,
  RotateCcw,
} from 'lucide-react';

export const VerifyPage: React.FC = () => {
  const navigate = useNavigate();
  const { latestEvidenceOutcome, setStep } = useWorkflowStore();
  const [activeTab, setActiveTab] = useState<'envelope' | 'chain'>('envelope');
  const [envelopeText, setEnvelopeText] = useState('');
  const [originalEnvelopeText, setOriginalEnvelopeText] = useState('');
  const [verifying, setVerifying] = useState(false);
  const [verifyResult, setVerifyResult] = useState<EvidenceVerifyResponse | null>(null);
  const [parseError, setParseError] = useState<string | null>(null);

  // Chain verification state
  const [chainLoading, setChainLoading] = useState(false);
  const [chainResult, setChainResult] = useState<ChainVerificationResponse | null>(null);
  const [chainError, setChainError] = useState<string | null>(null);
  const [deviceFilter, setDeviceFilter] = useState('');

  // Auto-populate with active session evidence if available
  useEffect(() => {
    if (latestEvidenceOutcome && !envelopeText) {
      const fullExport = {
        evidence_id: latestEvidenceOutcome.evidence_id,
        session_id: latestEvidenceOutcome.session_id,
        canonical_record_json: latestEvidenceOutcome.canonical_record_json,
        record_digest: latestEvidenceOutcome.record_digest,
        previous_record_hash: latestEvidenceOutcome.previous_record_hash,
        signature: latestEvidenceOutcome.signature,
        device_public_key_hex: latestEvidenceOutcome.device_public_key_hex,
        device_enrollment_id: latestEvidenceOutcome.device_enrollment_id,
        trust_registry_version: latestEvidenceOutcome.trust_registry_version,
        integrity_status: latestEvidenceOutcome.integrity_status,
        sealed_at_utc: latestEvidenceOutcome.sealed_at_utc,
      };
      const formatted = JSON.stringify(fullExport, null, 2);
      setEnvelopeText(formatted);
      setOriginalEnvelopeText(formatted);
      if (latestEvidenceOutcome.device_enrollment_id) {
        setDeviceFilter(latestEvidenceOutcome.device_enrollment_id);
      }
    }
  }, [latestEvidenceOutcome, envelopeText]);

  const handleVerify = async () => {
    setVerifying(true);
    setParseError(null);
    setVerifyResult(null);

    try {
      let parsed: Record<string, unknown>;
      try {
        parsed = JSON.parse(envelopeText);
      } catch (err: unknown) {
        throw new Error('Invalid JSON format. Please supply a valid JSON envelope object.');
      }

      // Extract required fields
      const canonicalRecordJson =
        (parsed.canonical_record_json as string) ||
        (parsed.canonical_json as string) ||
        (parsed.envelope as string) ||
        envelopeText;

      const recordDigest =
        (parsed.record_digest as string) ||
        (parsed.digest as string) ||
        (parsed.payload_digest as string) ||
        '';

      const signature = (parsed.signature as string) || '';
      const devicePublicKeyHex =
        (parsed.device_public_key_hex as string) ||
        (parsed.device_public_key as string) ||
        '';

      if (!recordDigest || !signature || !devicePublicKeyHex) {
        throw new Error(
          'Missing cryptographic metadata. An evidence envelope must contain record_digest, signature, and device_public_key_hex.'
        );
      }

      const resp = await apiClient.verifyEvidence({
        canonical_record_json: canonicalRecordJson,
        record_digest: recordDigest,
        signature: signature,
        device_public_key_hex: devicePublicKeyHex,
        device_enrollment_id: (parsed.device_enrollment_id as string) || undefined,
        trust_registry_version: (parsed.trust_registry_version as string) || undefined,
      });

      setVerifyResult(resp);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Verification failed';
      setParseError(message);
    } finally {
      setVerifying(false);
    }
  };

  const handleVerifyChain = async () => {
    setChainLoading(true);
    setChainError(null);
    try {
      const res = await apiClient.verifyEvidenceChain(deviceFilter || undefined);
      setChainResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Chain verification request failed';
      setChainError(msg);
    } finally {
      setChainLoading(false);
    }
  };

  const handleTamperOneByte = () => {
    try {
      if (!originalEnvelopeText) {
        setOriginalEnvelopeText(envelopeText);
      }
      const parsed = JSON.parse(envelopeText);
      if (parsed.canonical_record_json) {
        parsed.canonical_record_json = parsed.canonical_record_json.includes('PRESUMPTIVE_POSITIVE')
          ? parsed.canonical_record_json.replace('PRESUMPTIVE_POSITIVE', 'PRESUMPTIVE_NEGATIVE')
          : parsed.canonical_record_json + ' ';
      } else {
        parsed.tampered = true;
      }
      setEnvelopeText(JSON.stringify(parsed, null, 2));
      setVerifyResult(null);
      setParseError(null);
    } catch {
      setEnvelopeText(envelopeText + ' ');
      setVerifyResult(null);
    }
  };

  const handleRestoreOriginal = () => {
    if (originalEnvelopeText) {
      setEnvelopeText(originalEnvelopeText);
      setVerifyResult(null);
      setParseError(null);
    }
  };

  return (
    <div className="space-y-6 font-mono">
      <StepIndicator currentStep="verify" />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            8. Cryptographic Integrity & Hash Chain Verification
          </h1>
          <p className="text-xs text-slate-400">
            Authoritative judicial audit tool distinguishing cryptographic consistency from device trust establishment.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveTab('envelope')}
            className={`px-3 py-1.5 rounded text-xs font-bold transition-colors ${
              activeTab === 'envelope'
                ? 'bg-brand-600 text-white'
                : 'bg-surface-elevated text-slate-400 hover:text-slate-200'
            }`}
          >
            Individual Envelope
          </button>
          <button
            onClick={() => {
              setActiveTab('chain');
              if (!chainResult && !chainLoading) {
                handleVerifyChain();
              }
            }}
            className={`px-3 py-1.5 rounded text-xs font-bold transition-colors ${
              activeTab === 'chain'
                ? 'bg-brand-600 text-white'
                : 'bg-surface-elevated text-slate-400 hover:text-slate-200'
            }`}
          >
            Device Hash Chain
          </button>
        </div>
      </div>

      <PresumptiveWarning variant="banner" className="rounded-lg" />

      {/* Trust Establishment vs Cryptographic Integrity Banner */}
      <div className="p-4 rounded-xl bg-surface-elevated border border-amber-500/40 text-xs text-amber-200 space-y-2">
        <div className="flex items-center space-x-2 font-bold text-amber-300">
          <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
          <span>JUDICIAL TRUST BOUNDARY EDUCATION</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1 text-[11px] leading-relaxed">
          <div className="p-2.5 rounded bg-surface border border-amber-500/20">
            <span className="font-bold text-slate-200 block mb-1">1. Cryptographic Envelope Integrity</span>
            <span>
              Signature Valid (Local Key) proves mathematically that the canonical JSON record matches the SHA-256 digest and was signed by the embedded key.
            </span>
          </div>
          <div className="p-2.5 rounded bg-surface border border-amber-500/20">
            <span className="font-bold text-slate-200 block mb-1">2. Trusted Device Identity (Phase 7)</span>
            <span>
              Proves government/fleet hardware enrollment via Central PKI Trust Registry. (Not evaluated in local MVP verification).
            </span>
          </div>
        </div>
      </div>

      {activeTab === 'envelope' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Envelope Input Panel (2 cols) */}
          <div className="lg:col-span-2 space-y-4">
            <FieldCard
              title="Import Signed Evidence Envelope"
              subtitle="Paste Sealed Evidence JSON or Test Tamper Detection"
              icon={Upload}
              headerAction={
                <div className="flex items-center space-x-2">
                  <button
                    type="button"
                    onClick={handleTamperOneByte}
                    className="px-2.5 py-1 rounded bg-amber-950/40 hover:bg-amber-900/60 text-[11px] text-amber-300 border border-amber-500/40 transition-colors"
                  >
                    Simulate 1-Byte Tamper
                  </button>
                  {originalEnvelopeText && (
                    <button
                      type="button"
                      onClick={handleRestoreOriginal}
                      className="px-2.5 py-1 rounded bg-surface-elevated hover:bg-slate-700 text-[11px] text-slate-300 border border-border transition-colors flex items-center space-x-1"
                    >
                      <RotateCcw className="w-3 h-3" />
                      <span>Restore Original</span>
                    </button>
                  )}
                </div>
              }
            >
              <div className="space-y-4 text-xs">
                <textarea
                  rows={10}
                  placeholder="Paste signed evidence JSON envelope here..."
                  value={envelopeText}
                  onChange={(e) => {
                    setEnvelopeText(e.target.value);
                    setVerifyResult(null);
                    setParseError(null);
                  }}
                  className="w-full bg-surface-elevated border border-border rounded-lg p-3.5 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-brand-500 font-mono text-xs leading-relaxed"
                />

                {parseError && (
                  <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs flex items-center space-x-2">
                    <AlertTriangle className="w-4 h-4 flex-shrink-0 text-rose-400" />
                    <span>{parseError}</span>
                  </div>
                )}

                <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
                  <span className="text-[11px] text-slate-400">
                    {envelopeText.length > 0 ? `${envelopeText.length} bytes loaded` : 'Awaiting input payload'}
                  </span>

                  <PrimaryAction
                    label="Verify Cryptographic Signature"
                    icon={FileCheck}
                    isLoading={verifying}
                    disabled={!envelopeText.trim()}
                    onClick={handleVerify}
                    variant="primary"
                    className="w-full sm:w-auto"
                  />
                </div>
              </div>
            </FieldCard>

            {/* Verification Result Callout */}
            {verifyResult && (
              <div
                className={`p-5 rounded-xl bg-surface border space-y-3 font-mono text-xs ${
                  verifyResult.verification_status === 'VERIFIED'
                    ? 'border-emerald-500/40 bg-emerald-950/20'
                    : 'border-rose-500/40 bg-rose-950/20'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div
                    className={`flex items-center space-x-3 font-bold text-sm ${
                      verifyResult.verification_status === 'VERIFIED'
                        ? 'text-emerald-400'
                        : 'text-rose-400'
                    }`}
                  >
                    {verifyResult.verification_status === 'VERIFIED' ? (
                      <CheckCircle2 className="w-5 h-5" />
                    ) : (
                      <ShieldAlert className="w-5 h-5" />
                    )}
                    <span>STATUS: {verifyResult.verification_status}</span>
                  </div>
                  <span className="text-[11px] text-slate-400">
                    Verified at: {new Date(verifyResult.verified_at_utc).toLocaleTimeString()}
                  </span>
                </div>

                <p className="text-slate-300 text-xs font-sans leading-relaxed">
                  {verifyResult.details}
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-2 border-t border-border/60 text-[11px] text-slate-400">
                  <div className="flex justify-between p-2 rounded bg-surface-elevated">
                    <span>SHA-256 Digest:</span>
                    <span
                      className={`font-bold ${
                        verifyResult.digest_matches ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {verifyResult.digest_matches ? 'MATCH' : 'MISMATCH'}
                    </span>
                  </div>
                  <div className="flex justify-between p-2 rounded bg-surface-elevated">
                    <span>Ed25519 Curve:</span>
                    <span
                      className={`font-bold ${
                        verifyResult.signature_valid ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {verifyResult.signature_valid ? 'VALID' : 'INVALID'}
                    </span>
                  </div>
                  <div className="flex justify-between p-2 rounded bg-surface-elevated">
                    <span>Device Key Binding:</span>
                    <span className="text-brand-300 font-bold">
                      {verifyResult.signature_valid ? 'Signature Valid (Local Key)' : 'Invalid Key'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Verification Explanation Sidebar (1 col) */}
          <div className="space-y-6">
            <FieldCard
              title="Trust Model Specifications"
              subtitle="Local Device Key Boundary"
              icon={Lock}
            >
              <div className="space-y-3.5 text-xs font-sans text-slate-300">
                <div className="p-3 rounded-lg bg-surface-elevated border border-border/60 space-y-1">
                  <span className="font-mono font-bold text-white text-xs block">1. Mathematical Proof</span>
                  <p className="text-slate-400 text-[11px]">
                    Verifies that the canonical JSON payload matches the claimed SHA-256 digest and was signed by the enrolled Ed25519 device key.
                  </p>
                </div>

                <div className="p-3 rounded-lg bg-surface-elevated border border-border/60 space-y-1">
                  <span className="font-mono font-bold text-white text-xs block">2. Tamper Evident</span>
                  <p className="text-slate-400 text-[11px]">
                    Any alteration of even a single byte in the canonical envelope results in an immediate digest mismatch (TAMPER_DETECTED).
                  </p>
                </div>
              </div>
            </FieldCard>
          </div>
        </div>
      ) : (
        /* Device Hash Chain Verification Tab */
        <div className="space-y-6">
          <FieldCard
            title="Inter-Session Device Hash Chain Verification"
            subtitle="Monotonic Cryptographic Chain Audit Across Field Sessions"
            icon={Link}
            headerAction={
              <button
                onClick={handleVerifyChain}
                disabled={chainLoading}
                className="py-1 px-3 rounded bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold flex items-center space-x-1.5 transition-colors disabled:opacity-50"
              >
                {chainLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
                <span>Re-Verify Chain</span>
              </button>
            }
          >
            <div className="space-y-4 text-xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-lg bg-surface border border-border">
                <div className="flex items-center space-x-2">
                  <span className="text-slate-400">Device ID Filter:</span>
                  <input
                    type="text"
                    placeholder="All Devices (Default)"
                    value={deviceFilter}
                    onChange={(e) => setDeviceFilter(e.target.value)}
                    className="bg-surface-elevated border border-border rounded px-2.5 py-1 text-slate-100 text-xs font-mono focus:outline-none focus:border-brand-500"
                  />
                </div>
                <button
                  onClick={handleVerifyChain}
                  className="px-3 py-1 rounded bg-surface-elevated hover:bg-surface-highlight border border-border text-slate-300 text-xs"
                >
                  Apply Filter
                </button>
              </div>

              {chainLoading && (
                <div className="py-8 flex items-center justify-center space-x-2 text-slate-400">
                  <Loader2 className="w-4 h-4 animate-spin text-brand-400" />
                  <span>Traversing and cryptographically auditing device evidence chain...</span>
                </div>
              )}

              {chainError && (
                <div className="p-3 rounded-lg bg-red-950/70 border border-red-500/40 text-red-300 text-xs flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                  <span>{chainError}</span>
                </div>
              )}

              {chainResult && (
                <div className="space-y-4">
                  {/* Status Banner */}
                  <div
                    className={`p-4 rounded-xl border flex items-center justify-between ${
                      chainResult.chain_status === 'CHAIN_VALID'
                        ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
                        : chainResult.chain_status === 'EMPTY_CHAIN'
                        ? 'bg-slate-900 border-slate-700 text-slate-300'
                        : 'bg-red-950/40 border-red-500/40 text-red-300'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      {chainResult.chain_status === 'CHAIN_VALID' ? (
                        <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                      ) : (
                        <ShieldAlert className="w-6 h-6 text-red-400" />
                      )}
                      <div>
                        <div className="font-bold text-sm">
                          CHAIN STATUS: {chainResult.chain_status}
                        </div>
                        <div className="text-[11px] opacity-90">{chainResult.explanation}</div>
                      </div>
                    </div>
                    <div className="text-right text-[11px] text-slate-400">
                      <div>Total Records: {chainResult.total_records}</div>
                      <div>Device: {chainResult.device_enrollment_id}</div>
                    </div>
                  </div>

                  {/* Chain Records Sequence Table */}
                  <div className="space-y-2">
                    <div className="text-slate-400 text-[11px] font-bold">
                      Sequential Record Chaining Log ({chainResult.records.length} Nodes)
                    </div>

                    {chainResult.records.length === 0 ? (
                      <div className="p-4 rounded-lg bg-surface border border-border/60 text-center text-slate-500">
                        No sealed evidence records found on this device.
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {chainResult.records.map((rec) => (
                          <div
                            key={rec.evidence_id || rec.sequence_index}
                            className={`p-3.5 rounded-lg border text-xs space-y-2 ${
                              rec.chain_link_valid && rec.signature_valid && rec.digest_valid
                                ? 'bg-surface border-border/80'
                                : 'bg-red-950/20 border-red-500/50'
                            }`}
                          >
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                              <div className="flex items-center space-x-2">
                                <span className="px-2 py-0.5 rounded bg-surface-elevated border border-border text-brand-300 font-bold text-[10px]">
                                  #{rec.sequence_index}
                                </span>
                                <span className="text-white font-bold">{rec.evidence_id}</span>
                                <span className="text-slate-400 font-mono text-[11px]">
                                  ({rec.session_id})
                                </span>
                              </div>
                              <span className="text-slate-400 text-[10px]">
                                Sealed: {new Date(rec.sealed_at_utc).toLocaleString()}
                              </span>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[10px]">
                              <div className="p-2 rounded bg-surface-elevated border border-border/60 space-y-0.5">
                                <span className="text-slate-400 block">Record Digest:</span>
                                <code className="text-slate-200 font-mono block truncate">
                                  {rec.record_digest}
                                </code>
                              </div>
                              <div className="p-2 rounded bg-surface-elevated border border-border/60 space-y-0.5">
                                <span className="text-slate-400 block">Previous Record Hash:</span>
                                <code className="text-slate-200 font-mono block truncate">
                                  {rec.previous_record_hash || 'GENESIS (None — Root)'}
                                </code>
                              </div>
                            </div>

                            <div className="flex items-center space-x-4 text-[10px] pt-1 border-t border-border/40">
                              <div className="flex items-center space-x-1">
                                <span className="text-slate-400">Signature:</span>
                                <span
                                  className={
                                    rec.signature_valid ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'
                                  }
                                >
                                  {rec.signature_valid ? 'VALID' : 'INVALID'}
                                </span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <span className="text-slate-400">Digest:</span>
                                <span
                                  className={
                                    rec.digest_valid ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'
                                  }
                                >
                                  {rec.digest_valid ? 'VALID' : 'INVALID'}
                                </span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <span className="text-slate-400">Chain Linkage:</span>
                                <span
                                  className={
                                    rec.chain_link_valid ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'
                                  }
                                >
                                  {rec.chain_link_valid ? 'LINKED' : 'DISCONTINUITY'}
                                </span>
                              </div>
                            </div>

                            {rec.error_detail && (
                              <div className="text-[10px] text-rose-300 bg-rose-950/40 p-2 rounded border border-rose-500/30">
                                <strong>Error:</strong> {rec.error_detail}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </FieldCard>
        </div>
      )}

      {/* Navigation Controls */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-surface border border-border">
        <button
          type="button"
          onClick={() => {
            setStep('referral');
            navigate('/referral');
          }}
          className="w-full sm:w-auto px-4 py-2.5 rounded-lg bg-surface-elevated hover:bg-slate-700 text-slate-300 text-xs font-mono border border-border transition-colors flex items-center justify-center space-x-2"
        >
          <span>Back to Referral & QR</span>
        </button>

        <PrimaryAction
          label="View Authoritative Timeline"
          icon={ArrowRight}
          onClick={() => {
            setStep('timeline');
            navigate('/timeline');
          }}
          variant="primary"
          className="w-full sm:w-auto"
        />
      </div>
    </div>
  );
};
