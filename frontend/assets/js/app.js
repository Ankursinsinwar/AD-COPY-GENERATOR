/**
 * Ad Copy Generator + A/B Tester — Main App Script
 * Manages core navigation, toast notification system, and API health check.
 */

window.App = {
    currentCampaign: null,
    
    init() {
        this.bindNavigation();
        this.checkApiHealth();
    },

    bindNavigation() {
        const navGen = document.getElementById('navGeneratorBtn');
        const navHist = document.getElementById('navHistoryBtn');
        const genView = document.getElementById('generatorView');
        const histView = document.getElementById('historyView');
        const pageTitle = document.getElementById('pageTitle');
        const pageSubtitle = document.getElementById('pageSubtitle');

        if (navGen && navHist) {
            navGen.addEventListener('click', () => {
                navGen.classList.add('active');
                navHist.classList.remove('active');
                genView.style.display = 'block';
                histView.style.display = 'none';
                pageTitle.textContent = 'AI Ad Copy Generator & A/B Tester';
                pageSubtitle.textContent = 'Multi-platform campaign generation with quality analytics & A/B variation strategy';
            });

            navHist.addEventListener('click', () => {
                navHist.classList.add('active');
                navGen.classList.remove('active');
                genView.style.display = 'none';
                histView.style.display = 'block';
                pageTitle.textContent = 'Campaign History';
                pageSubtitle.textContent = 'Browse locally persisted generations from data/history.json';
                if (window.HistoryModule) {
                    window.HistoryModule.loadHistory();
                }
            });
        }
    },

    async checkApiHealth() {
        const badge = document.getElementById('apiStatusBadge');
        const text = document.getElementById('apiStatusText');
        
        try {
            const res = await fetch('/api/health');
            if (res.ok) {
                const data = await res.json();
                const groqConfigured = data.groq_configured;
                badge.style.borderColor = 'rgba(16, 185, 129, 0.3)';
                text.textContent = groqConfigured ? 'Groq API Ready' : 'API Online (Demo Mode)';
            } else {
                badge.style.background = 'rgba(239, 68, 68, 0.1)';
                badge.style.color = '#ef4444';
                text.textContent = 'Backend Offline';
            }
        } catch (e) {
            if (badge && text) {
                badge.style.background = 'rgba(239, 68, 68, 0.1)';
                badge.style.color = '#ef4444';
                text.textContent = 'Backend Offline';
            }
        }
    },

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let icon = 'fa-info-circle';
        if (type === 'success') icon = 'fa-check-circle';
        if (type === 'warning') icon = 'fa-exclamation-triangle';
        if (type === 'error') icon = 'fa-times-circle';

        toast.innerHTML = `<i class="fas ${icon}"></i> <span>${message}</span>`;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    },

    async copyToClipboard(text, successMsg = 'Copied to clipboard!') {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast(successMsg, 'success');
        } catch (err) {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            this.showToast(successMsg, 'success');
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    window.App.init();
});
