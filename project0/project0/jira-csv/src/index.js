const express = require('express');
const fs = require('fs');
const csv = require('csv-parser');
const app = express();
const port = 3000;

app.use(express.static('public'));

app.get('/data', (req, res) => {
  const results = [];
  fs.createReadStream('public/EFDDH-Jira-12Nov.csv')
    .pipe(csv())
    .on('data', (data) => results.push(data))
    .on('end', () => {
      res.json(results);
    });
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
