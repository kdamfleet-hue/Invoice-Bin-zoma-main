with open("static/app_ux.js", "r", encoding="utf-8") as f:
    content = f.read()

nav_update = """
        { href: '/', icon: '🏠', label: 'الرئيسية' },
        { href: '/fleet_dashboard', icon: '📊', label: 'لوحة القيادة' },
        { href: '/yard', icon: '🅿️', label: 'إدارة الساحات' },
        { href: '/schedule', icon: '📋', label: 'الجدول الأسبوعي' },
        { href: '/handover', icon: '🚗', label: 'تسليم واستلام' },
        { href: '/workshop', icon: '🔧', label: 'صيانة الورشة' },
        { href: '/oils', icon: '🛢️', label: 'الزيوت والفلاتر' },
        { href: '/inventory/tires', icon: '💿', label: 'سجل الإطارات' },
        { href: '/inventory/batteries', icon: '🔋', label: 'سجل البطاريات' },
        { href: '/fuel', icon: '⛽', label: 'تموين المحروقات' },
        { href: '/washing', icon: '🚿', label: 'محطة الغسيل' },
        { href: '/purchase', icon: '🛒', label: 'طلبات الشراء' },
        { href: '/spare_parts', icon: '📦', label: 'مستودع القطع' },
        { href: '/finance/petty-cash', icon: '💵', label: 'العهد والمصاريف' },
        { href: '/incidents', icon: '🚨', label: 'الحوادث والطوارئ' },
"""

content = content.replace("""        { href: '/', icon: '🏠', label: 'الرئيسية' },
        { href: '/fleet_dashboard', icon: '📊', label: 'لوحة القيادة' },
        { href: '/schedule', icon: '📋', label: 'الجدول الأسبوعي' },
        { href: '/handover', icon: '🚗', label: 'تسليم واستلام' },
        { href: '/workshop', icon: '🔧', label: 'صيانة الورشة' },
        { href: '/oils', icon: '🛢️', label: 'الزيوت والفلاتر' },
        { href: '/fuel', icon: '⛽', label: 'تموين المحروقات' },
        { href: '/washing', icon: '🚿', label: 'محطة الغسيل' },
        { href: '/purchase', icon: '🛒', label: 'طلبات الشراء' },
        { href: '/spare_parts', icon: '📦', label: 'مستودع القطع' },
        { href: '/incidents', icon: '🚨', label: 'الحوادث والمخالفات' },""", nav_update.strip() + ",")

with open("static/app_ux.js", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated masterNav in app_ux.js")
