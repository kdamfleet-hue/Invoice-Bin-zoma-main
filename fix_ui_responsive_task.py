import os
import re

def fix_css():
    css_path = 'static/base_styles.css'
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Optional: adjust top-bar to make it cleaner
    content = content.replace('padding: 0.6rem 1.2rem;', 'padding: 0.6rem 2rem; max-width: 1200px; margin: 0 auto; width: 100%; border-bottom: none;')
    content = content.replace('border-bottom: 2px solid var(--accent);', 'border-bottom: 1px solid var(--border); border-radius: 0 0 16px 16px;')
    
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed CSS.")

def fix_html_files():
    templates_dir = 'templates'
    for filename in os.listdir(templates_dir):
        if not filename.endswith('.html'):
            continue
            
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix body padding
        content = re.sub(r'body\s*\{\s*padding-top:\s*250px;\s*\}', 'body { padding-top: 100px; }', content)
        
        # In login.html it's 100px, but has a weird header.
        content = re.sub(r'body\s*\{\s*display:\s*flex;.*?padding-top:\s*100px;.*?\}', 'body { display: flex; align-items: center; justify-content: center; margin: 0; padding: 0; height: 100vh; overflow: hidden; }', content, flags=re.DOTALL)
        
        # Change max-width from 95% to specific pixels for better desktop view
        content = re.sub(r'max-width:\s*95%;', 'max-width: 1000px; width: 95%;', content)
        
        # Shrink the massive inline logos
        content = re.sub(r'height:\s*180px;', 'height: 120px;', content)
        content = re.sub(r'height:\s*260px;', 'height: 140px;', content)
        content = re.sub(r'max-width:\s*650px;', 'max-width: 300px;', content)
        
        # Remove old absolute header CSS if it exists
        header_css_pattern = r'/\*\s*الهيدر الأساسي\s*\*/.*?/\*\s*إخفاء وإظهار حسب حجم الشاشة \(الجوالات\)\s*\*/.*?\s*\}'
        content = re.sub(header_css_pattern, '', content, flags=re.DOTALL)
        
        header_css_pattern_2 = r'/\*\s*الهيدر الأساسي\s*\*/.*?/\*\s*إخفاء وإظهار حسب حجم الشاشة\s*\*/.*?\s*\}'
        content = re.sub(header_css_pattern_2, '', content, flags=re.DOTALL)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Fixed {filename}")

if __name__ == '__main__':
    fix_css()
    fix_html_files()
