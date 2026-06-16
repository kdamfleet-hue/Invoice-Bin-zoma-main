import os

print("Injecting exportExcel() into schedule.html")

with open('templates/schedule.html', 'r', encoding='utf-8') as f:
    html = f.read()

if 'function exportExcel()' not in html:
    export_js = """
    function exportExcel() {
        const btn = document.querySelector('.btn-outline');
        const oldText = btn.innerHTML;
        btn.innerHTML = 'جاري التصدير... ⏳';
        btn.disabled = true;

        const mainData = [];
        document.querySelectorAll('#mainDriversTable tbody tr').forEach(tr => {
            if (tr.classList.contains('empty-row')) return;
            mainData.push({
                car: tr.querySelector('.in-car')?.value || '',
                type: tr.querySelector('.in-type')?.value || '',
                plate: tr.querySelector('.in-plate')?.value || '',
                job: tr.querySelector('.in-job')?.value || '',
                driver: tr.querySelector('.in-driver')?.value || '',
                iqama: tr.querySelector('.in-iqama')?.value || '',
                notes: tr.querySelector('.in-notes')?.value || ''
            });
        });

        const spareData = [];
        document.querySelectorAll('#spareDriversTable tbody tr').forEach(tr => {
            if (tr.classList.contains('empty-row')) return;
            spareData.push({
                car: tr.querySelector('.in-car')?.value || '',
                type: tr.querySelector('.in-type')?.value || '',
                plate: tr.querySelector('.in-plate')?.value || '',
                job: tr.querySelector('.in-job')?.value || '',
                driver: tr.querySelector('.in-driver')?.value || '',
                iqama: tr.querySelector('.in-iqama')?.value || '',
                notes: tr.querySelector('.in-notes')?.value || ''
            });
        });

        const dateVal = document.getElementById('weekDate')?.value || '';

        fetch('/api/generate_schedule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                date: dateVal,
                main: mainData,
                spare: spareData
            })
        })
        .then(res => res.json())
        .then(data => {
            btn.innerHTML = oldText;
            btn.disabled = false;
            if (data.success && data.file_b64) {
                const link = document.createElement("a");
                link.href = "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64," + data.file_b64;
                link.download = "جدول_المركبات.xlsx";
                link.click();
            } else {
                alert('حدث خطأ أثناء التصدير');
            }
        })
        .catch(err => {
            btn.innerHTML = oldText;
            btn.disabled = false;
            alert('حدث خطأ أثناء الاتصال بالخادم');
        });
    }
"""
    # Find the closing </script> tag
    html = html.replace('</script>', export_js + '\n</script>')
    with open('templates/schedule.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Injected successfully.")
else:
    print("Already injected.")
