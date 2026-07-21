import os

theme_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\static\css\theme.css'

with open(theme_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_styles = """
/* =========================================
   Unified Luxury Inputs (bz-input)
   ========================================= */
.bz-input, .bz-select {
    width: 100%;
    padding: 12px 16px;
    background: rgba(10, 15, 25, 0.6);
    border: 1px solid rgba(197, 160, 89, 0.2);
    border-radius: 8px;
    color: var(--text-main);
    font-family: 'Cairo', sans-serif;
    font-size: 0.95rem;
    transition: all 0.3s ease;
    outline: none;
    box-sizing: border-box;
}

.bz-input:focus, .bz-select:focus {
    border-color: var(--gold-primary);
    box-shadow: 0 0 0 3px rgba(197, 160, 89, 0.15);
    background: rgba(10, 15, 25, 0.9);
}

.bz-input::placeholder {
    color: rgba(255, 255, 255, 0.3);
}

/* =========================================
   Unified Luxury Tables (bz-table)
   ========================================= */
.table-wrapper {
    overflow-x: auto;
    border-radius: 12px;
    border: 1px solid var(--glass-border);
    background: rgba(10, 15, 25, 0.4);
    margin-bottom: 1.5rem;
}

.bz-table {
    width: 100%;
    border-collapse: collapse;
    text-align: right;
    font-size: 0.95rem;
}

.bz-table th {
    background: rgba(0, 0, 0, 0.5);
    color: var(--gold-light);
    padding: 14px 16px;
    font-weight: 700;
    border-bottom: 2px solid var(--gold-primary);
    white-space: nowrap;
}

.bz-table td {
    padding: 12px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: var(--text-main);
    vertical-align: middle;
}

.bz-table tbody tr {
    transition: background 0.2s ease;
}

.bz-table tbody tr:hover {
    background: rgba(197, 160, 89, 0.05);
}

/* =========================================
   Unified Layout & Flex Utilities
   ========================================= */
.bz-actions-bar {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
    margin-bottom: 24px;
    background: rgba(0,0,0,0.2);
    padding: 16px;
    border-radius: 12px;
    border: 1px solid var(--glass-border);
}

.bz-card {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    margin-bottom: 24px;
}

.bz-card-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--gold-primary);
    margin-top: 0;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 12px;
}
"""

if "Unified Luxury Inputs" not in content:
    with open(theme_path, 'a', encoding='utf-8') as f:
        f.write("\n" + new_styles)
    print("Design system appended to theme.css.")
else:
    print("Design system already present in theme.css.")
