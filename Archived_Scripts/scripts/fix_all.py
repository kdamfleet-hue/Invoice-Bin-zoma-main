import glob, re
import os

target = r'<script>window\.BZ_BRANCH_ID = \{\{ active_branch_id \}\}; window\.BZ_BRANCH = \{\{ active_branch\|tojson \}\}; window\.BZ_SNAP_TAB = \{\{ snap_tab\|tojson \}\};</script>'

replacement = """<meta id="bz-meta" data-branch-id="{{ active_branch_id }}" data-branch="{{ active_branch }}" data-snap-tab="{{ snap_tab }}">
<script>
  const m = document.getElementById("bz-meta");
  if(m) {
      window.BZ_BRANCH_ID = parseInt(m.getAttribute("data-branch-id") || "0", 10);
      window.BZ_BRANCH = m.getAttribute("data-branch") || "";
      window.BZ_SNAP_TAB = m.getAttribute("data-snap-tab") || "";
  }
</script>"""

count = 0
for f in glob.glob(r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\*.html'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if re.search(target, content):
        new_content = re.sub(target, replacement, content)
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        count += 1

print(f"Fixed {count} files.")
