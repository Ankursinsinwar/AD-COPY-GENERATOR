/**
 * CSV & Notion Export Module Script
 */

window.ExportModule = {

    init() {
        this.bindExportButtons();
        this.bindModal();
    },

    bindExportButtons() {
        const csvBtn = document.getElementById('exportCsvBtn');
        const notionBtn = document.getElementById('exportNotionBtn');

        if (csvBtn) {
            csvBtn.addEventListener('click', () => this.handleCsvExport());
        }

        if (notionBtn) {
            notionBtn.addEventListener('click', () => this.handleNotionExport());
        }
    },

    bindModal() {
        const modal = document.getElementById('notionModal');
        const closeBtn = document.getElementById('closeModalBtn');
        const copyBtn = document.getElementById('copyMarkdownBtn');
        const downloadBtn = document.getElementById('downloadMdFileBtn');

        if (closeBtn && modal) {
            closeBtn.addEventListener('click', () => modal.classList.remove('open'));
            modal.addEventListener('click', (e) => {
                if (e.target === modal) modal.classList.remove('open');
            });
        }

        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                const content = document.getElementById('markdownPreviewContent').textContent;
                window.App.copyToClipboard(content, 'Notion Markdown copied!');
            });
        }

        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                const content = document.getElementById('markdownPreviewContent').textContent;
                const blob = new Blob([content], { type: 'text/markdown' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'campaign_notion_export.md';
                a.click();
                URL.revokeObjectURL(url);
                window.App.showToast('Downloaded .md file!', 'success');
            });
        }
    },

    async handleCsvExport() {
        const campaign = window.App.currentCampaign;
        if (!campaign) {
            window.App.showToast('No active campaign to export', 'warning');
            return;
        }

        try {
            const res = await fetch('/api/export/csv', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ campaign })
            });

            if (res.ok) {
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                const productName = campaign.product_name || 'campaign';
                a.download = `${productName.toLowerCase().replace(/\s+/g, '_')}_ad_copy.csv`;
                a.click();
                URL.revokeObjectURL(url);
                window.App.showToast('CSV downloaded successfully!', 'success');
            } else {
                window.App.showToast('Failed to export CSV', 'error');
            }
        } catch (e) {
            window.App.showToast('Error connecting for CSV export', 'error');
        }
    },

    async handleNotionExport() {
        const campaign = window.App.currentCampaign;
        if (!campaign) {
            window.App.showToast('No active campaign to export', 'warning');
            return;
        }

        const modal = document.getElementById('notionModal');
        const preview = document.getElementById('markdownPreviewContent');

        preview.textContent = 'Generating Notion Markdown...';
        modal.classList.add('open');

        try {
            const res = await fetch('/api/export/notion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ campaign })
            });

            const data = await res.json();
            if (res.ok && data.status === 'success') {
                preview.textContent = data.markdown;
            } else {
                preview.textContent = 'Failed to generate Notion Markdown export.';
            }
        } catch (e) {
            preview.textContent = 'Error connecting to server for Notion export.';
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    window.ExportModule.init();
});
