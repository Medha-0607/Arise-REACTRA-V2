import React from 'react';
import { Outlet } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { PresumptiveWarning } from '../components/PresumptiveWarning';
import { DemoModeBanner } from '../components/DemoModeBanner';

export const AppLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-background text-slate-100 selection:bg-brand-500/30 selection:text-brand-100">
      {/* Persistent Presumptive Safety Banner */}
      <PresumptiveWarning variant="banner" />

      {/* Simulation/Demo Banner if active */}
      <DemoModeBanner />

      {/* Global Top Bar */}
      <TopBar />

      {/* Main Routed Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <Outlet />
      </main>

      {/* Persistent Operational Footer */}
      <footer className="bg-surface/60 border-t border-border/50 px-4 sm:px-6 py-4 text-xs text-slate-500 font-mono">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-center sm:text-left">
          <span>REACTRA V2 • SIH26231 • Field Testing & Verifiable Evidence</span>
          <span>Presumptive Interpretation Model • Ed25519 Cryptographic Trust Envelope</span>
        </div>
      </footer>
    </div>
  );
};
