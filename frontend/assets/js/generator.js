/**
 * Ad Copy Generator Form Handler Script
 */

window.GeneratorModule = {
    selectedPlatforms: ['google', 'facebook', 'instagram'],
    selectedTone: 'professional',
    variationCount: 3,

    init() {
        this.bindPills();
        this.bindSegments();
        this.bindForm();
    },

    bindPills() {
        // Platform pills
        const platformPills = document.querySelectorAll('#platformPillGrid .platform-pill');
        platformPills.forEach(pill => {
            pill.addEventListener('click', () => {
                const platformKey = pill.dataset.platform;
                if (pill.classList.contains('selected')) {
                    // Don't deselect if it's the last selected
                    if (this.selectedPlatforms.length > 1) {
                        pill.classList.remove('selected');
                        this.selectedPlatforms = this.selectedPlatforms.filter(p => p !== platformKey);
                    } else {
                        window.App.showToast('Select at least one platform', 'warning');
                    }
                } else {
                    pill.classList.add('selected');
                    if (!this.selectedPlatforms.includes(platformKey)) {
                        this.selectedPlatforms.push(platformKey);
                    }
                }
            });
        });

        // Tone pills
        const tonePills = document.querySelectorAll('#tonePillGrid .tone-pill');
        tonePills.forEach(pill => {
            pill.addEventListener('click', () => {
                tonePills.forEach(p => p.classList.remove('selected'));
                pill.classList.add('selected');
                this.selectedTone = pill.dataset.tone;
            });
        });
    },

    bindSegments() {
        const btns = document.querySelectorAll('#variationSegment .segment-btn');
        btns.forEach(btn => {
            btn.addEventListener('click', () => {
                btns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.variationCount = parseInt(btn.dataset.count, 10) || 3;
            });
        });
    },

    bindForm() {
        const form = document.getElementById('campaignForm');
        const submitBtn = document.getElementById('generateBtn');

        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleGenerate();
            });
        }
    },

    async handleGenerate() {
        const productNameInput = document.getElementById('productNameInput');
        const descriptionInput = document.getElementById('descriptionInput');
        const targetAudienceInput = document.getElementById('targetAudienceInput');
        const submitBtn = document.getElementById('generateBtn');

        const productName = productNameInput.value.trim();
        if (!productName) {
            window.App.showToast('Product name is required', 'error');
            return;
        }

        if (this.selectedPlatforms.length === 0) {
            window.App.showToast('Select at least one platform', 'error');
            return;
        }

        // Show loading state
        this.setLoading(true);

        const payload = {
            product_name: productName,
            description: descriptionInput.value.trim(),
            target_audience: targetAudienceInput.value.trim(),
            platforms: this.selectedPlatforms,
            tone: this.selectedTone,
            variation_count: this.variationCount
        };

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                window.App.currentCampaign = data.campaign;
                if (window.ResultsModule) {
                    window.ResultsModule.renderResults(data.campaign);
                }
                window.App.showToast('Campaign generated successfully!', 'success');
            } else {
                const errMessage = data.error || 'Failed to generate campaign';
                window.App.showToast(errMessage, 'error');
            }
        } catch (error) {
            window.App.showToast('Server connection error. Make sure Flask backend is running.', 'error');
        } finally {
            this.setLoading(false);
        }
    },

    setLoading(isLoading) {
        const submitBtn = document.getElementById('generateBtn');
        const emptyState = document.getElementById('emptyState');
        const loadingBox = document.getElementById('loadingBox');
        const resultsDisplay = document.getElementById('campaignResultsDisplay');

        if (isLoading) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Generating...</span>';
            if (emptyState) emptyState.style.display = 'none';
            if (resultsDisplay) resultsDisplay.style.display = 'none';
            if (loadingBox) loadingBox.style.display = 'flex';
        } else {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> <span>Generate Ad Copies</span>';
            if (loadingBox) loadingBox.style.display = 'none';
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    window.GeneratorModule.init();
});
