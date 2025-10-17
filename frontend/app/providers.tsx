"use client";

import React from "react";
import { ThemeProvider, CssBaseline, createTheme } from "@mui/material";
import { CacheProvider } from "@emotion/react";
import createCache from "@emotion/cache";

interface Props {
  children: React.ReactNode;
}

const clientSideEmotionCache = createCache({ key: "css", prepend: true });

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#90caf9" },
    background: { default: "#121212", paper: "#1e1e1e" },
  },
  typography: { fontFamily: '"Inter", "Roboto", sans-serif', h4: { fontWeight: 700 } },
});

export default function Providers({ children }: Props) {
  return (
    <CacheProvider value={clientSideEmotionCache}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </CacheProvider>
  );
}
