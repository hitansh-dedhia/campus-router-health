let speedLatencyChartInstance = null;
let lossDisconnectsChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    loadRankings();
});

async function loadRankings() {
    try {
        const response = await fetch('/api/rankings');
        const routers = await response.json();
        
        const tbody = document.getElementById('rankings-body');
        tbody.innerHTML = ''; // clear loading state
        
        routers.forEach(router => {
            const tr = document.createElement('tr');
            
            // Add click event to load details
            tr.onclick = () => loadRouterDetail(router.router_id);
            
            tr.innerHTML = `
                <td>${router.router_id}</td>
                <td>${router.building}</td>
                <td>${router.health_score}</td>
                <td>${router.status}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error fetching rankings:', error);
        document.getElementById('rankings-body').innerHTML = `<tr><td colspan="4">Error loading data. Is the backend running?</td></tr>`;
    }
}

async function loadRouterDetail(routerId) {
    try {
        const response = await fetch(`/api/router/${routerId}`);
        const data = await response.json();
        
        // Hide empty state, show content
        document.getElementById('detail-empty').style.display = 'none';
        document.getElementById('detail-content').style.display = 'block';
        
        // Populate text fields
        document.getElementById('detail-title').textContent = `${data.router_id} (${data.status})`;
        document.getElementById('detail-building').textContent = data.building;
        document.getElementById('detail-room').textContent = data.room;
        document.getElementById('detail-model').textContent = data.model;
        document.getElementById('detail-firmware').textContent = data.firmware_version;
        
        // Populate scores
        document.getElementById('detail-overall').textContent = data.health_score;
        document.getElementById('detail-speed').textContent = data.speed_score;
        document.getElementById('detail-latency').textContent = data.latency_score;
        document.getElementById('detail-loss').textContent = data.loss_score;
        document.getElementById('detail-disconnects').textContent = data.disconnects_score;
        document.getElementById('detail-signal').textContent = data.signal_score;
        
        // Render Charts
        renderCharts(data.metrics);
        
    } catch (error) {
        console.error('Error fetching router details:', error);
        alert('Failed to load router details.');
    }
}

function renderCharts(metrics) {
    const hours = metrics.map(m => m.hour.split('T')[1]); // Extract time
    const speeds = metrics.map(m => m.avg_speed_mbps);
    const latencies = metrics.map(m => m.latency_ms);
    const losses = metrics.map(m => m.packet_loss_pct);
    const disconnects = metrics.map(m => m.disconnects);

    // Destroy old charts so they don't overlap when you click a new router
    if (speedLatencyChartInstance) speedLatencyChartInstance.destroy();
    if (lossDisconnectsChartInstance) lossDisconnectsChartInstance.destroy();

    const ctx1 = document.getElementById('speedLatencyChart').getContext('2d');
    speedLatencyChartInstance = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: hours,
            datasets: [
                { label: 'Speed (Mbps)', data: speeds, borderColor: 'blue', yAxisID: 'y' },
                { label: 'Latency (ms)', data: latencies, borderColor: 'red', yAxisID: 'y1' }
            ]
        },
        options: {
            scales: {
                y: { type: 'linear', position: 'left', title: {display: true, text: 'Speed (Mbps)'} },
                y1: { type: 'linear', position: 'right', grid: { drawOnChartArea: false }, title: {display: true, text: 'Latency (ms)'} }
            }
        }
    });

    const ctx2 = document.getElementById('lossDisconnectsChart').getContext('2d');
    lossDisconnectsChartInstance = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: hours,
            datasets: [
                { label: 'Packet Loss (%)', data: losses, backgroundColor: 'orange' },
                { label: 'Disconnects', data: disconnects, backgroundColor: 'purple' }
            ]
        },
        options: {
            scales: { y: { beginAtZero: true } }
        }
    });
}
