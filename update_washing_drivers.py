import sqlite3, json, re

def normalize_plate(p):
    if not p: return ''
    p = str(p)
    p = re.sub(r'\s+', '', p)
    for a, e in zip('٠١٢٣٤٥٦٧٨٩', '0123456789'): p = p.replace(a, e)
    digits = ''.join(re.findall(r'\d+', p))
    letters = ''.join(re.findall(r'[^\d]+', p))
    return digits + letters

conn = sqlite3.connect('database.sqlite')
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute('SELECT * FROM drivers')
drivers = [dict(r) for r in c.fetchall()]
plate_map = {normalize_plate(d['plate']): d for d in drivers if d['plate']}
conn.close()

with open('static/washing_data.js', 'r', encoding='utf-8') as f:
    js = f.read()

m = re.search(r'const WASHING_VEHICLES = (\[.*?\]);', js, re.DOTALL)
if m:
    array_str = m.group(1)
    
    # regex hack to convert simple JS objects to JSON
    json_str = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1"\2":', array_str)
    json_str = json_str.replace("'", '"')
    
    vehicles = json.loads(json_str)
    updated = 0
    for v in vehicles:
        norm = normalize_plate(v.get('plate', ''))
        if norm in plate_map:
            d = plate_map[norm]
            if d['name'] and v.get('driver') != d['name']:
                v['driver'] = d['name']
                v['type'] = d['car']
                updated += 1
                
    if updated > 0:
        new_js = js[:m.start(1)] + json.dumps(vehicles, ensure_ascii=False, indent=4) + js[m.end(1):]
        with open('static/washing_data.js', 'w', encoding='utf-8') as f:
            f.write(new_js)
        print(f'Updated {updated} records in washing_data.js')
    else:
        print('No updates needed.')
else:
    print('Could not find WASHING_VEHICLES array.')


