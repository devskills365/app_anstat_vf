// Variable globale pour l'état des suggestions
let isSuggestionsActive = false;

// Variables globales pour la carte
let svg, path, colorScale, selectedIndicator = "Population", selectedRegion = null;

// Section 1 : Menu
function setActive(element) {
    document.querySelectorAll('nav a').forEach(link => link.classList.remove('bg-[#49655A]', 'text-white'));
    element.classList.add('bg-[#49655A]', 'text-white');
}

function submitSearch() {
    const query = document.getElementById('search-input').value;
    console.log('Recherche soumise : ' + query);
    // Ajoutez ici la logique pour soumettre réellement la recherche si elle n'est pas gérée par le lien de suggestion
    return true; 
}

function redirectToSearch(indicatorName) {
    console.log('Redirection vers la recherche de : ' + indicatorName);
    window.location.href = `/filter_indicator/${encodeURIComponent(indicatorName)}`;
}




// Section 2 : Carte et Indicateurs (Fonctions D3.js)
const indicatorTitles = {
    "Rapport de Masculinité (RM) en %": "Cartographie du rapport de masculinité en 2021",
    "Taux de divortialité (%)": "Répartition du taux de divortialité en 2021",
    "Population": "Cartographie de la population en 2021"
};

const width = 760, height = 500;
const projection = d3.geoMercator().center([-5.547080, 7.539989]).scale(4000).translate([width / 2, height / 2]);
path = d3.geoPath().projection(projection);
svg = d3.select("#map").append("svg").attr("width", width).attr("height", height);
const legendGroup = svg.append("g").attr("class", "legend-group").attr("transform", `translate(${width - 170}, ${height - 150})`);

svg.append("rect").attr("x", 0).attr("y", 0).attr("width", width).attr("height", height).attr("fill", "#e0e0e0").attr("opacity", 0.2);

function updateMap(data, indicator) {
    // ... (Logique D3.js pour la carte)
    const values = data.features.map(d => d.properties[indicator]).filter(v => v !== undefined && v !== null);
    const minValue = d3.min(values) || 0;
    const maxValue = d3.max(values) || 100;
    colorScale = d3.scaleLinear().domain([minValue, maxValue]).range(["hsla(91, 35%, 22%, 0.1)", "#49655A"]);
    svg.selectAll(".region").attr("fill", d => {
        const value = d.properties[indicator];
        return value !== undefined && value !== null ? colorScale(value) : "#ccc";
    });
    updateLegend(minValue, maxValue, indicator);
}

function updateLegend(minValue, maxValue, indicator) {

    const legendWidth = 150;
    const legendScale = d3.scaleLinear().domain([minValue, maxValue]).range([0, legendWidth]);
    const legendAxis = d3.axisBottom(legendScale).ticks(5).tickFormat(d3.format(".2s"));
    legendGroup.select(".legend").remove();
    svg.select(".title").remove();
    const titleText = indicatorTitles[indicator] || `Cartographie ${indicator} en 2021`;
    svg.append("text")
        .attr("class", "title")
        .attr("x", width / 1.75)
        .attr("y", 15)
        .attr("text-anchor", "middle")
        .style("font-size", "18px")
        .style("font-weight", "bold")
        .style("fill", "black")
        .text(titleText);

    const legend = legendGroup.append("g").attr("class", "legend").attr("transform", "translate(0, 40)");
    let gradient = svg.select("defs").select("#gradient");
    if (gradient.empty()) {
        gradient = svg.append("defs").append("linearGradient").attr("id", "gradient").attr("x1", "0%").attr("y1", "0%").attr("x2", "100%").attr("y2", "0%");
    }
    gradient.selectAll("stop").remove();
    gradient.append("stop").attr("offset", "0%").attr("stop-color", "hsla(91, 35%, 22%, 0.1)");
    gradient.append("stop").attr("offset", "100%").attr("stop-color", "#49655A");

    legend.append("rect").attr("width", legendWidth).attr("height", 10).style("fill", "url(#gradient)").style("stroke", "#999").style("stroke-width", "0.5");
    legend.append("g").attr("transform", "translate(0, 10)").call(legendAxis).selectAll("text").style("font-size", "10px");

    if (indicator === 'Population') {
        legend.append("text").attr("x", 0).attr("y", 45).style("font-size", "12px").style("font-weight", "bold").style("fill", "black").text("Hommes: 15 344 990");
        legend.append("text").attr("x", 0).attr("y", 60).style("font-size", "12px").style("font-weight", "bold").style("fill", "black").text("Femmes: 14 044 160");
        legend.append("text").attr("x", 0).attr("y", 75).style("font-size", "12px").style("font-weight", "bold").style("fill", "black").text("Total: 29 389 150");
    }
}

// Section 3 : Fonctions pour la surbrillance des régions

function highlightRegion(regionName) {
    // 1. Réinitialiser la bordure des régions (optionnel, mais propre)
    svg.selectAll(".region")
        .attr("stroke", "none");

    // 2. Appliquer la surbrillance à la région survolée
    svg.selectAll(".region")
        .filter(d => d.properties.REGION === regionName)
        .attr("fill", "#F39323") // Couleur de surbrillance
        .attr("stroke", "#000000")
        .attr("stroke-width", 2)
        .raise(); // S'assurer que cette région est au-dessus des autres
}

function resetRegionHighlight() {
    // Réinitialise toutes les régions à leur couleur d'origine basée sur l'indicateur sélectionné
    svg.selectAll(".region")
        .attr("fill", d => {
            const value = d.properties[selectedIndicator];
            // Utilise la colorScale globale pour retrouver la couleur d'indicateur
            return value !== undefined && value !== null ? colorScale(value) : "#ccc"; 
        })
        .attr("stroke", "none");
}

// Section 4 : Fonctions pour les graphiques
function loadCharts() {
    // Fonction de base pour créer un graphique Chart.js
    const createChart = (elementId, type, label, apiEndpoint, borderColor, backgroundColor, yTitle, options = {}) => {
        fetch(apiEndpoint)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur API: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // S'assurer que les étiquettes (labels) sont des nombres pour l'échelle 'linear'
                const labels = data.map(item => item.Annee);
                const values = data.map(item => item.Valeur);

                // Les données pour un graphique de type 'line' ou 'bar' avec axe X 'linear' 
                // DOIVENT être fournies sous forme de paires {x: Annee, y: Valeur}
                const chartDataPoints = data
                    .filter(item => item.Annee !== null && item.Valeur !== null) // Filtre les données incomplètes
                    .map(item => ({
                        x: parseInt(item.Annee), // L'axe X (Année) doit être numérique (entier)
                        y: parseFloat(item.Valeur)
                    }));
                
                // Si aucune donnée n'est filtrée, n'affichez pas le graphique
                if (chartDataPoints.length === 0) {
                    console.warn(`Aucune donnée valide pour le graphique ${elementId}.`);
                    return;
                }

                new Chart(document.getElementById(elementId), {
                    type: type,
                    data: {
                        // Chart.js utilise les labels si l'axe est de type 'category'. 
                        // Ici, nous forçons l'utilisation de data points {x, y}
                        datasets: [{
                            label: label,
                            data: chartDataPoints, // Utiliser les paires {x, y}
                            borderColor: borderColor,
                            backgroundColor: type === 'line' ? 'transparent' : backgroundColor, // Rendre la ligne transparente
                            fill: type === 'line' ? false : true,
                            borderWidth: 1,
                            // Styles spécifiques aux lignes
                            pointRadius: type === 'line' ? 3 : 0, 
                            tension: 0.1 // Ajoute un peu de courbe aux lignes pour plus de fluidité
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { 
                            title: { display: false }, 
                            tooltip: { mode: 'index', intersect: false } 
                        },
                        scales: {
                            // CORRECTION CLÉ : Utiliser l'échelle 'linear' pour l'axe X (Année)
                            x: { 
                                type: 'linear', 
                                title: { display: true, text: 'Année' },
                                ticks: {
                                    // S'assurer que les ticks affichent des années entières
                                    callback: function(value, index, values) {
                                        if (value % 1 === 0) return value;
                                    },
                                    stepSize: 1 // Forcer un pas d'une année (optionnel, mais utile)
                                }
                            },
                            y: { 
                                title: { display: true, text: yTitle }, 
                                beginAtZero: options.beginAtZero || false
                            }
                        }
                    }
                });
            })
            .catch(error => console.error(`Erreur chargement ${elementId}:`, error));
    };

    // La fonction doit maintenant passer l'API endpoint et les options
    createChart('chart-line-ipc', 'line', 'IPC(‰)', '/api/data/ipc', "hsla(91, 35%, 22%, 0.773)", 'transparent', 'Echelle');
    createChart('chart-line-enrollment', 'line', 'IHPC – ANStat(%)', '/api/data/ihpc', '#F39323', 'transparent', "Taux d'inflation");
    // Graphique en barres (souvent mieux adapté aux données discrètes)
    createChart('chart-bar-sante-budget', 'bar', "Part(%)", '/api/data/sante-budget', '#0C6B23', 'rgba(12, 107, 35, 0.2)', 'Part(%)', { beginAtZero: true });
}

// Événements DOMContentLoaded
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("search-input");
    const suggestionsContainer = document.getElementById("suggestions");
    const regionList = document.querySelector(".region-list");

    // Autocomplétion
    searchInput.addEventListener("input", function () {
        const query = searchInput.value.trim();
        if (query.length < 2) {
            suggestionsContainer.innerHTML = "";
            suggestionsContainer.style.display = 'none';
            isSuggestionsActive = false;
            return;
        }
        fetch(`/autocomplete?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                suggestionsContainer.innerHTML = "";
                if (data.length > 0) {
                    data.forEach(item => {
                        const div = document.createElement("div");
                        div.textContent = item;
                        div.classList.add('px-4', 'py-2', 'cursor-pointer', 'hover:bg-[#d9e6db]', 'hover:text-[#49655A]', 'text-sm');
                        div.onclick = function () {
                            searchInput.value = item;
                            suggestionsContainer.innerHTML = "";
                            suggestionsContainer.style.display = 'none';
                            isSuggestionsActive = false;
                            window.location.href = `/filter_indicator/${encodeURIComponent(item)}`;
                        };
                        suggestionsContainer.appendChild(div);
                    });
                    suggestionsContainer.style.display = 'block';
                    isSuggestionsActive = true;
                } else {
                    suggestionsContainer.style.display = 'none';
                    isSuggestionsActive = false;
                }
            })
            .catch(error => console.error('Erreur autocomplétion :', error));
    });

    suggestionsContainer.addEventListener("mouseover", () => isSuggestionsActive = true);
    suggestionsContainer.addEventListener("mouseout", (event) => {
        if (!searchInput.contains(event.relatedTarget)) isSuggestionsActive = false;
    });

    document.addEventListener("click", function (event) {
        if (!searchInput.contains(event.target) && !suggestionsContainer.contains(event.target) && !regionList.contains(event.target)) {
            suggestionsContainer.innerHTML = "";
            suggestionsContainer.style.display = 'none';
            isSuggestionsActive = false;
        }
    });

    // Horloge démographique
    let totalPopulation = parseInt("{{ pop_minute | default('29389150', true) | string | replace(' ', '') }}") || 29389150;
    function updatePopulationBox() {
        console.log("Mise à jour de l’horloge démographique");
        fetch('/population_data')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('birthsBox').textContent = totalPopulation.toLocaleString('fr-FR');
                    document.getElementById('dateBox').textContent = 'Erreur de données';
                    return;
                }
                totalPopulation = data.population_actuelle;
                document.getElementById('birthsBox').textContent = totalPopulation.toLocaleString('fr-FR');
                const date = new Date(data.time * 1000);
                const formattedDate = `${String(date.getDate()).padStart(2, '0')}-${String(date.getMonth() + 1).padStart(2, '0')}-${date.getFullYear()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
                document.getElementById('dateBox').textContent = formattedDate;
            })
            .catch(error => {
                console.error('Erreur population :', error);
                document.getElementById('birthsBox').textContent = totalPopulation.toLocaleString('fr-FR');
                document.getElementById('dateBox').textContent = '10-04-2025';
            });
    }
    setInterval(updatePopulationBox, 1000);
    updatePopulationBox();

    const today = new Date();
    const formattedToday = `${String(today.getDate()).padStart(2, '0')}-${String(today.getMonth() + 1).padStart(2, '0')}-${today.getFullYear()}`;
    document.getElementById('birthDateRange').textContent = `Du 01-01-2025 au ${formattedToday}`;
    document.getElementById('deathDateRange').textContent = `Du 01-01-2025 au ${formattedToday}`;
    
    // Chargement de la carte D3.js et des indicateurs
    d3.json("/static/carte/populations_updated.json").then(function(geojsonData) {
        console.log("GeoJSON chargé :", geojsonData);
        svg.selectAll(".region")
            .data(geojsonData.features)
            .enter().append("path")
            .attr("class", "region")
            .attr("d", path)
            .style("cursor", "pointer")
            .on("mouseover", function(event, d) {
                const tooltip = d3.select("#tooltip");
                const mapContainer = document.getElementById("map");
                const mapRect = mapContainer.getBoundingClientRect();
                const scrollLeft = mapContainer.scrollLeft;
                const scrollTop = mapContainer.scrollTop;
                const value = d.properties[selectedIndicator];
                tooltip.classed("hidden", false)
                    .html(`<strong>${d.properties.REGION}</strong><br>${selectedIndicator}: ${value !== undefined ? value.toLocaleString('fr-FR') : 'N/A'}`);

                const tooltipWidth = tooltip.node().offsetWidth;
                const tooltipHeight = tooltip.node().offsetHeight;
                let leftPos = event.clientX - mapRect.left + scrollLeft - 100;
                let topPos = event.clientY - mapRect.top + scrollTop - tooltipHeight + 300;

                if (leftPos + tooltipWidth > mapRect.width + scrollLeft) {
                    leftPos = event.clientX - mapRect.left + scrollLeft - tooltipWidth - 20;
                }
                if (topPos < scrollTop) {
                    topPos = event.clientY - mapRect.top + scrollTop + 5;
                }

                tooltip.style("left", leftPos + "px")
                    .style("top", topPos + "px");

            })
            .on("mouseout", function(event, d) {
                d3.select("#tooltip").classed("hidden", true);
                resetRegionHighlight(event);
            })
            .on("click", (event, d) => window.location.href = `/region_vitrine/${d.properties.REGION}`);

        const sampleProperties = geojsonData.features[0].properties;
        const indicators = Object.keys(sampleProperties).filter(key => typeof sampleProperties[key] === 'number' && key !== 'Année' && key !== 'ID'); // Correction : ajouter ID à filtrer
        
        const indicatorList = d3.select("#indicators")
            .selectAll("li")
            .data(indicators)
            .enter().append("li")
            .text(d => d)
            .classed('text-[#49655A] text-sm font-medium cursor-pointer hover:bg-[#d9e6db] p-1 rounded', true)
            .on("click", function(event, indicator) {
                selectedIndicator = indicator;
                indicatorList.classed("active-indicator", false);
                d3.select(this).classed("active-indicator", true);
                updateMap(geojsonData, indicator);
            });
        
        indicatorList.filter(d => d === "Population").classed("active-indicator", true);
        updateMap(geojsonData, "Population");
    }).catch(error => {
        console.error("Erreur chargement GeoJSON :", error);
        svg.append("text").attr("x", width / 2).attr("y", height / 2)
           .attr("text-anchor", "middle").style("fill", "red").text("Erreur de chargement de la carte");
    });
    
    // Chargement des graphiques
    loadCharts();
});