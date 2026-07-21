html = """{% extends 'base.html' %}
{% block title %}سجل العهد والمصاريف | قسم الحسابات{% endblock %}

{% block content %}
<div class="content-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 2px solid var(--border-glass);">
    <div>
        <h2 style="margin: 0; color: var(--accent-primary); font-weight: 800; font-size: 1.8rem;"><i class="fas fa-wallet"></i> إدارة العهد والمصاريف</h2>
        <p style="margin: 5px 0 0 0; color: var(--text-muted);">مراجعة وتصفية المصاريف النثرية المرفوعة من السائقين ومحطات الوزن.</p>
    </div>
</div>

<div class="table-container" style="background: var(--bg-panel); border: 1px solid var(--border-glass); border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
    <table style="width: 100%; border-collapse: collapse; text-align: right;">
        <thead style="background: rgba(0,0,0,0.3); border-bottom: 1px solid var(--border-glass);">
            <tr>
                <th style="padding: 15px; color: var(--accent-primary);">تاريخ المصروف</th>
                <th style="padding: 15px; color: var(--text-muted);">السائق</th>
                <th style="padding: 15px; color: var(--text-muted);">النوع</th>
                <th style="padding: 15px; color: var(--text-muted);">المبلغ</th>
                <th style="padding: 15px; color: var(--text-muted);">التفاصيل</th>
                <th style="padding: 15px; color: var(--text-muted);">الحالة</th>
                <th style="padding: 15px; color: var(--text-muted);">الإجراءات</th>
            </tr>
        </thead>
        <tbody>
            {% for exp in expenses %}
            <tr style="border-bottom: 1px solid var(--border-glass); transition: background 0.2s;">
                <td style="padding: 15px; color: white;">{{ exp.date }}</td>
                <td style="padding: 15px; font-weight: bold; color: #ddd;">
                    {% if exp.driver %}{{ exp.driver.name }}{% else %}<span style="color:var(--text-muted);">غير محدد</span>{% endif %}
                </td>
                <td style="padding: 15px; color: #ddd;">{{ exp.expense_type }}</td>
                <td style="padding: 15px; font-weight: bold; color: #4ade80;">{{ exp.amount }} ريال</td>
                <td style="padding: 15px; color: #ddd;">{{ exp.description }}</td>
                <td style="padding: 15px;">
                    <span style="padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; background: {% if exp.status == 'معتمد' %}rgba(34,197,94,0.2); color:#4ade80;{% elif exp.status == 'معلق' %}rgba(234,179,8,0.2); color:#facc15;{% else %}rgba(239,68,68,0.2); color:#f87171;{% endif %}">{{ exp.status }}</span>
                </td>
                <td style="padding: 15px;">
                    {% if exp.status == 'معلق' %}
                    <button onclick="updateStatus({{ exp.id }}, 'معتمد')" style="background: rgba(34,197,94,0.2); color: #4ade80; border: 1px solid #4ade80; border-radius: 6px; padding: 5px 10px; cursor: pointer; margin-left: 5px;">إعتماد</button>
                    <button onclick="updateStatus({{ exp.id }}, 'مرفوض')" style="background: rgba(239,68,68,0.2); color: #f87171; border: 1px solid #f87171; border-radius: 6px; padding: 5px 10px; cursor: pointer;">رفض</button>
                    {% else %}
                    <span style="color:var(--text-muted); font-size: 0.9rem;">تمت المراجعة</span>
                    {% endif %}
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="7" style="padding: 30px; text-align: center; color: var(--text-muted);">لا توجد مصاريف مسجلة.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<script>
async function updateStatus(id, status) {
    if(!confirm('هل أنت متأكد من ' + status + ' هذا المصروف؟')) return;
    
    try {
        const r = await fetch(`/api/finance/petty-cash/${id}/status`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({status: status})
        });
        const res = await r.json();
        if(res.success) {
            location.reload();
        } else {
            alert('خطأ: ' + res.error);
        }
    } catch(e) {
        alert('خطأ في الاتصال');
    }
}
</script>
{% endblock %}
"""

with open("templates/petty_cash.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Created petty_cash.html")
