document.addEventListener("DOMContentLoaded", function () {
    // Ratios Élève/Enseignant
    fetch('/api/data/ratio-eleve-enseignant')
        .then(response => response.json())
        .then(dataRatioEleveEnseignant => {
            const departements = Object.keys(dataRatioEleveEnseignant);
            const datasets = departements.map((departement, index) => {
                return {
                    label: departement,
                    data: dataRatioEleveEnseignant[departement].map(d => d.ratio),
                    borderColor: ["orange", "blue", "green", "red"][index],
                    backgroundColor: "rgba(255,255,255,0.2)",
                    fill: false,
                };
            });

            var ctx1 = document.getElementById("pyramideAgesChart").getContext("2d");
            new Chart(ctx1, {
                type: "line",
                data: {
                    labels: dataRatioEleveEnseignant.Sinematiali.map(d => d.year),
                    datasets: datasets,
                },
                options: {
                    scales: {
                        x: { title: { display: true, text: "Année" } },
                        y: {
                            beginAtZero: false,
                            min: 30,
                            max: 55,
                            title: { display: true, text: "Ratio élèves/enseignant" }
                        }
                    },
                    plugins: {
                        legend: { display: true }
                    }
                }
            });
        });

    // Taux de Natalité
    fetch('/api/data/taux-natalite')
        .then(response => response.json())
        .then(dataNatalite => {
            const departements = Object.keys(dataNatalite);
            const datasets = departements.map((departement, index) => {
                return {
                    label: departement,
                    data: dataNatalite[departement].map(d => d.natalite),
                    borderColor: ["orange", "blue", "green", "red"][index],
                    backgroundColor: "rgba(255,255,255,0.2)",
                    fill: false,
                };
            });

            var ctx2 = document.getElementById("tauxNataliteChart").getContext("2d");
            new Chart(ctx2, {
                type: "line",
                data: {
                    labels: dataNatalite.Sinematiali.map(d => d.year),
                    datasets: datasets,
                },
                options: {
                    scales: {
                        x: { title: { display: true, text: "Année" } },
                        y: {
                            beginAtZero: true,
                            title: { display: true, text: "Taux de natalité (‰)" }
                        }
                    },
                    plugins: {
                        legend: { display: true }
                    }
                }
            });
        });

    // Population par département
    fetch('/api/data/population')
        .then(response => response.json())
        .then(dataPopulation => {
            var tableauPop = document.getElementById("tableauPop");
            var headersRow = tableauPop.querySelector("thead tr");
            var tbody = tableauPop.querySelector("tbody");

            // Clear existing rows
            tbody.innerHTML = '';
            
            // Add headers (if not already there)
            if (headersRow.children.length === 1) {
                ['Hommes', 'Femmes', 'Total'].forEach(headerText => {
                    const th = document.createElement("th");
                    th.textContent = headerText;
                    headersRow.appendChild(th);
                });
            }

            dataPopulation.forEach(function (d) {
                var row = document.createElement("tr");
                var tdDepartement = document.createElement("td");
                tdDepartement.textContent = d.departement;
                row.appendChild(tdDepartement);

                var tdHommes = document.createElement("td");
                tdHommes.textContent = d.hommes;
                row.appendChild(tdHommes);

                var tdFemmes = document.createElement("td");
                tdFemmes.textContent = d.femmes;
                row.appendChild(tdFemmes);

                var tdTotal = document.createElement("td");
                tdTotal.textContent = d.hommes + d.femmes;
                row.appendChild(tdTotal);

                tbody.appendChild(row);
            });
        });

    // Personnel Médical
    fetch('/api/data/personnel-medical')
        .then(response => response.json())
        .then(dataMedical => {
            const labelsMedical = ["Korhogo", "Sinematiali", "Dikodougou", "M'bengué"];
            const corpsMedical = Object.keys(dataMedical);
            const datasets = corpsMedical.map((corps, index) => {
                return {
                    label: corps,
                    data: labelsMedical.map(departement => dataMedical[corps][departement]),
                    backgroundColor: ["#e09705", "#006B45", "white"][index],
                    borderColor: "#000",
                    borderWidth: 1,
                };
            });

            var ctxMedical = document.getElementById("effectifMedical").getContext("2d");
            new Chart(ctxMedical, {
                type: "bar",
                data: {
                    labels: labelsMedical,
                    datasets: datasets,
                },
                options: {
                    scales: {
                        x: { beginAtZero: true },
                        y: { beginAtZero: true, max: 100 },
                    },
                },
            });
        });

    // Proportion de la Population à moins 5 km  Centre de santé (ppcs)
    fetch('/api/data/ppcs')
        .then(response => response.json())
        .then(dataIDH => {
            var ctxIDH = document.getElementById("ppcsChart").getContext("2d");
            new Chart(ctxIDH, {
                type: "line",
                data: {
                    labels: dataIDH.map(d => d.Annee),
                    datasets: [
                        {
                            label: "Proportion de la Population à moins 5 km  Centre de santé",
                            data: dataIDH.map(d => d.Valeur),
                            borderColor: "green",
                            fill: false,
                        },
                    ],
                },
                options: {
                    scales: {
                        y: { beginAtZero: true, max: 100 },
                    },
                },
            });
        });

    // Taux de Chômage
    fetch('/api/data/taux-chomage')
        .then(response => response.json())
        .then(dataTauxChomage => {
            var ctxTauxChomage = document.getElementById("tauxChomageChart").getContext("2d");
            new Chart(ctxTauxChomage, {
                type: "line",
                data: {
                    labels: dataTauxChomage.map(d => d.year),
                    datasets: [
                        {
                            label: "Taux",
                            data: dataTauxChomage.map(d => d.taux),
                            borderColor: "#e09705",
                            fill: false,
                            pointBackgroundColor: "#e09705",
                            pointBorderColor: "#e09705",
                        },
                    ],
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 2 },
                            title: { display: true, text: "Taux (%)" },
                        },
                        x: {
                            title: { display: false, text: "Année" },
                        },
                    },
                    plugins: {
                        legend: { display: true, position: "top" },
                    },
                },
            });
        });

    // Population Urbaine vs Rurale
    fetch('/api/data/population-urbaine-rurale')
        .then(response => response.json())
        .then(dataPopulationPoro => {
            var ctxPopRuralUrbain = document.getElementById("popRuralUrbain").getContext("2d");
            const labels = dataPopulationPoro.map(d => d.type_pop);
            const values = dataPopulationPoro.map(d => d.count);
            new Chart(ctxPopRuralUrbain, {
                type: "doughnut",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Répartition Population (Poro)",
                            data: values,
                            backgroundColor: ["#4CAF50", "#FFC107"],
                            hoverBackgroundColor: ["#388E3C", "#FFA000"],
                        },
                    ],
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: true,
                            position: "top",
                            labels: {
                                generateLabels: function (chart) {
                                    const data = chart.data;
                                    const total = data.datasets[0].data.reduce((acc, val) => acc + val, 0);
                                    return data.labels.map((label, i) => {
                                        const value = data.datasets[0].data[i];
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        return {
                                            text: `${label} (${percentage}%)`,
                                            fillStyle: data.datasets[0].backgroundColor[i],
                                            hidden: chart.isDatasetVisible(0) && !chart.getDataVisibility(i),
                                            lineWidth: 0,
                                            index: i,
                                        };
                                    });
                                },
                            },
                        },
                        tooltip: {
                            callbacks: {
                                label: function (tooltipItem) {
                                    let label = tooltipItem.label || "";
                                    let value = tooltipItem.raw;
                                    const dataset = tooltipItem.dataset;
                                    const total = dataset.data.reduce((acc, val) => acc + val, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ${value.toLocaleString()} habitants (${percentage}%)`;
                                },
                            },
                        },
                    },
                },
            });
        });

    // Taux d'Alphabétisation
    fetch('/api/data/taux-alphabetisation')
        .then(response => response.json())
        .then(dataAlphabetisation => {
            var ctxAlphabetisationPoro = document.getElementById("alphabetisationChartPoro").getContext("2d");
            new Chart(ctxAlphabetisationPoro, {
                type: "bar",
                data: {
                    labels: dataAlphabetisation.map(d => d.year),
                    datasets: [
                        {
                            label: "Taux d'Alphabétisation (%)",
                            data: dataAlphabetisation.map(d => d.taux),
                            backgroundColor: "#4CAF50",
                            borderColor: "#388E3C",
                            borderWidth: 1,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: true, position: "top" },
                        tooltip: {
                            callbacks: {
                                label: (tooltipItem) => `Taux : ${tooltipItem.raw}%`,
                            },
                        },
                    },
                    scales: {
                        x: { title: { display: true, text: "Année" } },
                        y: { beginAtZero: true, title: { display: true, text: "Taux d'Alphabétisation (%)" } },
                    },
                },
            });
        });
        
    // Taux Brut de Scolarité
    fetch('/api/data/taux-brute-scolarite')
        .then(response => response.json())
        .then(tauxBruteData => {
            var ctx = document.getElementById('tauxBruteChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: tauxBruteData.map(d => d.year),
                    datasets: [{
                        label: 'Taux (%)',
                        data: tauxBruteData.map(d => d.taux),
                        backgroundColor: '#e09705',
                        borderColor: '#e09705',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' }
                    }
                }
            });
        });

    // Taux d'Électrification
    fetch('/api/data/taux-electrification')
        .then(response => response.json())
        .then(tauxElectData => {
            var ctx = document.getElementById('tauxElectChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: tauxElectData.map(d => d.year),
                    datasets: [{
                        label: 'Nombre',
                        data: tauxElectData.map(d => d.nombre),
                        backgroundColor: '#006B45',
                        borderColor: '#006B45',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' }
                    }
                }
            });
        });
});