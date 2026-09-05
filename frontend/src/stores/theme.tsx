import React, { createContext, useContext, useEffect, useState } from "react";

type Theme = "light" | "dark" | "system";
type Ctx = { theme: Theme; setTheme: (t: Theme) => void; resolved: "light" | "dark" };

const ThemeContext = createContext<Ctx>({ theme: "system", setTheme: () => {}, resolved: "light" });

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    try {
      return (localStorage.getItem("bailanysta_theme") as Theme) ?? "system";
    } catch {
      return "system";
    }
  });

  const [resolved, setResolved] = useState<"light" | "dark">("light");

  useEffect(() => {
    try {
      localStorage.setItem("bailanysta_theme", theme);
    } catch {}
    const mql = window.matchMedia("(prefers-color-scheme: dark)");
    const apply = () => {
      const r: "light" | "dark" = theme === "system" ? (mql.matches ? "dark" : "light") : theme;
      setResolved(r);
      document.documentElement.classList.toggle("dark", r === "dark");
    };
    apply();
    if (theme === "system") {
      mql.addEventListener("change", apply);
      return () => mql.removeEventListener("change", apply);
    }
  }, [theme]);

  return <ThemeContext.Provider value={{ theme, setTheme, resolved }}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  return useContext(ThemeContext);
}
