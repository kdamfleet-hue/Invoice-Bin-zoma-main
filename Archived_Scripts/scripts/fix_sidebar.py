import os

css_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\static\base_styles.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css_content = f.read()

# Add the sidebar CSS at the end
sidebar_css = """

/* ============================================================ */
/* NEW SIDEBAR OVERRIDES (Requested by User for Sidebar Hover)  */
/* ============================================================ */

/* Hide useless tabs */
.bz-nav a[href="/purchase"],
.bz-nav a[href="/search"],
.bz-nav a[href="/gps_sync"],
.bz-nav a[href="/tracking"],
.bz-nav a[href="/cameras"] {
    display: none !important;
}

/* Transform Topbar into Hover Sidebar */
.bz-topbar {
    position: fixed !important;
    top: 0 !important;
    right: calc(-260px + 12px) !important; /* 12px peek zone */
    width: 260px !important;
    height: 100vh !important;
    flex-direction: column !important;
    justify-content: flex-start !important;
    align-items: flex-start !important;
    background: rgba(10, 15, 25, 0.98) !important;
    backdrop-filter: blur(20px) !important;
    border-left: 2px solid rgba(197, 160, 89, 0.3) !important;
    border-bottom: none !important;
    padding: 2rem 1rem !important;
    transition: right 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    z-index: 9999 !important;
    border-radius: 0 !important;
    box-shadow: -5px 0 20px rgba(0,0,0,0.5) !important;
}

/* Expand on Hover */
.bz-topbar:hover, .bz-topbar:focus-within {
    right: 0 !important;
}

/* Add an indicator line for the peek zone */
.bz-topbar::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 2px;
    width: 4px;
    height: 40px;
    background: var(--gold-primary);
    border-radius: 4px;
    transform: translateY(-50%);
    opacity: 0.6;
    transition: opacity 0.3s;
}
.bz-topbar:hover::before {
    opacity: 0;
}

/* Adjust internal elements for vertical layout */
.bz-topbar .bz-brand {
    flex-direction: column !important;
    align-items: center !important;
    text-align: center !important;
    margin-bottom: 2rem !important;
    width: 100% !important;
}
.bz-topbar .bz-brand img {
    margin-bottom: 1rem !important;
    width: 45px !important;
}
.bz-topbar .bz-nav {
    flex-direction: column !important;
    width: 100% !important;
    gap: 0.5rem !important;
    align-items: stretch !important;
    overflow-y: auto !important;
}
.bz-topbar .bz-nav a {
    width: 100% !important;
    padding: 12px 16px !important;
    justify-content: flex-start !important;
    border-radius: 8px !important;
}
.bz-topbar .bz-actions {
    margin-top: auto !important; /* Push to bottom */
    width: 100% !important;
    justify-content: space-between !important;
    padding-top: 1rem !important;
    border-top: 1px solid rgba(255,255,255,0.1) !important;
}

/* Make main content full width */
body {
    padding-top: 20px !important; /* Remove topbar space */
    padding-right: 12px !important; /* Space for the peek zone */
}
.bz-shell {
    margin-top: 0 !important;
}
"""

if "NEW SIDEBAR OVERRIDES" not in css_content:
    with open(css_path, 'a', encoding='utf-8') as f:
        f.write(sidebar_css)
        print("Sidebar CSS applied successfully.")
else:
    print("Sidebar CSS already applied.")
