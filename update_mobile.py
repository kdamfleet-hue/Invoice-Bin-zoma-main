import re

# --- Update base_styles.css ---
css_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\static\base_styles.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

mobile_css = r'''
/* =========================================
   Mobile Sidebar Overrides (No Push, Overlay Instead)
   ========================================= */
.bz-sidebar-backdrop {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    background: rgba(0, 0, 0, 0.6) !important;
    backdrop-filter: blur(4px) !important;
    z-index: 999 !important; /* Just below the sidebar */
    opacity: 0 !important;
    visibility: hidden !important;
    transition: all 0.3s ease !important;
}

body.sidebar-open .bz-sidebar-backdrop {
    opacity: 1 !important;
    visibility: visible !important;
}

@media (max-width: 768px) {
    /* Do NOT push the content on mobile */
    body.sidebar-open {
        margin-right: 0 !important;
        overflow: hidden !important; /* Prevent background scrolling */
    }
    
    /* Make sidebar slightly wider on mobile to be easily tappable */
    body .bz-topbar {
        width: 280px !important;
        right: -300px !important;
    }
    
    body.sidebar-open .bz-topbar {
        right: 0 !important;
        box-shadow: -10px 0 50px rgba(0,0,0,0.8) !important;
    }
}
'''

css += "\n" + mobile_css

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

# --- Update app_ux.js ---
js_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\static\app_ux.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the old hamburger logic with the new one that includes the backdrop
old_hamburger_logic = r'''document.addEventListener('DOMContentLoaded', () => {
    // Check if the hamburger already exists to prevent duplicates
    if (!document.querySelector('.bz-hamburger')) {
        const btn = document.createElement('button');
        // using lucide menu icon instead of raw ☰
        btn.innerHTML = '<i data-lucide="menu"></i>';
        btn.className = 'bz-hamburger';
        btn.onclick = () => {
            document.body.classList.toggle('sidebar-open');
        };
        document.body.appendChild(btn);
        
        // Re-render lucide icons if loaded
        if (typeof lucide !== 'undefined' && lucide.createIcons) {
            lucide.createIcons();
        }
    }
});'''

new_hamburger_logic = r'''document.addEventListener('DOMContentLoaded', () => {
    // Check if the hamburger already exists to prevent duplicates
    if (!document.querySelector('.bz-hamburger')) {
        const btn = document.createElement('button');
        // using lucide menu icon instead of raw ☰
        btn.innerHTML = '<i data-lucide="menu"></i>';
        btn.className = 'bz-hamburger';
        
        // Mobile backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'bz-sidebar-backdrop';
        
        btn.onclick = () => {
            document.body.classList.toggle('sidebar-open');
        };
        
        backdrop.onclick = () => {
            document.body.classList.remove('sidebar-open');
        };
        
        document.body.appendChild(backdrop);
        document.body.appendChild(btn);
        
        // Re-render lucide icons if loaded
        if (typeof lucide !== 'undefined' && lucide.createIcons) {
            lucide.createIcons();
        }
    }
});'''

js = js.replace(old_hamburger_logic, new_hamburger_logic)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("Mobile responsive sidebar logic successfully applied!")
