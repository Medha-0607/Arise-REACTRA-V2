import React, { useState } from 'react';
import { CustodyEventResponse, CustodyCreateRequest } from '../types/api';
import { apiClient } from '../services/apiClient';
import { UserCheck, ShieldCheck, Clock, PlusCircle, AlertCircle, CheckCircle2 } from 'lucide-react';

interface CustodyHandoffCardProps {
  sessionId: string;
  isSealed: boolean;
  operatorId: string;
  history: CustodyEventResponse[];
  onHandoffRecorded: (event: CustodyEventResponse) => void;
}

export const CustodyHandoffCard: React.FC<CustodyHandoffCardProps> = ({
  sessionId,
  isSealed,
  operatorId,
  history,
  onHandoffRecorded,
}) => {
  const [showForm, setShowForm] = useState(false);
  const [receiverName, setReceiverName] = useState('');
  const [receiverAgency, setReceiverAgency] = useState('State Forensic Science Laboratory');
  const [receiverBadge, setReceiverBadge] = useState('');
  const [packageSealVerified, setPackageSealVerified] = useState(true);
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!receiverName.trim()) {
      setError('Receiver Name is required.');
      return;
    }
    if (!receiverBadge.trim()) {
      setError('Receiver Badge / ID is required.');
      return;
    }
    if (!packageSealVerified) {
      setError('Package physical seal verification confirmation is required.');
      return;
    }

    setSubmitting(true);
    setError(null);
    setSuccessMsg(null);

    const payload: CustodyCreateRequest = {
      sender_operator_id: operatorId || 'OFC-OFFLINE',
      receiver_name: receiverName.trim(),
      receiver_agency: receiverAgency.trim(),
      receiver_badge_or_id: receiverBadge.trim(),
      package_seal_verified: packageSealVerified,
      notes: notes.trim() || undefined,
    };

    try {
      const recorded = await apiClient.recordCustodyHandoff(sessionId, payload);
      onHandoffRecorded(recorded);
      setSuccessMsg('Officer recorded custody handoff successfully.');
      setReceiverName('');
      setReceiverBadge('');
      setNotes('');
      setShowForm(false);
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to record custody handoff';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-4 rounded-xl bg-surface-elevated border border-border space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-border/60 pb-3">
        <div className="flex items-center space-x-2">
          <UserCheck className="w-4 h-4 text-brand-400" />
          <span className="font-bold text-white text-sm">Multi-Party Custody Handoff</span>
        </div>
        {isSealed && (
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-2.5 py-1 rounded bg-brand-600/80 hover:bg-brand-500 text-white text-[11px] font-bold flex items-center space-x-1 transition-colors"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>{showForm ? 'Cancel' : 'Record Transfer'}</span>
          </button>
        )}
      </div>

      {!isSealed && (
        <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px] flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>Custody handoff records can only be appended after evidence is sealed.</span>
        </div>
      )}

      {successMsg && (
        <div className="p-3 rounded-lg bg-emerald-950/70 border border-emerald-500/40 text-emerald-300 text-[11px] flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {error && (
        <div className="p-3 rounded-lg bg-red-950/70 border border-red-500/40 text-red-300 text-[11px] flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Custody Handoff Form */}
      {showForm && isSealed && (
        <form onSubmit={handleSubmit} className="p-3.5 rounded-lg bg-surface border border-border/80 space-y-3">
          <div className="text-[11px] text-slate-300 font-bold border-b border-border/40 pb-1">
            Officer-Recorded Physical Transfer Declaration
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-400 text-[10px] mb-1">Transferring Officer (Sender)</label>
              <input
                type="text"
                disabled
                value={operatorId || 'OFC-OFFLINE'}
                className="w-full bg-surface-elevated border border-border rounded p-2 text-slate-300 text-[11px] cursor-not-allowed"
              />
            </div>
            <div>
              <label className="block text-slate-300 text-[10px] mb-1">Receiving Officer / Official Name *</label>
              <input
                type="text"
                required
                placeholder="e.g., Inspector R. Sharma"
                value={receiverName}
                onChange={(e) => setReceiverName(e.target.value)}
                className="w-full bg-surface-elevated border border-border rounded p-2 text-slate-100 placeholder:text-slate-600 text-[11px] focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-300 text-[10px] mb-1">Receiving Agency / Unit *</label>
              <input
                type="text"
                required
                placeholder="e.g., SFSL Forensic Chemistry Division"
                value={receiverAgency}
                onChange={(e) => setReceiverAgency(e.target.value)}
                className="w-full bg-surface-elevated border border-border rounded p-2 text-slate-100 placeholder:text-slate-600 text-[11px] focus:outline-none focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 text-[10px] mb-1">Receiver Badge / Government ID *</label>
              <input
                type="text"
                required
                placeholder="e.g., FSL-ID-90412"
                value={receiverBadge}
                onChange={(e) => setReceiverBadge(e.target.value)}
                className="w-full bg-surface-elevated border border-border rounded p-2 text-slate-100 placeholder:text-slate-600 text-[11px] focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-300 text-[10px] mb-1">Physical Container & Seal Verification Notes</label>
            <input
              type="text"
              placeholder="e.g., Tamper-evident tape intact; unbroken lacquer seal ref #L-449"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full bg-surface-elevated border border-border rounded p-2 text-slate-100 placeholder:text-slate-600 text-[11px] focus:outline-none focus:border-brand-500"
            />
          </div>

          <div className="flex items-center space-x-2 pt-1">
            <input
              type="checkbox"
              id="seal_verified"
              checked={packageSealVerified}
              onChange={(e) => setPackageSealVerified(e.target.checked)}
              className="rounded border-border bg-surface text-brand-500 focus:ring-0"
            />
            <label htmlFor="seal_verified" className="text-[11px] text-slate-300 cursor-pointer">
              Officer verified physical evidence container seal is intact and matching recorded identifier.
            </label>
          </div>

          <div className="flex justify-end space-x-2 pt-2 border-t border-border/40">
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="py-1.5 px-3 rounded bg-surface hover:bg-surface-highlight border border-border text-slate-300 text-[11px]"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="py-1.5 px-3 rounded bg-brand-600 hover:bg-brand-500 text-white font-bold text-[11px] disabled:opacity-50"
            >
              {submitting ? 'Recording...' : 'Record Custody Handoff'}
            </button>
          </div>
        </form>
      )}

      {/* Custody History Timeline */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-slate-400 text-[11px] font-bold">
          <span>Custody Transfer History ({history.length})</span>
          <span className="text-[10px] text-slate-500">Append-Only Event Stream</span>
        </div>

        {history.length === 0 ? (
          <div className="p-3 rounded-lg bg-surface border border-border/60 text-slate-400 text-[11px] text-center">
            No physical custody transfers recorded yet for this sealed evidence.
          </div>
        ) : (
          <div className="space-y-2">
            {history.map((item, idx) => (
              <div
                key={item.id || idx}
                className="p-3 rounded-lg bg-surface border border-border/70 text-[11px] space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="px-1.5 py-0.5 rounded bg-blue-950/80 text-blue-300 border border-blue-500/30 text-[10px] font-bold">
                      HANDOFF #{idx + 1}
                    </span>
                    <span className="text-white font-bold">{item.receiver_name}</span>
                    <span className="text-slate-400">({item.receiver_agency})</span>
                  </div>
                  <div className="flex items-center space-x-1 text-slate-400 text-[10px]">
                    <Clock className="w-3 h-3" />
                    <span>{new Date(item.handoff_timestamp_utc).toLocaleString()}</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[10px] text-slate-400 border-t border-border/40 pt-1">
                  <div>
                    <span className="text-slate-500">Sender: </span>
                    <span className="text-slate-300 font-mono">{item.sender_operator_id}</span>
                    <span className="mx-2 text-slate-600">→</span>
                    <span className="text-slate-500">Receiver Badge: </span>
                    <span className="text-slate-300 font-mono">{item.receiver_badge_or_id}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <ShieldCheck className="w-3 h-3 text-emerald-400" />
                    <span className="text-emerald-300">
                      Seal Verified: {item.package_seal_verified ? 'Yes' : 'No'}
                    </span>
                  </div>
                </div>

                {item.notes && (
                  <div className="text-[10px] text-slate-300 bg-surface-elevated p-1.5 rounded border border-border/50">
                    <span className="text-slate-500">Notes: </span>
                    {item.notes}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="text-[10px] text-slate-500 leading-tight">
        * Officer-recorded custody events are cryptographically referenced in referral exports but do not alter the immutable original evidence envelope digest.
      </div>
    </div>
  );
};
