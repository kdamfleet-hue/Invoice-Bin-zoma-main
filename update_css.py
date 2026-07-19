import re

def update_css(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replacement map
    glass_root = '''    :root {
      --fd-bg: transparent;
      --fd-surface: var(--glass-bg);
      --fd-surface2: rgba(255,255,255,0.03);
      --fd-border: var(--glass-border);
      --fd-gold: var(--gold-primary);
      --fd-gold2: var(--gold-light);
      --fd-text: var(--text-main);
      --fd-muted: var(--text-muted);
      --fd-red: var(--sys-err);
      --fd-green: var(--sys-ok);
      --fd-orange: var(--sys-warn);
      
      --bg-panel: var(--glass-bg);
      --accent-primary: var(--gold-primary);
      --border-glass: var(--glass-border);
    }'''
    
    # Replace root block in fleet_dashboard
    content = re.sub(r':root\s*\{[^}]+\}', glass_root, content, count=1)
    
    # Make cards glassmorphic
    content = re.sub(r'\.fd-stat\s*\{', '.fd-stat {\\n      backdrop-filter: var(--glass-blur);', content)
    content = re.sub(r'\.bz-card-head\s*\{', '.bz-card-head {\\n      backdrop-filter: var(--glass-blur);', content)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {filename}")

update_css('templates/fleet_dashboard.html')
update_css('templates/schedule.html')
