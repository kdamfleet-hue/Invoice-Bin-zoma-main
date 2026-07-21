import re

theme_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\static\css\theme.css'
with open(theme_path, 'r', encoding='utf-8') as f:
    theme = f.read()

# Enhance glass-panel with a more luxurious blur and border
theme = re.sub(
    r'\.glass-panel \{[^}]+\}',
    r'''.glass-panel {
    background: rgba(19, 23, 34, 0.65);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(197, 160, 89, 0.15);
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}''', theme, flags=re.DOTALL
)

# Enhance glass-panel hover
theme = re.sub(
    r'\.glass-panel:hover \{[^}]+\}',
    r'''.glass-panel:hover {
    border-color: rgba(197, 160, 89, 0.5);
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.6), inset 0 0 20px rgba(197, 160, 89, 0.05);
    transform: translateY(-4px);
}''', theme, flags=re.DOTALL
)

with open(theme_path, 'w', encoding='utf-8') as f:
    f.write(theme)

base_styles_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\static\base_styles.css'
with open(base_styles_path, 'r', encoding='utf-8') as f:
    base_styles = f.read()

# Use regex to find and replace the topbar and nav blocks
base_styles = re.sub(r'\.bz-topbar\s*\{[^}]+\}', '', base_styles)
base_styles = re.sub(r'\.bz-nav\s*\{[^}]+\}', '', base_styles)
base_styles = re.sub(r'\.bz-nav\s+a\s*\{[^}]+\}', '', base_styles)
base_styles = re.sub(r'\.bz-nav\s+a:hover\s*\{[^}]+\}', '', base_styles)
base_styles = re.sub(r'\.bz-nav\s+a\.active\s*\{[^}]+\}', '', base_styles)

topbar_replacement = r'''.bz-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 32px;
    background: rgba(11, 13, 20, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(197, 160, 89, 0.2);
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
}

.bz-nav {
    display: flex;
    gap: 24px;
    align-items: center;
}

.bz-nav a {
    color: var(--text-muted, #94a3b8);
    text-decoration: none;
    font-size: 0.95rem;
    font-weight: 600;
    font-family: 'Cairo', sans-serif;
    padding: 8px 12px;
    border-radius: 8px;
    transition: all 0.3s ease;
    position: relative;
}

.bz-nav a::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 2px;
    background: var(--gold-primary, #c5a059);
    transition: width 0.3s ease;
}

.bz-nav a:hover {
    color: var(--text-main, #f8fafc);
    background: rgba(255, 255, 255, 0.03);
}

.bz-nav a:hover::after {
    width: 60%;
}

.bz-nav a.active {
    color: var(--gold-primary, #c5a059);
    background: rgba(197, 160, 89, 0.1);
}

.bz-nav a.active::after {
    width: 80%;
}
'''

base_styles += "\n" + topbar_replacement

with open(base_styles_path, 'w', encoding='utf-8') as f:
    f.write(base_styles)

print("CSS Overhauled!")
