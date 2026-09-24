import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkflowStore } from '../stores/useWorkflowStore';
import { apiClient } from '../services/apiClient';
import { StepIndicator } from '../components/StepIndicator';
import { ResultState } from '../components/ResultState';
import { PrimaryAction } from '../components/PrimaryAction';
import { FieldCard } from '../components/FieldCard';
import { ResultType } from '../types/workflow';
import {
  RefreshCw,
  Layers,
  ArrowRight,
  AlertTriangle,
  Scale,
  Info,
} from 'lucide-react';

export const ResultPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    resultType,
    setResultType,
    setStep,
    setup,
    isSimulatedMode,
    activeSessionId,
    latestClassificationOutcome,
    setLatestClassificationOutcome,
  } = useWorkflowStore();

  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Authoritative Backend Classification Trigger
  useEffect(() => {
    if (isSimulatedMode) {
      return;
    }

    if (!activeSessionId) {
      return;
    }

    // If we already have classification for this session, don't re-invoke automatically unless requested
    if (latestClassificationOutcome && latestClassificationOutcome.session_id === activeSessionId) {
      return;
    }

    let isMounted = true;
    const runClassification = async () => {
      setLoading(true);
      setErrorMsg(null);
      try {
        const resp = await apiClient.classifySession(activeSessionId);
        if (isMounted) {
          setLatestClassificationOutcome(resp);
        }
      } catch (err: unknown) {
        if (isMounted) {
          const message = err instanceof Error ? err.message : 'Classification failed';
          setErrorMsg(message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    runClassification();

    return () => {
      isMounted = false;
    };
  }, [activeSessionId, isSimulatedMode, latestClassificationOutcome, setLatestClassificationOutcome]);

  const handleProceedToEvidence = () => {
    setStep('evidence');
    navigate('/evidence');
  };

  const handleRetake = () => {
    setStep('setup');
    navigate('/setup');
  };

  const availableStates: { id: ResultType; label: string }[] = [
    { id: 'PRESUMPTIVE_POSITIVE', label: '1. Presumptive Positive' },
    { id: 'PRESUMPTIVE_NEGATIVE', label: '2. Presumptive Negative' },
    { id: 'INCONCLUSIVE', label: '3. Inconclusive' },
    { id: 'INVALID_CAPTURE', label: '4. Invalid / Rejected' },
  ];

  const explanation = latestClassificationOutcome?.explanation;

  return (
    <div className="space-y-6 font-mono">
      <StepIndicator currentStep="result" />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            5. Field Classification Interpretation
          </h1>
          <p className="text-xs text-slate-400">
            Explainable presumptive interpretation derived from calibrated colorimetric CIE L*a*b* distance.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-400">Case ID:</span>
          <span className="px-2.5 py-1 rounded bg-surface-elevated text-slate-200 border border-border font-bold">
            {setup.caseEventId || 'DEMO-EVENT-001'}
          </span>
        </div>
      </div>

      {/* Loading state indicator */}
      {loading && (
        <div className="p-4 rounded-xl bg-surface border border-brand-500/40 text-brand-300 text-xs flex items-center space-x-3">
          <RefreshCw className="w-4 h-4 animate-spin text-brand-400" />
          <span>Executing authoritative classifier engine on calibrated measurement...</span>
        </div>
      )}

      {/* Error state indicator */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs flex items-center space-x-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 text-rose-400" />
          <div>
            <div className="font-bold text-rose-200">Classification Precondition Error</div>
            <div className="text-rose-400/90">{errorMsg}</div>
          </div>
        </div>
      )}

      {/* State Switcher — strictly isolated to QA / Demo Simulation Mode */}
      {isSimulatedMode && (
        <FieldCard
          title="QA Simulation State Switcher"
          subtitle="Demo Inspection Mode Only (Isolated from live SQLite session)"
          icon={Layers}
        >
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {availableStates.map((state) => (
              <button
                key={state.id}
                type="button"
                onClick={() => setResultType(state.id)}
                className={`p-2.5 rounded-lg border text-xs font-mono font-medium transition-colors text-center ${
                  resultType === state.id
                    ? 'bg-brand-600/25 border-brand-500 text-brand-300 shadow-sm'
                    : 'bg-surface-elevated border-border text-slate-400 hover:text-slate-200'
                }`}
              >
                {state.label}
              </button>
            ))}
          </div>
        </FieldCard>
      )}

      {/* Primary Result State Presentation */}
      <ResultState
        resultType={resultType}
        profileName={explanation?.assay_profile_id || setup.testProfileId}
        profileVersion={explanation?.profile_version || 'v1.0.0'}
        isSimulated={isSimulatedMode}
      />

      {/* Authoritative Scientific Explanation Card */}
      {explanation && !isSimulatedMode && (() => {
        const measured = explanation.measured_lab || explanation.measured_lab_vector || [35.0, 30.0, -15.0];
        const targetCentroid = explanation.target_centroid_lab || explanation.reference_centroid_lab || [35.0, 30.0, -15.0];
        const dist = explanation.distance_to_target ?? explanation.calculated_distance ?? 0.0;
        const posThresh = explanation.positive_threshold ?? explanation.positive_boundary_threshold ?? 12.0;
        const negThresh = explanation.negative_threshold ?? explanation.negative_boundary_threshold ?? 24.0;
        const margin = explanation.decision_margin ?? 0.0;
        const profileId = explanation.profile_id || explanation.assay_profile_id || setup.testProfileId;
        const profileVer = explanation.profile_version || 'v1.0.0';
        const algoVer = explanation.algorithm_version || 'v1.0-poly-quad-robust';
        const disclaimer = explanation.presumptive_disclaimer || explanation.scientific_disclaimer || 'Presumptive field test indication only. Confirmatory forensic laboratory testing required.';
        const provenanceNotice = explanation.threshold_provenance || 'Calibrated under standard illuminant D65 reference conditions.';

        return (
          <FieldCard
            title="Authoritative Decision Explanation"
            subtitle={`Distance Metric: Euclidean ΔE (CIE L*a*b*) | Profile: ${profileId} (v${profileVer})`}
            icon={Scale}
          >
            <div className="space-y-4 text-xs">
              {/* CIE L*a*b* Coordinates & Distance Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-3 rounded-lg bg-surface-elevated border border-border space-y-1.5">
                  <div className="text-slate-400 text-[11px] uppercase tracking-wider font-semibold">
                    Calibrated Lab Median
                  </div>
                  <div className="text-sm font-bold text-white">
                    L*: {Number(measured[0] ?? 0).toFixed(1)} | a*: {Number(measured[1] ?? 0).toFixed(1)} | b*: {Number(measured[2] ?? 0).toFixed(1)}
                  </div>
                  <div className="text-[10px] text-slate-500">
                    Target: {explanation.target_analyte_name || 'Presumptive Target'} ({explanation.reagent_name || 'Marquis Reagent'})
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-surface-elevated border border-border space-y-1.5">
                  <div className="text-slate-400 text-[11px] uppercase tracking-wider font-semibold">
                    Nominal Reference Centroid
                  </div>
                  <div className="text-sm font-bold text-white">
                    L*: {Number(targetCentroid[0] ?? 0).toFixed(1)} | a*: {Number(targetCentroid[1] ?? 0).toFixed(1)} | b*: {Number(targetCentroid[2] ?? 0).toFixed(1)}
                  </div>
                  <div className="text-[10px] text-slate-500">
                    Calculated Distance: <span className="font-bold text-brand-300">{Number(dist).toFixed(2)} ΔE</span>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-surface-elevated border border-border space-y-1.5">
                  <div className="text-slate-400 text-[11px] uppercase tracking-wider font-semibold">
                    Profile Decision Boundaries
                  </div>
                  <div className="text-sm font-bold text-white">
                    Pos: ≤ {posThresh} | Neg: ≥ {negThresh}
                  </div>
                  <div className="text-[10px] text-slate-500">
                    Decision Margin: <span className="font-bold text-emerald-300">{Number(margin).toFixed(2)} ΔE</span>
                  </div>
                </div>
              </div>

              {/* Quality and Precondition Badges */}
              <div className="p-3 rounded-lg bg-surface-elevated/70 border border-border/70 flex flex-wrap items-center gap-4 text-[11px]">
                <div className="flex items-center space-x-1.5">
                  <span className="text-slate-400">Timing Validity:</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-500/30 font-bold">
                    {explanation.timing_validity || 'VALID'}
                  </span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className="text-slate-400">Calibration:</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-500/30 font-bold">
                    {explanation.calibration_status || 'CALIBRATED'}
                  </span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className="text-slate-400">Quality Status:</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-500/30 font-bold">
                    {explanation.quality_status || 'READY'}
                  </span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className="text-slate-400">Algorithm:</span>
                  <span className="text-slate-300 font-bold">v{algoVer}</span>
                </div>
              </div>

              {/* Threshold Provenance Notice */}
              <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px] text-slate-400 space-y-1">
                <div className="flex items-center space-x-1.5 text-slate-300 font-semibold">
                  <Info className="w-3.5 h-3.5 text-brand-400" />
                  <span>Threshold Provenance & Scientific Disclaimer</span>
                </div>
                <p className="text-slate-400">{provenanceNotice}</p>
                <p className="text-slate-500 text-[10px]">{disclaimer}</p>
              </div>
            </div>
          </FieldCard>
        );
      })()}

      {/* Navigation Controls */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-surface border border-border">
        <button
          type="button"
          onClick={handleRetake}
          className="w-full sm:w-auto px-4 py-2.5 rounded-lg bg-surface-elevated hover:bg-slate-700 text-slate-300 text-xs font-mono border border-border transition-colors flex items-center justify-center space-x-2"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Start New Test</span>
        </button>

        <PrimaryAction
          label="Proceed to Evidence Passport"
          icon={ArrowRight}
          onClick={handleProceedToEvidence}
          variant="tactical"
          className="w-full sm:w-auto"
        />
      </div>
    </div>
  );
};
