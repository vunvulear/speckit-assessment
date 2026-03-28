/* CloudLatency — SSE client with auto-reconnect and progressive UI population */
(function () {
    "use strict";

    const RECONNECT_DELAY_MS = 5000;
    const TIMESTAMP_INTERVAL_MS = 1000;

    // DOM references
    const statusDot = document.getElementById("status-dot");
    const statusLabel = document.getElementById("status-label");
    const timestampEl = document.getElementById("timestamp");
    const tableBody = document.getElementById("table-body");

    // Summary banner elements
    const awsAvg = document.getElementById("aws-avg");
    const awsClosest = document.getElementById("aws-closest");
    const azureAvg = document.getElementById("azure-avg");
    const azureClosest = document.getElementById("azure-closest");
    const gcpAvg = document.getElementById("gcp-avg");
    const gcpClosest = document.getElementById("gcp-closest");

    let lastUpdateTime = null;
    let evtSource = null;

    // --- Connection status ---
    function setConnectionStatus(state) {
        statusDot.className = "status-dot " + state;
        const labels = { connected: "Connected", reconnecting: "Reconnecting\u2026", disconnected: "Disconnected" };
        statusLabel.textContent = labels[state] || state;
    }

    // --- Timestamp freshness ---
    function updateTimestamp() {
        if (!lastUpdateTime) return;
        const ago = Math.round((Date.now() - lastUpdateTime) / 1000);
        timestampEl.textContent = "Updated " + ago + "s ago";
        if (ago <= 10) {
            timestampEl.className = "ts-fresh";
        } else if (ago <= 30) {
            timestampEl.className = "ts-stale";
        } else {
            timestampEl.className = "ts-old";
        }
    }

    // --- Provider name formatting ---
    function providerClass(provider) {
        return "provider-" + provider.toLowerCase();
    }
    function providerTitle(provider) {
        if (provider === "aws") return "AWS";
        if (provider === "gcp") return "GCP";
        return provider.charAt(0).toUpperCase() + provider.slice(1);
    }

    // --- Status badge ---
    function statusBadge(status) {
        var cls, label;
        if (status === "ok") { cls = "badge-ok"; label = "OK"; }
        else if (status === "slow") { cls = "badge-slow"; label = "Slow"; }
        else { cls = "badge-unreachable"; label = "Unreachable"; }
        return '<span class="inline-block px-2 py-0.5 rounded-full text-xs font-medium ' + cls + '">' + label + '</span>';
    }

    // --- Latency formatting ---
    function formatLatency(ms) {
        if (ms === null || ms === undefined) return "—";
        return Math.round(ms) + " ms";
    }

    // --- Render table ---
    function renderTable(results) {
        if (!results || results.length === 0) {
            tableBody.innerHTML = '<tr id="empty-row"><td colspan="4" class="text-center py-8" style="color:var(--color-text-muted);">Waiting for data...</td></tr>';
            return;
        }
        var html = "";
        for (var i = 0; i < results.length; i++) {
            var r = results[i];
            var pcls = providerClass(r.provider);
            html += '<tr class="fade-in" style="height:36px; border-left:3px solid transparent;" tabindex="0">';
            html += '<td class="px-4 py-1.5 text-xs font-semibold uppercase ' + pcls + '" style="border-left:3px solid;">' + providerTitle(r.provider) + '</td>';
            html += '<td class="px-4 py-1.5 text-xs" style="color:var(--color-text);">' + r.region + '</td>';
            html += '<td class="px-4 py-1.5 text-right font-mono-latency text-xs" style="color:var(--color-text);">' + formatLatency(r.latency_ms) + '</td>';
            html += '<td class="px-4 py-1.5">' + statusBadge(r.status) + '</td>';
            html += '</tr>';
        }
        tableBody.innerHTML = html;
    }

    // --- Render summary banner ---
    function renderSummary(summary) {
        if (!summary || !summary.providers) return;
        var p = summary.providers;
        function fmt(provider, avgEl, closestEl) {
            var d = p[provider];
            if (!d) { avgEl.textContent = "\u2014"; closestEl.textContent = "\u2014"; return; }
            avgEl.textContent = d.average_latency_ms !== null ? Math.round(d.average_latency_ms) + " ms" : "\u2014";
            closestEl.textContent = d.closest_region && d.closest_latency_ms !== null
                ? d.closest_region + " " + Math.round(d.closest_latency_ms) + " ms"
                : "\u2014";
        }
        fmt("aws", awsAvg, awsClosest);
        fmt("azure", azureAvg, azureClosest);
        fmt("gcp", gcpAvg, gcpClosest);
    }

    // --- SSE connection ---
    function connect() {
        if (evtSource) { evtSource.close(); }
        setConnectionStatus("reconnecting");

        evtSource = new EventSource("/api/v1/sse");

        evtSource.onopen = function () {
            setConnectionStatus("connected");
        };

        evtSource.onmessage = function (event) {
            lastUpdateTime = Date.now();
            updateTimestamp();
            try {
                var data = JSON.parse(event.data);
                renderTable(data.results);
                renderSummary(data.summary);
            } catch (e) {
                console.error("SSE parse error:", e);
            }
        };

        evtSource.onerror = function () {
            setConnectionStatus("disconnected");
            evtSource.close();
            evtSource = null;
            setTimeout(connect, RECONNECT_DELAY_MS);
        };
    }

    // --- Init ---
    setConnectionStatus("disconnected");
    connect();
    setInterval(updateTimestamp, TIMESTAMP_INTERVAL_MS);
})();
