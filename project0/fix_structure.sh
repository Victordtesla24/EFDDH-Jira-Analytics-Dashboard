#!/bin/bash

# Base directory
BASE_DIR="/Users/vicd/cursor-tutor/project0"

# Create main project directories
echo "Creating project directory structure..."

mkdir -p $BASE_DIR/{jira-csv,resume-optimizer}

# Create Jira CSV project structure
mkdir -p $BASE_DIR/jira-csv/{public,src}
touch $BASE_DIR/jira-csv/{package.json,README.md,.gitignore}
touch $BASE_DIR/jira-csv/public/{index.html,style.css}
touch $BASE_DIR/jira-csv/src/{index.js,App.js}

# Copy CSV file to public directory
cp "/Users/vicd/Downloads/EFDDH-Jira-12Nov.csv" "$BASE_DIR/jira-csv/public/"

# Create basic package.json
cat > $BASE_DIR/jira-csv/package.json << EOL
{
  "name": "jira-csv-viewer",
  "version": "1.0.0",
  "description": "JIRA CSV Data Viewer",
  "main": "src/index.js",
  "scripts": {
    "start": "python -m http.server 8000"
  },
  "dependencies": {}
}
EOL

# Create basic HTML file
cat > $BASE_DIR/jira-csv/public/index.html << EOL
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EFDDH Jira Issues</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>EFDDH Jira Issues</h1>
        <div id="loading" class="loading">Loading...</div>
        <table id="issuesTable">
            <thead><tr id="headerRow"></tr></thead>
            <tbody id="tableBody"></tbody>
        </table>
    </div>
    <script src="../src/App.js"></script>
</body>
</html>
EOL

# Create basic CSS file
cat > $BASE_DIR/jira-csv/public/style.css << EOL
body {
    font-family: Arial, sans-serif;
    margin: 20px;
    padding: 0;
}
.container { width: 100%; }
table {
    border-collapse: collapse;
    width: 100%;
}
th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}
th { background-color: #f2f2f2; }
.loading { text-align: center; padding: 20px; }
EOL

# Move App.js to src directory
cat > $BASE_DIR/jira-csv/src/App.js << EOL
// CSV loading and parsing functions
async function loadCSV() {
    try {
        const response = await fetch('./EFDDH-Jira-12Nov.csv');
        const csvText = await response.text();
        return csvText;
    } catch (error) {
        console.error('Error loading CSV:', error);
        return null;
    }
}

// ...rest of the existing App.js code...

init();
EOL

echo "Directory structure created successfully!"
echo "To run the Jira CSV viewer:"
echo "1. cd $BASE_DIR/jira-csv"
echo "2. python -m http.server 8000"
echo "3. Open http://localhost:8000/public/"