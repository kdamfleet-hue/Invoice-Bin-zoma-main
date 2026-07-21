import os
import glob
import re

html_files = glob.glob(r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\*.html')

old_pattern = re.compile(r'<script>\s*window\.BZ_BRANCH_ID\s*=\s*\{\{\s*active_branch_id\s*\}\};\s*window\.BZ_BRANCH\s*=\s*\{\{\s*active_branch\s*\|\s*tojson\s*\}\};\s*window\.BZ_SNAP_TAB\s*=\s*\{\{\s*snap_tab\s*\|\s*tojson\s*\}\};\s*window\.BZ_IS_ADMIN\s*=\s*\{\{\s*is_admin\s*\|\s*tojson\s*\}\};\s*window\.BZ_BRANCHES\s*=\s*\{\{\s*branches\s*\|\s*default\(\[\]\)\s*\|\s*tojson\s*\}\};\s*</script>', re.DOTALL)

new_code = """<meta id="bz-meta" 
      data-branch-id="{{ active_branch_id }}" 
      data-branch="{{ active_branch }}" 
      data-snap-tab="{{ snap_tab }}" 
      data-is-admin="{{ is_admin | lower }}" 
      data-branches="{{ branches | default([]) | tojson | forceescape }}">
<script>
  const bzMeta = document.getElementById('bz-meta');
  if(bzMeta) {
      window.BZ_BRANCH_ID = parseInt(bzMeta.getAttribute('data-branch-id') || '0', 10);
      window.BZ_BRANCH = bzMeta.getAttribute('data-branch') || '';
      window.BZ_SNAP_TAB = bzMeta.getAttribute('data-snap-tab') || '';
      window.BZ_IS_ADMIN = bzMeta.getAttribute('data-is-admin') === 'true';
      try { window.BZ_BRANCHES = JSON.parse(bzMeta.getAttribute('data-branches') || '[]'); } 
      catch(e) { window.BZ_BRANCHES = []; }
  }
</script>"""

count = 0
for f in html_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if old_pattern.search(content):
        new_content = old_pattern.sub(new_code, content)
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        count += 1
        print(f"Fixed JS Jinja syntax in {os.path.basename(f)}")

print(f"Total files fixed: {count}")
