import os

theme_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\static\css\theme.css'

with open(theme_path, 'r', encoding='utf-8') as f:
    content = f.read()

responsive_css = """
/* =========================================
   Responsive Design (Mobile, Tablet, Desktop)
   ========================================= */

@media (max-width: 1024px) { /* iPad / Tablet */
    .hub-grid {
        grid-template-columns: repeat(2, 1fr) !important;
    }
    .fd-stats {
        flex-wrap: wrap !important;
        justify-content: center !important;
    }
    .fd-stat {
        flex: 1 1 30% !important;
    }
}

@media (max-width: 768px) { /* Mobile phones */
    /* Dashboard Grid */
    .hub-grid {
        grid-template-columns: 1fr !important;
    }
    
    /* Topbar Navigation */
    .bz-topbar {
        flex-direction: column !important;
        align-items: center !important;
        padding: 15px 10px !important;
    }
    .bz-brand-text {
        font-size: 0.9rem !important;
        text-align: center !important;
    }
    
    /* Scrollable Horizontal Nav for Mobile */
    .bz-nav {
        display: flex !important;
        flex-direction: row !important;
        overflow-x: auto !important;
        white-space: nowrap !important;
        padding-bottom: 5px !important;
        justify-content: flex-start !important;
        width: 100% !important;
        -webkit-overflow-scrolling: touch;
        gap: 5px !important;
    }
    .bz-nav::-webkit-scrollbar {
        height: 4px;
    }
    .bz-nav::-webkit-scrollbar-thumb {
        background: var(--gold-primary);
        border-radius: 4px;
    }
    .bz-nav a {
        flex-shrink: 0 !important;
        font-size: 0.85rem !important;
        padding: 8px 12px !important;
    }
    
    /* Actions Bar */
    .bz-actions-bar {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 10px !important;
    }
    .bz-actions-bar button {
        width: 100% !important;
        justify-content: center !important;
    }
    
    /* Cards and Tables */
    .bz-card {
        padding: 16px !important;
    }
    .bz-card-title {
        font-size: 1.1rem !important;
    }
    
    .table-wrapper {
        margin-bottom: 1rem !important;
        -webkit-overflow-scrolling: touch;
    }
    .bz-table th, .bz-table td {
        padding: 10px !important;
        font-size: 0.85rem !important;
    }
    
    /* Fleet Stats */
    .fd-stats {
        flex-direction: column !important;
    }
    .fd-stat {
        width: 100% !important;
        margin-bottom: 10px !important;
    }
    
    /* Stats Circles */
    .stat-circle {
        width: 120px !important;
        height: 120px !important;
    }
    .stat-circle .count-up {
        font-size: 2rem !important;
    }
}
"""

if "Responsive Design (Mobile, Tablet, Desktop)" not in content:
    with open(theme_path, 'a', encoding='utf-8') as f:
        f.write("\n" + responsive_css)
    print("Responsive CSS appended to theme.css.")
else:
    print("Responsive CSS already present.")
