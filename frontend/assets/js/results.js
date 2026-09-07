/**
 * Ad Copy Results Renderer Script
 */

window.ResultsModule = {

    renderResults(campaign) {
        const emptyState = document.getElementById('emptyState');
        const loadingBox = document.getElementById('loadingBox');
        const resultsDisplay = document.getElementById('campaignResultsDisplay');
        const container = document.getElementById('platformCardsContainer');

        const activeProduct = document.getElementById('activeCampaignProduct');
        const activeMeta = document.getElementById('activeCampaignMeta');

        if (emptyState) emptyState.style.display = 'none';
        if (loadingBox) loadingBox.style.display = 'none';
        if (resultsDisplay) resultsDisplay.style.display = 'block';

        const productName = campaign.product_name || campaign.product || 'Campaign';
        const platformsCount = campaign.platforms ? campaign.platforms.length : 0;
        const toneName = campaign.tone ? campaign.tone.charAt(0).toUpperCase() + campaign.tone.slice(1) : 'Professional';
        const overallScore = campaign.overall_score || 0;

        if (activeProduct) activeProduct.textContent = `${productName} — Results`;
        if (activeMeta) activeMeta.textContent = `${platformsCount} Platforms • ${toneName} Tone • Overall Score: ${overallScore}/100`;

        container.innerHTML = '';

        const results = campaign.results || {};

        Object.keys(results).forEach(platformName => {
            const platformData = results[platformName];
            const platformSection = this.createPlatformSection(platformName, platformData);
            container.appendChild(platformSection);
        });
    },

    createPlatformSection(platformName, platformData) {
        const section = document.createElement('div');
        section.className = 'platform-section';

        let iconClass = 'fa-bullhorn';
        const lowerP = platformName.toLowerCase();
        if (lowerP.includes('google')) iconClass = 'fab fa-google';
        if (lowerP.includes('facebook')) iconClass = 'fab fa-facebook';
        if (lowerP.includes('instagram')) iconClass = 'fab fa-instagram';
        if (lowerP.includes('linkedin')) iconClass = 'fab fa-linkedin';
        if (lowerP.includes('twitter') || lowerP.includes('x')) iconClass = 'fab fa-twitter';

        let html = `
            <div class="platform-title">
                <i class="${iconClass}"></i> ${platformName}
            </div>
        `;

        if (platformData.error) {
            html += `
                <div class="variation-card" style="border-color: rgba(239, 68, 68, 0.4); background: rgba(239, 68, 68, 0.05);">
                    <div class="card-header">
                        <span class="variant-label" style="color: #ef4444;"><i class="fas fa-exclamation-circle"></i> Generation Warning</span>
                    </div>
                    <p class="field-content">${platformData.error}</p>
                </div>
            `;
            section.innerHTML = html;
            return section;
        }

        const variations = platformData.variations || [];
        html += `<div class="variations-grid">`;

        variations.forEach(v => {
            const scoreObj = v.score || {};
            const overall = scoreObj.overall !== undefined ? scoreObj.overall : (scoreObj.overall_performance || 0);
            const scoreClass = overall >= 80 ? '' : 'mid';

            const headline = this.escapeHtml(v.headline || '');
            const body = this.escapeHtml(v.body || v.description || '');
            const cta = this.escapeHtml(v.cta || '');
            const hashtags = (v.hashtags || []).join(' ');

            const headlineStr = scoreObj.headline_strength || 0;
            const clarity = scoreObj.clarity || 0;
            const emotional = scoreObj.emotional_appeal || 0;
            const ctaEff = scoreObj.cta_effectiveness || 0;

            const strengths = (v.strengths || []).map(s => `<div class="feedback-item strength"><i class="fas fa-check-circle"></i> <span>${this.escapeHtml(s)}</span></div>`).join('');
            const suggestions = (v.suggestions || []).map(s => `<div class="feedback-item suggestion"><i class="fas fa-lightbulb"></i> <span>${this.escapeHtml(s)}</span></div>`).join('');

            html += `
                <div class="variation-card">
                    <div class="card-header">
                        <div class="variant-tag">
                            <div class="variant-id">${v.id || 'A'}</div>
                            <div class="variant-label">${this.escapeHtml(v.label || 'Variation')}</div>
                        </div>
                        <div class="overall-score-badge ${scoreClass}">
                            Score: ${overall}/100
                        </div>
                    </div>

                    <!-- Headline Field -->
                    <div class="copy-field">
                        <div class="field-label">Headline</div>
                        <div class="field-content">${headline}</div>
                        <button class="copy-btn-icon" title="Copy Headline" onclick="window.App.copyToClipboard('${this.escapeJs(headline)}', 'Headline copied!')">
                            <i class="fas fa-copy"></i>
                        </button>
                    </div>

                    <!-- Body Field -->
                    <div class="copy-field">
                        <div class="field-label">Body / Primary Text</div>
                        <div class="field-content">${body}</div>
                        <button class="copy-btn-icon" title="Copy Body" onclick="window.App.copyToClipboard('${this.escapeJs(body)}', 'Body text copied!')">
                            <i class="fas fa-copy"></i>
                        </button>
                    </div>

                    <!-- CTA & Hashtags -->
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                        <div class="copy-field">
                            <div class="field-label">Call to Action</div>
                            <div class="field-content" style="font-weight: 600;">${cta}</div>
                        </div>
                        <div class="copy-field">
                            <div class="field-label">Hashtags</div>
                            <div class="field-content" style="font-size: 0.8rem; color: #6366f1;">${hashtags || 'None'}</div>
                        </div>
                    </div>

                    <!-- Scores Breakdown Grid -->
                    <div class="score-breakdown-grid">
                        <div class="metric-pill"><span>Headline Impact:</span> <span class="metric-score">${headlineStr}</span></div>
                        <div class="metric-pill"><span>Clarity:</span> <span class="metric-score">${clarity}</span></div>
                        <div class="metric-pill"><span>Emotional Appeal:</span> <span class="metric-score">${emotional}</span></div>
                        <div class="metric-pill"><span>CTA Power:</span> <span class="metric-score">${ctaEff}</span></div>
                    </div>

                    <!-- Strengths & Suggestions -->
                    <div class="card-feedback-box">
                        ${strengths}
                        ${suggestions}
                    </div>

                    <!-- Copy All Button -->
                    <button class="btn-secondary" style="margin-top: 0.5rem; justify-content: center;" onclick="window.ResultsModule.copyFullAd('${this.escapeJs(headline)}', '${this.escapeJs(body)}', '${this.escapeJs(cta)}', '${this.escapeJs(hashtags)}')">
                        <i class="fas fa-paste"></i> Copy Full Ad
                    </button>
                </div>
            `;
        });

        html += `</div>`;
        section.innerHTML = html;
        return section;
    },

    copyFullAd(headline, body, cta, hashtags) {
        let text = `Headline: ${headline}\n\nBody: ${body}\n\nCTA: ${cta}`;
        if (hashtags) {
            text += `\n\nHashtags: ${hashtags}`;
        }
        window.App.copyToClipboard(text, 'Full Ad Copy copied!');
    },

    escapeHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    },

    escapeJs(str) {
        return String(str)
            .replace(/\\/g, '\\\\')
            .replace(/'/g, "\\'")
            .replace(/\n/g, '\\n')
            .replace(/\r/g, '');
    }
};
