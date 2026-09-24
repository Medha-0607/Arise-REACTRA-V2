import React, { useEffect, useRef, useState } from 'react';
import QRCode from 'qrcode';
import { QrCode, Copy, Check, Download, AlertTriangle } from 'lucide-react';

interface AuthenticatedQRCodeProps {
  payload: Record<string, string> | string;
  testId?: string;
  evidenceId?: string;
}

export const AuthenticatedQRCode: React.FC<AuthenticatedQRCodeProps> = ({
  payload,
  testId,
  evidenceId,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const payloadString = typeof payload === 'string' ? payload : JSON.stringify(payload);

  useEffect(() => {
    if (canvasRef.current && payloadString) {
      QRCode.toCanvas(
        canvasRef.current,
        payloadString,
        {
          width: 220,
          margin: 2,
          color: {
            dark: '#000000',
            light: '#ffffff',
          },
          errorCorrectionLevel: 'M',
        },
        (err) => {
          if (err) {
            setError('Failed to generate QR code: ' + err.message);
          } else {
            setError(null);
          }
        }
      );
    }
  }, [payloadString]);

  const handleCopy = () => {
    navigator.clipboard.writeText(payloadString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (canvasRef.current) {
      const url = canvasRef.current.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = url;
      a.download = `REACTRA_QR_${evidenceId || testId || 'ATTESTATION'}.png`;
      a.click();
    }
  };

  const parsedPayload = typeof payload === 'object' ? payload : (() => {
    try {
      return JSON.parse(payload);
    } catch {
      return { raw: payload };
    }
  })();

  return (
    <div className="p-4 rounded-xl bg-surface-elevated border border-border space-y-4 font-mono text-xs">
      <div className="flex items-center justify-between border-b border-border/60 pb-3">
        <div className="flex items-center space-x-2">
          <QrCode className="w-4 h-4 text-brand-400" />
          <span className="font-bold text-white text-sm">Authenticated QR Attestation</span>
        </div>
        <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 font-bold">
          OFFLINE LOCAL ATTESTATION
        </span>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-4">
        <div className="p-2 bg-white rounded-lg border border-slate-300 flex-shrink-0 shadow-sm">
          <canvas ref={canvasRef} className="block" />
          {error && <p className="text-red-600 text-[10px] mt-1">{error}</p>}
        </div>

        <div className="flex-1 w-full space-y-2 text-[11px]">
          <div className="p-2.5 rounded bg-surface border border-border/70 space-y-1">
            <div className="flex justify-between">
              <span className="text-slate-400">Schema Version:</span>
              <span className="text-slate-200 font-bold">{parsedPayload.v || '2.0'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Evidence ID:</span>
              <span className="text-brand-300 truncate max-w-[180px]">{parsedPayload.evd || evidenceId}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Presumptive Finding:</span>
              <span className="text-amber-400 font-bold">{parsedPayload.res || 'PRESUMPTIVE'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Record Digest:</span>
              <span className="text-slate-300 font-mono truncate max-w-[150px]">{parsedPayload.dig ? `${parsedPayload.dig.slice(0, 16)}...` : 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Prev Hash:</span>
              <span className="text-slate-400 font-mono truncate max-w-[150px]">
                {parsedPayload.prv ? `${parsedPayload.prv.slice(0, 16)}...` : 'GENESIS (None)'}
              </span>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleCopy}
              className="flex-1 py-1.5 px-2 rounded bg-surface hover:bg-surface-highlight border border-border flex items-center justify-center space-x-1.5 text-slate-200 text-[11px] transition-colors"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-slate-400" />}
              <span>{copied ? 'Copied Payload' : 'Copy Payload'}</span>
            </button>
            <button
              onClick={handleDownload}
              className="flex-1 py-1.5 px-2 rounded bg-surface hover:bg-surface-highlight border border-border flex items-center justify-center space-x-1.5 text-slate-200 text-[11px] transition-colors"
            >
              <Download className="w-3.5 h-3.5 text-slate-400" />
              <span>Save PNG</span>
            </button>
          </div>
        </div>
      </div>

      {/* Critical Legal / Trust Boundary Callout */}
      <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-[11px] text-amber-200 space-y-1 leading-relaxed">
        <div className="flex items-center space-x-1.5 font-bold text-amber-300">
          <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
          <span>CRYPTOGRAPHIC BOUNDARY NOTICE</span>
        </div>
        <p>
          <strong>Signature Valid ≠ Trusted Device Identity:</strong> This QR proves cryptographic consistency with the embedded public key (<code className="text-slate-200">pk</code>) and envelope digest (<code className="text-slate-200">dig</code>). It does <em>not</em> independently prove real-world device authorization without a Phase 7 Central Trust Registry.
        </p>
      </div>
    </div>
  );
};
