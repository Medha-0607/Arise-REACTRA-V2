import {
  HealthResponse,
  AssayProfile,
  SessionCreateRequest,
  SessionTransitionRequest,
  SessionDetailResponse,
  SessionSummaryResponse,
  SessionTimelineResponse,
  MeasurementExecuteRequest,
  MeasurementExecutionOutcomeData,
  ClassificationResponse,
  EvidenceSealResponse,
  EvidenceVerifyRequest,
  EvidenceVerifyResponse,
  ProceduralUpdateRequest,
  ProceduralContextResponse,
  ReferralSummaryResponse,
  CustodyCreateRequest,
  CustodyEventResponse,
  ReferralExportResponse,
  ChainVerificationResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options?.headers,
    };

    try {
      const response = await fetch(url, { ...options, headers });
      if (!response.ok) {
        let errDetail = `API Error ${response.status}: ${response.statusText}`;
        try {
          const body = await response.json();
          if (body && body.detail) {
            errDetail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
          }
        } catch {
          // ignore non-json error bodies
        }
        throw new Error(errDetail);
      }
      return (await response.json()) as T;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Unknown network error';
      throw new Error(message);
    }
  }

  async getHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  async listProfiles(): Promise<AssayProfile[]> {
    return this.request<AssayProfile[]>('/profiles');
  }

  async createSession(data: SessionCreateRequest): Promise<SessionDetailResponse> {
    return this.request<SessionDetailResponse>('/sessions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getSession(sessionId: string): Promise<SessionDetailResponse> {
    return this.request<SessionDetailResponse>(`/sessions/${sessionId}`);
  }

  async listSessions(params?: {
    skip?: number;
    limit?: number;
    operator_id?: string;
    status?: string;
    case_id?: string;
  }): Promise<SessionSummaryResponse[]> {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.set('skip', String(params.skip));
    if (params?.limit !== undefined) searchParams.set('limit', String(params.limit));
    if (params?.operator_id) searchParams.set('operator_id', params.operator_id);
    if (params?.status) searchParams.set('status', params.status);
    if (params?.case_id) searchParams.set('case_id', params.case_id);
    const queryString = searchParams.toString();
    return this.request<SessionSummaryResponse[]>(`/sessions${queryString ? `?${queryString}` : ''}`);
  }

  async transitionSession(
    sessionId: string,
    data: SessionTransitionRequest
  ): Promise<SessionDetailResponse> {
    return this.request<SessionDetailResponse>(`/sessions/${sessionId}/transition`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getSessionTimeline(sessionId: string): Promise<SessionTimelineResponse> {
    return this.request<SessionTimelineResponse>(`/sessions/${sessionId}/timeline`);
  }

  async measureSession(
    sessionId: string,
    data: MeasurementExecuteRequest
  ): Promise<MeasurementExecutionOutcomeData> {
    return this.request<MeasurementExecutionOutcomeData>(`/sessions/${sessionId}/measure`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async classifySession(sessionId: string): Promise<ClassificationResponse> {
    return this.request<ClassificationResponse>(`/sessions/${sessionId}/classify`, {
      method: 'POST',
    });
  }

  async sealSession(sessionId: string): Promise<EvidenceSealResponse> {
    return this.request<EvidenceSealResponse>(`/sessions/${sessionId}/seal`, {
      method: 'POST',
    });
  }

  async verifyEvidence(data: EvidenceVerifyRequest): Promise<EvidenceVerifyResponse> {
    return this.request<EvidenceVerifyResponse>('/evidence/verify', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getProceduralContext(sessionId: string): Promise<ProceduralContextResponse> {
    return this.request<ProceduralContextResponse>(`/sessions/${sessionId}/procedural`);
  }

  async updateProceduralContext(
    sessionId: string,
    data: ProceduralUpdateRequest
  ): Promise<ProceduralContextResponse> {
    return this.request<ProceduralContextResponse>(`/sessions/${sessionId}/procedural`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async getReferralSummary(sessionId: string): Promise<ReferralSummaryResponse> {
    return this.request<ReferralSummaryResponse>(`/sessions/${sessionId}/referral-summary`);
  }

  async getReferralExport(sessionId: string): Promise<ReferralExportResponse> {
    return this.request<ReferralExportResponse>(`/sessions/${sessionId}/referral/export`);
  }

  async recordCustodyHandoff(
    sessionId: string,
    data: CustodyCreateRequest
  ): Promise<CustodyEventResponse> {
    return this.request<CustodyEventResponse>(`/sessions/${sessionId}/custody`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCustodyHistory(sessionId: string): Promise<CustodyEventResponse[]> {
    return this.request<CustodyEventResponse[]>(`/sessions/${sessionId}/custody`);
  }

  async verifyEvidenceChain(deviceEnrollmentId?: string): Promise<ChainVerificationResponse> {
    const query = deviceEnrollmentId ? `?device_enrollment_id=${encodeURIComponent(deviceEnrollmentId)}` : '';
    return this.request<ChainVerificationResponse>(`/evidence/chain/verify${query}`);
  }
}

export const apiClient = new ApiClient();

