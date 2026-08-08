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
        
    } catch (error) {
        console.error('Error fetching router details:', error);
        alert('Failed to load router details.');
    }
}
