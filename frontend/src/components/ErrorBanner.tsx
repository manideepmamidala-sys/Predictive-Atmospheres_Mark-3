import React from 'react';
import { usePlatformStore } from '../store/usePlatformStore';

const ErrorBanner: React.FC = () => {
  const error500 = usePlatformStore((state) => state.error500);

  if (!error500) return null;

  return (
    <div className="w-full bg-[#EF4444] text-white p-4 font-sans font-bold flex justify-center items-center z-50 sticky top-0">
      CRITICAL ERROR: {error500}
    </div>
  );
};

export default ErrorBanner;
