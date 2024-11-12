import React, { useEffect, useState } from 'react';
import Chart from 'chart.js/auto';

function App() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch('/data')
      .then(response => response.json())
      .then(data => setData(data));
  }, []);

  useEffect(() => {
    if (data.length > 0) {
      const ctx = document.getElementById('myChart').getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.map(item => item['Issue key']),
          datasets: [{
            label: 'Story Points',
            data: data.map(item => item['Custom field (Story Points)']),
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          }]
        },
        options: {
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    }
  }, [data]);

  return (
    <div className="App">
      <h1>JIRA Data Chart</h1>
      <canvas id="myChart"></canvas>
    </div>
  );
}

export default App;
