/**
 * Sentinel Dashboard - Real-time surveillance, Chart.js integrations, and simulation engine.
 */

let riskChart = null;
let timelineChart = null;
let autoStreamInterval = null;

document.addEventListener('DOMContentLoaded', function () {
    initializeDashboardCharts();
});

function initializeDashboardCharts() {
    fetch('/api/dashboard-charts')
        .then(response => response.json())
        .then(data => {
            renderRiskDoughnut(data.risk_distribution);
            renderTimelineChart(data.timeline);
        })
        .catch(err => console.error("Error loading dashboard chart metrics:", err));
}

function renderRiskDoughnut(riskData) {
    const ctx = document.getElementById('riskDoughnutChart');
    if (!ctx) return;

    if (riskChart) riskChart.destroy();

    riskChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Low Risk', 'Medium Risk', 'High Risk', 'Critical Risk'],
            datasets: [{
                data: [
                    riskData.Low || 0,
                    riskData.Medium || 0,
                    riskData.High || 0,
                    riskData.Critical || 0
                ],
                backgroundColor: [
                    '#10b981', // Emerald Green (Low)
                    '#f59e0b', // Amber (Medium)
                    '#f97316', // Orange (High)
                    '#ef4444'  // Rose Red (Critical)
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12, font: { size: 11 } }
                }
            },
            cutout: '68%'
        }
    });
}

function renderTimelineChart(timelineData) {
    const ctx = document.getElementById('timelineChart');
    if (!ctx) return;

    if (timelineChart) timelineChart.destroy();

    const labels = timelineData.map(item => item.id);
    const probabilities = timelineData.map(item => item.probability);
    const barColors = timelineData.map(item => {
        if (item.risk_level === 'Critical') return '#ef4444';
        if (item.risk_level === 'High') return '#f97316';
        if (item.risk_level === 'Medium') return '#f59e0b';
        return '#10b981';
    });

    timelineChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Fraud Probability (%)',
                data: probabilities,
                backgroundColor: barColors,
                borderRadius: 4,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { callback: v => v + '%' },
                    grid: { color: '#f1f5f9' }
                },
                x: {
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function simulateTransaction() {
    const btn = document.getElementById('btnSimulate');
    if (btn) btn.disabled = true;

    fetch('/api/simulate-transaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (btn) btn.disabled = false;
        if (data.success) {
            const tx = data.transaction;
            
            // Increment KPI counter
            const totalEl = document.getElementById('kpiTotal');
            if (totalEl) {
                let current = parseInt(totalEl.innerText.replace(/,/g, '')) || 0;
                totalEl.innerText = (current + 1).toLocaleString();
            }

            if (tx.is_fraud) {
                const fraudEl = document.getElementById('kpiFraud');
                if (fraudEl) {
                    let current = parseInt(fraudEl.innerText.replace(/,/g, '')) || 0;
                    fraudEl.innerText = (current + 1).toLocaleString();
                }
                const critEl = document.getElementById('kpiCritical');
                if (critEl && (tx.risk_level === 'High' || tx.risk_level === 'Critical')) {
                    let current = parseInt(critEl.innerText.replace(/,/g, '')) || 0;
                    critEl.innerText = (current + 1).toLocaleString();
                }

                // Prepend to suspicious table
                const tableBody = document.getElementById('suspiciousTableBody');
                if (tableBody) {
                    const rowHtml = `
                        <tr class="table-warning animate__animated animate__fadeIn">
                            <td><code class="text-primary fw-bold">${tx.transaction_id}</code></td>
                            <td class="fw-semibold">$${parseFloat(tx.amount).toFixed(2)}</td>
                            <td>
                                <div class="d-flex align-items-center gap-2">
                                    <div class="progress flex-grow-1" style="height: 6px; width: 60px;">
                                        <div class="progress-bar ${tx.fraud_probability > 0.5 ? 'bg-danger' : 'bg-warning'}" style="width: ${tx.fraud_probability * 100}%"></div>
                                    </div>
                                    <span class="small fw-bold">${(tx.fraud_probability * 100).toFixed(1)}%</span>
                                </div>
                            </td>
                            <td><span class="badge badge-${tx.risk_level.toLowerCase()} px-2 py-1">${tx.risk_level}</span></td>
                            <td><span class="badge bg-light text-secondary border">${tx.investigation_status}</span></td>
                            <td>
                                <a href="/transactions/results/${tx.id}" class="btn btn-outline-primary btn-sm py-1 px-2">
                                    <i class="fa-solid fa-magnifying-glass"></i> Details
                                </a>
                            </td>
                        </tr>
                    `;
                    tableBody.insertAdjacentHTML('afterbegin', rowHtml);
                }
            } else {
                const legitEl = document.getElementById('kpiLegit');
                if (legitEl) {
                    let current = parseInt(legitEl.innerText.replace(/,/g, '')) || 0;
                    legitEl.innerText = (current + 1).toLocaleString();
                }
            }

            // Refresh charts
            initializeDashboardCharts();
        }
    })
    .catch(err => {
        if (btn) btn.disabled = false;
        console.error("Simulation error:", err);
    });
}

function toggleAutoStream(checkbox) {
    if (checkbox.checked) {
        simulateTransaction();
        autoStreamInterval = setInterval(simulateTransaction, 4000);
    } else {
        if (autoStreamInterval) {
            clearInterval(autoStreamInterval);
            autoStreamInterval = null;
        }
    }
}
