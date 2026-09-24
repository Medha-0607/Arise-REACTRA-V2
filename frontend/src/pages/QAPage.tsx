import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FieldCard } from '../components/FieldCard';
import { PresumptiveWarning } from '../components/PresumptiveWarning';
import { useWorkflowStore } from '../stores/useWorkflowStore';
import { DemoScenarioId, DemoScenario } from '../types/workflow';
import {
  Sparkles,
  RotateCcw,
  ArrowRight,
} from 'lucide-react';

export const QAPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    selectedDemoScenario,
    isSimulatedMode,
    activateDemoScenario,
    resetToFieldMode,
  } = useWorkflowStore();

  const scenarios: DemoScenario[] = [
    {
      id: 'VALID_CAPTURE',
      title: '1. Valid Capture & Optimal Quality',
      description: 'Optimal diffuse lighting, sharp edge variance, plane parallel alignment. Passes all quality gates.',
      qualityStatus: 'READY',
      resultType: 'PRESUMPTIVE_POSITIVE',
      isSimulated: true,
    },
    {
      id: 'GLARE_FAILURE',
      title: '2. Specular Glare Rejection',
      description: 'Point-source highlight exceeds maximum 3.0% reflection area. Triggering deterministic quality rejection.',
      qualityStatus: 'INVALID',
      resultType: 'INVALID_CAPTURE',
      isSimulated: true,
    },
    {
      id: 'BLUR_FAILURE',
      title: '3. Motion / Focus Blur Failure',
      description: 'Laplacian variance falls below 250 threshold. Automated prompt to stabilize and retake.',
      qualityStatus: 'RECAPTURE',
      resultType: 'INVALID_CAPTURE',
      isSimulated: true,
    },
    {
      id: 'UNDEREXPOSURE',
      title: '4. Underexposure & Low Dynamic Range',
      description: 'Histogram clipping in shadow region. Cautionary review and illumination adjustment prompt.',
      qualityStatus: 'REVIEW',
      resultType: 'INVALID_CAPTURE',
      isSimulated: true,
    },
    {
      id: 'INCONCLUSIVE_RESULT',
      title: '5. Inconclusive Reaction Decision Margin',
      description: 'Reaction color gradient falls within indeterminate distance margin between target and benign profile.',
      qualityStatus: 'READY',
      resultType: 'INCONCLUSIVE',
      isSimulated: true,
    },
    {
      id: 'PRESUMPTIVE_POSITIVE',
      title: '6. Presumptive Positive Indication',
      description: 'Colorimetric shift matches profile reaction criteria. Explicit non-definitive match disclaimer.',
      qualityStatus: 'READY',
      resultType: 'PRESUMPTIVE_POSITIVE',
      isSimulated: true,
    },
    {
      id: 'PRESUMPTIVE_NEGATIVE',
      title: '7. Presumptive Negative Indication',
      description: 'No significant colorimetric shift observed within reaction timing window.',
      qualityStatus: 'READY',
      resultType: 'PRESUMPTIVE_NEGATIVE',
      isSimulated: true,
    },
    {
      id: 'INVALID_CAPTURE',
      title: '8. Invalid Measurement Pre-Gating',
      description: 'Simulates strict barrier preventing defective measurements from entering the classifier.',
      qualityStatus: 'INVALID',
      resultType: 'INVALID_CAPTURE',
      isSimulated: true,
    },
    {
      id: 'VERIFY_SUCCESS',
      title: '9. Evidence Verification Success',
      description: 'Valid Ed25519 signature and SHA-256 canonical digest verification demonstration.',
      qualityStatus: 'READY',
      resultType: 'PRESUMPTIVE_POSITIVE',
      isSimulated: true,
    },
    {
      id: 'VERIFY_FAILURE',
      title: '10. Evidence Verification Failure (Tamper Detected)',
      description: 'Simulates payload digest mismatch indicating corrupted or modified envelope record.',
      qualityStatus: 'INVALID',
      resultType: 'INVALID_CAPTURE',
      isSimulated: true,
    },
  ];

  const handleSelectScenario = (scenarioId: DemoScenarioId) => {
    activateDemoScenario(scenarioId);
  };

  const handleLaunchWorkflow = (path: string) => {
    navigate(path);
  };

  return (
    <div className="space-y-6 font-mono">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-purple-400" />
            <span>QA Simulation Lab & UI Test Rig</span>
          </h1>
          <p className="text-xs text-slate-400">
            Controlled environment for evaluating UI states and workflow paths across 10 defined scenarios.
          </p>
        </div>

        {isSimulatedMode && (
          <button
            type="button"
            onClick={resetToFieldMode}
            className="px-3.5 py-1.5 rounded-lg bg-surface-elevated hover:bg-slate-700 text-purple-300 border border-purple-500/40 text-xs flex items-center space-x-1.5 transition-colors self-start sm:self-auto"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset to Field Mode</span>
          </button>
        )}
      </div>

      <div className="p-4 rounded-xl bg-purple-950/50 border border-purple-500/40 text-xs text-purple-200 font-mono space-y-1.5">
        <div className="flex items-center space-x-2 font-bold text-purple-300 uppercase tracking-wider">
          <Sparkles className="w-4 h-4" />
          <span>Strict Simulation Boundary Policy</span>
        </div>
        <p className="text-[11px] text-purple-300/90 font-sans leading-relaxed">
          This screen is the <strong className="text-white">ONLY</strong> designated area where mock scenarios are selectable.
          All simulated states carry persistent <code>DEMO / SIMULATION</code> banners to ensure simulated metrics never masquerade as real field evidence.
        </p>
      </div>

      <PresumptiveWarning variant="banner" className="rounded-lg" />

      {/* 10 Scenarios Grid */}
      <FieldCard
        title="10 Controlled Demonstration Scenarios"
        subtitle="Select a scenario to configure presentation state"
        icon={Sparkles}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {scenarios.map((sc) => {
            const isSelected = selectedDemoScenario === sc.id;

            return (
              <div
                key={sc.id}
                className={`p-4 rounded-xl border transition-all flex flex-col justify-between space-y-3 text-xs ${
                  isSelected
                    ? 'bg-purple-950/40 border-purple-500 ring-1 ring-purple-500'
                    : 'bg-surface-elevated/70 border-border hover:border-slate-600'
                }`}
              >
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-white text-xs">{sc.title}</h3>
                    {isSelected && (
                      <span className="px-2 py-0.5 rounded bg-purple-600 text-white text-[9px] font-bold">
                        ACTIVE
                      </span>
                    )}
                  </div>
                  <p className="text-slate-400 text-[11px] font-sans leading-relaxed">{sc.description}</p>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-border/50 text-[10px] text-slate-400">
                  <span>Guard: <strong className="text-slate-300">{sc.qualityStatus}</strong></span>
                  <span>Result: <strong className="text-slate-300">{sc.resultType}</strong></span>
                  <button
                    type="button"
                    onClick={() => handleSelectScenario(sc.id)}
                    className={`px-3 py-1.5 rounded text-xs font-mono font-bold transition-colors ${
                      isSelected
                        ? 'bg-purple-600 text-white'
                        : 'bg-surface hover:bg-slate-700 text-slate-300 border border-slate-700'
                    }`}
                  >
                    {isSelected ? 'Applied' : 'Apply State'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </FieldCard>

      {/* Jump to Workflow Screen Controls */}
      {isSimulatedMode && (
        <FieldCard
          title="Inspect Active Scenario in Workflow Screens"
          subtitle="Navigate to preview UI rendering under selected simulation"
          icon={ArrowRight}
        >
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <button
              type="button"
              onClick={() => handleLaunchWorkflow('/check')}
              className="p-3 rounded-lg bg-surface-elevated hover:bg-slate-700 border border-border text-slate-200 text-center transition-colors"
            >
              1. Check Screen
            </button>
            <button
              type="button"
              onClick={() => handleLaunchWorkflow('/analysis')}
              className="p-3 rounded-lg bg-surface-elevated hover:bg-slate-700 border border-border text-slate-200 text-center transition-colors"
            >
              2. Analysis Screen
            </button>
            <button
              type="button"
              onClick={() => handleLaunchWorkflow('/result')}
              className="p-3 rounded-lg bg-surface-elevated hover:bg-slate-700 border border-border text-slate-200 text-center transition-colors"
            >
              3. Result Screen
            </button>
            <button
              type="button"
              onClick={() => handleLaunchWorkflow('/evidence')}
              className="p-3 rounded-lg bg-surface-elevated hover:bg-slate-700 border border-border text-slate-200 text-center transition-colors"
            >
              4. Evidence Screen
            </button>
          </div>
        </FieldCard>
      )}
    </div>
  );
};
