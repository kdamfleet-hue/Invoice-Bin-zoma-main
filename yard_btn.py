import re

with open("templates/yard.html", "r", encoding="utf-8") as f:
    content = f.read()

old_item = """<div class="yard-item" draggable="true" ondragstart="drag(event)" id="veh-${v.id}" data-id="${v.id}">
                    <h4>${v.plate}</h4>
                    <p>${v.type} <span class="badge ${badge}">${v.condition}</span></p>
                </div>"""
                
new_item = """<div class="yard-item" draggable="true" ondragstart="drag(event)" id="veh-${v.id}" data-id="${v.id}">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <h4>${v.plate}</h4>
                            <p>${v.type} <span class="badge ${badge}">${v.condition}</span></p>
                        </div>
                        <a href="/api/vehicles/${v.id}/qr" target="_blank" title="طباعة باركود المركبة" style="text-decoration:none; font-size:1.2rem; cursor:pointer;" onclick="event.stopPropagation();">🖨️</a>
                    </div>
                </div>"""

content = content.replace(old_item, new_item)

with open("templates/yard.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Added print button to yard.html")
