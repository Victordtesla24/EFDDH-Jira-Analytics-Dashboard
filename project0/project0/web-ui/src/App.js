const ITEMS_PER_PAGE = 25;
let currentPage = 1;
let filteredData = [];
let allData = [];

// ...existing loadCSV function...

// ...existing parseCSV function...

function filterData(searchText) {
    if (!searchText) {
        filteredData = allData;
    } else {
        searchText = searchText.toLowerCase();
        filteredData = allData.filter(row => 
            row.some(cell => cell.toString().toLowerCase().includes(searchText))
        );
    }
    currentPage = 1;
    displayData(headers, filteredData);
    updatePagination();
}

function displayData(headers, data) {
    const headerRow = document.getElementById('headerRow');
    const tableBody = document.getElementById('tableBody');
    
    // Clear existing content
    headerRow.innerHTML = '';
    tableBody.innerHTML = '';
    
    // Display headers
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });

    // Calculate pagination
    const startIdx = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIdx = startIdx + ITEMS_PER_PAGE;
    const paginatedData = data.slice(startIdx, endIdx);

    // Display data
    paginatedData.forEach(row => {
        if (row.length > 1) { // Skip empty rows
            const tr = document.createElement('tr');
            row.forEach(cell => {
                const td = document.createElement('td');
                td.textContent = cell;
                tr.appendChild(td);
            });
            tableBody.appendChild(tr);
        }
    });

    // Hide loading message
    document.getElementById('loading').style.display = 'none';
}

function updatePagination() {
    const totalPages = Math.ceil(filteredData.length / ITEMS_PER_PAGE);
    const pageInfo = document.getElementById('pageInfo');
    const prevButton = document.getElementById('prevPage');
    const nextButton = document.getElementById('nextPage');

    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    prevButton.disabled = currentPage === 1;
    nextButton.disabled = currentPage === totalPages;
}

function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const prevButton = document.getElementById('prevPage');
    const nextButton = document.getElementById('nextPage');

    searchInput.addEventListener('input', (e) => {
        filterData(e.target.value);
    });

    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            displayData(headers, filteredData);
            updatePagination();
        }
    });

    nextButton.addEventListener('click', () => {
        const totalPages = Math.ceil(filteredData.length / ITEMS_PER_PAGE);
        if (currentPage < totalPages) {
            currentPage++;
            displayData(headers, filteredData);
            updatePagination();
        }
    });
}

async function init() {
    const csvText = await loadCSV();
    if (csvText) {
        const { headers: headerData, data: rowData } = parseCSV(csvText);
        headers = headerData;
        allData = rowData;
        filteredData = rowData;
        displayData(headers, filteredData);
        updatePagination();
        setupEventListeners();
    } else {
        document.getElementById('loading').textContent = 'Error loading data';
    }
}

init();