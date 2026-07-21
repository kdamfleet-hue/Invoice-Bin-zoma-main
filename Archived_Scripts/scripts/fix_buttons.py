with open("templates/schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace('class="btn-primary"', 'class="btn-neon"')
html = html.replace('class="btn-submit-gold"', 'class="btn-neon"')
html = html.replace('class="btn-submit-orange"', 'class="btn-neon"')

with open("templates/schedule.html", "w", encoding="utf-8") as f:
    f.write(html)
