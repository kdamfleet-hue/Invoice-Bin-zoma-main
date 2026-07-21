import re

file_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\static\app_ux.js'
with open(file_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Remove the old hover logic if it exists (the one that opened on the edge of the screen)
# We will just append the hamburger logic to DOMContentLoaded

hamburger_logic = r'''
document.addEventListener('DOMContentLoaded', () => {
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
});
'''

# Check if we already injected it
if 'bz-hamburger' not in js:
    js += "\n" + hamburger_logic

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("app_ux.js updated with Hamburger logic!")
