with open('static/app_ux.js', 'a', encoding='utf-8') as f:
    f.write('''
// ==========================================================================
// DYNAMIC UI RESPONSE (الاستجابة الذكية للواجهة)
// ==========================================================================
document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/system_features')
      .then(function(r) { return r.json(); })
      .then(function(data) {
          if (data && data.features) {
              if (data.features.ai_assistant === false) {
                  var aiFab = document.getElementById('bzAiFab');
                  if (aiFab) aiFab.style.display = 'none';
              }
          }
      })
      .catch(function(err) { console.warn("Failed to load system features for UI response", err); });
});
''')
print("Appended dynamic UI response to app_ux.js")
