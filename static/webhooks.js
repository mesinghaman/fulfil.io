// Webhook management functionality

document.addEventListener('DOMContentLoaded', function() {
    const webhookForm = document.getElementById('webhook-form');
    const webhookList = document.getElementById('webhook-list');
    const testResults = document.getElementById('test-results');

    // Handle webhook form submission
    webhookForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const url = document.getElementById('webhook-url').value;
        const eventTypes = Array.from(document.getElementById('event-types').selectedOptions).map(o => o.value);
        const enabled = document.getElementById('webhook-enabled').checked;
        
        try {
            const response = await fetch('/webhooks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    url: url,
                    event_types: eventTypes.length ? eventTypes : ["product.created", "product.updated", "product.deleted"],
                    enabled: enabled
                })
            });
            
            if (response.ok) {
                document.getElementById('webhook-url').value = '';
                document.getElementById('webhook-enabled').checked = true;
                loadWebhooks();
            }
        } catch (error) {
            console.error('Error creating webhook:', error);
        }
    });

    // Load and display webhooks
    async function loadWebhooks() {
        try {
            const response = await fetch('/api/webhooks');
            const data = await response.json();
            
            if (data.webhooks.length === 0) {
                webhookList.innerHTML = '<p>No webhooks configured</p>';
                return;
            }
            
            webhookList.innerHTML = data.webhooks.map(webhook => `
                <div class="webhook-item">
                    <div class="webhook-info">
                        <strong>URL:</strong> ${webhook.url}<br>
                        <strong>Events:</strong> ${webhook.event_types.join(', ')}<br>
                        <strong>Status:</strong> <span style="color: ${webhook.enabled ? '#28a745' : '#dc3545'}">${webhook.enabled ? 'Enabled' : 'Disabled'}</span>
                    </div>
                    <div class="webhook-actions">
                        <button class="btn btn-small" onclick="toggleWebhook(${webhook.id}, ${!webhook.enabled})">
                            ${webhook.enabled ? 'Disable' : 'Enable'}
                        </button>
                        <button class="btn btn-small" onclick="testWebhook(${webhook.id})">Test</button>
                        <button class="btn btn-small btn-danger" onclick="deleteWebhook(${webhook.id})">Delete</button>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading webhooks:', error);
            webhookList.innerHTML = '<p>Error loading webhooks</p>';
        }
    }

    // Global functions for webhook actions
    window.toggleWebhook = async function(id, enabled) {
        try {
            await fetch(`/webhooks/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: enabled })
            });
            loadWebhooks();
        } catch (error) {
            console.error('Error toggling webhook:', error);
        }
    };

    window.testWebhook = async function(id) {
        testResults.innerHTML = '<p>Testing webhook...</p>';
        try {
            const response = await fetch(`/webhooks/${id}/test`, { method: 'POST' });
            const result = await response.json();
            
            testResults.innerHTML = `
                <div class="test-result ${result.success ? 'success' : 'error'}">
                    <strong>Test Result:</strong><br>
                    URL: ${result.url}<br>
                    ${result.success ? 
                        `Status: ${result.status_code}<br>Response Time: ${result.response_time_ms}ms` :
                        `Error: ${result.error}<br>Response Time: ${result.response_time_ms}ms`
                    }
                </div>
            `;
        } catch (error) {
            testResults.innerHTML = `<div class="test-result error">Test failed: ${error.message}</div>`;
        }
    };

    window.deleteWebhook = async function(id) {
        if (confirm('Are you sure you want to delete this webhook?')) {
            try {
                await fetch(`/webhooks/${id}`, { method: 'DELETE' });
                loadWebhooks();
            } catch (error) {
                console.error('Error deleting webhook:', error);
            }
        }
    };

    // Initial load
    loadWebhooks();
});
