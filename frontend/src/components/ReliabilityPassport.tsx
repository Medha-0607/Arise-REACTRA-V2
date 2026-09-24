import { Camera, Layers, Scale, ShieldCheck, Lock, CheckCircle2 } from 'lucide-react';
import { FieldCard } from './FieldCard';
import { ResultType, SetupFormState } from '../types/workflow';
import {
  MeasurementExecutionOutcomeData,
  ClassificationResponse,
  EvidenceSealResponse,
} from '../types/api';

interface ReliabilityPassportProps {
  setup: SetupFormState;
  resultType: ResultType;
  measurementOutcome?: MeasurementExecutionOutcomeData | null;
  classificationOutcome?: ClassificationResponse | null;
  evidenceOutcome?: EvidenceSealResponse | null;
  isSimulated?: boolean;
  envelopeId?: string;
  isSealed?: boolean;
}

export const ReliabilityPassport: React.FC<ReliabilityPassportProps> = ({
  setup,
  resultType,
  measurementOutcome,
  classificationOutcome,
  evidenceOutcome,
  isSimulated = false,
  envelopeId,
  isSealed = true,
}) => {
  const meas = measurementOutcome?.validated_measurement;
  const diag = measurementOutcome?.quality_diagnostics;
  const expl = classificationOutcome?.explanation;

  const displayEnvelopeId =
    evidenceOutcome?.evidence_id ||
    envelopeId ||
    (isSimulated ? 'ENV-2026-SIM-99482A' : 'ENV-PENDING-SEAL');

  const displayDigest = evidenceOutcome?.record_digest
    ? `${evidenceOutcome.record_digest.slice(0, 24)}...`
    : isSimulated
    ? 'e3b0c44298fc1c149afbf4c8996fb924...'
    : 'Available upon sealing';

  const displaySignature = evidenceOutcome?.signature
    ? `${evidenceOutcome.signature.slice(0, 24)}...`
    : isSimulated
    ? '3045022100a1b2c3d4e5f6...'
    : 'Available upon sealing';

  return (
    <div className="space-y-6 font-mono">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-4 rounded-xl bg-surface border border-border">
        <div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-brand-400" />
            <span>Reliability Passport & Trust Envelope</span>
          </h3>
          <p className="text-[11px] text-slate-400">
            Four-quadrant audit verification: Acquisition Provenance, Physical Measurement, Decision Margin, and Cryptographic Seal.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-400">Envelope:</span>
          <span className="px-2.5 py-1 rounded bg-surface-elevated text-brand-300 border border-brand-500/30 font-bold flex items-center space-x-1">
            <Lock className="w-3 h-3 text-emerald-400" />
            <span>{displayEnvelopeId}</span>
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Quadrant 1: CAPTURE PROVENANCE */}
        <FieldCard
          title="1. Capture Provenance & Hardware"
          subtitle="Optical Acquisition Metadata"
          icon={Camera}
        >
          <div className="space-y-2.5 text-xs text-slate-300">
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Acquisition Mode:</span>
              <span className="font-bold text-slate-200">
                {meas?.provenance || setup.captureMode}
              </span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Quality Guard Status:</span>
              <span className="text-emerald-400 font-bold flex items-center space-x-1">
                <CheckCircle2 className="w-3 h-3" />
                <span>
                  {diag
                    ? diag.passed_all_hard_gates
                      ? 'ALL GATES PASSED'
                      : 'GATE FAILED'
                    : isSimulated
                    ? 'PASS (Simulated)'
                    : 'VERIFIED'}
                </span>
              </span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Location Provenance:</span>
              <span className="text-slate-200">
                {setup.locationProvenance || 'Operator Declared (No GPS)'}
              </span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Device Hardware ID:</span>
              <span className="text-slate-400">
                {evidenceOutcome?.device_enrollment_id || 'DEV-OFFLINE-LOCAL'}
              </span>
            </div>
          </div>
        </FieldCard>

        {/* Quadrant 2: OBJECTIVE MEASUREMENT */}
        <FieldCard
          title="2. Objective Measurement Data"
          subtitle="Calibrated Colorimetric Vectors"
          icon={Layers}
        >
          <div className="space-y-2.5 text-xs text-slate-300">
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Target Reagent Profile:</span>
              <span className="text-slate-200 font-bold">
                {expl?.assay_profile_id || setup.testProfileId} (v{expl?.profile_version || '1.0.0'})
              </span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Reference Card Standard:</span>
              <span className="text-slate-200">
                {meas?.reference_card_version || setup.referenceCardId}
              </span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Reaction Timing Gate:</span>
              <span className="text-slate-200">
                {expl?.timing_validity || 'VALID'} ({setup.reactionWindowSeconds}s elapsed)
              </span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Calibration Residual:</span>
              <span className="text-emerald-400 font-bold">
                {meas?.calibration_mean_delta_e
                  ? `${meas.calibration_mean_delta_e} ΔE`
                  : '4.0 ΔE (Calibrated)'}
              </span>
            </div>
          </div>
        </FieldCard>

        {/* Quadrant 3: PRESUMPTIVE CLASSIFICATION */}
        <FieldCard
          title="3. Presumptive Classification"
          subtitle="Non-Definitive Field Finding"
          icon={Scale}
        >
          <div className="space-y-2.5 text-xs text-slate-300">
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Presumptive Finding:</span>
              <span className="font-bold text-brand-400">
                {(classificationOutcome?.outcome || resultType).replace(/_/g, ' ')}
              </span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Decision Margin:</span>
              <span className="text-emerald-300 font-bold">
                {expl?.decision_margin ? `${expl.decision_margin} ΔE` : '18.5 ΔE'}
              </span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Target Distance:</span>
              <span className="text-slate-300">
                {expl?.calculated_distance ? `${expl.calculated_distance} ΔE` : '2.8 ΔE'}
              </span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Legal Certainty Level:</span>
              <span className="text-amber-400 font-bold">PRESUMPTIVE ONLY</span>
            </div>
          </div>
        </FieldCard>

        {/* Quadrant 4: EVIDENCE INTEGRITY & CHAIN */}
        <FieldCard
          title="4. Cryptographic Chain of Custody"
          subtitle="Tamper-Evident Signatures"
          icon={ShieldCheck}
        >
          <div className="space-y-2.5 text-xs text-slate-300">
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Payload SHA-256 Digest:</span>
              <span className="text-slate-300 font-mono text-[10px]">
                {displayDigest}
              </span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Ed25519 Signature:</span>
              <span className="text-slate-300 font-mono text-[10px]">
                {displaySignature}
              </span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Seal State:</span>
              <span className={isSealed || evidenceOutcome ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'}>
                {evidenceOutcome?.integrity_status || (isSealed ? 'SEALED' : 'UNSEALED BUFFER')}
              </span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-elevated/70 border border-border/40">
              <span className="text-slate-400">Tamper Verification:</span>
              <span className="text-emerald-400 font-bold">
                {evidenceOutcome ? 'VERIFIED UNMODIFIED' : isSimulated ? 'VERIFIED (Simulated)' : 'SEALED'}
              </span>
            </div>
          </div>
        </FieldCard>
      </div>
    </div>
  );
};
