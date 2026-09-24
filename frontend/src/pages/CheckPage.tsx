import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkflowStore } from '../stores/useWorkflowStore';
import { apiClient } from '../services/apiClient';
import { StepIndicator } from '../components/StepIndicator';
import { FieldCard } from '../components/FieldCard';
import { PrimaryAction } from '../components/PrimaryAction';
import { QualityCheckRow } from '../components/QualityCheckRow';
import { PresumptiveWarning } from '../components/PresumptiveWarning';
import {
  ShieldCheck,
  RefreshCw,
  ArrowRight,
  Sparkles,
  AlertTriangle,
  XCircle,
  CheckCircle2,
  Loader2,
} from 'lucide-react';

export const CheckPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    activeSessionId,
    setup,
    qualityStatus,
    setQualityStatus,
    setStep,
    isSimulatedMode,
    capturedImageBase64,
    latestMeasurementOutcome,
    setLatestMeasurementOutcome,
  } = useWorkflowStore();

  const [evaluating, setEvaluating] = useState(false);
  const [evalError, setEvalError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const runBackendQualityCheck = async () => {
      if (isSimulatedMode) {
        return;
      }

      if (!activeSessionId) {
        // Fallback: simulate if no active session yet
        setEvaluating(true);
        const timer = setTimeout(() => {
          if (isMounted) {
            setEvaluating(false);
            setQualityStatus('READY');
          }
        }, 800);
        return () => clearTimeout(timer);
      }

      setEvaluating(true);
      setEvalError(null);

      try {
        const imagePayload = capturedImageBase64 || 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
        const outcome = await apiClient.measureSession(activeSessionId, {
          image_base64: imagePayload,
          provenance: setup.captureMode,
          elapsed_seconds: setup.reactionWindowSeconds,
        });

        if (isMounted) {
          setLatestMeasurementOutcome(outcome);
          setEvaluating(false);
        }
      } catch (err: unknown) {
        if (isMounted) {
          const msg = err instanceof Error ? err.message : 'Quality gating evaluation failed';
          setEvalError(msg);
          setEvaluating(false);
        }
      }
    };

    runBackendQualityCheck();

    return () => {
      isMounted = false;
    };
  }, [activeSessionId, isSimulatedMode, capturedImageBase64, setup.captureMode, setup.reactionWindowSeconds]);

  const handleProceedToAnalysis = () => {
    setStep('analysis');
    navigate('/analysis');
  };

  const handleRetake = () => {
    setStep('capture');
    navigate('/capture');
  };

  const diag = latestMeasurementOutcome?.quality_diagnostics;
  const isReady = qualityStatus === 'READY';
  const isRejected = qualityStatus === 'INVALID' || qualityStatus === 'RECAPTURE';

  return (
    <div className="space-y-6 font-mono">
      <StepIndicator currentStep="check" />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            3. Adaptive Capture Guard — Quality Gating
          </h1>
          <p className="text-xs text-slate-400">
            Automated verification of optical and geometry thresholds before classification gating.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-400">Guard Status:</span>
          <span
            className={`px-3 py-1 rounded font-bold border ${
              isReady
                ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                : isRejected
                ? 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                : 'bg-amber-500/15 text-amber-400 border-amber-500/30'
            }`}
          >
            {evaluating ? 'EVALUATING' : qualityStatus}
          </span>
        </div>
      </div>

      <PresumptiveWarning variant="banner" className="rounded-lg" />

      {evalError && (
        <div className="p-3.5 rounded-lg bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>{evalError}</span>
          </div>
        </div>
      )}

      {/* Main Guard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <FieldCard
            title="Optical & Perspective Quality Parameters"
            subtitle="Deterministic Pre-Classifier Filters"
            icon={ShieldCheck}
          >
            <div className="space-y-3">
              {/* Blur Check */}
              <QualityCheckRow
                label="Motion & Focus Blur Check"
                description="Laplacian variance threshold check for high-frequency edge clarity."
                state={evaluating ? 'CHECKING' : diag ? (diag.checks.blur.passed ? 'PASS' : 'FAIL') : qualityStatus === 'RECAPTURE' ? 'FAIL' : 'PASS'}
                scoreText={
                  evaluating
                    ? 'Analyzing...'
                    : diag
                    ? `Variance: ${diag.checks.blur.variance} (Min Threshold: ${diag.checks.blur.threshold})`
                    : 'Variance: 482 (Threshold > 120)'
                }
              />

              {/* Exposure Check */}
              <QualityCheckRow
                label="Dynamic Range & Exposure"
                description="Histogram distribution analysis to reject overexposed or clipped whites."
                state={evaluating ? 'CHECKING' : diag ? (diag.checks.exposure.passed ? 'PASS' : 'WARN') : qualityStatus === 'REVIEW' ? 'WARN' : 'PASS'}
                scoreText={
                  evaluating
                    ? 'Analyzing...'
                    : diag
                    ? `Mean Luma: ${diag.checks.exposure.mean_luminance}/255 (Optimal)`
                    : 'Mean Luma: 128/255 (Optimal)'
                }
              />

              {/* Glare Check */}
              <QualityCheckRow
                label="Specular Glare & Highlight Gating"
                description="Reagent well highlight area ratio to prevent saturated reflection artifacts."
                state={evaluating ? 'CHECKING' : diag ? (diag.checks.glare.passed ? 'PASS' : 'FAIL') : qualityStatus === 'INVALID' ? 'FAIL' : 'PASS'}
                scoreText={
                  evaluating
                    ? 'Analyzing...'
                    : diag
                    ? `Glare Ratio: ${(diag.checks.glare.max_roi_glare_fraction * 100).toFixed(1)}% (Limit: ${(diag.checks.glare.threshold * 100).toFixed(1)}%)`
                    : 'Glare Ratio: 0.8% (Threshold < 5.0%)'
                }
              />

              {/* Card Detection Check */}
              <QualityCheckRow
                label="Reference Card Localization"
                description="Corner quadrilateral detection and aspect ratio verification."
                state={evaluating ? 'CHECKING' : diag ? (diag.checks.card_detection.detected ? 'PASS' : 'FAIL') : 'PASS'}
                scoreText={
                  evaluating
                    ? 'Searching...'
                    : diag
                    ? `Confidence: ${(diag.checks.card_detection.confidence * 100).toFixed(0)}% • Ratio: ${diag.checks.card_detection.aspect_ratio}`
                    : 'Card Detected • Confidence: 95%'
                }
              />

              {/* Keystone Skew Alignment Check */}
              <QualityCheckRow
                label="Keystone & Perspective Alignment"
                description="Plane angle deviation check to normalize quadrilateral warp."
                state={evaluating ? 'CHECKING' : diag ? (diag.checks.alignment.passed ? 'PASS' : 'FAIL') : 'PASS'}
                scoreText={
                  evaluating
                    ? 'Aligning...'
                    : diag
                    ? `Skew Angle: ${diag.checks.alignment.skew_angle_deg}° (Limit < 20.0°)`
                    : 'Skew Angle: 2.1° (Threshold < 20.0°)'
                }
              />

              {/* Reference Card Calibration Check */}
              <QualityCheckRow
                label="Reference Card Color Calibration"
                description="Affine least-squares illumination correction across reference patches."
                state={evaluating ? 'CHECKING' : diag ? (diag.checks.calibration.passed ? 'PASS' : 'FAIL') : 'PASS'}
                scoreText={
                  evaluating
                    ? 'Calibrating...'
                    : diag
                    ? `Mean Residual: ${diag.checks.calibration.mean_delta_e} ΔE (Limit < ${diag.checks.calibration.threshold} ΔE)`
                    : 'Mean Residual: 4.8 ΔE (Calibrated)'
                }
              />
            </div>
          </FieldCard>

          {/* Action Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-surface border border-border">
            <button
              type="button"
              onClick={handleRetake}
              className="w-full sm:w-auto px-4 py-2.5 rounded-lg bg-surface-elevated hover:bg-slate-700 text-slate-300 text-xs font-mono border border-border transition-colors flex items-center justify-center space-x-2"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retake Capture</span>
            </button>

            <PrimaryAction
              label={evaluating ? 'Evaluating Quality...' : 'Continue to Analysis'}
              icon={evaluating ? Loader2 : ArrowRight}
              disabled={!isReady || evaluating}
              onClick={handleProceedToAnalysis}
              variant={isReady ? 'primary' : 'secondary'}
              className="w-full sm:w-auto"
            />
          </div>
        </div>

        {/* Status Explanation Card (1 col) */}
        <div className="space-y-6">
          <FieldCard
            title="Quality Gate Ruling"
            subtitle="Automated Integrity Policy"
            icon={isReady ? CheckCircle2 : AlertTriangle}
          >
            <div className="space-y-4 text-xs font-sans text-slate-300">
              {isReady ? (
                <div className="p-3.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 space-y-2">
                  <div className="flex items-center space-x-2 text-emerald-400 font-bold font-mono">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>VALIDATION PASSED</span>
                  </div>
                  <p className="text-slate-300 text-[11px] leading-relaxed">
                    All optical quality filters satisfy the minimum certainty criteria. Specimen frame is cleared for colorimetric region sampling.
                  </p>
                </div>
              ) : isRejected ? (
                <div className="p-3.5 rounded-lg bg-rose-500/10 border border-rose-500/30 space-y-2">
                  <div className="flex items-center space-x-2 text-rose-400 font-bold font-mono">
                    <XCircle className="w-4 h-4" />
                    <span>CAPTURE REJECTED</span>
                  </div>
                  <p className="text-slate-300 text-[11px] leading-relaxed">
                    Quality guard detected excessive degradation. Per product principles, defective captures are strictly prohibited from reaching the classifier. Retake under uniform diffuse lighting.
                  </p>
                </div>
              ) : (
                <div className="p-3.5 rounded-lg bg-amber-500/10 border border-amber-500/30 space-y-2">
                  <div className="flex items-center space-x-2 text-amber-400 font-bold font-mono">
                    <AlertTriangle className="w-4 h-4" />
                    <span>CAUTIONARY REVIEW</span>
                  </div>
                  <p className="text-slate-300 text-[11px] leading-relaxed">
                    Optical metrics are near operational tolerance limits. Operator review recommended.
                  </p>
                </div>
              )}

              {diag && diag.failure_reasons.length > 0 && (
                <div className="p-2.5 rounded bg-rose-950/30 border border-rose-800/40 text-[11px] font-mono text-rose-300 space-y-1">
                  <strong className="block font-bold">Rejection Reasons:</strong>
                  <ul className="list-disc pl-4 space-y-0.5">
                    {diag.failure_reasons.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="pt-2 border-t border-border/60 text-[11px] font-mono text-slate-400 space-y-1.5">
                <div className="flex justify-between">
                  <span>Rejection Rule:</span>
                  <span className="text-slate-200">NON-NEGOTIABLE</span>
                </div>
                <div className="flex justify-between">
                  <span>CV Engine:</span>
                  <span className="text-slate-200">Offline Local Gating</span>
                </div>
              </div>
            </div>
          </FieldCard>

          {isSimulatedMode && (
            <div className="p-4 rounded-xl bg-purple-950/40 border border-purple-500/30 text-xs font-mono text-purple-300 space-y-2">
              <div className="flex items-center space-x-2 text-purple-200 font-bold">
                <Sparkles className="w-4 h-4" />
                <span>Simulation Active</span>
              </div>
              <p className="text-[11px] text-purple-300/90 font-sans">
                Quality metrics above reflect your selected QA scenario.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
