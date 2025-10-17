"use client";

import React from 'react';
import PortfolioInput from '@/components/PortfolioInput';
import Providers from "./providers";
import { CssBaseline, Container, Typography, Box, createTheme } from '@mui/material';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 700,
    },
  },
});

export default function HomePage() {
  return (
    <Providers>
      <CssBaseline />
      <Container component="main" maxWidth="md">
        <Box
          sx={{
            marginTop: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}>
          <Typography component="h1" variant="h4" gutterBottom>
            SimFolio
          </Typography>
          <Typography component="p" color="text.secondary" sx={{ mb: 4, textAlign: 'center' }}>
            Test what-if scenarios and understand your portfolio's risk exposure in seconds.
          </Typography>
          <PortfolioInput/>
        </Box>
      </Container>
    </Providers>
  );
}
