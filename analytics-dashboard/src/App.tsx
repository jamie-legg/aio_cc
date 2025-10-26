import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import LandingPage from './pages/LandingPage';
import PricingPage from './pages/PricingPage';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import DashboardLayout from './components/DashboardLayout';
import UploadsPage from './pages/UploadsPage';
import AIConfigPage from './pages/AIConfigPage';
import IntegrationsPage from './pages/IntegrationsPage';
import DocsPage from './pages/DocsPage';
import SettingsPage from './pages/SettingsPage';

function AppRoutes() {
  const { login } = useAuth();

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/pricing" element={<PricingPage />} />
      <Route path="/login" element={<LoginPage onLogin={login} />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<AnalyticsDashboard />} />
        <Route path="uploads" element={<UploadsPage />} />
        <Route path="ai-config" element={<AIConfigPage />} />
        <Route path="integrations" element={<IntegrationsPage />} />
        <Route path="docs" element={<DocsPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      {/* Redirect unknown routes to dashboard */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}

export default App;
