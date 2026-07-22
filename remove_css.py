import re

with open('templates/schedule.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The block to remove is:
#     /* Fixed table alignment */
#     table.sched {
#         table-layout: fixed !important;
#         ...
#     table.sched input {
#         width: 100% !important;
#         min-width: 1900px !important;
#         box-sizing: border-box !important;
#     }

pattern = r'\s*/\*\s*Fixed table alignment\s*\*/[\s\S]*?table\.sched input \{[\s\S]*?\}'
new_content = re.sub(pattern, '', content)

with open('templates/schedule.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Done')
