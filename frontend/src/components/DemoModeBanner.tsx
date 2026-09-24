import React from 'react';
import { X } from 'lucide-react';
import { useWorkflowStore } from '../stores/useWorkflowStore';

export const DemoModeBanner: React.FC = () => {
  const { isSimulatedMode, selectedDemoScenario, resetToFieldMode } = useWorkflowStore();

  if (!isSimulatedMode) return null;

  return (
    <div className="bg-purple-950/70 border-b border-purple-500/40 px-4 py-2 text-xs font-mono text-purple-200 flex items-center justify-between">
      <div className="flex items-center space-x-2">
        <span className="px-2 py-0.5 rounded bg-purple-600 text-white font-bold text-[10px] tracking-wider uppercase">
          DEMO / SIMULATION ACTIVE
        </span>
        <span className="text-purple-300">
          Scenario: <strong className="text-white">{selectedDemoScenario}</strong> — Simulated metrics are NOT field evidence.
        </span>
      </div>
      <button
        onClick={resetToFieldMode}
        className="px-2 py-0.5 rounded hover:bg-purple-800 text-purple-200 hover:text-white transition-colors flex items-center space-x-1"
        title="Exit demo mode"
      >
        <span>Exit Simulation</span>
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};
