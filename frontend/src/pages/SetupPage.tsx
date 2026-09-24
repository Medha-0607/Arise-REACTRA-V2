import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkflowStore } from '../stores/useWorkflowStore';
import { apiClient } from '../services/apiClient';
import { AssayProfile, ProceduralContextResponse, ProceduralUpdateRequest } from '../types/api';
import { StepIndicator } from '../components/StepIndicator';
import { FieldCard } from '../components/FieldCard';
import { PrimaryAction } from '../components/PrimaryAction';
import { PresumptiveWarning } from '../components/PresumptiveWarning';
import { ProceduralContextCard } from '../components/ProceduralContextCard';
import {
  UserCheck,
  Sliders,
  Camera,
  Clock,
  ArrowRight,
  Info,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  FileCheck2,
} from 'lucide-react';

export const SetupPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    setup,
    updateSetup,
    setStep,
    activeSessionId,
    authoritativeState,
    activeSessionDetail,
    setActiveSession,
    setLatestProceduralContext,
    apiError,
    setApiError,
    isLoading,
    setIsLoading,
  } = useWorkflowStore();

  const [profiles, setProfiles] = useState<AssayProfile[]>([]);
  const [transitionMsg, setTransitionMsg] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'session' | 'procedural'>('session');
  const [proceduralData, setProceduralData] = useState<ProceduralContextResponse | null>(null);
  const [proceduralFormData, setProceduralFormData] = useState<ProceduralUpdateRequest>({
    search_context_type: 'VEHICLE_SEARCH',
    panchnama_memo_ref_no: '',
    witness_1_name: '',
    witness_1_contact: '',
    witness_2_name: '',
    witness_2_contact: '',
    section_50_applicable: false,
    section_50_option_informed: false,
    section_50_choice: 'NOT_APPLICABLE',
    section_50_officer_name: '',
    section_50_officer_designation: '',
    section_52a_inventory_prepared: false,
    section_52a_application_ref: '',
    section_52a_magistrate_court: '',
    sample_drawal_status: 'PENDING',
    magistrate_cert_status: 'PENDING',
    representative_sample_id: '',
    sample_seal_identifier: '',
    section_57_report_status: 'NOT_SUBMITTED',
    section_57_report_ref: '',
    section_57_submitted_to: '',
    kit_lot_number: '',
    kit_expiry_date: '',
    officer_notes: '',
  });

  useEffect(() => {
    let isMounted = true;
    const loadProfiles = async () => {
      try {
        const data = await apiClient.listProfiles();
        if (isMounted && data.length > 0) {
          setProfiles(data);
        }
      } catch {
        // Fallback to standard hardcoded options if server unreachable in dev
      }
    };
    loadProfiles();

    const loadProcedural = async () => {
      if (activeSessionId) {
        try {
          const proc = await apiClient.getProceduralContext(activeSessionId);
          if (isMounted) {
            setProceduralData(proc);
            setProceduralFormData(proc);
            setLatestProceduralContext(proc);
          }
        } catch {
          // ignore if new session
        }
      }
    };
    loadProcedural();

    return () => {
      isMounted = false;
    };
  }, [activeSessionId, setLatestProceduralContext]);

  const handleCreateSession = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setApiError(null);
    setTransitionMsg(null);

    try {
      const session = await apiClient.createSession({
        case_id: setup.caseEventId,
        operator_id: setup.operatorBadge,
        device_enrollment_id: localStorage.getItem('reactra_device_id') || 'DEV-FIELD-UNIT-01',
        is_demo_mode: false,
        agency_id: setup.agencyDepartment || undefined,
        profile_id: setup.testProfileId,
        reference_card_id: setup.referenceCardId,
        capture_mode: setup.captureMode,
        location_provenance: setup.locationProvenance || undefined,
        notes: 'Session created via Field Setup UI',
      });

      // Persist procedural context if entered
      try {
        const updatedProc = await apiClient.updateProceduralContext(session.id, proceduralFormData);
        setProceduralData(updatedProc);
        setLatestProceduralContext(updatedProc);
      } catch (procErr) {
        console.warn('Procedural metadata persistence note:', procErr);
      }

      setActiveSession(session);
      setStep('capture');
      navigate('/capture');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to initialize session';
      setApiError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveProcedural = async (data: ProceduralUpdateRequest) => {
    setProceduralFormData(data);
    if (!activeSessionId) {
      // Stored locally in form state until session initialization
      return;
    }
    setIsLoading(true);
    setApiError(null);
    try {
      const updated = await apiClient.updateProceduralContext(activeSessionId, data);
      setProceduralData(updated);
      setLatestProceduralContext(updated);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to update procedural context';
      setApiError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const isSealed = authoritativeState === 'EVIDENCE_SEALED' || authoritativeState === 'ARCHIVED';

  return (
    <div className="space-y-6 font-mono">
      {/* Workflow Step Tracker */}
      <StepIndicator currentStep="setup" />

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            1. Test Session Setup & Procedural Context
          </h1>
          <p className="text-xs text-slate-400">
            Define operator identity, target assay profile, reference card, and statutory procedural safeguards.
          </p>
        </div>
      </div>

      <PresumptiveWarning variant="banner" className="rounded-lg" />

      {/* Tab Selector */}
      <div className="flex border-b border-border/80 gap-2">
        <button
          type="button"
          onClick={() => setActiveTab('session')}
          className={`px-4 py-2.5 text-xs font-semibold rounded-t-lg transition-colors flex items-center space-x-2 border-t border-x ${
            activeTab === 'session'
              ? 'bg-surface text-brand-400 border-border border-b-transparent -mb-px'
              : 'bg-transparent text-slate-400 border-transparent hover:text-slate-200'
          }`}
        >
          <Sliders className="w-3.5 h-3.5" />
          <span>Session Parameters</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('procedural')}
          className={`px-4 py-2.5 text-xs font-semibold rounded-t-lg transition-colors flex items-center space-x-2 border-t border-x ${
            activeTab === 'procedural'
              ? 'bg-surface text-brand-400 border-border border-b-transparent -mb-px'
              : 'bg-transparent text-slate-400 border-transparent hover:text-slate-200'
          }`}
        >
          <FileCheck2 className="w-3.5 h-3.5" />
          <span>Procedural Context & Safeguards (§50 / §52A / §57)</span>
          {activeSessionId && (
            <span className="ml-1 px-1.5 py-0.2 rounded text-[9px] bg-brand-500/20 text-brand-300">
              Live
            </span>
          )}
        </button>
      </div>

      {/* Authoritative State Banner if session is active */}
      {activeSessionDetail && (
        <div className="p-4 rounded-lg bg-surface-elevated border border-brand-500/30 text-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-brand-400 flex-shrink-0" />
            <div>
              <span className="text-slate-400">Authoritative Session: </span>
              <span className="text-brand-300 font-bold">{activeSessionDetail.session_id}</span>
              <span className="ml-2 px-2 py-0.5 rounded text-[10px] font-bold bg-brand-500/20 text-brand-400 border border-brand-500/30">
                STATE: {authoritativeState}
              </span>
            </div>
          </div>
          <span className="text-[11px] text-slate-400 font-mono">
            Active Offline Session
          </span>
        </div>
      )}

      {/* Success Notification */}
      {transitionMsg && (
        <div className="p-3 rounded-lg bg-emerald-950/40 border border-emerald-800/50 text-xs text-emerald-300 flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>{transitionMsg}</span>
        </div>
      )}

      {/* Error Notification */}
      {apiError && (
        <div className="p-3.5 rounded-lg bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 flex items-center justify-between gap-3">
          <div className="flex items-center space-x-2.5">
            <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <div>
              <strong className="block font-semibold">Validation / Initialization Error</strong>
              <span className="text-rose-200/90">{apiError}</span>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setApiError(null)}
            className="text-xs text-rose-400 underline hover:text-rose-200"
          >
            Dismiss
          </button>
        </div>
      )}

      {activeTab === 'procedural' ? (
        <div className="space-y-4">
          <ProceduralContextCard
            initialData={proceduralData || proceduralFormData}
            isSealed={isSealed}
            onChange={(updated) => setProceduralFormData(updated)}
            onSave={activeSessionId ? handleSaveProcedural : undefined}
            isLoading={isLoading}
          />
          <div className="p-4 rounded-xl bg-surface border border-border flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-xs text-slate-400 font-mono">
              <span>Procedural safeguard entries remain preserved in local session state.</span>
            </div>
            <PrimaryAction
              label={isLoading ? 'Initializing Session...' : 'Initialize Session & Proceed'}
              icon={isLoading ? Loader2 : ArrowRight}
              onClick={() => handleCreateSession()}
              disabled={isLoading || !setup.caseEventId || !setup.operatorBadge}
              className="w-full sm:w-auto"
            />
          </div>
        </div>
      ) : (
        <form onSubmit={handleCreateSession} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Section 1: Operator & Case Provenance */}
          <FieldCard
            title="Operator & Case Provenance"
            subtitle="Immutable Audit Record Metadata"
            icon={UserCheck}
          >
            <div className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">
                  Operator Badge / Identifier <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. OFC-8492"
                  value={setup.operatorBadge}
                  onChange={(e) => updateSetup({ operatorBadge: e.target.value })}
                  className="w-full bg-surface-elevated border border-border rounded-lg px-3.5 py-2.5 text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-brand-500 text-xs"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">
                  Agency / Department
                </label>
                <input
                  type="text"
                  placeholder="e.g. Metro Narcotics Enforcement Taskforce"
                  value={setup.agencyDepartment}
                  onChange={(e) => updateSetup({ agencyDepartment: e.target.value })}
                  className="w-full bg-surface-elevated border border-border rounded-lg px-3.5 py-2.5 text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-brand-500 text-xs"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">
                  Case / Incident Event ID <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. CAS-2026-0923-01A"
                  value={setup.caseEventId}
                  onChange={(e) => updateSetup({ caseEventId: e.target.value })}
                  className="w-full bg-surface-elevated border border-border rounded-lg px-3.5 py-2.5 text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-brand-500 text-xs"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">
                  Field Location Provenance
                </label>
                <input
                  type="text"
                  placeholder="e.g. Sector 4 Checkpoint (No synthetic GPS fabricated)"
                  value={setup.locationProvenance}
                  onChange={(e) => updateSetup({ locationProvenance: e.target.value })}
                  className="w-full bg-surface-elevated border border-border rounded-lg px-3.5 py-2.5 text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-brand-500 text-xs"
                />
                <span className="text-[10px] text-slate-400 mt-1 block">
                  Location is logged strictly via operator declaration or hardware GPS when permitted.
                </span>
              </div>
            </div>
          </FieldCard>

          {/* Section 2: Assay Profile & Hardware Calibration */}
          <div className="space-y-6">
            <FieldCard
              title="Assay Profile & Reference Card"
              subtitle="Reagent Curve Specifications"
              icon={Sliders}
            >
              <div className="space-y-4 text-xs">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1.5">
                    Target Reagent Profile
                  </label>
                  <select
                    value={setup.testProfileId}
                    onChange={(e) => updateSetup({ testProfileId: e.target.value })}
                    className="w-full bg-surface-elevated border border-border rounded-lg px-3.5 py-2.5 text-slate-100 focus:outline-none focus:border-brand-500 text-xs"
                  >
                    {profiles.length > 0 ? (
                      profiles.map((p) => (
                        <option key={p.profile_id} value={p.profile_id}>
                          {p.name} (v{p.profile_version})
                        </option>
                      ))
                    ) : (
                      <>
                        <option value="marquis-standard-v1">Marquis Reagent Profile (v1.0.0)</option>
                        <option value="scott-cocaine-v1">Scott Reagent Profile (v1.0.0)</option>
                        <option value="duquenois-cannabis-v1">Duquenois-Levine Profile (v1.0.0)</option>
                        <option value="mecke-opiates-v1">Mecke Reagent Profile (v1.0.0)</option>
                      </>
                    )}
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1.5">
                    Reference Card Standard
                  </label>
                  <select
                    value={setup.referenceCardId}
                    onChange={(e) => updateSetup({ referenceCardId: e.target.value })}
                    className="w-full bg-surface-elevated border border-border rounded-lg px-3.5 py-2.5 text-slate-100 focus:outline-none focus:border-brand-500 text-xs"
                  >
                    <option value="ref-card-grid-3x2">Standard Multi-Well Grid (3x2 Wells + Color Checker)</option>
                    <option value="ref-card-single-vial">Legacy Single-Vial Field Pouch Standard</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1.5">
                    Reaction Window Limit (Seconds)
                  </label>
                  <div className="flex items-center space-x-3">
                    <Clock className="w-4 h-4 text-brand-400 flex-shrink-0" />
                    <input
                      type="number"
                      min="5"
                      max="300"
                      value={setup.reactionWindowSeconds}
                      onChange={(e) => updateSetup({ reactionWindowSeconds: Number(e.target.value) })}
                      className="w-28 bg-surface-elevated border border-border rounded-lg px-3 py-2 text-slate-100 text-xs"
                    />
                    <span className="text-[11px] text-slate-400">Recommended: 30s to 60s</span>
                  </div>
                </div>
              </div>
            </FieldCard>

            <FieldCard
              title="Capture Acquisition Mode"
              subtitle="Explicit Provenance Classification"
              icon={Camera}
            >
              <div className="space-y-3 text-xs">
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => updateSetup({ captureMode: 'LIVE_CAMERA' })}
                    className={`p-3 rounded-lg border text-left flex flex-col justify-between transition-colors ${
                      setup.captureMode === 'LIVE_CAMERA'
                        ? 'bg-brand-600/20 border-brand-500 text-white'
                        : 'bg-surface-elevated border-border text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <span className="font-bold text-xs">LIVE CAMERA</span>
                    <span className="text-[10px] text-slate-400 mt-1">Live field camera viewport</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => updateSetup({ captureMode: 'IMPORTED_IMAGE' })}
                    className={`p-3 rounded-lg border text-left flex flex-col justify-between transition-colors ${
                      setup.captureMode === 'IMPORTED_IMAGE'
                        ? 'bg-amber-600/20 border-amber-500 text-white'
                        : 'bg-surface-elevated border-border text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <span className="font-bold text-xs">IMPORTED IMAGE</span>
                    <span className="text-[10px] text-amber-400/90 mt-1">Explicitly labelled import</span>
                  </button>
                </div>
                <div className="p-2.5 rounded bg-surface-elevated/60 border border-border/50 text-[11px] text-slate-400 flex items-center space-x-2">
                  <Info className="w-3.5 h-3.5 text-brand-400 flex-shrink-0" />
                  <span>
                    Non-negotiable rule: Imported images are permanently tagged with <code>IMPORTED_IMAGE</code> provenance.
                  </span>
                </div>
              </div>
            </FieldCard>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-border">
          <div className="text-xs text-slate-400 font-mono">
            <span>Configuring Session: </span>
            <strong className="text-slate-200">
              {setup.caseEventId || 'Awaiting Event ID'}
            </strong>
          </div>

          <PrimaryAction
            label={isLoading ? 'Creating Session...' : 'Initialize Session & Proceed'}
            icon={isLoading ? Loader2 : ArrowRight}
            type="submit"
            disabled={isLoading}
            className="w-full sm:w-auto"
          />
        </div>
      </form>
      )}
    </div>
  );
};
