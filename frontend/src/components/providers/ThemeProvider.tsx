'use client';

import { createContext, useContext, useEffect, ReactNode } from 'react';
import { usePrefersDarkScheme } from '@/lib/hooks/usePrefersDarkScheme';
import { useStoredValue } from '@/lib/hooks/useStoredValue';

type Theme = 'light' | 'dark';

const ThemeContext = createContext<{ theme: Theme; toggle: () => void }>({
  theme: 'light',
  toggle: () => {},
});

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [saved, setSaved] = useStoredValue('theme');
  const prefersDark = usePrefersDarkScheme();
  const theme: Theme = saved === 'dark' || saved === 'light' ? saved : prefersDark ? 'dark' : 'light';

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  const toggle = () => setSaved(theme === 'dark' ? 'light' : 'dark');

  return <ThemeContext.Provider value={{ theme, toggle }}>{children}</ThemeContext.Provider>;
}

export const useTheme = () => useContext(ThemeContext);
