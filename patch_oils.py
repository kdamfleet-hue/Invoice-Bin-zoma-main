import os

html_path = r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy\InvoiceApp\templates\oils.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add datalist to body
if '<datalist id="driversList"></datalist>' not in content:
    content = content.replace('<body>', '<body>\n    <datalist id="driversList"></datalist>')

# Update addRow
old_driver_input = '<td><input type="text" class="t-driver" placeholder="اسم السائق"></td>'
new_driver_input = '<td><input type="text" class="t-driver" list="driversList" placeholder="اسم السائق" onchange="autofillRow(this)"></td>'
content = content.replace(old_driver_input, new_driver_input)

# Add fetchDrivers and autofillRow scripts
scripts = """
        let driversData = [];
        async function fetchDrivers() {
            try {
                const res = await fetch('/api/drivers');
                const data = await res.json();
                driversData = data;
                const dl = document.getElementById('driversList');
                dl.innerHTML = '';
                data.forEach(d => {
                    const opt = document.createElement('option');
                    opt.value = d.name;
                    dl.appendChild(opt);
                });
            } catch (err) { console.error('Error fetching drivers', err); }
        }

        function autofillRow(elem) {
            const name = elem.value;
            const driver = driversData.find(d => d.name === name);
            if (driver) {
                const tr = elem.closest('tr');
                const carInput = tr.querySelector('.t-car');
                const plateInput = tr.querySelector('.t-plate');
                if(driver.car && driver.car !== 'None') carInput.value = driver.car;
                if(driver.plate && driver.plate !== 'None') plateInput.value = driver.plate;
            }
        }
        
        // Fetch drivers before adding initial rows
"""
if 'async function fetchDrivers()' not in content:
    content = content.replace('let rowCount = 0;', scripts + '\n        let rowCount = 0;')
    # Update window.onload to fetch drivers then add rows
    old_onload = 'window.onload = () => { for(let i=0; i<3; i++) addRow(); };'
    new_onload = 'window.onload = async () => { await fetchDrivers(); for(let i=0; i<3; i++) addRow(); };'
    content = content.replace(old_onload, new_onload)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated oils.html with autocomplete and autofill.")


