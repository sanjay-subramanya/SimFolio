"use client";
import React, { useState, useEffect } from 'react';
import StockRow from './StockRow';
import HypotheticalInput from './HypotheticalInput';
import { Box, Button, Card, CardContent, Stack, Typography, Alert } from '@mui/material';

// TYPE DEFINITIONS 
export interface PortfolioStock {
  stock: string;
  shares: number;
}

interface RowState {
  id: number;
  stock: string | null;
  shares: string; 
  error: string | null;
}

const ALL_STOCKS = [
    // Tech
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", 
    "AMD", "INTC", "QCOM", "AVGO", "TSM", "ASML", "MU",
    "ADBE", "CRM", "ORCL", "SAP", "SNOW", "NOW", "MSI",
    "IBM", "DELL", "HPQ", "CSCO", "NOK", "ERIC",
    "NET", "PANW", "CRWD", "ZS", "DDOG", "TEAM",
    "SHOP", "PYPL",
    
    // Finance
    "JPM", "BAC", "WFC", "C", "GS", "MS",
    "MET", "MA", "AXP", "V",
    "BLK", "SCHW", "SPGI", "MCO",
    
    // Energy
    "XOM", "CVX", "COP", "SLB", "OXY", "EOG", "MPC", "VLO",
    "NEE", "DUK", "SO", "AEP", "EXC",
    "FSLR", "ENPH", "SEDG", "HAL",
    "BKR", "KMI",  "BE", "PLUG",
].sort()


/**
 * A component to dynamically manage a list of stock portfolio inputs.
 * It handles adding, removing, and validating rows of stocks and their share quantities.
 */
export default function PortfolioInput() {
  // State for managing the list of input rows
  const [rows, setRows] = useState<RowState[]>([
    { id: Date.now(), stock: null, shares: '', error: null }
  ]);
  
  // State for submission status message for Step 1
  const [submissionMessage, setSubmissionMessage] = useState<string | null>(null);
  
  // State to hold the submitted portfolio data and control the step
  const [submittedPortfolio, setSubmittedPortfolio] = useState<PortfolioStock[] | null>(null);

  // Memoize the set of selected stocks for efficient lookup
  const selectedStocks = React.useMemo(() =>
    new Set(rows.map(row => row.stock).filter(Boolean))
  , [rows]);

  /**
   * Filters the master stock list to get available options for a given row.
   * A stock is available if it's not selected in another row OR if it's the one
   * currently selected in the row being considered.
   * @param {string | null} currentStock - The stock currently selected in the row.
   * @returns {string[]} An array of available stock symbols.
   */
  const getAvailableStocks = (currentStock: string | null): string[] => {
    return ALL_STOCKS.filter(stock => !selectedStocks.has(stock) || stock === currentStock);
  }; 

  /**
   * Handles changes to the stock selection in a row.
   * @param {number} id - The ID of the row being changed.
   * @param {string | null} newStock - The newly selected stock symbol.
   */
  const handleStockChange = (id: number, newStock: string | null) => {
    let isLastRow = false;
    const updatedRows = rows.map((row, index) => {
      if (row.id === id) {
        if (index === rows.length - 1) isLastRow = true;
        // When a stock is selected, default shares to 1 if empty
        const newShares = newStock && !row.shares ? '1' : row.shares;
        return { ...row, stock: newStock, shares: newShares };
      }
      return row;
    });

    // If a stock was selected in the last row and we haven't hit the cap, add a new row.
    if (isLastRow && newStock && rows.length < 12) {
      setRows([...updatedRows, { id: Date.now(), stock: null, shares: '', error: null }]);
    } else {
      setRows(updatedRows);
    }
  };

  /**
   * Handles changes to the share quantity input in a row and validates it.
   * @param {number} id - The ID of the row being changed.
   * @param {string} newShares - The new value from the shares input.
   */
  const handleSharesChange = (id: number, newShares: string) => {
    setRows(rows.map(row => {
      if (row.id === id) {
        const numShares = Number(newShares);
        let error: string | null = null;
        // Validate only if the input is not empty
        if (newShares && (numShares < 1 || numShares > 10000 || !Number.isInteger(numShares))) {
          error = "Please enter a whole number between 1 and 10000.";
        }
        return { ...row, shares: newShares, error };
      }
      return row;
    }));
  };

  /**
   * Removes a row from the list.
   * @param {number} id - The ID of the row to delete.
   */
  const handleDeleteRow = (id: number) => {
    const newRows = rows.filter(row => row.id !== id);
    // Ensure there is always at least one row present
    if (newRows.length === 0) {
      setRows([{ id: Date.now(), stock: null, shares: '', error: null }]);
    } else {
      setRows(newRows);
    }
  };

  /**
   * Handles the form submission (Step 1).
   * It validates the inputs and prepares the data for the next step.
   */
  const handleSubmit = () => {
    setSubmissionMessage(null);
    setSubmittedPortfolio(null);

    // 1. Basic Filtering and Validation Checks
    const validRows = rows.filter(row => row.stock && !row.error);
    
    if (validRows.length === 0) {
      setSubmissionMessage("Error: Please add at least one valid stock holding.");
      return;
    }
    
    // 2. Check for any rows with a selected stock but empty/invalid shares
    const incompleteOrInvalidRows = rows.some(row => row.stock && (!row.shares || !!row.error));
    if(incompleteOrInvalidRows) {
       setSubmissionMessage("Error: Please ensure all selected stocks have a valid share quantity (1-10000).");
       return;
    }

    // 3. Prepare Data
    const portfolioData: PortfolioStock[] = validRows.map(row => ({
      stock: row.stock!,
      shares: Number(row.shares),
    }));

    // 4. Move to Step 2
    console.log("Portfolio validated. Moving to Step 2:", portfolioData);
    setSubmittedPortfolio(portfolioData);
  };

  // Handler to go back to Step 1
  const handleBack = () => {
    setSubmittedPortfolio(null);
    setSubmissionMessage(null);
  };


  if (submittedPortfolio) {
    // RENDER STEP 2
    return <HypotheticalInput 
      initialPortfolio={submittedPortfolio} 
      onBack={handleBack} 
    />;
  }
  
  // RENDER STEP 1
  return (
    <Card sx={{ width: '100%', p: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Step 1: Define Holdings
        </Typography>
        <Stack spacing={2}>
          {rows.map((row) => (
            <StockRow
              key={row.id}
              rowData={row}
              availableStocks={getAvailableStocks(row.stock)}
              onStockChange={handleStockChange}
              onSharesChange={handleSharesChange}
              onDelete={handleDeleteRow}
            />
          ))}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', pt: 2 }}>
            <Button variant="contained" color="secondary" onClick={handleSubmit}>
              Next: Enter Changes &rarr;
            </Button>
          </Box>
          {submissionMessage && (
            <Alert severity={'error'}>
              {submissionMessage}
            </Alert>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}