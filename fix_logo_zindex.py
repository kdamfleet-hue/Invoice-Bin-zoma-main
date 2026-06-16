import glob
import shutil
import os

print("Copying clean logo to site_logo.png")
shutil.copy(r'New\bin_zomah_logo_clean_v2.png', r'static\site_logo.png')

print("Updating HTML files")
for file in glob.glob('templates/*.html'):
    with open(file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Replace site_logo.jpg with site_logo.png
    html = html.replace('site_logo.jpg', 'site_logo.png')
    # Also replace gemini_logo_header_v223.png with site_logo.png in index.html just in case
    html = html.replace("gemini_logo_header_v223.png', v=4", "site_logo.png'")
    html = html.replace("gemini_logo_header_v223.png", "site_logo.png")
    
    # Fix Logout button z-index
    html = html.replace('z-index: 100;', 'z-index: 9999;')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(html)

print("Done updating.")
