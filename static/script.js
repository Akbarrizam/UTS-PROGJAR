const workerSlider = document.getElementById('workerSlider');
const workerValue = document.getElementById('workerValue');
const crawlerForm = document.getElementById('crawlerForm');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const startBtn = document.getElementById('startBtn');

// Update worker value display
workerSlider.addEventListener('input', (e) => {
    workerValue.textContent = e.target.value;
});

// Handle form submission
crawlerForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const searchQuery = document.getElementById('searchQuery').value;
    const numPages = parseInt(document.getElementById('numPages').value);
    const numWorkers = parseInt(workerSlider.value);

    // Show loading
    loading.style.display = 'block';
    results.style.display = 'none';
    startBtn.disabled = true;

    try {
        const response = await fetch('/crawl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: searchQuery,
                pages: numPages,
                workers: numWorkers
            })
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data.properties, numWorkers);
            loading.style.display = 'none';
            results.style.display = 'block';
        } else {
            alert('Error: ' + data.error);
            loading.style.display = 'none';
        }
    } catch (error) {
        alert('Error connecting to server: ' + error);
        loading.style.display = 'none';
    }

    startBtn.disabled = false;
});

function displayResults(properties, workers) {
    // Display stats
    const statsContainer = document.getElementById('statsContainer');
    const uniqueLocations = [...new Set(properties.map(p => p.location))].length;

    statsContainer.innerHTML = `
        <div class="stat-item">
            <div class="stat-number">${properties.length}</div>
            <div class="stat-label">Properties Found</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">${workers}</div>
            <div class="stat-label">Workers Used</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">${properties.filter(p => p.price !== 'Hubungi Agen').length}</div>
            <div class="stat-label">With Price Data</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">${uniqueLocations}</div>
            <div class="stat-label">Locations</div>
        </div>
    `;

    // Display properties
    const propertiesGrid = document.getElementById('propertiesGrid');
    propertiesGrid.innerHTML = properties.map(prop => `
        <div class="property-card">
            <div class="property-header">
                <img src="${prop.images[0]}" alt="${prop.title}" class="property-image" 
                     onerror="this.src='https://via.placeholder.com/800x600?text=No+Image'">
                <div class="property-badge">📸 ${prop.images.length} Photo${prop.images.length > 1 ? 's' : ''}</div>
                <div class="property-info">
                    <div class="property-title">${prop.title}</div>
                    <div class="property-price">${prop.price}</div>
                    <div class="property-location">📍 ${prop.location}</div>
                </div>
            </div>
            <div class="property-body">
                <div class="property-specs">
                    <div class="spec-item">
                        <span class="spec-icon">🛏️</span>
                        <span class="spec-text">${prop.bedrooms}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-icon">🚿</span>
                        <span class="spec-text">${prop.bathrooms}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-icon">📏</span>
                        <span class="spec-text">${prop.land_size}</span>
                    </div>
                    <div class="spec-item">
                        <span class="spec-icon">🏗️</span>
                        <span class="spec-text">${prop.building_size}</span>
                    </div>
                </div>
                <div class="property-description">
                    ${prop.description}
                </div>
                <div class="property-footer">
                    <div class="agent-info">
                        <div class="agent-name">👤 ${prop.agent}</div>
                        <div>⏰ ${prop.scraped_at}</div>
                    </div>
                    <a href="${prop.url}" target="_blank" class="view-link">View Details</a>
                </div>
            </div>
        </div>
    `).join('');
}