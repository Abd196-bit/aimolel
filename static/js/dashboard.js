// DieAI Dashboard JavaScript

class DieAIDashboard {
    constructor() {
        this.apiKeys = [];
        this.usageStats = {};
        
        this.initializeEventListeners();
        this.loadDashboardData();
    }
    
    initializeEventListeners() {
        // Generate API key button
        const generateBtn = document.getElementById('generate-api-key');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generateAPIKey());
        }
        
        // Copy API key buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('copy-api-key')) {
                const apiKey = e.target.dataset.apiKey;
                this.copyToClipboard(apiKey);
            }
        });
        
        // Revoke API key buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('revoke-api-key')) {
                const apiKey = e.target.dataset.apiKey;
                this.revokeAPIKey(apiKey);
            }
        });
        
        // Refresh data button
        const refreshBtn = document.getElementById('refresh-data');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadDashboardData());
        }
    }
    
    async loadDashboardData() {
        try {
            // Show loading state
            this.showLoading(true);
            
            // This would typically load from the server
            // For now, we'll use the data already passed to the template
            this.updateDashboard();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showAlert('Failed to load dashboard data', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async generateAPIKey() {
        try {
            const response = await fetch('/generate_api_key', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.api_key) {
                this.showAlert('API key generated successfully!', 'success');
                this.addAPIKeyToList(data.api_key);
                
                // Show the new API key prominently
                this.showNewAPIKey(data.api_key);
            } else {
                this.showAlert('Failed to generate API key', 'error');
            }
            
        } catch (error) {
            console.error('Error generating API key:', error);
            this.showAlert('Failed to generate API key', 'error');
        }
    }
    
    async revokeAPIKey(apiKey) {
        if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch('/revoke_api_key', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ api_key: apiKey })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.showAlert('API key revoked successfully', 'success');
                this.removeAPIKeyFromList(apiKey);
            } else {
                this.showAlert('Failed to revoke API key', 'error');
            }
            
        } catch (error) {
            console.error('Error revoking API key:', error);
            this.showAlert('Failed to revoke API key', 'error');
        }
    }
    
    addAPIKeyToList(apiKey) {
        const container = document.getElementById('api-keys-list');
        if (!container) return;
        
        const keyElement = document.createElement('div');
        keyElement.className = 'api-key-item';
        keyElement.innerHTML = `
            <div class="api-key-info">
                <div class="api-key-text">${this.maskAPIKey(apiKey)}</div>
                <small class="text-muted">Created: ${new Date().toLocaleString()}</small>
            </div>
            <div class="api-key-actions">
                <button class="btn btn-sm btn-outline-primary copy-api-key" 
                        data-api-key="${apiKey}">
                    <i class="fas fa-copy"></i> Copy
                </button>
                <button class="btn btn-sm btn-outline-danger revoke-api-key" 
                        data-api-key="${apiKey}">
                    <i class="fas fa-trash"></i> Revoke
                </button>
            </div>
        `;
        
        keyElement.classList.add('animate-fade-in-up');
        container.appendChild(keyElement);
    }
    
    removeAPIKeyFromList(apiKey) {
        const keyElements = document.querySelectorAll('.api-key-item');
        keyElements.forEach(element => {
            const copyBtn = element.querySelector('.copy-api-key');
            if (copyBtn && copyBtn.dataset.apiKey === apiKey) {
                element.remove();
            }
        });
    }
    
    showNewAPIKey(apiKey) {
        const modal = document.createElement('div');
        modal.className = 'modal fade show';
        modal.style.display = 'block';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">New API Key Generated</h5>
                        <button type="button" class="btn-close" onclick="this.closest('.modal').remove()"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-3">Your new API key has been generated. Please copy it now as you won't be able to see it again.</p>
                        <div class="input-group">
                            <input type="text" class="form-control" value="${apiKey}" readonly>
                            <button class="btn btn-outline-secondary" onclick="this.parentElement.querySelector('input').select(); document.execCommand('copy'); this.textContent='Copied!'">
                                Copy
                            </button>
                        </div>
                        <div class="mt-3">
                            <small class="text-muted">
                                Store this key securely. You'll need it to authenticate API requests.
                            </small>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="this.closest('.modal').remove()">
                            I've copied the key
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Auto-remove after 30 seconds
        setTimeout(() => {
            if (modal.parentNode) {
                modal.remove();
            }
        }, 30000);
    }
    
    maskAPIKey(apiKey) {
        if (apiKey.length <= 8) return apiKey;
        return apiKey.substring(0, 8) + '...' + apiKey.substring(apiKey.length - 8);
    }
    
    updateDashboard() {
        this.updateUsageStats();
        this.updateAPIKeysList();
    }
    
    updateUsageStats() {
        // Update usage statistics display
        const totalRequests = document.getElementById('total-requests');
        const totalEndpoints = document.getElementById('total-endpoints');
        const lastActivity = document.getElementById('last-activity');
        
        if (totalRequests) {
            totalRequests.textContent = this.usageStats.total_requests || 0;
        }
        
        if (totalEndpoints) {
            totalEndpoints.textContent = this.usageStats.by_endpoint?.length || 0;
        }
        
        if (lastActivity) {
            const lastDate = this.usageStats.last_activity || new Date().toISOString();
            lastActivity.textContent = new Date(lastDate).toLocaleString();
        }
    }
    
    updateAPIKeysList() {
        const container = document.getElementById('api-keys-list');
        if (!container) return;
        
        // Clear existing keys
        container.innerHTML = '';
        
        if (this.apiKeys.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-key fa-3x mb-3"></i>
                    <p>No API keys yet. Generate your first key to get started.</p>
                </div>
            `;
            return;
        }
        
        this.apiKeys.forEach(key => {
            this.addAPIKeyToList(key.api_key);
        });
    }
    
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showAlert('API key copied to clipboard!', 'success');
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showAlert('API key copied to clipboard!', 'success');
        });
    }
    
    showAlert(message, type = 'info') {
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${type} alert-dismissible fade show`;
        alertElement.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.main-content .container');
        if (container) {
            container.insertBefore(alertElement, container.firstChild);
        }
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertElement.parentNode) {
                alertElement.remove();
            }
        }, 5000);
    }
    
    showLoading(show) {
        const loadingElement = document.getElementById('loading-spinner');
        if (loadingElement) {
            loadingElement.style.display = show ? 'block' : 'none';
        }
    }
    
    exportUsageData() {
        const data = {
            timestamp: new Date().toISOString(),
            api_keys: this.apiKeys,
            usage_stats: this.usageStats
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dieai-usage-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Usage Analytics Chart
class UsageChart {
    constructor(containerId) {
        this.containerId = containerId;
        this.chart = null;
        this.initializeChart();
    }
    
    initializeChart() {
        const ctx = document.getElementById(this.containerId);
        if (!ctx) return;
        
        // Check if Chart.js is loaded
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js not loaded. Usage charts will not be displayed.');
            return;
        }
        
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'API Requests',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'API Usage Over Time'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    updateData(labels, data) {
        if (!this.chart) return;
        
        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = data;
        this.chart.update();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('dashboard-container')) {
        window.dieaiDashboard = new DieAIDashboard();
        
        // Initialize usage chart if container exists
        if (document.getElementById('usage-chart')) {
            window.usageChart = new UsageChart('usage-chart');
        }
    }
});

// API Testing Interface
class APITester {
    constructor() {
        this.apiKey = '';
        this.initializeInterface();
    }
    
    initializeInterface() {
        const testContainer = document.getElementById('api-test-container');
        if (!testContainer) return;
        
        testContainer.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h5>API Testing Interface</h5>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <label class="form-label">API Key</label>
                        <input type="password" class="form-control" id="test-api-key" placeholder="Enter your API key">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Test Message</label>
                        <textarea class="form-control" id="test-message" rows="3" placeholder="Enter a test message"></textarea>
                    </div>
                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="test-search">
                            <label class="form-check-label" for="test-search">
                                Enable Search
                            </label>
                        </div>
                    </div>
                    <button class="btn btn-primary" onclick="this.testAPI()">Test API</button>
                    <div id="test-results" class="mt-3"></div>
                </div>
            </div>
        `;
    }
    
    async testAPI() {
        const apiKey = document.getElementById('test-api-key').value;
        const message = document.getElementById('test-message').value;
        const useSearch = document.getElementById('test-search').checked;
        const resultsDiv = document.getElementById('test-results');
        
        if (!apiKey || !message) {
            resultsDiv.innerHTML = '<div class="alert alert-warning">Please enter both API key and message</div>';
            return;
        }
        
        try {
            resultsDiv.innerHTML = '<div class="alert alert-info">Testing API...</div>';
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': apiKey
                },
                body: JSON.stringify({
                    message: message,
                    use_search: useSearch
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                resultsDiv.innerHTML = `
                    <div class="alert alert-success">
                        <h6>API Test Successful!</h6>
                        <p><strong>Response:</strong> ${data.response}</p>
                        <p><strong>Timestamp:</strong> ${data.timestamp}</p>
                    </div>
                `;
            } else {
                resultsDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <h6>API Test Failed</h6>
                        <p><strong>Error:</strong> ${data.error || 'Unknown error'}</p>
                    </div>
                `;
            }
            
        } catch (error) {
            resultsDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h6>API Test Failed</h6>
                    <p><strong>Error:</strong> ${error.message}</p>
                </div>
            `;
        }
    }
}

// Initialize API tester if container exists
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('api-test-container')) {
        window.apiTester = new APITester();
    }
});
