class TextConverter {
    constructor() {
        this.currentMode = 'humanize';
        this.currentModel = null;
        this.currentTemperature = 0.7;
        this.models = {};
        this.history = JSON.parse(localStorage.getItem('conversionHistory')) || [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadModels();
        this.loadUsageStats();
        this.renderHistory();
        // Refresh usage stats every 30 seconds
        setInterval(() => this.loadUsageStats(), 30000);
    }

    setupEventListeners() {
        // Mode buttons
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.selectMode(e.currentTarget));
        });

        // Model selector
        document.getElementById('model-select').addEventListener('change', (e) => {
            this.selectModel(e.target.value);
        });

        // Temperature slider
        document.getElementById('temperature').addEventListener('input', (e) => {
            this.currentTemperature = parseFloat(e.target.value);
            document.getElementById('temp-display').textContent = this.currentTemperature.toFixed(1);
        });

        // Refresh usage button
        document.getElementById('refresh-usage-btn').addEventListener('click', () => this.refreshUsageWithLoader());

        // Primary key buttons
        document.getElementById('primary-key-btn-1').addEventListener('click', () => this.setPrimaryKey('key1'));
        document.getElementById('primary-key-btn-2').addEventListener('click', () => this.setPrimaryKey('key2'));

        // Clear history button
        document.getElementById('clear-history-btn').addEventListener('click', () => this.clearHistory());

        // Convert button
        document.getElementById('convert-btn').addEventListener('click', () => this.convert());

        // Clear button
        document.getElementById('clear-btn').addEventListener('click', () => this.clear());

        // Copy button
        document.getElementById('copy-btn').addEventListener('click', () => this.copy());

        // Input text tracking
        document.getElementById('input-text').addEventListener('input', (e) => {
            const count = e.target.value.length;
            document.getElementById('char-count').textContent = `${count} characters`;
        });

        // Enter to convert (Ctrl+Enter)
        document.getElementById('input-text').addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                this.convert();
            }
        });

        // Modal close
        document.querySelector('.close').addEventListener('click', () => {
            document.getElementById('modal').classList.add('hidden');
        });

        window.addEventListener('click', (e) => {
            const modal = document.getElementById('modal');
            if (e.target === modal) {
                modal.classList.add('hidden');
            }
        });
    }

    async loadModels() {
        try {
            const response = await fetch('/api/models');
            const data = await response.json();

            this.models = data.models;
            const grouped = data.grouped;
            const defaultModel = data.default;

            // Build select options grouped by provider
            const select = document.getElementById('model-select');
            select.innerHTML = '';

            Object.keys(grouped).sort().forEach(category => {
                const optgroup = document.createElement('optgroup');
                optgroup.label = `${category} (${grouped[category].length})`;

                grouped[category].forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.name;
                    if (model.id === defaultModel) {
                        option.selected = true;
                    }
                    optgroup.appendChild(option);
                });

                select.appendChild(optgroup);
            });

            // Set default model
            this.currentModel = defaultModel;
            this.updateModelInfo(defaultModel);
        } catch (error) {
            console.error('Failed to load models:', error);
            this.showStatus('Failed to load available models', 'error');
        }
    }

    selectModel(modelId) {
        this.currentModel = modelId;
        this.updateModelInfo(modelId);
    }

    updateModelInfo(modelId) {
        const model = this.models.find(m => m.id === modelId);
        if (model) {
            const infoDiv = document.getElementById('model-info');
            infoDiv.innerHTML = `
                <strong>${model.name}</strong> by ${model.provider}
            `;
        }
    }

    async loadUsageStats() {
        try {
            const response = await fetch('/api/usage');
            if (!response.ok) {
                console.error('API returned status:', response.status);
                return;
            }

            const data = await response.json();
            console.log('Usage data received:', data);

            if (data.usage && data.usage.key1 && data.usage.key2) {
                this.updateUsageDisplay('key1', data.usage.key1, data.preferences.primary_key);
                this.updateUsageDisplay('key2', data.usage.key2, data.preferences.primary_key);
            } else {
                console.warn('Invalid usage data structure:', data);
            }
        } catch (error) {
            console.error('Failed to load usage stats:', error);
        }
    }

    async refreshUsageWithLoader() {
        const btn = document.getElementById('refresh-usage-btn');
        const originalText = btn.textContent;
        btn.disabled = true;
        btn.textContent = '⏳ Loading...';

        try {
            await this.loadUsageStats();
            btn.textContent = '✅ Updated';
            setTimeout(() => {
                btn.textContent = originalText;
                btn.disabled = false;
            }, 2000);
        } catch (error) {
            btn.textContent = '❌ Failed';
            setTimeout(() => {
                btn.textContent = originalText;
                btn.disabled = false;
            }, 2000);
            console.error('Failed to refresh usage:', error);
        }
    }

    updateUsageDisplay(keyId, stats, primaryKey) {
        const keyNum = keyId === 'key1' ? '1' : '2';
        const fillBar = document.getElementById(`usage-fill-${keyNum}`);
        const statusBadge = document.getElementById(`usage-status-${keyNum}`);
        const usageText = document.getElementById(`usage-text-${keyNum}`);
        const usageMeta = document.getElementById(`usage-meta-${keyNum}`);
        const primaryBtn = document.getElementById(`primary-key-btn-${keyNum}`);

        if (!fillBar || !stats) {
            console.warn(`Missing elements for ${keyId}`);
            return;
        }

        // Update fill bar
        const percentage = stats.percentage_used || 0;
        fillBar.style.width = Math.min(percentage, 100) + '%';
        fillBar.className = `usage-fill ${stats.status || 'good'}`;

        // Update status badge
        const statusText = (stats.status || 'good').charAt(0).toUpperCase() + (stats.status || 'good').slice(1);
        statusBadge.textContent = statusText;
        statusBadge.className = `status-badge ${stats.status || 'good'}`;

        // Update text
        const tokensUsed = stats.tokens_used || 0;
        const dailyLimit = stats.daily_limit || 100000;
        usageText.textContent = `Tokens: ${tokensUsed.toLocaleString()} / ${dailyLimit.toLocaleString()}`;

        // Update metadata
        const callsMade = stats.calls_made || 0;
        const remaining = stats.remaining || dailyLimit;
        usageMeta.textContent = `${callsMade} calls • ${remaining.toLocaleString()} remaining`;

        // Update primary key indicator
        if (primaryKey === keyId) {
            primaryBtn.textContent = '⭐ Primary';
            primaryBtn.style.background = 'var(--primary)';
            primaryBtn.style.color = 'white';
        } else {
            primaryBtn.textContent = '⚪ Set Primary';
            primaryBtn.style.background = 'var(--bg-light)';
            primaryBtn.style.color = 'var(--text-dark)';
        }
    }

    setPrimaryKey(keyId) {
        console.log(`Setting primary key to: ${keyId}`);

        fetch('/api/preferences', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ primary_key: keyId })
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Preference updated:', data);
            this.loadUsageStats();
            const displayName = keyId === 'key1' ? 'API Key 1' : 'API Key 2';
            this.showStatus(`✅ Switched to ${displayName} as primary`, 'success');
        })
        .catch(err => {
            console.error('Error updating preference:', err);
            this.showStatus(`❌ Failed to update: ${err.message}`, 'error');
        });
    }


    selectMode(btn) {
        // Update active button
        document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update current mode
        this.currentMode = btn.dataset.mode;
    }

    async convert() {
        const inputText = document.getElementById('input-text').value.trim();

        if (!inputText) {
            this.showStatus('Please enter some text to convert', 'error');
            return;
        }

        if (!this.currentModel) {
            this.showStatus('Please select a model', 'error');
            return;
        }

        const convertBtn = document.getElementById('convert-btn');
        convertBtn.disabled = true;
        convertBtn.innerHTML = '<span class="spinner"></span>Converting...';

        this.showStatus(`Processing with ${this.models.find(m => m.id === this.currentModel)?.name}...`, 'loading');

        try {
            const response = await fetch('/api/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: inputText,
                    mode: this.currentMode,
                    model: this.currentModel,
                    temperature: this.currentTemperature
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Conversion failed');
            }

            const data = await response.json();

            // Display output
            document.getElementById('output-text').value = data.converted;

            // Add to history
            this.addToHistory({
                original: data.original.substring(0, 50) + (data.original.length > 50 ? '...' : ''),
                converted: data.converted,
                mode: data.mode,
                model: data.model,
                tokens_used: data.tokens_used,
                api_key_used: data.api_key_used,
                timestamp: new Date().toLocaleString()
            });

            // Reload usage stats
            this.loadUsageStats();

            this.showStatus(`✅ Converted! Used ${data.tokens_used} tokens from ${data.api_key_used.toUpperCase()}`, 'success');
        } catch (error) {
            this.showStatus(`❌ Error: ${error.message}`, 'error');
            console.error('Conversion error:', error);
        } finally {
            convertBtn.disabled = false;
            convertBtn.textContent = '✨ Convert';
        }
    }

    clear() {
        document.getElementById('input-text').value = '';
        document.getElementById('output-text').value = '';
        document.getElementById('char-count').textContent = '0 characters';
        this.showStatus('');
    }

    copy() {
        const outputText = document.getElementById('output-text');

        if (!outputText.value) {
            this.showStatus('No text to copy', 'error');
            return;
        }

        navigator.clipboard.writeText(outputText.value).then(() => {
            this.showStatus('📋 Copied to clipboard!', 'success');
        }).catch(() => {
            this.showStatus('Failed to copy', 'error');
        });
    }

    addToHistory(item) {
        this.history.unshift(item);
        this.history = this.history.slice(0, 20); // Keep last 20
        localStorage.setItem('conversionHistory', JSON.stringify(this.history));
        this.renderHistory();
    }

    renderHistory() {
        const historyDiv = document.getElementById('history');

        if (this.history.length === 0) {
            historyDiv.innerHTML = '<p style="color: var(--text-light);">No conversions yet</p>';
            return;
        }

        historyDiv.innerHTML = this.history.map((item, idx) => `
            <div class="history-item" onclick="converter.showHistoryItem(${idx})">
                <div class="history-item-text">${this.escapeHtml(item.original)}</div>
                <div class="history-item-mode">📌 ${item.mode} • ${item.model || 'default'} • ${item.timestamp}</div>
            </div>
        `).join('');
    }

    clearHistory() {
        if (confirm('Are you sure you want to clear all conversion history? This cannot be undone.')) {
            this.history = [];
            localStorage.removeItem('conversionHistory');
            this.renderHistory();
            this.showStatus('✅ History cleared', 'success');
        }
    }

    showHistoryItem(idx) {
        const item = this.history[idx];
        const modal = document.getElementById('modal');
        const modalBody = document.getElementById('modal-body');
        const modelName = this.models.find(m => m.id === item.model)?.name || item.model || 'default';

        modalBody.innerHTML = `
            <h3>Conversion History</h3>
            <div style="margin-top: 20px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px; font-size: 0.9em;">
                    <div><strong>Mode:</strong> ${item.mode}</div>
                    <div><strong>Model:</strong> ${modelName}</div>
                    <div><strong>Tokens:</strong> ${item.tokens_used || 'N/A'}</div>
                    <div><strong>API Key:</strong> ${(item.api_key_used || 'N/A').toUpperCase()}</div>
                    <div colspan="2" style="grid-column: 1/-1;"><strong>Time:</strong> ${item.timestamp}</div>
                </div>
                <h4>Original:</h4>
                <p style="background: var(--bg-light); padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                    ${this.escapeHtml(item.original)}
                </p>
                <h4>Converted:</h4>
                <p style="background: var(--bg-light); padding: 15px; border-radius: 6px; margin-bottom: 20px; white-space: pre-wrap;">
                    ${this.escapeHtml(item.converted)}
                </p>
            </div>
        `;

        modal.classList.remove('hidden');
    }

    showStatus(message, type) {
        const status = document.getElementById('status');

        if (!message) {
            status.classList.remove('visible', 'loading', 'success', 'error');
            return;
        }

        status.textContent = message;
        status.className = `status visible ${type}`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.converter = new TextConverter();
});
