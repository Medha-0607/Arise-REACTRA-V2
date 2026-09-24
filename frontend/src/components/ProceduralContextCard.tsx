import React, { useState } from 'react';
import { FieldCard } from './FieldCard';
import {
  Shield,
  Users,
  CheckCircle2,
  Lock,
  Package,
  Save,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { ProceduralUpdateRequest, ProceduralContextResponse } from '../types/api';

interface ProceduralContextCardProps {
  initialData?: ProceduralContextResponse | ProceduralUpdateRequest | null;
  isSealed?: boolean;
  onSave?: (data: ProceduralUpdateRequest) => Promise<void>;
  onChange?: (data: ProceduralUpdateRequest) => void;
  isLoading?: boolean;
}

export const ProceduralContextCard: React.FC<ProceduralContextCardProps> = ({
  initialData,
  isSealed = false,
  onSave,
  onChange,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState<ProceduralUpdateRequest>({
    search_context_type: initialData?.search_context_type || 'VEHICLE_SEARCH',
    panchnama_memo_ref_no: initialData?.panchnama_memo_ref_no || '',
    witness_1_name: initialData?.witness_1_name || '',
    witness_1_contact: initialData?.witness_1_contact || '',
    witness_2_name: initialData?.witness_2_name || '',
    witness_2_contact: initialData?.witness_2_contact || '',
    section_50_applicable: initialData?.section_50_applicable ?? false,
    section_50_option_informed: initialData?.section_50_option_informed ?? false,
    section_50_choice: initialData?.section_50_choice || 'NOT_APPLICABLE',
    section_50_officer_name: initialData?.section_50_officer_name || '',
    section_50_officer_designation: initialData?.section_50_officer_designation || '',
    section_52a_inventory_prepared: initialData?.section_52a_inventory_prepared ?? false,
    section_52a_application_ref: initialData?.section_52a_application_ref || '',
    section_52a_magistrate_court: initialData?.section_52a_magistrate_court || '',
    sample_drawal_status: initialData?.sample_drawal_status || 'PENDING',
    magistrate_cert_status: initialData?.magistrate_cert_status || 'PENDING',
    representative_sample_id: initialData?.representative_sample_id || '',
    sample_seal_identifier: initialData?.sample_seal_identifier || '',
    section_57_report_status: initialData?.section_57_report_status || 'NOT_SUBMITTED',
    section_57_report_ref: initialData?.section_57_report_ref || '',
    section_57_submitted_to: initialData?.section_57_submitted_to || '',
    kit_lot_number: initialData?.kit_lot_number || '',
    kit_expiry_date: initialData?.kit_expiry_date || '',
    officer_notes: initialData?.officer_notes || '',
  });

  const [savedSuccess, setSavedSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleChange = (field: keyof ProceduralUpdateRequest, value: unknown) => {
    if (isSealed) return;
    const updated = { ...formData, [field]: value };
    setFormData(updated);
    setSavedSuccess(false);
    if (onChange) {
      onChange(updated);
    }
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSealed || !onSave) return;
    setErrorMsg(null);
    try {
      await onSave(formData);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 4000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to save procedural metadata';
      setErrorMsg(msg);
    }
  };

  return (
    <div className="space-y-4">
      {/* Immutability Banner */}
      {isSealed && (
        <div className="p-3.5 rounded-lg bg-amber-950/40 border border-amber-800/60 text-xs text-amber-200 flex items-center space-x-2.5">
          <Lock className="w-4 h-4 text-amber-400 flex-shrink-0" />
          <div>
            <strong>Session Immutable (Evidence Sealed)</strong>
            <p className="text-[11px] text-amber-300/80">
              Procedural context is cryptographically bound into the sealed evidence envelope and cannot be modified.
            </p>
          </div>
        </div>
      )}

      {errorMsg && (
        <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {savedSuccess && (
        <div className="p-3 rounded-lg bg-emerald-950/40 border border-emerald-800/60 text-xs text-emerald-300 flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>Authoritative procedural context updated and logged to audit trail.</span>
        </div>
      )}

      <form onSubmit={handleFormSubmit} className="space-y-4">
        {/* Card 1: Kit Metadata & Seizure Context */}
        <FieldCard
          title="Kit Metadata & Field Seizure Reference"
          subtitle="Physical Assay Lot Tracking & Panchnama Memo Reference"
          icon={Package}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Kit Lot Number</label>
              <input
                type="text"
                disabled={isSealed || isLoading}
                placeholder="e.g. LOT-2026-MQ-04"
                value={formData.kit_lot_number}
                onChange={(e) => handleChange('kit_lot_number', e.target.value)}
                className="w-full bg-surface-elevated border border-border rounded-lg px-3 py-2 text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-brand-500 disabled:opacity-50"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Kit Expiry Date</label>
              <input
                type="text"
                disabled={isSealed || isLoading}
                placeholder="e.g. 2027-12-31"
                value={formData.kit_expiry_date}
                onChange={(e) => handleChange('kit_expiry_date', e.target.value)}
                className="w-full bg-surface-elevated border border-border rounded-lg px-3 py-2 text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-brand-500 disabled:opacity-50"
              />
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">Search Context Type</label>
              <select
                disabled={isSealed || isLoading}
                value={formData.search_context_type}
                onChange={(e) => handleChange('search_context_type', e.target.value)}
                className="w-full bg-surface-elevated border border-border rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-brand-500 disabled:opacity-50"
              >
                <option value="VEHICLE_SEARCH">Vehicle Search / Transit Check</option>
                <option value="PERSONAL_SEARCH">Personal Search (NDPS §50 applicable)</option>
                <option value="PREMISES_SEARCH">Premises / Building Search</option>
                <option value="PARCEL_INTERCEPTION">Parcel / Cargo Interception</option>
                <option value="OTHER">Other Field Operation</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Seizure Memo / Panchnama Ref No.
              </label>
              <input
                type="text"
                disabled={isSealed || isLoading}
                placeholder="e.g. PANCH/2026/0923/04"
                value={formData.panchnama_memo_ref_no}
                onChange={(e) => handleChange('panchnama_memo_ref_no', e.target.value)}
                className="w-full bg-surface-elevated border border-border rounded-lg px-3 py-2 text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-brand-500 disabled:opacity-50"
              />
            </div>
          </div>
        </FieldCard>

        {/* Card 2: Witnesses / Independent Panches */}
        <FieldCard
          title="Independent Witnesses / Panchnama Observers"
          subtitle="Officer-Entered Observer Metadata"
          icon={Users}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="space-y-2 p-3 bg-surface-elevated/50 rounded-lg border border-border/60">
              <span className="font-semibold text-slate-300 block">Witness 1 (Primary Panch)</span>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Full Name</label>
                <input
                  type="text"
                  disabled={isSealed || isLoading}
                  placeholder="e.g. Rajesh Sharma"
                  value={formData.witness_1_name}
                  onChange={(e) => handleChange('witness_1_name', e.target.value)}
                  className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-slate-100 disabled:opacity-50"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Contact / Address</label>
                <input
                  type="text"
                  disabled={isSealed || isLoading}
                  placeholder="e.g. Phone or Residential Area"
                  value={formData.witness_1_contact}
                  onChange={(e) => handleChange('witness_1_contact', e.target.value)}
                  className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-slate-100 disabled:opacity-50"
                />
              </div>
            </div>

            <div className="space-y-2 p-3 bg-surface-elevated/50 rounded-lg border border-border/60">
              <span className="font-semibold text-slate-300 block">Witness 2 (Secondary Panch)</span>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Full Name</label>
                <input
                  type="text"
                  disabled={isSealed || isLoading}
                  placeholder="e.g. Anand Kumar"
                  value={formData.witness_2_name}
                  onChange={(e) => handleChange('witness_2_name', e.target.value)}
                  className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-slate-100 disabled:opacity-50"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Contact / Address</label>
                <input
                  type="text"
                  disabled={isSealed || isLoading}
                  placeholder="e.g. Phone or Residential Area"
                  value={formData.witness_2_contact}
                  onChange={(e) => handleChange('witness_2_contact', e.target.value)}
                  className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-slate-100 disabled:opacity-50"
                />
              </div>
            </div>
          </div>
        </FieldCard>

        {/* Card 3: Statutory Safeguards (Section 50, 52A, 57) */}
        <FieldCard
          title="Statutory Procedural Safeguards"
          subtitle="Neutral Recording of Officer-Entered Safeguard Metadata (No Legal Adjudication)"
          icon={Shield}
        >
          <div className="space-y-4 text-xs">
            {/* Section 50 */}
            <div className="p-3 bg-surface-elevated/40 rounded-lg border border-border/60 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-200">NDPS §50 — Personal Search Safeguards</span>
                <span className="text-[10px] text-slate-400">Officer-Entered Status</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <label className="flex items-center space-x-2 text-slate-300 cursor-pointer">
                  <input
                    type="checkbox"
                    disabled={isSealed || isLoading}
                    checked={formData.section_50_applicable}
                    onChange={(e) => handleChange('section_50_applicable', e.target.checked)}
                    className="rounded border-border bg-surface text-brand-500 focus:ring-0"
                  />
                  <span>Section 50 Applicable</span>
                </label>
                <label className="flex items-center space-x-2 text-slate-300 cursor-pointer">
                  <input
                    type="checkbox"
                    disabled={isSealed || isLoading}
                    checked={formData.section_50_option_informed}
                    onChange={(e) => handleChange('section_50_option_informed', e.target.checked)}
                    className="rounded border-border bg-surface text-brand-500 focus:ring-0"
                  />
                  <span>Option Informed to Suspect</span>
                </label>
              </div>

              {formData.section_50_applicable && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 border-t border-border/40">
                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Suspect Choice Recorded</label>
                    <select
                      disabled={isSealed || isLoading}
                      value={formData.section_50_choice}
                      onChange={(e) => handleChange('section_50_choice', e.target.value)}
                      className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-slate-100 text-xs disabled:opacity-50"
                    >
                      <option value="NOT_APPLICABLE">Not Applicable</option>
                      <option value="GAZETTED_OFFICER">Gazetted Officer Requested</option>
                      <option value="MAGISTRATE">Magistrate Requested</option>
                      <option value="DECLINED">Declined / Proceeded Before Officer</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Officer / Magistrate Name</label>
                    <input
                      type="text"
                      disabled={isSealed || isLoading}
                      placeholder="e.g. S. Sen, ACP"
                      value={formData.section_50_officer_name}
                      onChange={(e) => handleChange('section_50_officer_name', e.target.value)}
                      className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-slate-100 disabled:opacity-50"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] text-slate-400 mb-1">Designation</label>
                    <input
                      type="text"
                      disabled={isSealed || isLoading}
                      placeholder="e.g. Gazetted Officer / Magistrate"
                      value={formData.section_50_officer_designation}
                      onChange={(e) => handleChange('section_50_officer_designation', e.target.value)}
                      className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-slate-100 disabled:opacity-50"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Section 52A */}
            <div className="p-3 bg-surface-elevated/40 rounded-lg border border-border/60 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-200">NDPS §52A — Inventory & Sample Certification</span>
                <span className="text-[10px] text-slate-400">Recorded References</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
                <label className="flex items-center space-x-2 text-slate-300 cursor-pointer">
                  <input
                    type="checkbox"
                    disabled={isSealed || isLoading}
                    checked={formData.section_52a_inventory_prepared}
                    onChange={(e) => handleChange('section_52a_inventory_prepared', e.target.checked)}
                    className="rounded border-border bg-surface text-brand-500 focus:ring-0"
                  />
                  <span>Inventory Prepared</span>
                </label>
                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Application Ref</label>
                  <input
                    type="text"
                    disabled={isSealed || isLoading}
                    placeholder="e.g. 52A/APP/2026/88"
                    value={formData.section_52a_application_ref}
                    onChange={(e) => handleChange('section_52a_application_ref', e.target.value)}
                    className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-slate-100 disabled:opacity-50"
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Sample Seal ID</label>
                  <input
                    type="text"
                    disabled={isSealed || isLoading}
                    placeholder="e.g. SEAL-NDPS-8841"
                    value={formData.sample_seal_identifier}
                    onChange={(e) => handleChange('sample_seal_identifier', e.target.value)}
                    className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-slate-100 disabled:opacity-50"
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Sample ID</label>
                  <input
                    type="text"
                    disabled={isSealed || isLoading}
                    placeholder="e.g. SMP-2026-A1"
                    value={formData.representative_sample_id}
                    onChange={(e) => handleChange('representative_sample_id', e.target.value)}
                    className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-slate-100 disabled:opacity-50"
                  />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-border/40">
                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Sample Drawal Status</label>
                  <select
                    disabled={isSealed || isLoading}
                    value={formData.sample_drawal_status}
                    onChange={(e) => handleChange('sample_drawal_status', e.target.value)}
                    className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-slate-100 text-xs disabled:opacity-50"
                  >
                    <option value="PENDING">Pending Drawal</option>
                    <option value="DRAWN_BEFORE_MAGISTRATE">Drawn in Presence of Magistrate</option>
                    <option value="NOT_APPLICABLE">Not Applicable</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Magistrate Certification Status</label>
                  <select
                    disabled={isSealed || isLoading}
                    value={formData.magistrate_cert_status}
                    onChange={(e) => handleChange('magistrate_cert_status', e.target.value)}
                    className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-slate-100 text-xs disabled:opacity-50"
                  >
                    <option value="PENDING">Pending Certification</option>
                    <option value="CERTIFIED">Certified by Magistrate</option>
                    <option value="NOT_APPLICABLE">Not Applicable</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Section 57 */}
            <div className="p-3 bg-surface-elevated/40 rounded-lg border border-border/60 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-200">NDPS §57 — Report of Arrest / Seizure</span>
                <span className="text-[10px] text-slate-400">Report Reference</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Report Status</label>
                  <select
                    disabled={isSealed || isLoading}
                    value={formData.section_57_report_status}
                    onChange={(e) => handleChange('section_57_report_status', e.target.value)}
                    className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-slate-100 text-xs disabled:opacity-50"
                  >
                    <option value="NOT_SUBMITTED">Not Yet Submitted</option>
                    <option value="SUBMITTED_WITHIN_48H">Submitted Within 48 Hours</option>
                    <option value="SUBMITTED_DELAYED">Submitted (Delayed)</option>
                    <option value="NOT_APPLICABLE">Not Applicable</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Report Reference No.</label>
                  <input
                    type="text"
                    disabled={isSealed || isLoading}
                    placeholder="e.g. S57/2026/0923/02"
                    value={formData.section_57_report_ref}
                    onChange={(e) => handleChange('section_57_report_ref', e.target.value)}
                    className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-slate-100 disabled:opacity-50"
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-slate-400 mb-1">Submitted To (Designation)</label>
                  <input
                    type="text"
                    disabled={isSealed || isLoading}
                    placeholder="e.g. Superintendent of Police"
                    value={formData.section_57_submitted_to}
                    onChange={(e) => handleChange('section_57_submitted_to', e.target.value)}
                    className="w-full bg-surface border border-border rounded px-2.5 py-1.5 text-slate-100 disabled:opacity-50"
                  />
                </div>
              </div>
            </div>

            {/* Officer Notes */}
            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Officer Procedural Remarks / Observations
              </label>
              <textarea
                rows={2}
                disabled={isSealed || isLoading}
                placeholder="Enter neutral factual observations recorded during field operation..."
                value={formData.officer_notes}
                onChange={(e) => handleChange('officer_notes', e.target.value)}
                className="w-full bg-surface-elevated border border-border rounded-lg p-2.5 text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-brand-500 disabled:opacity-50 text-xs"
              />
            </div>
          </div>
        </FieldCard>

        {/* Save Button if onSave provided and not sealed */}
        {onSave && !isSealed && (
          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={isLoading}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs transition-colors disabled:opacity-50 shadow-md shadow-brand-900/30"
            >
              {isLoading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Save className="w-3.5 h-3.5" />
              )}
              <span>Save & Log Procedural Context</span>
            </button>
          </div>
        )}
      </form>
    </div>
  );
};
