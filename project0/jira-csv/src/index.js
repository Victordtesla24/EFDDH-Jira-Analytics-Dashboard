import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import csvData from '../public/EFDDH-Jira-12Nov.csv';

// Add error handling for CSV import
if (!csvData) {
  console.error('Failed to load CSV data');
}

ReactDOM.render(
  <App initialData={csvData} />,
  document.getElementById('root')
);