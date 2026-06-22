import os

file_path = 'templates/purchase.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update the HTML table for Summary Totals
# Replace readonly styling
html = html.replace(
    '<td><input type="number" id="sumParts" readonly style="background:rgba(0,0,0,0.05);font-weight:bold;text-align:center;"></td>',
    '<td><input type="number" id="sumParts" style="font-weight:bold;text-align:center;background:var(--surface);" placeholder="الإجمالي"></td>'
)
html = html.replace(
    '<td><input type="number" id="sumRepairs" readonly style="background:rgba(0,0,0,0.05);font-weight:bold;text-align:center;"></td>',
    '<td><input type="number" id="sumRepairs" style="font-weight:bold;text-align:center;background:var(--surface);" placeholder="الإجمالي"></td>'
)
html = html.replace(
    '<td><input type="number" id="sumTires" readonly style="background:rgba(0,0,0,0.05);font-weight:bold;text-align:center;" placeholder="أدخل التكلفة"></td>',
    '<td><input type="number" id="sumTires" style="font-weight:bold;text-align:center;background:var(--surface);" placeholder="الإجمالي"></td>'
)
html = html.replace(
    '<td><input type="number" id="sumBatteries" readonly style="background:rgba(0,0,0,0.05);font-weight:bold;text-align:center;"></td>',
    '<td><input type="number" id="sumBatteries" style="font-weight:bold;text-align:center;background:var(--surface);" placeholder="الإجمالي"></td>'
)

# Replace JS function recalcSummary() and add updateSummaryFieldsFromTables()
old_recalc = """        function recalcSummary() {
            // Parts total
            let partsTotal = 0;
            document.querySelectorAll('#partsTable tbody tr:not(.empty-row)').forEach(tr => {
                partsTotal += parseFloat(tr.querySelector('.p-val')?.value) || 0;
            });
            // Repairs total
            let repairsTotal = 0;
            document.querySelectorAll('#repairsTable tbody tr:not(.empty-row)').forEach(tr => {
                repairsTotal += parseFloat(tr.querySelector('.r-val')?.value) || 0;
            });
            // Tires total (no price column in tires, user enters manually if needed)
            let tiresTotal = parseFloat(document.getElementById('sumTires').value) || 0;
            // Batteries total
            let batteriesTotal = 0;
            document.querySelectorAll('#batteriesTable tbody tr:not(.empty-row)').forEach(tr => {
                const count = parseFloat(tr.querySelector('.b-count')?.value) || 0;
                const price = parseFloat(tr.querySelector('.b-price')?.value) || 0;
                batteriesTotal += count * price;
            });

            document.getElementById('sumParts').value = partsTotal ? partsTotal.toFixed(2) : '';
            document.getElementById('sumRepairs').value = repairsTotal ? repairsTotal.toFixed(2) : '';
            document.getElementById('sumBatteries').value = batteriesTotal ? batteriesTotal.toFixed(2) : '';

            const subtotal = partsTotal + repairsTotal + tiresTotal + batteriesTotal;
            const vat = subtotal * 0.15;
            const grandTotal = subtotal + vat;

            document.getElementById('sumSubtotal').value = subtotal ? subtotal.toFixed(2) : '';
            document.getElementById('sumVat').value = vat ? vat.toFixed(2) : '';
            document.getElementById('sumGrandTotal').value = grandTotal ? grandTotal.toFixed(2) : '';
        }"""

new_recalc = """        function updateSummaryFieldsFromTables() {
            let partsTotal = 0;
            document.querySelectorAll('#partsTable tbody tr:not(.empty-row)').forEach(tr => {
                partsTotal += parseFloat(tr.querySelector('.p-val')?.value) || 0;
            });
            let repairsTotal = 0;
            document.querySelectorAll('#repairsTable tbody tr:not(.empty-row)').forEach(tr => {
                repairsTotal += parseFloat(tr.querySelector('.r-val')?.value) || 0;
            });
            let batteriesTotal = 0;
            document.querySelectorAll('#batteriesTable tbody tr:not(.empty-row)').forEach(tr => {
                const count = parseFloat(tr.querySelector('.b-count')?.value) || 0;
                const price = parseFloat(tr.querySelector('.b-price')?.value) || 0;
                batteriesTotal += count * price;
            });

            if (partsTotal > 0) document.getElementById('sumParts').value = partsTotal.toFixed(2);
            if (repairsTotal > 0) document.getElementById('sumRepairs').value = repairsTotal.toFixed(2);
            if (batteriesTotal > 0) document.getElementById('sumBatteries').value = batteriesTotal.toFixed(2);
        }

        function recalcSummary() {
            let partsTotal = parseFloat(document.getElementById('sumParts').value) || 0;
            let repairsTotal = parseFloat(document.getElementById('sumRepairs').value) || 0;
            let tiresTotal = parseFloat(document.getElementById('sumTires').value) || 0;
            let batteriesTotal = parseFloat(document.getElementById('sumBatteries').value) || 0;

            const subtotal = partsTotal + repairsTotal + tiresTotal + batteriesTotal;
            const vat = subtotal * 0.15;
            const grandTotal = subtotal + vat;

            document.getElementById('sumSubtotal').value = subtotal ? subtotal.toFixed(2) : '';
            document.getElementById('sumVat').value = vat ? vat.toFixed(2) : '';
            document.getElementById('sumGrandTotal').value = grandTotal ? grandTotal.toFixed(2) : '';
        }"""

if old_recalc in html:
    html = html.replace(old_recalc, new_recalc)
else:
    print("recalcSummary not found, might need manual check")

# Fix event listener
old_listener = """        document.addEventListener('input', function(e) {
            if (e.target.closest('#partsTable') || e.target.closest('#repairsTable') || e.target.closest('#batteriesTable') || e.target.id === 'sumTires') {
                recalcSummary();
            }
        });"""

new_listener = """        document.addEventListener('input', function(e) {
            if (e.target.closest('#partsTable') || e.target.closest('#repairsTable') || e.target.closest('#batteriesTable')) {
                updateSummaryFieldsFromTables();
                recalcSummary();
            } else if (e.target.id === 'sumParts' || e.target.id === 'sumRepairs' || e.target.id === 'sumTires' || e.target.id === 'sumBatteries') {
                recalcSummary();
            }
        });"""
        
if old_listener in html:
    html = html.replace(old_listener, new_listener)

# Fix inline onclick updates
html = html.replace('updatePartIds();recalcSummary()', 'updatePartIds();updateSummaryFieldsFromTables();recalcSummary()')
html = html.replace('calcPartVal(this)">', 'calcPartVal(this);updateSummaryFieldsFromTables();recalcSummary()">')
html = html.replace('updateRepairIds();recalcSummary()', 'updateRepairIds();updateSummaryFieldsFromTables();recalcSummary()')
html = html.replace('oninput="recalcSummary()"', 'oninput="updateSummaryFieldsFromTables();recalcSummary()"')
html = html.replace('updateBatteryIds();recalcSummary()', 'updateBatteryIds();updateSummaryFieldsFromTables();recalcSummary()')
html = html.replace('calcPartVal(this)', 'calcPartVal(this);updateSummaryFieldsFromTables();recalcSummary()')

# Remove the JS lines at the bottom that explicitly remove readonly for sumTires
remove_lines = [
    "document.getElementById('sumTires').removeAttribute('readonly');",
    "document.getElementById('sumTires').style.background = 'var(--surface)';",
    "document.getElementById('sumTires').placeholder = 'أدخل التكلفة';"
]
for line in remove_lines:
    html = html.replace(line, "")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Finished updating purchase.html")
