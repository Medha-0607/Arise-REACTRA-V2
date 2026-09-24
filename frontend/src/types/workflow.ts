export type WorkflowStep =
  | 'home'
  | 'setup'
  | 'capture'
  | 'check'
  | 'analysis'
  | 'result'
  | 'evidence'
  | 'referral'
  | 'verify'
  | 'timeline';

export type ResultType =
  | 'PRESUMPTIVE_POSITIVE'
  | 'PRESUMPTIVE_NEGATIVE'
  | 'INCONCLUSIVE'
  | 'INVALID_CAPTURE';

export type QualityStatus = 'CHECKING' | 'READY' | 'REVIEW' | 'RECAPTURE' | 'INVALID';

export type CaptureSourceType = 'LIVE_CAMERA' | 'IMPORTED_IMAGE';

export interface SetupFormState {
  operatorBadge: string;
  agencyDepartment: string;
  caseEventId: string;
  locationProvenance: string;
  testProfileId: string;
  referenceCardId: string;
  captureMode: CaptureSourceType;
  reactionWindowSeconds: number;
}

export type DemoScenarioId =
  | 'VALID_CAPTURE'
  | 'GLARE_FAILURE'
  | 'BLUR_FAILURE'
  | 'UNDEREXPOSURE'
  | 'INCONCLUSIVE_RESULT'
  | 'PRESUMPTIVE_POSITIVE'
  | 'PRESUMPTIVE_NEGATIVE'
  | 'INVALID_CAPTURE'
  | 'VERIFY_SUCCESS'
  | 'VERIFY_FAILURE';

export interface DemoScenario {
  id: DemoScenarioId;
  title: string;
  description: string;
  qualityStatus: QualityStatus;
  resultType: ResultType;
  isSimulated: boolean;
}
