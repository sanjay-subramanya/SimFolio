'use client';
import React, { useRef, useEffect, useState, useMemo } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Collapse,
  Stack,
  Typography,
  Alert,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Paper,
} from '@mui/material';
import ChangeRow, { ChangeRowData } from './ChangeRow';
import { PortfolioStock } from './PortfolioInput';
import { NEXT_PUBLIC_BACKEND_URL } from "@/lib/config";

interface HypotheticalInputProps {
  initialPortfolio: PortfolioStock[];
  onBack: () => void;
}

// A component to input hypothetical percentage changes for a submitted portfolio.
export default function HypotheticalInput({
  initialPortfolio,
  onBack,
}: HypotheticalInputProps) {
  // Array of available stock symbols from the initial portfolio
  const ALL_STOCKS_FROM_PORTFOLIO = useMemo(
    () => initialPortfolio.map((item) => item.stock),
    [initialPortfolio]
  );

  // State for managing the list of input rows
  const [rows, setRows] = useState<ChangeRowData[]>([
    { id: Date.now(), stock: null, change: '', error: null },
  ]);

  const [submissionMessage, setSubmissionMessage] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  
  const resultsRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
  if (analysisResult && resultsRef.current) {
    const scrollOptions = {
      behavior: 'smooth',
      block: 'start', 
      inline: 'nearest'
    };
    
    // Longer timeout if you want to wait for animation to complete
    setTimeout(() => {
      resultsRef.current.scrollIntoView(scrollOptions);
    }, 300);
  }
}, [analysisResult]);

  // Set of stocks currently selected in the change rows
  const selectedStocks = useMemo(
    () => new Set(rows.map((row) => row.stock).filter(Boolean)),
    [rows]
  );

  // Available stocks for the dropdown: stocks in the portfolio that haven't been selected yet.
  const getAvailableStocks = (currentStock: string | null): string[] => {
    return ALL_STOCKS_FROM_PORTFOLIO.filter(
      (stock) => !selectedStocks.has(stock) || stock === currentStock
    ).sort();
  };

  // Check if any row has an error
  const hasError = useMemo(() => rows.some((row) => row.error), [rows]);

  const handleStockChange = (id: number, newStock: string | null) => {
    let isLastRow = false;
    const updatedRows = rows.map((row, index) => {
      if (row.id === id) {
        if (index === rows.length - 1) isLastRow = true;
        const newChange = newStock && !row.change ? '0' : row.change;
        return { ...row, stock: newStock, change: newChange, error: null };
      }
      return row;
    });

    if (
      isLastRow &&
      newStock &&
      rows.length < ALL_STOCKS_FROM_PORTFOLIO.length &&
      rows.length < 12
    ) {
      setRows([...updatedRows, { id: Date.now(), stock: null, change: '', error: null }]);
    } else {
      setRows(updatedRows);
    }
  };

  const handleChange = (id: number, newChange: string) => {
    setSubmissionMessage(null);
    setRows((prevRows) =>
      prevRows.map((row) => {
        if (row.id === id) {
          const numChange = Number(newChange);
          let error: string | null = null;

          if (newChange && (isNaN(numChange) || numChange < -100 || numChange > 100)) {
            error = 'Please enter a number between -100 and 100.';
          }

          return { ...row, change: newChange, error };
        }
        return row;
      })
    );
  };

  const handleDeleteRow = (id: number) => {
    const newRows = rows.filter((row) => row.id !== id);
    if (newRows.length === 0) {
      setRows([{ id: Date.now(), stock: null, change: '', error: null }]);
    } else {
      setRows(newRows);
    }
  };

  // Final submission handler
  const handleFinalSubmit = async () => {
    setSubmissionMessage(null);
    const validRows = rows.filter((row) => row.stock && !row.error);

    if (validRows.length === 0) {
      setSubmissionMessage('Error: Please select at least one stock to apply a change.');
      return;
    }

    if (hasError) {
      setSubmissionMessage('Error: Please correct the input errors before simulating.');
      return;
    }

    const nonZeroChangeExists = validRows.some(
      (row) => Number(row.change || '0') !== 0
    );
    if (!nonZeroChangeExists) {
      setSubmissionMessage(
        'Error: At least one selected stock must have a non-zero percentage change (-100 to 100, excluding 0).'
      );
      return;
    }

    // Prepare payload for backend
    const payload = {
      portfolio: initialPortfolio.map((stock) => ({
        stock: stock.stock,
        shares: stock.shares,
      })),
      shocks: validRows.map((row) => ({
        stock: row.stock!,
        change_percent: Number(row.change),
      })),
    };

    try {
      // Clear previous results before new submission
      setAnalysisResult(null);

      const response = await fetch(`${NEXT_PUBLIC_BACKEND_URL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || 'Request failed');
      }

      const result = await response.json();
      console.log('Backend /analyze response:', result);

      setAnalysisResult(result);
      setSubmissionMessage('Success! Analysis complete.');
    } catch (err: any) {
      console.error('Error calling /analyze:', err);
      setSubmissionMessage(`Error: Failed to analyze (${err.message})`);
    }
  };

  return (
  <Card sx={{ width: '100%', p: 2 }}>
    <CardContent>
      <Typography variant="h6" gutterBottom>
        Step 2: Simulate Price Changes
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Your selected portfolio stocks: {ALL_STOCKS_FROM_PORTFOLIO.join(', ')}
      </Typography>

      <Stack spacing={2} pt={1}>
        {rows.map((row) => (
          <ChangeRow
            key={row.id}
            rowData={row}
            availableStocks={getAvailableStocks(row.stock)}
            onStockChange={handleStockChange}
            onChange={handleChange}
            onDelete={handleDeleteRow}
          />
        ))}

        {submissionMessage && (
          <Alert
            severity={submissionMessage.startsWith('Error') ? 'error' : 'success'}
            sx={{ mt: 2 }}
          >
            {submissionMessage}
          </Alert>
        )}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', pt: 2 }}>
          <Button variant="outlined" onClick={onBack}>
            &larr; Back to Portfolio
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleFinalSubmit}
            disabled={hasError || rows.filter((r) => r.stock).length === 0}
          >
            See What Happens
          </Button>
        </Box>
      </Stack>

      <div ref={resultsRef}>
      <Collapse in={!!analysisResult} timeout={500}>
        {analysisResult && (
          <Card 
            sx={{ 
              mt: 3,
              p: 0,
              backgroundColor: 'transparent',
              backgroundImage: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
              border: '1px solid #404040',
              boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
              overflow: 'hidden'
            }}>
            <Box 
              sx={{ 
                p: 3,
                backgroundColor: 'rgba(0,0,0,0.4)',
                borderBottom: '1px solid #404040'
              }}>
              <Typography 
                variant="h5" 
                gutterBottom 
                sx={{ 
                  color: '#ffffff',
                  fontWeight: '600',
                  mb: 1
                }}>
                📊 Scenario Outcomes
              </Typography>
              
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, alignItems: 'center' }}>
                <Typography 
                  variant="body1" 
                  sx={{ 
                    color: '#e0e0e0',
                    fontSize: '1.1rem'
                  }}>
                  <strong>Overall Portfolio Impact:</strong>{' '}
                  <Box
                    component="span"
                    sx={{
                      color: analysisResult.portfolio_impact >= 0 ? '#4caf50' : '#f44336',
                      fontWeight: 'bold',
                    }}>
                    {analysisResult.portfolio_impact.toFixed(2)}%
                  </Box>
                </Typography>
                
                {/* Add timestamp (Optional) */}
                {/* <Typography 
                  variant="body2" 
                  sx={{ 
                    color: '#b0b0b0',
                    fontStyle: 'italic'
                  }}
                >
                  {new Date().toLocaleString()}
                </Typography> */}
              </Box>
            </Box>

            {/* Table Section */}
            <Box sx={{ p: 3 }}>
              <Typography 
                variant="h6" 
                gutterBottom 
                sx={{ 
                  color: '#ffffff',
                  mb: 2,
                  fontSize: '1.1rem',
                  textAlign: 'center'

                }}>
                Component Analysis
              </Typography>

              <TableContainer 
                component={Paper} 
                elevation={0}
                sx={{
                  backgroundColor: 'transparent',
                  border: '1px solid #404040',
                  borderRadius: '8px',
                  overflow: 'hidden'
                }}
              >
                <Table size="medium" aria-label="Hypothetical stock impact analysis">
                  <TableHead>
                    <TableRow sx={{ backgroundColor: 'rgba(0,0,0,0.3)' }}>
                      <TableCell sx={{ fontSize: '1rem', color: '#ffffff', fontWeight: '600' }}>
                        Stock
                      </TableCell>
                      <TableCell align="right" sx={{ fontSize: '1rem', color: '#ffffff', fontWeight: '600' }}>
                        Impact (%)
                      </TableCell>
                      <TableCell align="right" sx={{ fontSize: '1rem', color: '#ffffff', fontWeight: '600' }}>
                        Correlation
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {analysisResult.impacts.map((imp: any) => (
                      <TableRow
                        key={imp.stock}
                        sx={{ 
                          '&:last-child td, &:last-child th': { border: 0 },
                          backgroundColor: 'rgba(255,255,255,0.02)',
                          '&:hover': {
                            backgroundColor: 'rgba(255,255,255,0.05)',
                            transition: 'background-color 0.2s ease'
                          }
                        }}
                      >
                        <TableCell 
                          component="th" 
                          scope="row" 
                          sx={{ 
                            fontSize: '0.9rem',
                            color: '#e0e0e0',
                            borderColor: '#404040'
                          }}
                        >
                          {imp.stock}
                        </TableCell>
                        <TableCell
                          align="right"
                          sx={{
                            fontWeight: 'bold',
                            color: imp.impact_percent >= 0 ? '#4caf50' : '#f44336',
                            fontSize: '0.9rem',
                            borderColor: '#404040'
                          }}
                        >
                          {imp.impact_percent.toFixed(2)}
                        </TableCell>
                        <TableCell 
                          align="right" 
                          sx={{ 
                            fontSize: '0.9rem',
                            color: '#e0e0e0',
                            borderColor: '#404040'
                          }}
                        >
                          {imp.correlation !== null ? imp.correlation.toFixed(3) : '—'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          </Card>
        )}
      </Collapse>
    </div>
  </CardContent>
</Card>
);