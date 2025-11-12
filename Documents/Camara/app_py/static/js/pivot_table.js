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


// Pour supprimer les mauvais combinaison
const COLUMN_DEPENDENCIES = {
    'Région': ['Département', 'Sous-préfecture'],
    'Département': ['Région', 'Sous-préfecture'],
    'Sous-préfecture': ['Région', 'Département'],
};

// Obtenez le nom de l'indicateur depuis l'URL actuelle
const pathArray = window.location.pathname.split('/');
const indicateur_name = decodeURIComponent(pathArray[pathArray.length - 1]);

// Écouteurs d'événements pour le glisser-déposer
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

// Fonction MODIFIÉE pour gérer l'interdiction de dépôt
function handleDragOver(event) {
    event.preventDefault();

    // Récupère la colonne que l'utilisateur essaie de glisser
    const columnToDrop = event.dataTransfer.getData('text/plain');
    if (!columnToDrop) return;

    // Concatène toutes les colonnes actuellement sélectionnées dans les zones de lignes et de colonnes
    const currentlySelectedColumns = [...rowColumns, ...colColumns];

    let dropAllowed = true;

    // Vérifie si la colonne en cours de dépôt est exclue par une colonne déjà présente
    for (const selectedCol of currentlySelectedColumns) {
        const excludedCols = COLUMN_DEPENDENCIES[selectedCol];
        if (excludedCols && excludedCols.includes(columnToDrop)) {
            dropAllowed = false;
            break;
        }
    }
    
    // Si le dépôt n'est pas autorisé, modifie l'apparence et empêche le dépôt
    if (!dropAllowed) {
        event.dataTransfer.dropEffect = 'none';
        
        // Optionnel: ajouter un retour visuel (exemple: fond rouge)
        event.currentTarget.classList.add('not-allowed-drop');
        setTimeout(() => event.currentTarget.classList.remove('not-allowed-drop'), 500);

    } else {
        event.dataTransfer.dropEffect = 'move';
    }
}

function handleDrop(event, type) {
    event.preventDefault();
    const column = event.dataTransfer.getData('text/plain');
    const sourceId = event.dataTransfer.getData('source-id');
    const draggedElement = document.querySelector(`[data-column="${column}"][id="${sourceId}"]`) || document.querySelector(`[data-column="${column}"]`);

    if (!draggedElement) return;

    // Vérification de la dépendance (répétée pour être sûr, même si handleDragOver a déjà empêché)
    if (type !== 'initial') {
        const currentlySelectedColumns = [...rowColumns, ...colColumns];
        for (const selectedCol of currentlySelectedColumns) {
            const excludedCols = COLUMN_DEPENDENCIES[selectedCol];
            if (excludedCols && excludedCols.includes(column)) {
              
                
                return;
            }
        }
    }

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
            // 1. SUPPRIMER l'élément de la zone actuelle
            area.removeChild(newItem);

            // 2. Supprimer de la liste (rowColumns ou colColumns)
            if (columnList) {
                columnList.splice(columnList.indexOf(column), 1);
            }
    
            addColumnToArea(column, initialList, null, 'initial');
            togglePlaceholders();
            sendColumnsToServer();
        });
    }

    area.appendChild(newItem);
}

function togglePlaceholders() {
    const rowPlaceholder = droppableAreaRows.querySelector('#placeholder-rows');
    const colPlaceholder = droppableAreaCols.querySelector('#placeholder-cols');
    if (rowPlaceholder) rowPlaceholder.style.display = droppableAreaRows.children.length > 1 ? 'none' : 'block';
    if (colPlaceholder) colPlaceholder.style.display = droppableAreaCols.children.length > 1 ? 'none' : 'block';
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
        return;
    }
    isLoading = true;

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
        // Au lieu de retourner response.json(), on retourne le texte
        return response.text(); 
    })
    .then(text => { // 'text' contient la réponse brute du serveur
        // 🚨 Correction pour gérer les NaN non valides en JSON
        const cleanedText = text.replace(/NaN/g, 'null'); 
        
        let data;
        try {
            data = JSON.parse(cleanedText);
        } catch (e) {
            console.error('Erreur de Parsing JSON après nettoyage:', e);
            console.error('Texte brut responsable:', text);
            isLoading = false;
            return;
        }
        
        if (data.error) {
            console.error('Server error:', data.error);
            isLoading = false;
            return;
        }
        if (data.data.length < limit) {
             hasMoreData = false;
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
            tableData.columns = data.columns;
            applyFilters();
            generateFilters();
        } else {
             // Chargements suivants : ajouter de nouvelles lignes
             const newFilteredRows = newRows.filter(row => doesRowMatchFilters(row, getActiveFilters()));
             appendRows({
                 columns: data.columns,
                 data: newFilteredRows.map(row => {
                     return data.columns.map(col => row[col.join(' ')]);
                 })
             });
        }

        isLoading = false;
    })
    .catch(error => {
         console.error('Erreur:', error);
         isLoading = false;
    });
}

// Fonction pour récupérer les filtres actifs
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
    const levels = columns.length > 0 && Array.isArray(columns[0]) ? columns[0].length : 0;

    // Génération des en-têtes de table avec colspan
    for (let level = 0; level < levels; level++) {
        const headerRow = document.createElement('tr');
        let colspanCount = 1;
        let previousValue = columns.length > 0 ? columns[0][level] : null;

        for (let i = 1; i <= columns.length; i++) {
            const currentValue = i < columns.length ? columns[i][level] : null;

            if (currentValue === previousValue) {
                colspanCount++;
            } else {
                const th = document.createElement('th');
                th.textContent = previousValue || '';
                th.setAttribute('colspan', colspanCount);
                th.classList.add('sticky', 'top-0', 'z-10', 'bg-[#49655A]');
                headerRow.appendChild(th);

                previousValue = currentValue;
                colspanCount = 1;
            }
        }
        thead.appendChild(headerRow);
    }
    
    // Génération du corps de la table
    data.data.forEach(row => {
        const tr = document.createElement('tr');
        columns.forEach((col, index) => {
            const td = document.createElement('td');
            const key = Array.isArray(col) ? col.join(' ') : col;
            td.textContent = row[key] !== undefined ? row[key] : ' ';
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
    const table = document.querySelector('#data-table');
    if (!table) return;
    const tbody = table.querySelector('tbody') || document.createElement('tbody');
    
    data.data.forEach(row => {
        const tr = document.createElement('tr');
        data.columns.forEach((col, index) => {
            const td = document.createElement('td');
            const key = Array.isArray(col) ? col.join(' ') : col;
            td.textContent = row[key] !== undefined ? row[key] : ' ';
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
        uniqueValues = uniqueValues.filter(val => val !== undefined && val !== null);
        
        if (uniqueValues.length === 0 && lastValidValues[colKey]) {
            uniqueValues = lastValidValues[colKey];
        } else if (uniqueValues.length > 0) {
            lastValidValues[colKey] = uniqueValues;
        } else {
            uniqueValues = ["Missing data"];
        }

        const filterGroup = document.createElement('div');
        filterGroup.classList.add('filter-group');

        const filterTitle = document.createElement('div');
        filterTitle.classList.add('filter-title');
        filterTitle.innerHTML = `<span class="icon-orange">&#43;</span> ${col}`;
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
        return filterValues.includes(row[column]);
    });
}

function applyFilters() {
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
    
    if (tableData.columns) {
        generateTable({
            columns: tableData.columns,
            data: filteredTableData.map(row => {
                const newRow = {};
                tableData.columns.forEach(col => {
                    const key = Array.isArray(col) ? col.join(' ') : col;
                    newRow[key] = row[key];
                });
                return newRow;
            })
        });
    }
}

// Fonction de fusion des cellules (optimisée)
function mergeTableCells() {
    const table = document.querySelector('#data-table');
    if (!table) return;

    const rows = table.rows;
    const rowCount = rows.length;
    
    // Fusionner les cellules pour les colonnes des "lignes"
    const rowHeaderCount = rowColumns.length;
    
    if (rowCount > 1) {
        for (let col = 0; col < rowHeaderCount; col++) {
            let startRow = 1;
            let startValue = rows[startRow].cells[col].innerText;

            for (let row = 2; row <= rowCount; row++) {
                if (row === rowCount || rows[row].cells[col].innerText !== startValue) {
                    if (row - startRow > 1) {
                        rows[startRow].cells[col].rowSpan = row - startRow;
                        for (let i = startRow + 1; i < row; i++) {
                            rows[i].cells[col].style.display = 'none';
                        }
                    }
                    if (row < rowCount) {
                        startRow = row;
                        startValue = rows[row].cells[col].innerText;
                    }
                }
            }
        }
    }
}

// Gestion des téléchargements
document.getElementById('download-xlsx').addEventListener('click', () => downloadFullData('xlsx'));
document.getElementById('download-csv').addEventListener('click', () => downloadFullData('csv'));

function downloadFullData(format) {
    // Remplacement de 'alert' par une gestion sans alerte bloquante
    const alertUser = (message) => console.log('Download Alert:', message);

    if (isLoading) {
        alertUser("Veuillez patienter, un téléchargement est déjà en cours.");
        return;
    }
    
    isLoading = true;

    // Récupérer toutes les données sans pagination
    fetch('/process_columns?offset=0&limit=999999', {
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
        if (!response.ok) throw new Error('Erreur réseau lors du téléchargement: ' + response.status);
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error('Erreur du serveur:', data.error);
            alertUser("Erreur du serveur lors de la récupération des données.");
            return;
        }

        const fullData = data.data.map(row => {
            const rowData = {};
            data.columns.forEach((col, index) => {
                rowData[col.join(' ')] = row[index];
            });
            return rowData;
        });

        // Appliquer les filtres du client
        const filters = getActiveFilters();
        const filteredDataForDownload = fullData.filter(row => doesRowMatchFilters(row, filters));

        if (format === 'xlsx') {
            const wb = XLSX.utils.book_new();

            // Générer une matrice d'en-tête à plusieurs niveaux
            const columns = data.columns;
            const headerMatrix = [];
            const levels = columns.length > 0 && Array.isArray(columns[0]) ? columns[0].length : 0;

            for (let level = 0; level < levels; level++) {
                const headerRow = [];
                columns.forEach(col => {
                    headerRow.push(col[level] || '');
                });
                headerMatrix.push(headerRow);
            }

            // Préparer les lignes de données
            const columnsKeys = columns.map(col => col.join(' '));
            const dataRows = filteredDataForDownload.map(row => columnsKeys.map(col => row[col]));
            
            // Combiner les en-têtes et les données
            const finalData = headerMatrix.concat(dataRows);
            const ws = XLSX.utils.aoa_to_sheet(finalData);

            // Appliquer la fusion des cellules pour les en-têtes
            const merges = [];
            for (let level = 0; level < levels; level++) {
                let startCol = 0;
                let colCount = 1;
                for (let i = 1; i <= columns.length; i++) {
                    const value = i < columns.length ? columns[i][level] : null;
                    if (value === columns[startCol][level]) {
                        colCount++;
                    } else {
                        if (colCount > 1) {
                            merges.push({
                                s: { r: level, c: startCol },
                                e: { r: level, c: startCol + colCount - 1 }
                            });
                        }
                        startCol = i;
                        colCount = 1;
                    }
                }
            }
            if (merges.length > 0) {
                ws['!merges'] = merges;
            }
            
            XLSX.utils.book_append_sheet(wb, ws, 'Données');
            XLSX.writeFile(wb, `Données_${indicateur_name}.xlsx`);

        } else if (format === 'csv') {
            // Le format CSV ne gère pas les en-têtes à plusieurs niveaux.
            // On utilise les en-têtes aplatis.
            const columnsForDownload = data.columns.map(col => col.join(' '));
            const finalData = [columnsForDownload, ...filteredDataForDownload.map(row => columnsForDownload.map(col => row[col]))];
            
            let csvContent = finalData.map(e => e.join(",")).join("\n");
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement("a");
            link.setAttribute("href", URL.createObjectURL(blob));
            link.setAttribute("download", `ANStat_${indicateur_name}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        }
    })
    .catch(error => {
        console.error('Erreur lors du téléchargement:', error);
        alertUser("Une erreur est survenue lors du téléchargement.");
    })
    .finally(() => {
        isLoading = false;
    });
}


document.getElementById('download-pdf').addEventListener('click', downloadPDF);

function downloadPDF() {
    // Remplacement de 'alert' par une gestion sans alerte bloquante
    const alertUser = (message) => console.log('PDF Alert:', message);
    
    if (!filteredTableData || filteredTableData.length === 0) {
        alertUser("Aucune variable sélectionnée");
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
    if (isLoading || !hasMoreData) {
        return;
    }
    if (tableContainer.scrollTop + tableContainer.clientHeight >= tableContainer.scrollHeight - 25) {
        offset += limit;
        loadData(offset, limit);
    }
});

// Appeler le chargement initial au démarrage
document.addEventListener('DOMContentLoaded', () => {
    togglePlaceholders();
    sendColumnsToServer();
});