const draggableItems = document.querySelectorAll('.draggable-item');
const droppableAreaRows = document.getElementById('droppable-area-rows');
const droppableAreaCols = document.getElementById('droppable-area-cols');
const initialList = document.getElementById('initial-list');
const tableContainer = document.getElementById('table-container');
const filterContainer = document.getElementById('filter-container');

let offset = 0;
const limit = 50;
let isLoading = false;
let hasMoreData = true;
let tableData = [];
let filteredTableData = [];
let rowColumns = [];
let colColumns = [];

// Obtenez le nom de l'indicateur depuis l'URL actuelle
const pathArray = window.location.pathname.split('/');
const indicateur_name = decodeURIComponent(pathArray[pathArray.length - 1]);

draggableItems.forEach(item => {
    item.addEventListener('dragstart', handleDragStart);
});

droppableAreaRows.addEventListener('dragover', handleDragOver);
droppableAreaRows.addEventListener('drop', event => handleDrop(event, 'row'));

droppableAreaCols.addEventListener('dragover', handleDragOver);
droppableAreaCols.addEventListener('drop', event => handleDrop(event, 'col'));

initialList.addEventListener('dragover', handleDragOver);
initialList.addEventListener('drop', event => handleDrop(event, 'initial'));

function handleDragStart(event) {
    event.dataTransfer.setData('text/plain', event.target.dataset.column);
    event.dataTransfer.setData('source-id', event.target.id);
}

function handleDragOver(event) {
    event.preventDefault();
}

function handleDrop(event, type) {
    event.preventDefault();
    const column = event.dataTransfer.getData('text/plain');
    const sourceId = event.dataTransfer.getData('source-id');
    const draggedElement = document.querySelector(`[data-column="${column}"][id="${sourceId}"]`) || document.querySelector(`[data-column="${column}"]`);

    if (!draggedElement) return;

    if (draggedElement.parentElement) {
        draggedElement.parentElement.removeChild(draggedElement);
    }

    if (rowColumns.includes(column)) {
        rowColumns.splice(rowColumns.indexOf(column), 1);
    } else if (colColumns.includes(column)) {
        colColumns.splice(colColumns.indexOf(column), 1);
    }

    if (type === 'row' && !rowColumns.includes(column)) {
        rowColumns.push(column);
        addColumnToArea(column, droppableAreaRows, rowColumns, type);
    } else if (type === 'col' && !colColumns.includes(column)) {
        colColumns.push(column);
        addColumnToArea(column, droppableAreaCols, colColumns, type);
    } else if (type === 'initial') {
        addColumnToArea(column, initialList, null, type);
    }

    togglePlaceholders();
    sendColumnsToServer();
}

function addColumnToArea(column, area, columnList, type) {
    const newItem = document.createElement('div');
    newItem.classList.add('draggable-item');
    newItem.textContent = column;
    newItem.setAttribute('draggable', 'true');
    newItem.setAttribute('data-column', column);
    newItem.id = `drag-${column}-${Date.now()}`;
    newItem.addEventListener('dragstart', handleDragStart);

    if (type !== 'initial') {
        newItem.addEventListener('click', function () {
            area.removeChild(newItem);
            if (columnList) {
                columnList.splice(columnList.indexOf(column), 1);
            }
            togglePlaceholders();
            sendColumnsToServer();
        });
    }

    area.appendChild(newItem);
}

function togglePlaceholders() {
    const rowPlaceholder = droppableAreaRows.querySelector('#placeholder-rows');
    const colPlaceholder = droppableAreaCols.querySelector('#placeholder-cols');
    rowPlaceholder.style.display = droppableAreaRows.children.length > 1 ? 'none' : 'block';
    colPlaceholder.style.display = droppableAreaCols.children.length > 1 ? 'none' : 'block';
}

function sendColumnsToServer() {
    offset = 0;
    hasMoreData = true;
    tableData = []; 
    filteredTableData = [];
    tableContainer.innerHTML = '';
    loadData(offset, limit, true);
}

function loadData(offset, limit, isInitialLoad = false) {
    if (isLoading || !hasMoreData) {
        console.log('Load ignored: isLoading=', isLoading, 'hasMoreData=', hasMoreData);
        return;
    }
    isLoading = true;
    console.log('Fetching data: offset=', offset, 'limit=', limit);

    fetch('/process_columns?offset=' + offset + '&limit=' + limit, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            row_columns: rowColumns,
            col_columns: colColumns,
            value_column: 'Valeur',
            indicateur_name: indicateur_name
        })
    })
    .then(response => {
        if (!response.ok) throw new Error('Erreur réseau: ' + response.status);
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error('Server error:', data.error);
            isLoading = false;
            return;
        }
        
        if (data.data.length === 0) {
            hasMoreData = false;
        } else {
            hasMoreData = true;
        }
        
        const newRows = data.data.map(row => {
            const rowData = {};
            data.columns.forEach((col, index) => {
                rowData[col.join(' ')] = row[index];
            });
            return rowData;
        });

        tableData = tableData.concat(newRows);
        
        if (isInitialLoad) {
            if (!tableData.columns) {
                tableData.columns = data.columns;
            }
            applyFilters();
            generateFilters();
            generateTable({
                columns: tableData.columns,
                data: filteredTableData.map(row => {
                    return tableData.columns.map(col => row[col.join(' ')]);
                })
            });
        } else {
            // Chargements suivants : ajouter de nouvelles lignes
            const newFilteredRows = newRows.filter(row => doesRowMatchFilters(row, getActiveFilters()));
            appendRows({
                columns: data.columns,
                data: newFilteredRows.map(row => {
                     return data.columns.map(col => row[col.join(' ')]);
                })
            });
            mergeTableCells(); // <-- Ajout de l'appel pour fusionner les cellules après l'ajout
        }

        isLoading = false;
    })
    .catch(error => {
        console.error('Erreur:', error);
        isLoading = false;
    });
}

// Fonction pour récupérer les filtres actifs, nécessaire pour la nouvelle logique
function getActiveFilters() {
    const filters = {};
    const checkedCheckboxes = filterContainer.querySelectorAll('input[type="checkbox"]:checked');
    checkedCheckboxes.forEach(checkbox => {
        const column = checkbox.getAttribute('data-column');
        const value = checkbox.value;
        if (!filters[column]) {
            filters[column] = [];
        }
        filters[column].push(value);
    });
    return filters;
}

function generateTable(data) {
    tableContainer.innerHTML = '';

    const table = document.createElement('table');
    table.id = 'data-table';
    table.classList.add('w-full', 'border-collapse');

    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');

    const columns = data.columns;
    const levels = columns.length > 0 ? columns[0].length : 0;

    for (let level = 0; level < levels; level++) {
        const headerRow = document.createElement('tr');
        let previousValue = null;
        let colspan = 0;

        columns.forEach((col, index) => {
    const currentValue = col[level];

    if (currentValue === previousValue) {
        return; // <-- Correct ! Passe à l'itération suivante.
    } else {
                if (colspan > 1) {
                    headerRow.lastChild.setAttribute('colspan', colspan);
                }
                const th = document.createElement('th');
                th.textContent = currentValue || '';

                th.classList.add(
                    'sticky',
                    'top-0',
                    'z-10',
                    'bg-[#006B45]'
                );

                headerRow.appendChild(th);
                previousValue = currentValue;
                colspan = 1;
            }

            if (index === columns.length - 1 && colspan > 1) {
                headerRow.lastChild.setAttribute('colspan', colspan);
            }
        });
        thead.appendChild(headerRow);
    }

    data.data.forEach(row => {
        const tr = document.createElement('tr');
        columns.forEach((col, index) => {
            const td = document.createElement('td');
            td.textContent = row[index] || ' ';
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });

    table.appendChild(thead);
    table.appendChild(tbody);
    tableContainer.appendChild(table);
    mergeTableCells();
}

function appendRows(data) {
    const table = document.querySelector('#table-container table');
    const tbody = table.querySelector('tbody') || document.createElement('tbody');
    
    data.data.forEach(row => {
        const tr = document.createElement('tr');
        data.columns.forEach((col, index) => {
            const td = document.createElement('td');
            td.textContent = row[index] || ' ';
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    
    if (!table.querySelector('tbody')) {
        table.appendChild(tbody);
    }
    mergeTableCells();
}

const lastValidValues = {};

function generateFilters() {
    filterContainer.innerHTML = '';

    const allRows = [...rowColumns];

    allRows.forEach(col => {
        if (colColumns.includes(col)) {
            return;
        }

        const colKey = Array.isArray(col) ? col.join(' ') : col;
        let uniqueValues = [...new Set(tableData.map(row => row[colKey]))];
        uniqueValues = uniqueValues.filter(val => val !== undefined);

        if (uniqueValues.length === 0 && lastValidValues[colKey]) {
            uniqueValues = lastValidValues[colKey];
        } else if (uniqueValues.length > 0) {
            lastValidValues[colKey] = uniqueValues;
        } else {
            uniqueValues = ["Valeur manquante"];
        }

        const filterGroup = document.createElement('div');
        filterGroup.classList.add('filter-group');

        const filterTitle = document.createElement('div');
        filterTitle.classList.add('filter-title');
        filterTitle.innerHTML = `<span class="icon-orange">&#43;</span> Filtrer sur ${col}`;
        filterTitle.style.cursor = 'pointer';

        const checkboxContainer = document.createElement('div');
        checkboxContainer.classList.add('checkbox-container');
        checkboxContainer.style.display = 'none';

        filterTitle.addEventListener('click', () => {
            checkboxContainer.style.display =
                checkboxContainer.style.display === 'none' ? 'block' : 'none';
        });

        uniqueValues.forEach(value => {
            const checkboxWrapper = document.createElement('div');
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = value;
            checkbox.setAttribute('data-column', colKey);

            const checkboxLabel = document.createElement('label');
            checkboxLabel.textContent = value;

            checkbox.addEventListener('change', applyFilters);

            checkboxWrapper.appendChild(checkbox);
            checkboxWrapper.appendChild(checkboxLabel);
            checkboxContainer.appendChild(checkboxWrapper);
        });

        filterGroup.appendChild(filterTitle);
        filterGroup.appendChild(checkboxContainer);
        filterContainer.appendChild(filterGroup);
    });
}

function doesRowMatchFilters(row, filters) {
    return Object.keys(filters).every(column => {
        const filterValues = filters[column];
        return Object.values(row).some(rowValue => filterValues.includes(rowValue));
    });
}
function applyFilters() {
    console.log("Applying filters...");

    const checkedCheckboxes = filterContainer.querySelectorAll('input[type="checkbox"]:checked');
    const filters = {};

    checkedCheckboxes.forEach(checkbox => {
        const column = checkbox.getAttribute('data-column');
        const value = checkbox.value;

        if (!filters[column]) {
            filters[column] = [];
        }
        filters[column].push(value);
    });

    if (Object.keys(filters).length === 0) {
        filteredTableData = [...tableData];
    } else {
        filteredTableData = tableData.filter(row => doesRowMatchFilters(row, filters));
    }

    console.log('tableau obtenir', filteredTableData);

    if (tableData.columns) {
        generateTable({
            columns: tableData.columns,
            data: filteredTableData.map(row => {
                return tableData.columns.map(col => {
                    const key = Array.isArray(col) ? col.join(' ') : col;
                    return row[key];
                });
            })
        });
    }
}

function mergeTableCells() {
    const table = document.querySelector('#table-container table');
    const rows = table.rows;
    const rowCount = rows.length;

    for (let col = 0; col < rows[0].cells.length; col++) {
        let startRow = 0;
        let value = rows[0].cells[col].innerText;
        for (let row = 1; row <= rowCount; row++) {
            if (row < rowCount && rows[row].cells[col].innerText === value) {
                continue;
            } else {
                if (row - startRow > 1) {
                    rows[startRow].cells[col].rowSpan = row - startRow;
                    for (let i = startRow + 1; i < row; i++) {
                        rows[i].cells[col].style.display = 'none';
                    }
                }
                if (row < rowCount) {
                    startRow = row;
                    value = rows[row].cells[col].innerText;
                }
            }
        }
    }
}

document.getElementById('download-xlsx').addEventListener('click', downloadXLSX);
document.getElementById('download-csv').addEventListener('click', downloadCSV);
document.getElementById('download-pdf').addEventListener('click', downloadPDF);

function downloadXLSX() {
    if (!filteredTableData || filteredTableData.length === 0) {
        alert("No data selected.");
        return;
    }

    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.aoa_to_sheet([]);
    const columns = tableData.columns;
    const levels = columns.length > 0 ? columns[0].length : 0;
    let rowOffset = 0;
    ws['!merges'] = [];

    for (let level = 0; level < levels; level++) {
        const headerRow = [];
        let previousValue = null;
        let colspanStartIndex = 0;

        columns.forEach((col, index) => {
            const currentValue = col[level];

            if (currentValue === previousValue) {
                return;
            } else {
                if (previousValue !== null && index - colspanStartIndex > 1) {
                    ws['!merges'].push({
                        s: { r: rowOffset, c: colspanStartIndex },
                        e: { r: rowOffset, c: index - 1 }
                    });
                }

                headerRow.push(currentValue || '');
                previousValue = currentValue;
                colspanStartIndex = index;
            }

            if (index === columns.length - 1 && index - colspanStartIndex > 0) {
                ws['!merges'].push({
                    s: { r: rowOffset, c: colspanStartIndex },
                    e: { r: rowOffset, c: index }
                });
            }
        });

        XLSX.utils.sheet_add_aoa(ws, [headerRow], { origin: rowOffset });
        rowOffset++;
    }

    filteredTableData.forEach(row => {
        const rowData = tableData.columns.map(col => {
            const key = Array.isArray(col) ? col.join(' ') : col;
            return row[key];
        });

        XLSX.utils.sheet_add_aoa(ws, [rowData], { origin: rowOffset });
        rowOffset++;
    });

    XLSX.utils.book_append_sheet(wb, ws, 'Data');
    XLSX.writeFile(wb, 'donnees_filtrees.xlsx');
}

function downloadCSV() {
    if (!filteredTableData || filteredTableData.length === 0) {
        alert("Aucune variable sélectionnée");
        return;
    }
    const columns = tableData.columns;
    const levels = columns.length > 0 ? columns[0].length : 0;
    const headerRows = Array.from({ length: levels }, () => Array(columns.length).fill(''));
    columns.forEach((col, colIndex) => {
        col.forEach((value, levelIndex) => {
            headerRows[levelIndex][colIndex] = value || '';
        });
    });
    const dataRows = filteredTableData.map(row =>
        columns.map(col => {
            const key = Array.isArray(col) ? col.join(' ') : col;
            return row[key] || '';
        })
    );
    const csvContent = [
        ...headerRows.map(row => row.map(value => {
            if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
                return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
        }).join(',')),
        ...dataRows.map(row => row.map(value => {
            if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
                return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
        }).join(','))
    ].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'donnees_filtrees.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function downloadPDF() {
    if (!filteredTableData || filteredTableData.length === 0) {
        alert("Aucune variable sélectionnée");
        return;
    }
    const { jsPDF } = window.jspdf;
    const pageWidth = 210;
    const columnWidths = tableData.columns.map(() => 30);
    const totalWidth = columnWidths.reduce((sum, width) => sum + width, 0);
    const orientation = totalWidth > pageWidth ? 'landscape' : 'portrait';
    const doc = new jsPDF({ orientation });
    const availablePageWidth = orientation === 'landscape' ? 297 - 20 : 210 - 20;
    const adjustedColumnWidths = columnWidths.map(width =>
        (width / totalWidth) * availablePageWidth
    );
    const pdfTitleElement = document.getElementById('pdf-title');
    const pdfTitle = pdfTitleElement ? pdfTitleElement.textContent.trim() : 'Données Filtrées';
    doc.setFontSize(16);
    doc.text(pdfTitle, 10, 15);
    const columns = tableData.columns;
    const bodyRows = filteredTableData.map(row =>
        columns.map(col => {
            const key = Array.isArray(col) ? col.join(' ') : col;
            const value = row[key] || '';
            return value.length > 50 ? `${value.substring(0, 47)}...` : value;
        })
    );
    doc.autoTable({
        startY: 25,
        head: [columns],
        body: bodyRows,
        theme: 'grid',
        headStyles: { fillColor: [0, 107, 69], textColor: [255, 153, 0], fontStyle: 'bold' },
        bodyStyles: { fontSize: 10, cellPadding: 2, halign: 'center' },
        alternateRowStyles: { fillColor: [245, 245, 245] },
        margin: { left: 10, right: 10 },
        styles: {
            overflow: 'linebreak',
            cellWidth: 'auto',
        },
        columnStyles: columns.reduce((acc, _, index) => {
            acc[index] = { cellWidth: adjustedColumnWidths[index] || 'auto' };
            return acc;
        }, {})
    });
    const filename = orientation === 'landscape' ? 'donnees_filtrees_landscape.pdf' : 'donnees_filtrees_portrait.pdf';
    doc.save(filename);
}

tableContainer.addEventListener('scroll', function () {
    console.log('Scroll event triggered');
    console.log('scrollTop:', tableContainer.scrollTop, 
                'clientHeight:', tableContainer.clientHeight, 
                'scrollHeight:', tableContainer.scrollHeight);
    if (isLoading || !hasMoreData) {
        console.log('Scroll ignored: isLoading=', isLoading, 'hasMoreData=', hasMoreData);
        return;
    }
    if (tableContainer.scrollTop + tableContainer.clientHeight >= tableContainer.scrollHeight - 25) {
        console.log('Loading more data: offset=', offset + limit);
        offset += limit;
        loadData(offset, limit);
    }
});