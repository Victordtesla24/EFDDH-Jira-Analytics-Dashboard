import React, { useState, useEffect } from 'react';
import { Container, CssBaseline, Typography, AppBar, Toolbar, Button, Paper, Grid, TextField, Tooltip, IconButton } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import InfoIcon from '@material-ui/icons/Info';

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  appBar: {
    marginBottom: theme.spacing(4),
  },
  title: {
    flexGrow: 1,
  },
  paper: {
    padding: theme.spacing(4),
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
  form: {
    '& > *': {
      margin: theme.spacing(1),
      width: '100%',
    },
  },
  button: {
    marginTop: theme.spacing(2),
  },
  infoButton: {
    marginLeft: theme.spacing(1),
  },
}));

// CSV loading and parsing functions
const loadCSVData = async () => {
  try {
    const response = await fetch('/EFDDH-Jira-12Nov.csv');
    const csvText = await response.text();
    return csvText;
  } catch (error) {
    console.error('Error loading CSV:', error);
    return null;
  }
};

const parseCSVData = (csvText) => {
  if (!csvText) return { headers: [], data: [] };
  
  const lines = csvText.split('\n');
  const headers = lines[0].split(',');
  
  const data = lines.slice(1).map(line => {
    const values = [];
    let inQuotes = false;
    let currentValue = '';
    
    for (let char of line) {
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        values.push(currentValue);
        currentValue = '';
      } else {
        currentValue += char;
      }
    }
    values.push(currentValue);
    return values;
  });

  return { headers, data };
};

function App() {
  const classes = useStyles();
  const [csvData, setCSVData] = useState({ headers: [], data: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const csvText = await loadCSVData();
        if (csvText) {
          const parsedData = parseCSVData(csvText);
          setCSVData(parsedData);
        } else {
          setError('Failed to load CSV data');
        }
      } catch (err) {
        setError('Error processing CSV data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  return (
    <div className={classes.root}>
      <CssBaseline />
      <AppBar position="static" className={classes.appBar}>
        <Toolbar>
          <Typography variant="h6" className={classes.title}>
            EFDDH Jira Issues
          </Typography>
        </Toolbar>
      </AppBar>
      <Container>
        {loading && <Typography>Loading...</Typography>}
        {error && <Typography color="error">{error}</Typography>}
        {!loading && !error && (
          <Paper className={classes.paper}>
            <div style={{ overflowX: 'auto' }}>
              <table>
                <thead>
                  <tr>
                    {csvData.headers.map((header, index) => (
                      <th key={index}>{header}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {csvData.data.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                      {row.map((cell, cellIndex) => (
                        <td key={cellIndex}>{cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Paper>
        )}
      </Container>
    </div>
  );
}

export default App;