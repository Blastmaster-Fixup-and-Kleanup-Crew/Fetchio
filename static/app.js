const API_BASE = '/api';

// Crawl Form Handler
document.getElementById('crawlForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const startUrls = document.getElementById('startUrls').value.split(',').map(u => u.trim());
    const allowedDomains = document.getElementById('allowedDomains').value.split(',').map(d => d.trim());
    const maxPages = parseInt(document.getElementById('maxPages').value);

    try {
        const response = await fetch(`${API_BASE}/crawl`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_urls: startUrls,
                allowed_domains: allowedDomains,
                max_pages: maxPages
            })
        });
        const job = await response.json();
        document.getElementById('crawlForm').reset();
        refreshJobs();
    } catch (error) {
        alert('Error starting crawl: ' + error.message);
    }
});

// Search Form Handler
document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = document.getElementById('query').value;
    const limit = parseInt(document.getElementById('limit').value);

    if (!query) return;

    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, limit })
        });
        const results = await response.json();
        displayResults(results);
    } catch (error) {
        alert('Error searching: ' + error.message);
    }
});

function displayResults(results) {
    const container = document.getElementById('results');
    if (results.length === 0) {
        container.innerHTML = '<p class="text-gray-400">No results found.</p>';
        return;
    }
    container.innerHTML = results.map(r => `
        <div class="bg-slate-700 rounded p-4 border-l-4 border-cyan-400">
            <a href="${r.url}" target="_blank" class="text-cyan-300 hover:text-cyan-200 font-semibold underline">${r.title || r.url}</a>
            <p class="text-gray-400 text-sm mt-1">${r.snippet}</p>
            <p class="text-gray-500 text-xs mt-1">Score: ${r.score.toFixed(2)}</p>
        </div>
    `).join('');
}

async function refreshJobs() {
    try {
        const response = await fetch(`${API_BASE}/crawls`);
        const jobs = await response.json();
        const container = document.getElementById('jobsList');
        if (jobs.length === 0) {
            container.innerHTML = '<p class="text-gray-400">No crawl jobs yet.</p>';
            return;
        }
        container.innerHTML = jobs.map(job => `
            <div class="bg-slate-700 rounded p-4 border-l-4 border-blue-400">
                <p class="font-semibold">Job ID: ${job.id.substring(0, 8)}...</p>
                <p class="text-sm text-gray-400">Status: <span class="text-blue-300">${job.status}</span></p>
                <p class="text-sm text-gray-400">Pages: ${job.pages_crawled} | Errors: ${job.errors}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error fetching jobs:', error);
    }
}

// Refresh jobs every 3 seconds
refreshJobs();
setInterval(refreshJobs, 3000);
