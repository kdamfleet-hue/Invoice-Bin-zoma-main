import re
from collections import Counter

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Total chars: {len(content)}")
print(f"Total lines: {content.count(chr(10))}")

# Duplicate functions
funcs = re.findall(r'function\s+(\w+)\s*\(', content)
dupes = [(k,v) for k,v in Counter(funcs).items() if v > 1]
print(f"Duplicate functions: {dupes}")

# Script tags
print(f"Script open tags: {content.count('<script')}")
print(f"Script close tags: {content.count('</script>')}")

# Inline styles
print(f"Inline styles: {content.count('style=')}")

# Check for commented-out code blocks
comments = re.findall(r'<!--.*?-->', content, re.DOTALL)
print(f"HTML comments: {len(comments)}")

# Check for empty or broken function patterns
broken = re.findall(r'function\s+\w+\([^)]*\)\s*\{\s*\}', content)
print(f"Empty functions: {len(broken)}")

# Check duplicate openEditModal
oem = content.count('function openEditModal')
print(f"openEditModal definitions: {oem}")

# Check duplicate saveDriverChanges
sdc = content.count('function saveDriverChanges')
print(f"saveDriverChanges definitions: {sdc}")

# File size
print(f"\nFile size: {len(content.encode('utf-8')) / 1024:.1f} KB")
