from flask import render_template, session, jsonify, Response
from helpers import role_required, login_required, load_logo
from routes.schedule import schedule_bp

@schedule_bp.route("/schedule/transport")
@role_required("admin", "operations")
def schedule_transport():
    return render_template(
        "schedule_transport.html",
        google_user=session.get("google_user"),
        b64_en=load_logo(),
    )

@schedule_bp.route("/m/transport")
@login_required
def transport_mobile_app():
    return render_template("transport_app.html")

@schedule_bp.route("/m/transport/manifest.json")
def transport_manifest():
    return jsonify({
        "name": "نقل بن زومة",
        "short_name": "النقل",
        "start_url": "/m/transport",
        "scope": "/m/transport",
        "display": "standalone",
        "dir": "rtl",
        "lang": "ar",
        "background_color": "#071018",
        "theme_color": "#071018",
        "icons": [
            {"src": "/static/logo_192.png", "sizes": "192x192", "type": "image/png"}
        ]
    })

@schedule_bp.route("/m/transport/sw.js")
def transport_sw():
    js = """self.addEventListener('install', e => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', e => {
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});"""
    return Response(js, mimetype="application/javascript")
