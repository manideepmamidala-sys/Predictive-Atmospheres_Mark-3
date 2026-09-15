import React from 'react';
import HeroSection from './components/HeroSection';
import ResearchNarrative from './components/ResearchNarrative';
import FindingsVisualizer from './components/FindingsVisualizer';
import InteractiveStudio from './components/InteractiveStudio';
import ErrorBanner from './components/ErrorBanner';

const App: React.FC = () => {
  return (
    <div className="w-full min-h-screen flex flex-col font-sans bg-background text-foreground">
      <ErrorBanner />
      <HeroSection />
      <ResearchNarrative />
      <FindingsVisualizer />
      <InteractiveStudio />
    </div>
  );
};

export default App;
