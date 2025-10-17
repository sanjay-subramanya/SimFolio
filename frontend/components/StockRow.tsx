'use client';

import React, { useEffect, useState } from 'react';
import { Autocomplete, TextField, IconButton, Grid, FormHelperText } from '@mui/material';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';

// TYPE DEFINITIONS
interface RowData {
  id: number;
  stock: string | null;
  shares: string;
  error: string | null;
}

interface StockRowProps {
  rowData: RowData;
  availableStocks: string[];
  onStockChange: (id: number, newValue: string | null) => void;
  onSharesChange: (id: number, newValue: string) => void;
  onDelete: (id: number) => void;
}

// A presentational component for a single row in the portfolio input form.
const StockRow: React.FC<StockRowProps> = ({
  rowData,
  availableStocks,
  onStockChange,
  onSharesChange,
  onDelete,
}) => {
  const { id, stock, shares, error } = rowData;

  return (
    <Grid container spacing={2} alignItems="flex-start">
      <Grid size={{ xs: 12, sm: 6 }}>

        <Autocomplete
          fullWidth
          value={stock}
          onChange={(event, newValue: string | null) => {
            onStockChange(id, newValue);
          }}
          options={availableStocks}
          renderInput={(params) => (
            <TextField {...params} label="Select Stock" variant="outlined" />
          )}
          size="small"
        />
      </Grid>

      <Grid size={{ xs: 9, sm: 4 }}>
        <TextField
          fullWidth
          type="number"
          label="Shares"
          variant="outlined"
          value={shares}
          onChange={(e) => onSharesChange(id, e.target.value)}
          inputProps={{
            min: "1",
            max: "10000",
            step: "1",
          }}
          // The component is disabled if no stock is selected
          disabled={!stock}
          error={!!error}
          size="small"
        />
        {error && <FormHelperText error>{error}</FormHelperText>}
      </Grid>
      
      <Grid size={{ xs: 3, sm: 2 }} sx={{ textAlign: 'right' }}>
        <IconButton
          aria-label="delete row"
          onClick={() => onDelete(id)}
          color="warning"
        >
          <DeleteOutlineIcon />
        </IconButton>
      </Grid>
    </Grid>
  );
};

export default React.memo(StockRow);
