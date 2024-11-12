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
