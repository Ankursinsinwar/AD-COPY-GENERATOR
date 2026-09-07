/**
 * Campaign History Renderer Script
 */

window.HistoryModule = {

    init() {
        const refreshBtn = document.getElementById('refreshHistoryBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadHistory());
        }
    },

    async loadHistory() {
        const container = document.getElementById('historyListContainer');
        if (!container) return;

        container.innerHTML = `
            <div class="loading-box">
                <div class="spinner"></div>
                <p>Loading history...</p>
            </div>
        `;

        try {
            const res = await fetch('/api/history');
            const data = await res.json();

            if (res.ok && data.status === 'success') {
                this.renderHistoryList(data.history || []);
            } else {
                container.innerHTML = `<div class="empty-state">Failed to load history: ${data.error || 'Unknown error'}</div>`;
            }
        } catch (e) {
            container.innerHTML = `<div class="empty-state">Connection error loading history.</div>`;
        }
    },

    renderHistoryList(history) {
        const container = document.getElementById('historyListContainer');
        if (!container) return;

        if (history.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-history"></i>
                    <h3>No Saved Campaigns Yet</h3>
                    <p>Generated campaigns will automatically be saved and listed here.</p>
                </div>
            `;
            return;
        }

        let html = `<div style="display: flex; flex-direction: column; gap: 1rem;">`;

        history.forEach(item => {
            const dateStr = item.timestamp ? new Date(item.timestamp).toLocaleString() : 'Recent';
            const product = item.product_name || item.product || 'Campaign';
            const tone = item.tone ? item.tone.charAt(0).toUpperCase() + item.tone.slice(1) : 'Professional';
            const platforms = (item.platforms || item.selected_platforms || []).join(', ') || 'All Platforms';
            const score = item.overall_score || 0;
            const campaignId = item.id || item.campaign_id;

            html += `
                <div class="results-header-bar" style="cursor: pointer;" onclick="window.HistoryModule.openHistoryCampaign('${campaignId}')">
                    <div>
                        <h3 style="font-size: 1.1rem; margin-bottom: 0.25rem;">${this.escapeHtml(product)}</h3>
                        <p class="text-secondary" style="font-size: 0.85rem;">
                            <i class="far fa-clock"></i> ${dateStr} • <strong>Platforms:</strong> ${this.escapeHtml(platforms)} • <strong>Tone:</strong> ${tone}
                        </p>
                    </div>
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div class="overall-score-badge ${score >= 80 ? '' : 'mid'}">
                            Score: ${score}/100
                        </div>
                        <button class="btn-secondary" style="padding: 0.5rem 0.8rem;">
                            <i class="fas fa-folder-open"></i> View
                        </button>
                    </div>
                </div>
            `;
        });

        html += `</div>`;
        container.innerHTML = html;
    },

    async openHistoryCampaign(campaignId) {
        try {
            const res = await fetch(`/api/history/${campaignId}`);
            const data = await res.json();

            if (res.ok && data.status === 'success' && data.campaign) {
                window.App.currentCampaign = data.campaign;

                // Switch to generator tab & render results
                const navGen = document.getElementById('navGeneratorBtn');
                const navHist = document.getElementById('navHistoryBtn');
                const genView = document.getElementById('generatorView');
                const histView = document.getElementById('historyView');

                navGen.classList.add('active');
                navHist.classList.remove('active');
                genView.style.display = 'block';
                histView.style.display = 'none';

                if (window.ResultsModule) {
                    window.ResultsModule.renderResults(data.campaign);
                }
                window.App.showToast('Loaded campaign from history!', 'success');
            } else {
                window.App.showToast('Could not load selected campaign', 'error');
            }
        } catch (e) {
            window.App.showToast('Error fetching campaign details', 'error');
        }
    },

    escapeHtml(str) {
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    window.HistoryModule.init();
});
