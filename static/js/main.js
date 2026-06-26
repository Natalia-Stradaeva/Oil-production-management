/*
 * Oleificio Simulation - Frontend Logic
 * Gestione interazioni dinamiche, aggiornamento dashboard (AJAX) e grafici.
 */

// =============================================================================
// UTILITIES E GESTIONE EVENTI BASE
// =============================================================================

function checkTemperature(temp) {
    if (temp > 27.0) {
        console.warn("Attenzione: Temperatura elevata (" + temp + "°C). Sistema in raffreddamento.");
    }
}

// Intercetta la vendita totale per conferma utente
document.querySelectorAll('.btn-red').forEach(button => {
    button.addEventListener('click', function(e) {
        const confirmAction = confirm("Sei sicuro di voler vendere l'intero stock?");
        if (!confirmAction) e.preventDefault();
    });
});

// Gestione invio form tramite AJAX (evita ricaricamento pagina)
document.addEventListener('submit', function(e) {
    if (e.target.classList.contains('sale-form')) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        
        fetch(form.action, { method: 'POST', body: formData })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateDashboard(); 
                } else {
                    alert(data.message || "Errore!");
                }
            })
            .catch(err => console.error("Errore di rete:", err));
    }
});

// Auto-hide alerts dopo 3 secondi
setTimeout(() => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(a => a.style.display = 'none');
}, 3000);

// Gestione scroll della pagina
window.addEventListener('beforeunload', () => localStorage.setItem('scrollPosition', window.scrollY));
window.addEventListener('load', () => {
    const savedScroll = localStorage.getItem('scrollPosition');
    if (savedScroll) {
        window.scrollTo({ top: parseInt(savedScroll), behavior: 'instant' });
        localStorage.removeItem('scrollPosition');
    }
});

// =============================================================================
// DASHBOARD E AGGIORNAMENTO DATI
// =============================================================================

let productChart, tempChart, revenueChart, efficiencyChart, inventoryChart;
let lastDataSnapshot = null;

function updateDashboard() {
    fetch('/api/status_data')
        .then(response => response.json())
        .then(data => {
            if (!data.inventory) return;
            const currentSnapshot = JSON.stringify(data.inventory);
            if (lastDataSnapshot === currentSnapshot) return;
            lastDataSnapshot = currentSnapshot;

            const inv = data.inventory;
            const fields = {
                'val-money': `${inv.money.toFixed(2)} €`,
                'val-olives-own': `${inv.olives_own.toFixed(1)} kg`,
                'val-olives-bought': `${inv.olives_bought.toFixed(1)} kg`,
                'val-bottles': `${inv.bottles} unità`,
                'val-corks': `${inv.corks} unità`,
                'val-virgin': `${inv.oil_virgin.toFixed(1)} L`,
                'val-evo': `${inv.oil_extra.toFixed(1)} L`,
                'val-sansa': `${inv.sansa.toFixed(1)} kg`,
                'val-empty-bags': `${inv.empty_bags} pz`,
                'val-bottled-virgin': `${Math.floor(inv.bottled_virgin)} unità`,
                'val-bottled-extra': `${Math.floor(inv.bottled_extra)} unità`,
                'val-sansa-bags': `${inv.sansa_bags} unità`
};
            for (const [id, value] of Object.entries(fields)) {
                const el = document.getElementById(id);
                if (el) el.innerText = value;
            }
            if (typeof updateCharts === 'function') updateCharts(data);
            if (data.logs) {
                updateTableContent(data.logs);
            }
        })
        .catch(error => console.warn('Aggiornamento:', error));
}

// =============================================================================
// LOGICA GRAFICI (CHART.JS)
// =============================================================================

function updateCharts(data) {
    const inv = data.inventory;

    // 1. Grafico produzione (Pie chart)
    if (productChart && inv) {
        productChart.data.datasets[0].data = [inv.oil_virgin, inv.oil_extra, inv.sansa];
        productChart.update('none');
    }

    // 2. Grafico temperatura (Line chart)
    if (tempChart && data.temp_data) {
        tempChart.data.labels = data.temp_data.map(l => l.date);
        tempChart.data.datasets[0].data = data.temp_data.map(l => l.temperature);
        tempChart.update('none'); 
    }

    // 3. Grafico ricavi/saldo (Line chart)
    if (revenueChart && inv) {
        if (revenueChart.data.datasets[0].data.length === 0 || 
            revenueChart.data.datasets[0].data[revenueChart.data.datasets[0].data.length - 1] !== inv.money) {
            
            revenueChart.data.labels.push(new Date().toLocaleTimeString().slice(-8));
            revenueChart.data.datasets[0].data.push(inv.money);
            
            if (revenueChart.data.labels.length > 10) {
                revenueChart.data.labels.shift();
                revenueChart.data.datasets[0].data.shift();
            }
            revenueChart.update('none');
        }
    }

    // 4. Grafico efficienza produttiva (Line chart)
    if (efficiencyChart && inv) {
        const eff = inv.olives_bought > 0 ? ((inv.oil_extra + inv.oil_virgin) / inv.olives_bought * 100).toFixed(1) : 0;
        
        if (efficiencyChart.data.datasets[0].data.length === 0 || 
            efficiencyChart.data.datasets[0].data[efficiencyChart.data.datasets[0].data.length - 1] != eff) {
            
            efficiencyChart.data.labels.push(new Date().toLocaleTimeString().slice(-8));
            efficiencyChart.data.datasets[0].data.push(eff);
            
            if (efficiencyChart.data.labels.length > 10) {
                efficiencyChart.data.labels.shift();
                efficiencyChart.data.datasets[0].data.shift();
            }
            efficiencyChart.update('none');
        }
    }

    // 5. Grafico inventario corrente (Bar chart)
    if (inventoryChart && inv) {
        inventoryChart.data.datasets[0].data = [
            inv.oil_virgin, 
            inv.oil_extra, 
            inv.sansa, 
            inv.bottles
        ];
        inventoryChart.update('none');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Inizializzazione grafico produzione
    productChart = new Chart(document.getElementById('productChart'), {
        type: 'pie',
        data: {
            labels: ['Virgin', 'EVO', 'Sansa'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#27ae60', '#2980b9', '#a0522d']
            }]
        }
    });

    // Inizializzazione grafico temperatura
    tempChart = new Chart(document.getElementById('tempChart'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{ label: 'Temp', data: [], borderColor: '#e74c3c' }]
        }
    });

    // Inizializzazione grafico ricavi/saldo
    revenueChart = new Chart(document.getElementById('revenueChart'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{ label: 'Saldo', data: [], borderColor: '#f1c40f', fill: true }]
        }
    });

    // Inizializzazione grafico efficienza produttiva
    efficiencyChart = new Chart(document.getElementById('efficiencyChart'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{ label: 'Eff', data: [], borderColor: '#9b59b6' }]
        }
    });

    // Inizializzazione grafico inventario corrente
    inventoryChart = new Chart(document.getElementById('inventoryChart'), {
        type: 'bar',
        data: {
            labels: ['Virgin', 'EVO', 'Sansa', 'Bottles'],
            datasets: [{
                label: 'Quantità',
                data: [0, 0, 0, 0],
                backgroundColor: ['#27ae60', '#2980b9', '#a0522d', '#f39c12']
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });

    document.querySelectorAll('.input-sell').forEach(input => {
        input.addEventListener('invalid', () => input.setCustomValidity("Errore!"));
        input.addEventListener('input', () => input.setCustomValidity(''));
    });
});

// =============================================================================
// AGGIORNAMENTO TABELLA LOG E AZIONI
// =============================================================================

function updateLogTable() {
    fetch('/api/status_data')
        .then(response => response.json())
        .then(data => {
            
            if (data.logs) {
                updateTableContent(data.logs);
            }
        })
        .catch(err => console.error("Errore nell'aggiornamento della tabella:", err));
}

document.querySelectorAll('.action-btn').forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault(); 
        const url = this.getAttribute('data-url'); 

        fetch(url, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateDashboard(); 
                } else {
                    alert(data.message || "Errore nell'operazione!");
                }
            })
            .catch(err => console.error("Errore:", err));
    });
});
function updateTableContent(logs) {
    const tbody = document.getElementById('log-table-body');
    if (!tbody) return;

    tbody.innerHTML = logs.map(log => `
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 12px;">${log.date || '---'}</td>
            <td style="padding: 12px;">${log.type || '---'}</td>
            <td style="padding: 12px;">${log.desc || '---'}</td>
            <td style="padding: 12px; font-weight: bold;">${log.val || '---'}</td>
        </tr>`).join('');
}

