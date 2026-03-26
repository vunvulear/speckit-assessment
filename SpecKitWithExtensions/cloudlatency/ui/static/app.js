/* CloudLatency — Client-side rendering and SSE auto-update */

const PROVIDER_NAMES = { aws: "AWS", azure: "Azure", gcp: "GCP" };
const PROVIDER_COLORS = { aws: "#ff9900", azure: "#0078d4", gcp: "#4285f4" };

let avgChart = null;
let closestChart = null;
let eventSource = null;

/* ---------- Table rendering ---------- */

function renderTable(measurements) {
    const tbody = document.getElementById("latency-tbody");
    const countBadge = document.getElementById("table-count");
    if (!tbody) return;

    const scrollTop = tbody.parentElement.scrollTop;

    const rows = measurements.map((m, i) => {
        const providerClass = `provider-${m.provider_id}`;
        const providerLabel = PROVIDER_NAMES[m.provider_id] || m.provider_id;
        const latency = m.is_reachable && m.latency_ms != null
            ? m.latency_ms.toFixed(1)
            : "Timeout";
        const statusIcon = m.is_reachable ? "✅" : "⏱️";
        const rowClass = m.is_reachable ? "" : "unreachable";

        return `<tr class="${rowClass}">
            <td>${i + 1}</td>
            <td><span class="provider-badge ${providerClass}">${providerLabel}</span></td>
            <td>${m.region_name || m.region_code}</td>
            <td><code>${m.region_code}</code></td>
            <td>${latency}</td>
            <td><span class="status-icon">${statusIcon}</span></td>
        </tr>`;
    }).join("");

    tbody.innerHTML = rows;
    countBadge.textContent = measurements.length;

    // Preserve scroll position (FR-009)
    tbody.parentElement.scrollTop = scrollTop;
}

/* ---------- Chart rendering ---------- */

function renderAvgChart(summaries) {
    const ctx = document.getElementById("avg-chart");
    if (!ctx) return;

    const labels = summaries.map(s => PROVIDER_NAMES[s.provider_id] || s.provider_id);
    const data = summaries.map(s => s.average_latency_ms ?? 0);
    const colors = summaries.map(s => PROVIDER_COLORS[s.provider_id] || "#999");

    if (avgChart) {
        avgChart.data.labels = labels;
        avgChart.data.datasets[0].data = data;
        avgChart.data.datasets[0].backgroundColor = colors;
        avgChart.update("none");
    } else {
        avgChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels,
                datasets: [{
                    label: "Average Latency (ms)",
                    data,
                    backgroundColor: colors,
                    borderRadius: 4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const val = ctx.parsed.y;
                                return val > 0 ? `${val.toFixed(1)} ms` : "No data";
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: "ms" }
                    }
                }
            }
        });
    }
}

function renderClosestChart(summaries) {
    const ctx = document.getElementById("closest-chart");
    if (!ctx) return;

    const labels = summaries.map(s => {
        const name = PROVIDER_NAMES[s.provider_id] || s.provider_id;
        return s.closest_region_code ? `${name}\n(${s.closest_region_code})` : name;
    });
    const data = summaries.map(s => s.closest_latency_ms ?? 0);
    const colors = summaries.map(s => PROVIDER_COLORS[s.provider_id] || "#999");

    if (closestChart) {
        closestChart.data.labels = labels;
        closestChart.data.datasets[0].data = data;
        closestChart.data.datasets[0].backgroundColor = colors;
        closestChart.update("none");
    } else {
        closestChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels,
                datasets: [{
                    label: "Closest Region Latency (ms)",
                    data,
                    backgroundColor: colors,
                    borderRadius: 4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const val = ctx.parsed.y;
                                return val > 0 ? `${val.toFixed(1)} ms` : "No data";
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: "ms" }
                    }
                }
            }
        });
    }
}

/* ---------- Data update ---------- */

function updateUI(data) {
    renderTable(data.measurements || []);
    renderAvgChart(data.vendor_summaries || []);
    renderClosestChart(data.vendor_summaries || []);

    const tsEl = document.getElementById("last-updated");
    if (tsEl && data.measured_at) {
        const d = new Date(data.measured_at);
        tsEl.textContent = `Last updated: ${d.toLocaleTimeString()}`;
    }

    const countEl = document.getElementById("region-count");
    if (countEl && data.measurements) {
        const reachable = data.measurements.filter(m => m.is_reachable).length;
        countEl.textContent = `${reachable}/${data.measurements.length} regions reachable`;
    }
}

/* ---------- SSE connection ---------- */

function setConnectionStatus(status) {
    const dot = document.getElementById("connection-status");
    if (!dot) return;
    dot.className = `status-dot status-${status}`;
    dot.title = status === "connected" ? "Live" : status === "connecting" ? "Connecting..." : "Disconnected";
}

function connectSSE() {
    if (eventSource) {
        eventSource.close();
    }

    eventSource = new EventSource("/api/v1/stream");
    setConnectionStatus("connecting");

    eventSource.onopen = () => {
        setConnectionStatus("connected");
    };

    eventSource.addEventListener("latency_update", (event) => {
        try {
            const data = JSON.parse(event.data);
            updateUI(data);
        } catch (e) {
            console.error("Failed to parse SSE data:", e);
        }
    });

    eventSource.onerror = () => {
        setConnectionStatus("disconnected");
        eventSource.close();
        // Reconnect after 3 seconds
        setTimeout(connectSSE, 3000);
    };
}

/* ---------- Initial load ---------- */

async function initialLoad() {
    try {
        const resp = await fetch("/api/v1/latency");
        if (resp.ok) {
            const data = await resp.json();
            updateUI(data);
        }
    } catch (e) {
        console.log("Initial load — waiting for first measurement cycle");
    }
}

// Boot
document.addEventListener("DOMContentLoaded", async () => {
    await initialLoad();
    connectSSE();
});
