import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

export type ThemeMode = 'light' | 'dark' | 'system';
const KEY = 'pa-theme';
const ThemeContext = createContext<{ mode: ThemeMode; setMode: (mode: ThemeMode) => void }>({ mode: 'system', setMode: () => undefined });

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<ThemeMode>(() => {
    const stored = localStorage.getItem(KEY);
    return stored === 'light' || stored === 'dark' || stored === 'system' ? stored : 'system';
  });
  useEffect(() => {
    localStorage.setItem(KEY, mode);
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const update = () => { document.documentElement.dataset.theme = mode === 'system' ? (media.matches ? 'dark' : 'light') : mode; };
    update(); media.addEventListener('change', update);
    return () => media.removeEventListener('change', update);
  }, [mode]);
  return <ThemeContext.Provider value={{ mode, setMode }}>{children}</ThemeContext.Provider>;
}

export const useTheme = () => useContext(ThemeContext);
