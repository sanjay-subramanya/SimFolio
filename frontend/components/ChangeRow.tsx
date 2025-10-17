'use client';

import React from 'react';
import {
  TextField,
  IconButton,
  Grid,
  InputAdornment,
  FormHelperText,
  Autocomplete,
} from '@mui/material';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';

export interface ChangeRowData {
  id: number;
  stock: string | null;
  change: string;
  error: string | null;
}

interface ChangeRowProps {
  rowData: ChangeRowData;
  availableStocks: string[];
  onStockChange: (id: number, newValue: string | null) => void;
  onChange: (id: number, newValue: string) => void;
  onDelete: (id: number) => void;
}

const ChangeRow: React.FC<ChangeRowProps> = ({
  rowData,
  availableStocks,
  onStockChange,
  onChange,
  onDelete,
}) => {
  const { id, stock, change, error } = rowData;

  return (
    <Grid container spacing={2} alignItems="flex-start">
      <Grid size={{ xs: 12, sm: 6 }}>
        <Autocomplete
          fullWidth
          size="small"
          value={stock}
          onChange={(_, newValue: string | null) => onStockChange(id, newValue)}
          options={availableStocks}
          getOptionLabel={(option) =>
            typeof option === 'string' ? option : String(option)
          }
          isOptionEqualToValue={(option, value) => option === value}
          renderInput={(params) => (
            <TextField {...params} label="Select Stock to Change" variant="outlined" />
          )}
        />
      </Grid>

      <Grid size={{ xs: 9, sm: 4 }}>
        <TextField
          fullWidth
          size="small"
          type="number"
          label="Percentage Change"
          variant="outlined"
          value={change}
          onChange={(e) => onChange(id, e.target.value)}
          disabled={!stock}
          inputProps={{
            min: '-100',
            max: '100',
            step: '0.1',
          }}
          InputProps={{
            endAdornment: <InputAdornment position="end">%</InputAdornment>,
          }}
          error={!!error}
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

export default React.memo(ChangeRow);
