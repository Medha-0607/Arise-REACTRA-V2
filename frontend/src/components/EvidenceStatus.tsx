import React from 'react';
import { ShieldCheck, Lock, Hash, Key, CheckCircle2 } from 'lucide-react';
import { cn } from '../lib/utils';

interface EvidenceStatusProps {
  envelopeId?: string;
  hashAlgorithm?: string;
  signatureAlgorithm?: string;
  isSealed?: boolean;
  className?: string;
}

export const EvidenceStatus: React.FC<EvidenceStatusProps> = ({
  envelopeId = 'ENV-PENDING-UNSEALED',
  hashAlgorithm = 'SHA-256 (Canonical JSON)',
  signatureAlgorithm = 'Ed25519 Asymmetric Signature',
  isSealed = true,
  className,
}) => {
  return (
    <div className={cn('bg-surface rounded-xl p-5 border border-border space-y-4 font-mono text-xs', className)}>
      <div className="flex items-center justify-between border-b border-border/70 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-lg bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <h4 className="font-semibold text-white">Cryptographic Tamper-Evidence</h4>
            <span className="text-[11px] text-slate-400">Deterministic Chain of Custody</span>
          </div>
        </div>
        <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 text-[11px] font-bold">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>{isSealed ? 'SEALED' : 'DRAFT'}</span>
        </span>
      </div>

      <div className="space-y-2.5 text-[11px] text-slate-300">
        <div className="flex items-center justify-between p-2 rounded bg-surface-elevated/70 border border-border/50">
          <div className="flex items-center space-x-2">
            <Lock className="w-3.5 h-3.5 text-brand-400" />
            <span className="text-slate-400">Envelope ID:</span>
          </div>
          <span className="font-bold text-slate-200">{envelopeId}</span>
        </div>

        <div className="flex items-center justify-between p-2 rounded bg-surface-elevated/70 border border-border/50">
          <div className="flex items-center space-x-2">
            <Hash className="w-3.5 h-3.5 text-brand-400" />
            <span className="text-slate-400">Digest Schema:</span>
          </div>
          <span className="text-slate-200">{hashAlgorithm}</span>
        </div>

        <div className="flex items-center justify-between p-2 rounded bg-surface-elevated/70 border border-border/50">
          <div className="flex items-center space-x-2">
            <Key className="w-3.5 h-3.5 text-brand-400" />
            <span className="text-slate-400">Digital Signature:</span>
          </div>
          <span className="text-slate-200">{signatureAlgorithm}</span>
        </div>
      </div>
    </div>
  );
};
