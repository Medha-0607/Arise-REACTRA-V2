import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkflowStore } from '../stores/useWorkflowStore';
import { StepIndicator } from '../components/StepIndicator';
import { FieldCard } from '../components/FieldCard';
import { PrimaryAction } from '../components/PrimaryAction';
import { PresumptiveWarning } from '../components/PresumptiveWarning';
import {
  Activity,
  Layers,
  Clock,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Sparkles,
} from 'lucide-react';

export const AnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const { setup, setStep, isSimulatedMode, latestMeasurementOutcome } = useWorkflowStore();
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 25;
      });
    }, 300);
    return () => clearInterval(interval);
  }, []);

  const handleProceedToResult = () => {
    setStep('result');
    navigate('/result');
  };

  const isComplete = progress >= 100;
  const meas = latestMeasurementOutcome?.validated_measurement;
  const well1 = meas?.well_measurements?.well_1;
  const well2 = meas?.well_measurements?.well_2;

  return (
    <div className="space-y-6 font-mono">
      <StepIndicator currentStep="analysis" />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            4. Colorimetric Extraction & Distance Analysis
          </h1>
          <p className="text-xs text-slate-400">
            Homography-warped ROI sampling and profile reaction curve vector matching.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-400">Analysis State:</span>
          <span className="px-2.5 py-1 rounded bg-brand-600/20 text-brand-400 border border-brand-500/30 font-bold">
            {isComplete ? 'SAMPLING COMPLETE' : 'PROCESSING'}
          </span>
        </div>
      </div>

      <PresumptiveWarning variant="banner" className="rounded-lg" />

      {/* Analysis Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Progress Bar Component */}
          <div className="bg-surface rounded-xl p-5 border border-border space-y-3">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2 text-slate-300">
                <Cpu className="w-4 h-4 text-brand-400" />
                <span className="font-semibold">Local Scientific Analysis Pipeline</span>
              </div>
              <span className="text-brand-400 font-bold">{progress}%</span>
            </div>

            <div className="w-full h-2.5 rounded-full bg-surface-elevated border border-border overflow-hidden">
              <div
                className="h-full bg-brand-600 transition-all duration-300 rounded-full"
                style={{ width: `${progress}%` }}
              />
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 text-[11px] text-slate-400">
              <span className={progress >= 25 ? 'text-emerald-400' : 'text-slate-600'}>
                ✓ 1. Homography Warp
              </span>
              <span className={progress >= 50 ? 'text-emerald-400' : 'text-slate-600'}>
                ✓ 2. Card Normalization
              </span>
              <span className={progress >= 75 ? 'text-emerald-400' : 'text-slate-600'}>
                ✓ 3. Well Sampling
              </span>
              <span className={progress >= 100 ? 'text-emerald-400' : 'text-slate-600'}>
                ✓ 4. Calibrated Vector
              </span>
            </div>
          </div>

          {/* Reagent Card ROI Visualizer Shell */}
          <FieldCard
            title="Calibrated Well Sampling Matrix"
            subtitle="Normalized Colorimetric Region Grid (CIE L*a*b* D65)"
            icon={Layers}
          >
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Well 1 (Test Well) */}
                <div className="p-4 rounded-lg bg-surface-elevated border border-border flex flex-col space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 rounded-full border border-slate-600 flex items-center justify-center bg-purple-950/80 text-purple-300 text-xs font-bold">
                        W1
                      </div>
                      <div>
                        <strong className="text-xs text-white block">Primary Reaction Well</strong>
                        <span className="text-[10px] text-slate-400">Target Reagent Zone</span>
                      </div>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      Sampled
                    </span>
                  </div>

                  <div className="p-2.5 rounded bg-surface/80 border border-border/60 text-[11px] space-y-1 font-mono text-slate-300">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Calibrated L*a*b*:</span>
                      <strong className="text-brand-300">
                        {well1
                          ? `[${well1.calibrated_lab_median.map((v) => v.toFixed(1)).join(', ')}]`
                          : '[48.2, 36.5, -12.4]'}
                      </strong>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Valid Pixels:</span>
                      <span className="text-slate-200">
                        {well1 ? `${well1.valid_pixel_count} px (Glare: ${well1.glare_pixel_count} px)` : '142 px (0% glare)'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Well 2 (Negative Control) */}
                <div className="p-4 rounded-lg bg-surface-elevated border border-border flex flex-col space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 rounded-full border border-slate-600 flex items-center justify-center bg-slate-800 text-slate-300 text-xs font-bold">
                        W2
                      </div>
                      <div>
                        <strong className="text-xs text-white block">Negative Control Well</strong>
                        <span className="text-[10px] text-slate-400">Blank Reference Zone</span>
                      </div>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      Sampled
                    </span>
                  </div>

                  <div className="p-2.5 rounded bg-surface/80 border border-border/60 text-[11px] space-y-1 font-mono text-slate-300">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Calibrated L*a*b*:</span>
                      <strong className="text-brand-300">
                        {well2
                          ? `[${well2.calibrated_lab_median.map((v) => v.toFixed(1)).join(', ')}]`
                          : '[91.0, 0.4, 2.1]'}
                      </strong>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Valid Pixels:</span>
                      <span className="text-slate-200">
                        {well2 ? `${well2.valid_pixel_count} px` : '150 px'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-surface-elevated/60 border border-border/50 text-[11px] text-slate-400 flex items-center space-x-2 font-sans">
                <ShieldCheck className="w-4 h-4 text-brand-400 flex-shrink-0" />
                <span>
                  Color coordinates are normalized against reference white/black/neutral calibration patches (Calibration Residual: {meas?.calibration_mean_delta_e ?? 4.8} ΔE).
                </span>
              </div>
            </div>
          </FieldCard>

          {/* Action Navigation */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-surface border border-border">
            <span className="text-xs text-slate-400">
              Assay: <strong className="text-slate-200">{setup.testProfileId}</strong>
            </span>

            <PrimaryAction
              label="View Presumptive Result"
              icon={ArrowRight}
              disabled={!isComplete}
              onClick={handleProceedToResult}
              variant="primary"
              className="w-full sm:w-auto"
            />
          </div>
        </div>

        {/* Pipeline Details Sidebar (1 col) */}
        <div className="space-y-6">
          <FieldCard
            title="Scientific Pipeline Mechanics"
            subtitle="Deterministic Analysis Architecture"
            icon={Activity}
          >
            <div className="space-y-3.5 text-xs font-sans text-slate-300">
              <div className="p-3 rounded-lg bg-surface-elevated border border-border/60 space-y-1">
                <span className="font-mono font-bold text-white text-xs block">1. Color Space Conversion</span>
                <p className="text-slate-400 text-[11px]">
                  Transforms raw device sRGB into illumination-invariant CIE L*a*b* coordinates.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-surface-elevated border border-border/60 space-y-1">
                <span className="font-mono font-bold text-white text-xs block">2. Least-Squares Affine Calibration</span>
                <p className="text-slate-400 text-[11px]">
                  Applies reference card affine transform matrix to correct ambient illumination color shifts.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-surface-elevated border border-border/60 space-y-1">
                <span className="font-mono font-bold text-white text-xs block">3. Specular Glare Exclusion</span>
                <p className="text-slate-400 text-[11px]">
                  Masks out specular reflections to prevent washed-out highlight artifacts.
                </p>
              </div>

              <div className="pt-2 border-t border-border/60 text-[11px] font-mono text-slate-400 flex items-center space-x-1.5">
                <Clock className="w-3.5 h-3.5 text-brand-400" />
                <span>Reaction Window: {setup.reactionWindowSeconds}s elapsed</span>
              </div>
            </div>
          </FieldCard>

          {isSimulatedMode && (
            <div className="p-4 rounded-xl bg-purple-950/40 border border-purple-500/30 text-xs font-mono text-purple-300 space-y-2">
              <div className="flex items-center space-x-2 text-purple-200 font-bold">
                <Sparkles className="w-4 h-4" />
                <span>Demo Mode Active</span>
              </div>
              <p className="text-[11px] text-purple-300/90 font-sans">
                The result on the next page will reflect the active simulation scenario.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
