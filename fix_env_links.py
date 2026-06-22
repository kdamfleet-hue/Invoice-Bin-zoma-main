import os
import glob
import re

# 1. Update .env and .env.example
for env_file in ['.env', '.env.example']:
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r'GPS_PERMANENT_TOKEN=.*', 'GPS_PERMANENT_TOKEN=WUTOWPHXLQFTFIUOVBONDTOPVULUPVLM', content)
        content = re.sub(r'GPS_ASSET_URL=.*', 'GPS_ASSET_URL=https://fleetmanagement-api-clust03.gpscockpit.com/api/asset', content)
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)

# 2. Update HTML links
html_files = glob.glob('templates/*.html')
for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Replace the old external links with internal /tracking link
    html = re.sub(
        r'href=[\"\']https://fleetmanagement-clust03\.gpscockpit\.com[^\"\']*[\"\']',
        'href="/tracking"',
        html
    )

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)

print('Updated .env and HTML templates successfully.')
