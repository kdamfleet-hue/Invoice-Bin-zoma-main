html = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بوابة السائقين | تسجيل الدخول</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #c5a059;
            --dark: #0f172a;
            --light: #f8fafc;
            --text-muted: #94a3b8;
        }
        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, var(--dark) 0%, #1e293b 100%);
            margin: 0;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        .login-box {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 20px;
            width: 100%;
            max-width: 350px;
            text-align: center;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        .login-box img {
            height: 60px;
            margin-bottom: 20px;
        }
        .login-box h2 {
            margin: 0 0 5px 0;
            font-weight: 800;
            font-size: 1.5rem;
            color: var(--primary);
        }
        .login-box p {
            color: var(--text-muted);
            margin-bottom: 30px;
            font-size: 0.9rem;
        }
        .input-group {
            margin-bottom: 20px;
            text-align: right;
        }
        .input-group label {
            display: block;
            margin-bottom: 8px;
            color: #cbd5e1;
            font-size: 0.9rem;
        }
        .input-group input {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(0,0,0,0.2);
            color: white;
            font-family: 'Cairo', sans-serif;
            box-sizing: border-box;
            transition: all 0.3s;
        }
        .input-group input:focus {
            outline: none;
            border-color: var(--primary);
            background: rgba(0,0,0,0.4);
        }
        .btn-submit {
            width: 100%;
            padding: 14px;
            background: var(--primary);
            color: var(--dark);
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(197, 160, 89, 0.3);
        }
        .alert {
            background: rgba(239, 68, 68, 0.1);
            color: #fca5a5;
            border: 1px solid rgba(239, 68, 68, 0.3);
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 0.85rem;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <img src="data:image/png;base64,{{ b64_en }}" alt="Logo">
        <h2>بوابة السائقين</h2>
        <p>BIN ZOMAH INTL. FLEET</p>
        
        {% if error %}
        <div class="alert"><i class="fas fa-exclamation-circle"></i> {{ error }}</div>
        {% endif %}
        
        <form method="POST">
            <div class="input-group">
                <label>رقم الهوية / الإقامة</label>
                <input type="text" name="iqama_number" required placeholder="أدخل رقم الإقامة">
            </div>
            <div class="input-group">
                <label>رقم الجوال المسجل</label>
                <input type="tel" name="phone" required placeholder="أدخل رقم الجوال">
            </div>
            <button type="submit" class="btn-submit">دخول</button>
        </form>
    </div>
</body>
</html>
"""

with open("templates/driver_login.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Created driver login template")
