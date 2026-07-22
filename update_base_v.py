with open("templates/base.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("app_ux.js', v=36", "app_ux.js', v=37")

with open("templates/base.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated cache bust in base.html")
