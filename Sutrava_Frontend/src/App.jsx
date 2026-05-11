import { Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { AuthProvider } from './context/AuthContext';
import { ResultsProvider } from './context/ResultsContext';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import BenefitsSection from './components/BenefitsSection';
import StepsSection from './components/StepsSection';
import Footer from './components/Footer';
import UploadPage from './pages/UploadPage';
import ExtractedPage from './pages/ExtractedPage';
import ClassificationPage from './pages/ClassificationPage';
import ClusteringPage from './pages/ClusteringPage';
import PrioritizationPage from './pages/PrioritizationPage';
import SummaryPage from './pages/SummaryPage';
import IntegrationsPage from './pages/IntegrationsPage';
import SettingsPage from './pages/SettingsPage';
import JiraConsole from './pages/integrations/JiraConsole';
import SlackConsole from './pages/integrations/SlackConsole';
import GitHubConsole from './pages/integrations/GitHubConsole';

const pageVariants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.15 } },
};

function PageWrapper({ children }) {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      {children}
    </motion.div>
  );
}

function HomePage() {
  return (
    <>
      <HeroSection />
      <BenefitsSection />

      {/* Welcome aboard section */}
      <section className="py-16 px-6 relative overflow-hidden">
        <div className="absolute inset-0 hero-gradient opacity-30" />
        <div className="relative z-10 max-w-4xl mx-auto text-center">
          <h2
            className="font-display font-light leading-none mb-6"
            style={{
              fontSize: 'clamp(2.5rem, 6vw, 5rem)',
              color: 'var(--text-primary)',
              letterSpacing: '-0.02em',
            }}
          >
            Welcome aboard
          </h2>
          <p className="text-sm uppercase tracking-widest mb-6" style={{ color: 'var(--text-muted)' }}>
            WE'RE EXCITED TO PARTNER WITH YOU!
          </p>
          <a href="/upload" className="btn-dark inline-block">
            Complete intake form
          </a>
        </div>
      </section>

      {/* Congratulations section */}
      <section className="py-24 px-6 relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-0 left-0 w-72 h-72 iridescent-blob opacity-20"
               style={{ animation: 'float 8s ease-in-out infinite' }} />
        </div>
        <div className="relative z-10 max-w-3xl mx-auto text-center">
          <span className="badge mb-8">CONGRATULATIONS</span>
          <h2 className="heading-lg mt-6 max-w-lg mx-auto">
            This is the first step to real impact and better results.
          </h2>
          <a
            className="btn-outlined mt-8 inline-block"
            href="/results"
          >
            Explore your toolkit
          </a>
        </div>
      </section>

      {/* Upload section preview */}
      <section className="py-16 px-6">
        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16">
          <div>
            <span className="badge mb-6">GET STARTED</span>
            <h2 className="heading-lg mt-4">
              Help us personalize your setup
            </h2>
          </div>
          <div>
            <UploadPage compact />
          </div>
        </div>
      </section>

      <StepsSection />
      <Footer />
    </>
  );
}

export default function App() {
  const location = useLocation();

  return (
    <AuthProvider>
      <ResultsProvider>
      <div className="w-full min-h-screen" style={{ background: 'var(--bg-primary)' }}>
        <Navbar />

        {/* Top padding for fixed navbar */}
        <div className="pt-[72px]">
          <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
              <Route path="/" element={
                <PageWrapper><HomePage /></PageWrapper>
              } />
              <Route path="/upload" element={
                <PageWrapper>
                  <div className="max-w-4xl mx-auto px-6 py-12">
                    <UploadPage />
                  </div>
                </PageWrapper>
              } />
              <Route path="/results" element={
                <PageWrapper>
                  <div className="max-w-6xl mx-auto px-6 py-12 space-y-16">
                    <ExtractedPage />
                    <div className="section-divider" />
                    <ClassificationPage />
                    <div className="section-divider" />
                    <ClusteringPage />
                    <div className="section-divider" />
                    <PrioritizationPage />
                    <div className="section-divider" />
                    <SummaryPage />
                  </div>
                </PageWrapper>
              } />
              <Route path="/integrations" element={
                <PageWrapper><IntegrationsPage /></PageWrapper>
              } />
              <Route path="/integrations/jira" element={
                <PageWrapper><JiraConsole /></PageWrapper>
              } />
              <Route path="/integrations/slack" element={
                <PageWrapper><SlackConsole /></PageWrapper>
              } />
              <Route path="/integrations/github" element={
                <PageWrapper><GitHubConsole /></PageWrapper>
              } />
              <Route path="/settings" element={
                <PageWrapper>
                  <div className="max-w-3xl mx-auto px-6 py-12">
                    <SettingsPage />
                  </div>
                </PageWrapper>
              } />
              {/* Fallback to home */}
              <Route path="*" element={
                <PageWrapper><HomePage /></PageWrapper>
              } />
            </Routes>
          </AnimatePresence>
        </div>
      </div>
      </ResultsProvider>
    </AuthProvider>
  );
}
