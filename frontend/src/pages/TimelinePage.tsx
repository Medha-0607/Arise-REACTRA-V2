import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkflowStore } from '../stores/useWorkflowStore';
import { apiClient } from '../services/apiClient';
import { StepIndicator } from '../components/StepIndicator';
import { TimelineItem } from '../components/TimelineItem';
import { FieldCard } from '../components/FieldCard';
import { PrimaryAction } from '../components/PrimaryAction';
import { PresumptiveWarning } from '../components/PresumptiveWarning';
import { AuditEventItem } from '../types/api';
import {
  History,
  Home,
  FlaskConical,
  Sparkles,
  Download,
  Loader2,
} from 'lucide-react';

export const TimelinePage: React.FC = () => {
  const navigate = useNavigate();
  const { setup, activeSessionId, isSimulatedMode } = useWorkflowStore();
  const [realEvents, setRealEvents] = useState<AuditEventItem[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    if (activeSessionId && !isSimulatedMode) {
      setLoading(true);
      apiClient
        .getSessionTimeline(activeSessionId)
        .then((res) => {
          if (isMounted) {
            setRealEvents(res.events);
            setLoading(false);
          }
        })
        .catch(() => {
          if (isMounted) {
            setLoading(false);
          }
        });
    }
    return () => {
      isMounted = false;
    };
  }, [activeSessionId, isSimulatedMode]);

  const demoEvents = [
    {
      timestamp: '2026-09-23 00:15:02 UTC',
      title: '1. Test Session Initialized',
      description: `Operator ${setup.operatorBadge || 'OFC-8492'} created test session for Case Event #${setup.caseEventId || 'CAS-2026-001'}. Target assay: ${setup.testProfileId}.`,
      status: 'COMPLETED' as const,
      actor: setup.operatorBadge || 'OFC-8492',
    },
    {
      timestamp: '2026-09-23 00:15:35 UTC',
      title: '2. Optical Capture Frame Acquired',
      description: 'Reference card placed flat; direct optical capture frame buffered in secure memory.',
      status: 'COMPLETED' as const,
      actor: 'Local Camera Driver',
    },
    {
      timestamp: '2026-09-23 00:15:37 UTC',
      title: '3. Adaptive Quality Guard Passed',
      description: 'Laplace blur variance (482), dynamic range exposure, and glare filters satisfied. Zero rejection triggers.',
      status: 'COMPLETED' as const,
      actor: 'Local CV Guard Engine',
    },
    {
      timestamp: '2026-09-23 00:15:39 UTC',
      title: '4. Calibrated Well Sampling Executed',
      description: 'Homography perspective warp mapped grid coordinates; normalized CIE LAB color vectors extracted.',
      status: 'COMPLETED' as const,
      actor: 'Local Colorimetry Engine',
    },
    {
      timestamp: '2026-09-23 00:15:40 UTC',
      title: '5. Presumptive Interpretation Generated',
      description: 'Calibrated Delta-E distance matched reference curve. Explicit presumptive disclaimer attached.',
      status: 'COMPLETED' as const,
      actor: 'Presumptive Rule Engine',
    },
    {
      timestamp: '2026-09-23 00:15:42 UTC',
      title: '6. Cryptographic Evidence Envelope Sealed',
      description: 'Canonical JSON record digested via SHA-256 and digitally signed with device-bound Ed25519 private key.',
      status: 'COMPLETED' as const,
      actor: 'Cryptographic Subsystem',
    },
    {
      timestamp: '2026-09-23 00:15:45 UTC',
      title: '7. Laboratory Referral Package Ready',
      description: 'Tamper-evident archive prepared for secure chain-of-custody transfer.',
      status: 'COMPLETED' as const,
      actor: 'Evidence Exporter',
    },
  ];

  const hasRealEvents = realEvents && realEvents.length > 0;

  return (
    <div className="space-y-6 font-mono">
      <StepIndicator currentStep="timeline" />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            8. Chronological Evidence Audit Timeline
          </h1>
          <p className="text-xs text-slate-400">
            Immutable monotonic sequence of field actions, quality guard checks, and cryptographic sealing events.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          {hasRealEvents ? (
            <span className="px-2.5 py-1 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-500/30 flex items-center space-x-1 font-bold">
              <span>AUTHORITATIVE SESSION STREAM</span>
            </span>
          ) : (
            <span className="px-2.5 py-1 rounded bg-purple-950/60 text-purple-300 border border-purple-500/30 flex items-center space-x-1 font-bold">
              <Sparkles className="w-3 h-3" />
              <span>DEMO TIMELINE DATASET</span>
            </span>
          )}
        </div>
      </div>

      <PresumptiveWarning variant="banner" className="rounded-lg" />

      {/* Timeline Stream Container */}
      <FieldCard
        title={hasRealEvents ? `Session Audit Stream (${realEvents.length} events)` : 'Session Event Sequence'}
        subtitle="Cryptographically Chained Monotonic Audit Stream"
        icon={History}
      >
        <div className="pt-2">
          {loading ? (
            <div className="py-8 flex items-center justify-center space-x-2 text-slate-400 text-xs">
              <Loader2 className="w-4 h-4 animate-spin text-brand-400" />
              <span>Loading authoritative audit trail...</span>
            </div>
          ) : hasRealEvents ? (
            realEvents.map((evt, idx) => {
              let desc = `State transition: ${evt.from_state || 'INITIAL'} → ${evt.to_state || 'UNKNOWN'}`;
              if (evt.event_payload) {
                if (evt.event_type === 'PROCEDURAL_CONTEXT_UPDATED') {
                  const fields = evt.event_payload.updated_fields as string[] | undefined;
                  desc = `Procedural metadata recorded: ${fields ? fields.join(', ') : 'Updated'}`;
                } else if (evt.event_type === 'SAFEGUARD_RECORDED') {
                  desc = `Statutory safeguard metadata logged: ${JSON.stringify(evt.event_payload)}`;
                } else {
                  desc = typeof evt.event_payload === 'string'
                    ? evt.event_payload
                    : JSON.stringify(evt.event_payload);
                }
              }
              return (
                <TimelineItem
                  key={evt.event_id}
                  timestamp={new Date(evt.event_timestamp_utc).toUTCString()}
                  title={`${idx + 1}. ${evt.event_type.replace(/_/g, ' ')}`}
                  description={desc}
                  status="COMPLETED"
                  actor={evt.actor_id || 'Device Subsystem'}
                  isLast={idx === realEvents.length - 1}
                />
              );
            })
          ) : (
            demoEvents.map((evt, idx) => (
              <TimelineItem
                key={evt.title}
                timestamp={evt.timestamp}
                title={evt.title}
                description={evt.description}
                status={evt.status}
                actor={evt.actor}
                isLast={idx === demoEvents.length - 1}
              />
            ))
          )}
        </div>
      </FieldCard>

      {/* Final Action Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-surface border border-border">
        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <button
            type="button"
            onClick={() => navigate('/referral')}
            className="flex-1 sm:flex-initial px-4 py-2.5 rounded-lg bg-surface-elevated hover:bg-slate-700 text-slate-300 text-xs font-mono border border-border transition-colors flex items-center justify-center space-x-2"
          >
            <FlaskConical className="w-3.5 h-3.5 text-cyan-400" />
            <span>Prepare Lab Referral</span>
          </button>
          <button
            type="button"
            className="flex-1 sm:flex-initial px-4 py-2.5 rounded-lg bg-surface-elevated hover:bg-slate-700 text-slate-300 text-xs font-mono border border-border transition-colors flex items-center justify-center space-x-2"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Audit Trail</span>
          </button>
        </div>

        <PrimaryAction
          label="Return to Field Console"
          icon={Home}
          onClick={() => navigate('/home')}
          variant="primary"
          className="w-full sm:w-auto"
        />
      </div>
    </div>
  );
};

