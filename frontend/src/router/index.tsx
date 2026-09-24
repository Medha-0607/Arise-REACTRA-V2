import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '../layouts/AppLayout';
import { HomePage } from '../pages/HomePage';
import { SetupPage } from '../pages/SetupPage';
import { CapturePage } from '../pages/CapturePage';
import { CheckPage } from '../pages/CheckPage';
import { AnalysisPage } from '../pages/AnalysisPage';
import { ResultPage } from '../pages/ResultPage';
import { EvidencePage } from '../pages/EvidencePage';
import { TimelinePage } from '../pages/TimelinePage';
import { ReferralPage } from '../pages/ReferralPage';
import { HistoryPage } from '../pages/HistoryPage';
import { VerifyPage } from '../pages/VerifyPage';
import { QAPage } from '../pages/QAPage';
import { StatusPage } from '../pages/StatusPage';
import { ErrorBoundary } from '../components/ErrorBoundary';

export const AppRouter: React.FC = () => {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            {/* Primary Workflow Routes */}
            <Route index element={<HomePage />} />
            <Route path="home" element={<HomePage />} />
            <Route path="setup" element={<SetupPage />} />
            <Route path="capture" element={<CapturePage />} />
            <Route path="check" element={<CheckPage />} />
            <Route path="analysis" element={<AnalysisPage />} />
            <Route path="result" element={<ResultPage />} />
            <Route path="evidence" element={<EvidencePage />} />
            <Route path="timeline" element={<TimelinePage />} />

            {/* Operational & Support Routes */}
            <Route path="referral" element={<ReferralPage />} />
            <Route path="history" element={<HistoryPage />} />
            <Route path="verify" element={<VerifyPage />} />
            <Route path="qa" element={<QAPage />} />
            <Route path="status" element={<StatusPage />} />

            {/* Catch-all fallback */}
            <Route path="*" element={<Navigate to="/home" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
};
