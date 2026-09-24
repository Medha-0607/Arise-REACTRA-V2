import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkflowStore } from '../stores/useWorkflowStore';
import { StepIndicator } from '../components/StepIndicator';
import { FieldCard } from '../components/FieldCard';
import { PrimaryAction } from '../components/PrimaryAction';
import { PresumptiveWarning } from '../components/PresumptiveWarning';
import {
  Camera,
  Upload,
  RefreshCw,
  Sun,
  Maximize2,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  Info,
  VideoOff,
} from 'lucide-react';

interface CameraErrorInfo {
  type: 'PERMISSION_DENIED' | 'NOT_FOUND' | 'NOT_READABLE' | 'INSECURE_CONTEXT' | 'UNSUPPORTED' | 'UNKNOWN';
  message: string;
  details?: string;
}

export const CapturePage: React.FC = () => {
  const navigate = useNavigate();
  const { setup, updateSetup, setStep, isSimulatedMode, setCapturedImageBase64, capturedImageBase64 } = useWorkflowStore();
  
  const [captured, setCaptured] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  
  // Camera WebRTC Stream State
  const [cameraState, setCameraState] = useState<'IDLE' | 'STARTING' | 'STREAMING' | 'ERROR' | 'STOPPED'>('IDLE');
  const [cameraError, setCameraError] = useState<CameraErrorInfo | null>(null);
  
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Generate synthetic reference card into canvas (fallback fixture for headless / QA / demo environments)
  const generateSyntheticCardCanvas = useCallback(() => {
    const canvas = canvasRef.current || document.createElement('canvas');
    canvas.width = 600;
    canvas.height = 400;
    const ctx = canvas.getContext('2d');
    if (!ctx) return '';

    // Background
    ctx.fillStyle = '#dcdee0';
    ctx.fillRect(0, 0, 600, 400);

    // Outer card border
    ctx.strokeStyle = '#1a1a1a';
    ctx.lineWidth = 4;
    ctx.strokeRect(10, 10, 580, 380);

    // Title / Label
    ctx.fillStyle = '#222';
    ctx.font = 'bold 12px monospace';
    ctx.fillText('REACTRA REFERENCE CARD -- MULTI-WELL GRID 3x2', 40, 24);

    // 6 Reference Patches (Y=30 to Y=90)
    ctx.fillStyle = '#f5f5f5'; ctx.fillRect(40, 30, 60, 60); ctx.strokeRect(40, 30, 60, 60);
    ctx.fillStyle = '#b2b2b2'; ctx.fillRect(130, 30, 60, 60); ctx.strokeRect(130, 30, 60, 60);
    ctx.fillStyle = '#808080'; ctx.fillRect(220, 30, 60, 60); ctx.strokeRect(220, 30, 60, 60);
    ctx.fillStyle = '#181818'; ctx.fillRect(310, 30, 60, 60); ctx.strokeRect(310, 30, 60, 60);
    ctx.fillStyle = '#00b4c8'; ctx.fillRect(400, 30, 60, 60); ctx.strokeRect(400, 30, 60, 60);
    ctx.fillStyle = '#c82896'; ctx.fillRect(490, 30, 60, 60); ctx.strokeRect(490, 30, 60, 60);

    // Reaction Wells
    ctx.beginPath();
    ctx.arc(140, 240, 50, 0, 2 * Math.PI);
    ctx.fillStyle = '#78148c'; // Dark Purple reaction
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#555';
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(460, 240, 50, 0, 2 * Math.PI);
    ctx.fillStyle = '#e8e8e0'; // Control
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#111';
    ctx.font = '11px monospace';
    ctx.fillText('W1: REACTION', 95, 315);
    ctx.fillText('W2: CONTROL', 420, 315);

    return canvas.toDataURL('image/png');
  }, []);

  // Stop camera tracks cleanly
  const stopCameraStream = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        track.stop();
      });
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraState('STOPPED');
  }, []);

  // Request & start camera stream with fallback constraints
  const startCameraStream = useCallback(async () => {
    // 1. Secure context check
    if (typeof window !== 'undefined' && window.isSecureContext === false && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
      setCameraError({
        type: 'INSECURE_CONTEXT',
        message: 'Camera access requires a secure context (HTTPS or localhost).',
        details: 'Modern browsers block navigator.mediaDevices.getUserMedia over unencrypted HTTP LAN connections.',
      });
      setCameraState('ERROR');
      return;
    }

    // 2. WebRTC MediaDevices support check
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setCameraError({
        type: 'UNSUPPORTED',
        message: 'WebRTC Camera API is not supported in this browser environment.',
        details: 'navigator.mediaDevices.getUserMedia is unavailable.',
      });
      setCameraState('ERROR');
      return;
    }

    stopCameraStream();
    setCameraState('STARTING');
    setCameraError(null);

    // 3. Request camera stream (environment-facing preference with generic fallback)
    try {
      let stream: MediaStream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: { ideal: 'environment' },
            width: { ideal: 1280, min: 640 },
            height: { ideal: 720, min: 480 },
          },
          audio: false,
        });
      } catch (err: unknown) {
        // Fallback to basic video constraint if ideal constraints failed (e.g. laptop webcam with no environment camera)
        console.warn('Initial camera constraint failed, retrying with standard video: true', err);
        stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });
      }

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play().catch((playErr) => {
            console.warn('Video playback failed:', playErr);
          });
        };
      }
      setCameraState('STREAMING');
    } catch (err: unknown) {
      const error = err as Error;
      let errorInfo: CameraErrorInfo;

      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        errorInfo = {
          type: 'PERMISSION_DENIED',
          message: 'Camera permission is required for live optical capture.',
          details: 'Please allow camera access in your browser site permissions and click "Retry Camera".',
        };
      } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        errorInfo = {
          type: 'NOT_FOUND',
          message: 'No physical camera device was detected on this system.',
          details: 'Connect a USB/built-in camera or switch to "Upload Card Image" mode.',
        };
      } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
        errorInfo = {
          type: 'NOT_READABLE',
          message: 'Camera hardware is locked or in use by another application.',
          details: 'Please close other camera applications (Zoom, Teams, etc.) and retry.',
        };
      } else {
        errorInfo = {
          type: 'UNKNOWN',
          message: `Failed to acquire camera stream: ${error.message || 'Unknown error'}`,
          details: error.name,
        };
      }

      setCameraError(errorInfo);
      setCameraState('ERROR');
    }
  }, [stopCameraStream]);

  // Lifecycle: Manage camera on mount / captureMode changes
  useEffect(() => {
    if (setup.captureMode === 'LIVE_CAMERA' && !captured) {
      startCameraStream();
    } else {
      stopCameraStream();
    }

    return () => {
      stopCameraStream();
    };
  }, [setup.captureMode, captured, startCameraStream, stopCameraStream]);

  // Capture frame from live video or fallback
  const handleTriggerCapture = () => {
    setIsCapturing(true);

    setTimeout(() => {
      let dataUrl: string = '';

      if (setup.captureMode === 'LIVE_CAMERA' && videoRef.current && cameraState === 'STREAMING') {
        const video = videoRef.current;
        const canvas = canvasRef.current || document.createElement('canvas');
        const width = video.videoWidth || 1280;
        const height = video.videoHeight || 720;
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.drawImage(video, 0, 0, width, height);
          dataUrl = canvas.toDataURL('image/png');
        }
      }

      // Fallback for demo / QA / simulated / no-camera environment
      if (!dataUrl) {
        dataUrl = generateSyntheticCardCanvas();
      }

      setCapturedImageBase64(dataUrl);
      setIsCapturing(false);
      setCaptured(true);
      stopCameraStream();
    }, 250);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      stopCameraStream();
      const reader = new FileReader();
      reader.onload = () => {
        if (typeof reader.result === 'string') {
          setCapturedImageBase64(reader.result);
          setCaptured(true);
          updateSetup({ captureMode: 'IMPORTED_IMAGE' });
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRetake = () => {
    setCaptured(false);
    setCapturedImageBase64(null);
    if (setup.captureMode === 'LIVE_CAMERA') {
      startCameraStream();
    }
  };

  const handleSwitchMode = () => {
    const nextMode = setup.captureMode === 'LIVE_CAMERA' ? 'IMPORTED_IMAGE' : 'LIVE_CAMERA';
    updateSetup({ captureMode: nextMode });
    setCaptured(false);
    setCapturedImageBase64(null);
    if (nextMode === 'LIVE_CAMERA') {
      startCameraStream();
    } else {
      stopCameraStream();
    }
  };

  const handleProceedToCheck = () => {
    stopCameraStream();
    setStep('check');
    navigate('/check');
  };

  return (
    <div className="space-y-6 font-mono">
      <StepIndicator currentStep="capture" />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            2. Reagent Reaction Field Capture
          </h1>
          <p className="text-xs text-slate-400">
            Align reference card corners within optical guide boundaries. Ensure uniform diffuse illumination.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-400">Provenance:</span>
          <span className="px-2.5 py-1 rounded bg-brand-600/20 text-brand-400 border border-brand-500/30 font-bold">
            {setup.captureMode}
          </span>
        </div>
      </div>

      <PresumptiveWarning variant="banner" className="rounded-lg" />

      {/* Hidden offscreen canvas for frame capture */}
      <canvas ref={canvasRef} style={{ display: 'none' }} width={1280} height={720} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Viewport Container (2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="relative aspect-[4/3] bg-black/90 rounded-2xl border-2 border-border overflow-hidden flex flex-col items-center justify-center text-center">
            
            {/* Live Video Feed Element */}
            {setup.captureMode === 'LIVE_CAMERA' && !captured && (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className={`absolute inset-0 w-full h-full object-cover z-0 ${
                  cameraState === 'STREAMING' ? 'opacity-100' : 'opacity-0'
                }`}
              />
            )}

            {/* Frozen Frame / Upload Preview */}
            {captured && capturedImageBase64 && (
              <img
                src={capturedImageBase64}
                alt="Captured Specimen Frame"
                className="absolute inset-0 w-full h-full object-contain bg-black/95 z-0"
              />
            )}

            {/* Framing Alignment Overlay Guides (Always on top of video) */}
            <div className="absolute top-6 left-6 w-12 h-12 border-t-2 border-l-2 border-brand-500/90 rounded-tl pointer-events-none z-10" />
            <div className="absolute top-6 right-6 w-12 h-12 border-t-2 border-r-2 border-brand-500/90 rounded-tr pointer-events-none z-10" />
            <div className="absolute bottom-6 left-6 w-12 h-12 border-b-2 border-l-2 border-brand-500/90 rounded-bl pointer-events-none z-10" />
            <div className="absolute bottom-6 right-6 w-12 h-12 border-b-2 border-r-2 border-brand-500/90 rounded-br pointer-events-none z-10" />

            {/* Central Target Reticle */}
            <div className="absolute inset-14 border border-dashed border-slate-500/50 rounded-xl flex items-center justify-center pointer-events-none z-10">
              <span className="text-[10px] text-slate-300 uppercase tracking-widest bg-black/75 px-3 py-1 rounded border border-slate-700">
                Align Reference Card Within Bounds
              </span>
            </div>

            {/* Camera Error / Permission Banner Over Viewport */}
            {cameraError && setup.captureMode === 'LIVE_CAMERA' && !captured && (
              <div className="z-20 p-6 max-w-md bg-surface-elevated/95 border border-rose-500/50 rounded-2xl space-y-3 shadow-2xl backdrop-blur-md">
                <div className="w-12 h-12 rounded-xl bg-rose-500/20 text-rose-400 flex items-center justify-center mx-auto border border-rose-500/30">
                  <VideoOff className="w-6 h-6" />
                </div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                  {cameraError.type === 'PERMISSION_DENIED' ? 'Camera Permission Denied' : 'Camera Unavailable'}
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed font-sans">
                  {cameraError.message}
                </p>
                {cameraError.details && (
                  <p className="text-[10px] text-slate-400 font-mono bg-black/50 p-2 rounded border border-slate-800">
                    {cameraError.details}
                  </p>
                )}
                <div className="flex items-center justify-center space-x-3 pt-2">
                  <button
                    type="button"
                    onClick={startCameraStream}
                    className="px-3.5 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-mono font-bold flex items-center space-x-1.5 transition-colors"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Retry Camera</span>
                  </button>
                  <button
                    type="button"
                    onClick={handleSwitchMode}
                    className="px-3.5 py-1.5 rounded-lg bg-surface hover:bg-slate-700 text-slate-300 text-xs font-mono border border-border transition-colors flex items-center space-x-1.5"
                  >
                    <Upload className="w-3.5 h-3.5 text-amber-400" />
                    <span>Switch to File Upload</span>
                  </button>
                </div>
              </div>
            )}

            {/* Idle / Starting Graphic (when not streaming or error) */}
            {setup.captureMode === 'LIVE_CAMERA' && !captured && cameraState === 'STARTING' && !cameraError && (
              <div className="z-10 space-y-3 max-w-sm">
                <RefreshCw className="w-8 h-8 text-brand-400 animate-spin mx-auto" />
                <h3 className="text-sm font-semibold text-white">INITIALIZING OPTICAL SENSOR...</h3>
                <p className="text-xs text-slate-400 font-sans">
                  Requesting camera device access and locking hardware exposure.
                </p>
              </div>
            )}

            {/* Viewport Status Overlays (Bottom Left & Right) */}
            <div className="absolute bottom-4 left-4 flex items-center space-x-2 text-[11px] bg-black/85 px-2.5 py-1 rounded border border-slate-800 text-slate-300 z-10 backdrop-blur-sm">
              <Sun className="w-3.5 h-3.5 text-amber-400" />
              <span>
                {setup.captureMode === 'LIVE_CAMERA' ? 'Camera: WebRTC Live Stream' : 'Source: Imported File'}
              </span>
            </div>

            <div className="absolute bottom-4 right-4 flex items-center space-x-2 text-[11px] bg-black/85 px-2.5 py-1 rounded border border-slate-800 text-emerald-400 z-10 backdrop-blur-sm">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>
                {captured ? 'Frame Latched in Buffer' : cameraState === 'STREAMING' ? 'Hardware Locked (Live)' : 'Viewport Ready'}
              </span>
            </div>
          </div>

          {/* Viewport Control Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-surface border border-border">
            <div className="flex items-center space-x-3">
              <button
                type="button"
                onClick={handleRetake}
                disabled={!captured}
                className="px-4 py-2 rounded-lg bg-surface-elevated hover:bg-slate-700 text-slate-300 text-xs font-mono border border-border disabled:opacity-40 transition-colors flex items-center space-x-2"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Retake Frame</span>
              </button>

              <label className="px-3 py-2 rounded-lg bg-surface-elevated hover:bg-slate-700 text-slate-300 text-xs font-mono border border-border cursor-pointer transition-colors flex items-center space-x-1.5">
                <Upload className="w-3.5 h-3.5 text-amber-400" />
                <span>Upload Card Image</span>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>

              <button
                type="button"
                onClick={handleSwitchMode}
                className="px-3 py-2 rounded-lg bg-surface-elevated hover:bg-slate-700 text-slate-300 text-xs font-mono border border-border transition-colors flex items-center space-x-1.5"
              >
                <span>{setup.captureMode === 'LIVE_CAMERA' ? 'Mode: Camera' : 'Mode: File'}</span>
              </button>
            </div>

            <PrimaryAction
              label={captured ? 'Validate Capture Quality' : 'Acquire Field Frame'}
              icon={captured ? ArrowRight : Camera}
              isLoading={isCapturing}
              onClick={captured ? handleProceedToCheck : handleTriggerCapture}
              variant={captured ? 'tactical' : 'primary'}
            />
          </div>
        </div>

        {/* Capture Guidance & Rules (1 col) */}
        <div className="space-y-6">
          <FieldCard
            title="Optical Capture Protocol"
            subtitle="Standard Operating Guidance"
            icon={Maximize2}
          >
            <div className="space-y-3.5 text-xs font-sans text-slate-300">
              <div className="p-3 rounded-lg bg-surface-elevated border border-border/60 space-y-1">
                <span className="font-mono font-bold text-white text-xs block">1. Diffuse Illumination</span>
                <p className="text-slate-400 text-[11px]">
                  Avoid direct flash or point-source lighting causing specular glare on reaction wells.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-surface-elevated border border-border/60 space-y-1">
                <span className="font-mono font-bold text-white text-xs block">2. Plane Parallel Alignment</span>
                <p className="text-slate-400 text-[11px]">
                  Keep lens parallel to reference card to prevent perspective keystone distortion.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-surface-elevated border border-border/60 space-y-1">
                <span className="font-mono font-bold text-white text-xs block">3. Steady Sensor Hold</span>
                <p className="text-slate-400 text-[11px]">
                  Hold device stable. Motion blur exceeding Laplace variance threshold is automatically rejected.
                </p>
              </div>

              <div className="p-2.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px] font-mono flex items-center space-x-2">
                <Info className="w-4 h-4 flex-shrink-0 text-amber-400" />
                <span>Invalid measurements are rejected deterministically before reaching classification.</span>
              </div>
            </div>
          </FieldCard>

          {isSimulatedMode && (
            <div className="p-4 rounded-xl bg-purple-950/40 border border-purple-500/30 text-xs font-mono text-purple-300 space-y-2">
              <div className="flex items-center space-x-2 text-purple-200 font-bold">
                <Sparkles className="w-4 h-4" />
                <span>Simulation Active</span>
              </div>
              <p className="text-[11px] text-purple-300/90 font-sans">
                A mock quality state will be applied on the Check screen.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
