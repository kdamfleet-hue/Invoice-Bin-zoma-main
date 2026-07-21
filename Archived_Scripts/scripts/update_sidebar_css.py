import re

file_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\static\base_styles.css'
with open(file_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Remove old bz-topbar styles
css = re.sub(r'\.bz-topbar\s*\{[^}]+\}', '', css)
css = re.sub(r'\.bz-nav\s*\{[^}]+\}', '', css)
css = re.sub(r'\.bz-nav\s+a\s*\{[^}]+\}', '', css)
css = re.sub(r'\.bz-nav\s+a:hover\s*\{[^}]+\}', '', css)
css = re.sub(r'\.bz-nav\s+a\.active\s*\{[^}]+\}', '', css)

sidebar_css = r'''
/* =========================================
   Professional Push Sidebar (Replaces Topbar)
   ========================================= */
.bz-topbar {
    position: fixed;
    top: 0;
    right: -280px; /* Hidden off-screen in RTL */
    width: 260px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    padding: 30px 20px;
    background: rgba(11, 13, 20, 0.95);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-left: 1px solid rgba(197, 160, 89, 0.15);
    z-index: 1000;
    transition: right 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
    box-shadow: -5px 0 30px rgba(0, 0, 0, 0.5);
    overflow-y: auto;
}

body.sidebar-open .bz-topbar {
    right: 0;
}

/* Push content to avoid overlap */
body {
    transition: margin-right 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}
body.sidebar-open {
    margin-right: 260px;
}

/* Inner Navigation styling */
.bz-nav {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 40px;
    width: 100%;
}

.bz-nav a {
    color: var(--text-muted, #94a3b8);
    text-decoration: none;
    font-size: 1.05rem;
    font-weight: 600;
    font-family: 'Cairo', sans-serif;
    padding: 12px 16px;
    border-radius: 12px;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    background: transparent;
    border: 1px solid transparent;
}

.bz-nav a:hover {
    color: var(--text-main, #f8fafc);
    background: rgba(255, 255, 255, 0.04);
    border-color: rgba(197, 160, 89, 0.1);
    transform: translateX(-5px); /* Move left slightly in RTL */
}

.bz-nav a.active {
    color: var(--gold-primary, #c5a059);
    background: rgba(197, 160, 89, 0.1);
    border-color: rgba(197, 160, 89, 0.3);
    box-shadow: inset 0 0 10px rgba(197, 160, 89, 0.05);
}

/* Brand area */
.bz-brand {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 10px;
}
.bz-brand img { width: 60px; height: auto; }
.bz-brand-text strong { color: var(--gold-primary); font-size: 1.2rem; display: block; }
.bz-brand-text span { font-size: 0.8rem; color: var(--text-muted); }

/* Hamburger Button */
.bz-hamburger {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 45px;
    height: 45px;
    border-radius: 12px;
    background: rgba(11, 13, 20, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(197, 160, 89, 0.3);
    color: var(--gold-primary);
    font-size: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 1001; /* Above sidebar */
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.bz-hamburger:hover {
    background: rgba(197, 160, 89, 0.15);
    transform: scale(1.05);
}

body.sidebar-open .bz-hamburger {
    /* If sidebar is open, keep hamburger visible but pushed slightly or styled differently if desired */
    background: rgba(197, 160, 89, 0.2);
    color: #fff;
}
'''

css += "\n" + sidebar_css

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(css)

print("base_styles.css updated for push sidebar!")
