import os

template_path = r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy\InvoiceApp\templates\index.html'
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Make Logo Bigger
content = content.replace("max-width: 300px;", "max-width: 450px; width: 90%;")

# Add Dark Mode CSS
dark_mode_css = """
        body.dark-mode {
            --bg-color: #121212;
            --text-main: #e0e0e0;
            background-image: radial-gradient(#333 1px, transparent 1px);
        }
        body.dark-mode .header-title { color: #82aaff !important; }
        body.dark-mode .header-subtitle { color: #aaa; }
        body.dark-mode .btn-outline { border-color: #82aaff; color: #82aaff; }
        body.dark-mode .btn-outline:hover { background: #82aaff; color: #121212; }
        body.dark-mode input, body.dark-mode select { background: #222; color: #fff; border-color: #555; }
        body.dark-mode .modal-content { background: #1e1e1e; color: #eee; }
        body.dark-mode .modal-content h3 { color: #82aaff; }
        body.dark-mode .modal-content p { color: #bbb; }
        body.dark-mode .site-logo { filter: drop-shadow(0 4px 6px rgba(255,255,255,0.1)); }
        
        /* Mobile Responsive Padding */
        @media (max-width: 768px) {
            body { padding: 1rem; }
            .header-title { font-size: 1.8rem; }
            .grid-container { grid-template-columns: 1fr; }
        }
        </style>
"""
if "body.dark-mode" not in content:
    content = content.replace("</style>", dark_mode_css)

# Add Dark Mode Button HTML
toggle_btn = """
    <button id="darkModeToggle" onclick="toggleDarkMode()" style="position: absolute; top: 20px; left: 20px; background: rgba(0,0,0,0.05); border: 1px solid #ccc; font-size: 1.5rem; cursor: pointer; border-radius: 50%; width: 45px; height: 45px; display: flex; align-items: center; justify-content: center; transition: 0.3s; z-index: 1000;">🌙</button>
"""
if "darkModeToggle" not in content:
    content = content.replace("<body>", f"<body>\n{toggle_btn}")

# Add JS logic for saving dark mode preference
dark_mode_js = """
        // Dark Mode Logic
        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
            document.getElementById('darkModeToggle').innerText = isDark ? '☀️' : '🌙';
            document.getElementById('darkModeToggle').style.background = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)';
        }

        // Apply on load
        if (localStorage.getItem('darkMode') === 'enabled') {
            document.body.classList.add('dark-mode');
            document.getElementById('darkModeToggle').innerText = '☀️';
            document.getElementById('darkModeToggle').style.background = 'rgba(255,255,255,0.1)';
        }
        
        async function generateExcel() {
"""
if "toggleDarkMode()" not in content:
    content = content.replace("async function generateExcel() {", dark_mode_js)

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Applied responsive styles, bigger logo, and dark mode.")
