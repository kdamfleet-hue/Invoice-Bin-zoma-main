import re

file_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\static\base_styles.css'
with open(file_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Add a highly specific override block at the very end
override_css = r'''
/* =========================================
   HARD OVERRIDE FOR SIDEBAR (Fixing Specificity Issues)
   ========================================= */
body .bz-topbar {
    position: fixed !important;
    top: 0 !important;
    right: -280px !important;
    width: 260px !important;
    height: 100vh !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: stretch !important;
    padding: 30px 20px !important;
    background: rgba(11, 13, 20, 0.95) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-left: 1px solid rgba(197, 160, 89, 0.15) !important;
    border-bottom: none !important;
    z-index: 1000 !important;
    transition: right 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    box-shadow: -5px 0 30px rgba(0, 0, 0, 0.5) !important;
    overflow-y: auto !important;
}

body.sidebar-open .bz-topbar {
    right: 0 !important;
}

body .bz-topbar .bz-brand {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    text-align: center !important;
    gap: 10px !important;
    margin-bottom: 20px !important;
}

body .bz-topbar .bz-nav {
    display: flex !important;
    flex-direction: column !important;
    gap: 12px !important;
    width: 100% !important;
    align-items: stretch !important;
}

body .bz-topbar .bz-nav a {
    display: flex !important;
    width: auto !important;
    color: var(--text-muted, #94a3b8) !important;
    text-decoration: none !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    font-family: 'Cairo', sans-serif !important;
    padding: 12px 16px !important;
    border-radius: 12px !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    transition: all 0.3s ease !important;
}

body .bz-topbar .bz-nav a:hover {
    color: var(--text-main, #f8fafc) !important;
    background: rgba(255, 255, 255, 0.04) !important;
    border-color: rgba(197, 160, 89, 0.1) !important;
    transform: translateX(-5px) !important;
}

body .bz-topbar .bz-nav a.active {
    color: var(--gold-primary, #c5a059) !important;
    background: rgba(197, 160, 89, 0.1) !important;
    border-color: rgba(197, 160, 89, 0.3) !important;
    box-shadow: inset 0 0 10px rgba(197, 160, 89, 0.05) !important;
}

body .bz-topbar .bz-actions {
    display: flex !important;
    flex-direction: column !important;
    gap: 10px !important;
    margin-top: auto !important;
    align-items: center !important;
}
'''

css += "\n" + override_css

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(css)

print("base_styles.css hard overrides applied!")
