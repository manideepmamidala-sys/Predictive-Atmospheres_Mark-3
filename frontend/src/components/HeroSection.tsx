import React from 'react';

const HeroSection: React.FC = () => {
  return (
    <section className="relative w-full h-screen flex flex-col justify-center items-center overflow-hidden border-b border-border">
      {/* Fallback dark background in case video fails */}
      <div className="absolute inset-0 bg-background z-0" />
      
      {/* Content */}
      <div className="z-10 text-center px-4">
        <h1 className="text-5xl md:text-7xl font-bold mb-6 tracking-tight uppercase">
          Predictive Atmospheres
        </h1>
        <p className="text-lg md:text-2xl font-light opacity-80 max-w-2xl mx-auto">
          Transitioning architecture from subjective intuition to objective predictability.
        </p>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-10 animate-bounce z-10 flex flex-col items-center">
        <span className="text-sm opacity-50 uppercase tracking-widest mb-2">Scroll</span>
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="square" strokeLinejoin="miter">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </div>
    </section>
  );
};

export default HeroSection;
