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
            
            // Add click event for the next subpart
            tr.onclick = () => alert(`You clicked router ${router.router_id}. Details coming soon!`);
            
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
