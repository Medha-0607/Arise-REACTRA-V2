import { create } from 'zustand';
import {
  WorkflowStep,
  ResultType,
  QualityStatus,
  SetupFormState,
  DemoScenarioId,
} from '../types/workflow';
import {
  SessionDetailResponse,
  MeasurementExecutionOutcomeData,
  ClassificationResponse,
  EvidenceSealResponse,
  ProceduralContextResponse,
} from '../types/api';

interface WorkflowState {
  currentStep: WorkflowStep;
  setup: SetupFormState;
  qualityStatus: QualityStatus;
  resultType: ResultType;
  selectedDemoScenario: DemoScenarioId | null;
  isSimulatedMode: boolean;
  
  // Authoritative Server Session State
  activeSessionId: string | null;
  authoritativeState: string | null;
  activeSessionDetail: SessionDetailResponse | null;
  apiError: string | null;
  isLoading: boolean;

  // Phase 3: Captured Image Buffer & Measurement Diagnostics
  capturedImageBase64: string | null;
  latestMeasurementOutcome: MeasurementExecutionOutcomeData | null;

  // Phase 4: Classification & Evidence Sealing Authoritative Outcomes
  latestClassificationOutcome: ClassificationResponse | null;
  latestEvidenceOutcome: EvidenceSealResponse | null;
  
  // Phase 5: Procedural Context
  latestProceduralContext: ProceduralContextResponse | null;
  
  // Actions
  setStep: (step: WorkflowStep) => void;
  updateSetup: (fields: Partial<SetupFormState>) => void;
  setQualityStatus: (status: QualityStatus) => void;
  setResultType: (result: ResultType) => void;
  setActiveSession: (session: SessionDetailResponse | null) => void;
  setAuthoritativeState: (state: string | null) => void;
  setApiError: (error: string | null) => void;
  setIsLoading: (loading: boolean) => void;
  setCapturedImageBase64: (img: string | null) => void;
  setLatestMeasurementOutcome: (outcome: MeasurementExecutionOutcomeData | null) => void;
  setLatestClassificationOutcome: (outcome: ClassificationResponse | null) => void;
  setLatestEvidenceOutcome: (outcome: EvidenceSealResponse | null) => void;
  setLatestProceduralContext: (context: ProceduralContextResponse | null) => void;
  activateDemoScenario: (scenarioId: DemoScenarioId) => void;
  resetToFieldMode: () => void;
}

const initialSetup: SetupFormState = {
  operatorBadge: 'OFC-8492',
  agencyDepartment: 'Metro Narcotics Enforcement Taskforce',
  caseEventId: 'CAS-2026-0923-01A',
  locationProvenance: 'Sector 4 Checkpoint (No synthetic GPS fabricated)',
  testProfileId: 'marquis-standard-v1',
  referenceCardId: 'ref-card-grid-3x2',
  captureMode: 'LIVE_CAMERA',
  reactionWindowSeconds: 30,
};

export const useWorkflowStore = create<WorkflowState>((set) => ({
  currentStep: 'home',
  setup: initialSetup,
  qualityStatus: 'CHECKING',
  resultType: 'PRESUMPTIVE_POSITIVE',
  selectedDemoScenario: null,
  isSimulatedMode: false,

  activeSessionId: null,
  authoritativeState: null,
  activeSessionDetail: null,
  apiError: null,
  isLoading: false,

  capturedImageBase64: null,
  latestMeasurementOutcome: null,
  latestClassificationOutcome: null,
  latestEvidenceOutcome: null,
  latestProceduralContext: null,

  setStep: (step) => set({ currentStep: step }),
  updateSetup: (fields) =>
    set((state) => ({ setup: { ...state.setup, ...fields } })),
  setQualityStatus: (status) => set({ qualityStatus: status }),
  setResultType: (result) => set({ resultType: result }),
  
  setActiveSession: (session) =>
    set({
      activeSessionDetail: session,
      activeSessionId: session ? (session.session_id || session.id) : null,
      authoritativeState: session ? session.status : null,
      apiError: null,
    }),
  setAuthoritativeState: (state) => set({ authoritativeState: state }),
  setApiError: (error) => set({ apiError: error }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  setCapturedImageBase64: (img) => set({ capturedImageBase64: img }),
  setLatestMeasurementOutcome: (outcome) =>
    set({
      latestMeasurementOutcome: outcome,
      authoritativeState: outcome ? outcome.session_status : null,
      qualityStatus: outcome
        ? (outcome.overall_quality_status === 'READY'
            ? 'READY'
            : outcome.overall_quality_status === 'RECAPTURE'
            ? 'RECAPTURE'
            : outcome.overall_quality_status === 'INVALID'
            ? 'INVALID'
            : 'REVIEW')
        : 'CHECKING',
    }),
  setLatestClassificationOutcome: (outcome) =>
    set({
      latestClassificationOutcome: outcome,
      resultType: outcome ? (outcome.outcome as ResultType) : 'PRESUMPTIVE_POSITIVE',
      authoritativeState: outcome ? outcome.session_status : null,
    }),
  setLatestEvidenceOutcome: (outcome) =>
    set({
      latestEvidenceOutcome: outcome,
    }),
  setLatestProceduralContext: (context) =>
    set({
      latestProceduralContext: context,
    }),

  activateDemoScenario: (scenarioId) => {
    switch (scenarioId) {
      case 'VALID_CAPTURE':
        set({
          selectedDemoScenario: scenarioId,
          isSimulatedMode: true,
          qualityStatus: 'READY',
          resultType: 'PRESUMPTIVE_POSITIVE',
        });
        break;
      case 'GLARE_FAILURE':
        set({
          selectedDemoScenario: scenarioId,
          isSimulatedMode: true,
          qualityStatus: 'INVALID',
          resultType: 'INVALID_CAPTURE',
        });
        break;
      case 'BLUR_FAILURE':
        set({
          selectedDemoScenario: scenarioId,
          isSimulatedMode: true,
          qualityStatus: 'RECAPTURE',
          resultType: 'INVALID_CAPTURE',
        });
        break;
      case 'UNDEREXPOSURE':
        set({
          selectedDemoScenario: scenarioId,
          isSimulatedMode: true,
          qualityStatus: 'REVIEW',
          resultType: 'INVALID_CAPTURE',
        });
        break;
      case 'INCONCLUSIVE_RESULT':
        set({
          selectedDemoScenario: scenarioId,
          isSimulatedMode: true,
          qualityStatus: 'READY',
          resultType: 'INCONCLUSIVE',
        });
        break;
      case 'PRESUMPTIVE_POSITIVE':
        set({
          selectedDemoScenario: scenarioId,
          isSimulatedMode: true,
          qualityStatus: 'READY',
          resultType: 'PRESUMPTIVE_POSITIVE',
        });
        break;
      case 'PRESUMPTIVE_NEGATIVE':
        set({
          selectedDemoScenario: scenarioId,
          isSimulatedMode: true,
          qualityStatus: 'READY',
          resultType: 'PRESUMPTIVE_NEGATIVE',
        });
        break;
      case 'INVALID_CAPTURE':
        set({
          selectedDemoScenario: scenarioId,
          isSimulatedMode: true,
          qualityStatus: 'INVALID',
          resultType: 'INVALID_CAPTURE',
        });
        break;
      case 'VERIFY_SUCCESS':
      case 'VERIFY_FAILURE':
        set({
          selectedDemoScenario: scenarioId,
          isSimulatedMode: true,
        });
        break;
      default:
        set({ selectedDemoScenario: null, isSimulatedMode: false });
    }
  },

  resetToFieldMode: () =>
    set({
      selectedDemoScenario: null,
      isSimulatedMode: false,
      qualityStatus: 'CHECKING',
      resultType: 'PRESUMPTIVE_POSITIVE',
      apiError: null,
      latestMeasurementOutcome: null,
    }),
}));
