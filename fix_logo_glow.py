import glob
import re

for filename in glob.glob('templates/*.html'):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to remove the specific filter or just empty the block so it doesn't apply glowing effects
    # Match: body.dark-mode .site-logo { filter: brightness(0) invert(1) drop-shadow(...) }
    new_content = re.sub(r'(body\.dark-mode \.site-logo\s*\{)[^}]+(\})', r'\1 filter: drop-shadow(0 4px 6px rgba(0,0,0,0.5)); \2', content)
    
    if new_content != content:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filename}")
