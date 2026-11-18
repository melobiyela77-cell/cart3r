from flask import Flask, render_template_string, request, session, redirect
import random, string, json, os, time
from datetime import datetime

app = Flask(__name__)
app.secret_key = "cart3r-secret-123"
KEYS_FILE = "keys.json"
ADMIN_PASSWORD = "cart3radmin"

def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE) as f:
            return json.load(f)
    return {}

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f)

def make_key():
    part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"CART3R-{part1}-{part2}"

LOCK_HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{background:#0a0a0a;color:white;font-family:Arial;text-align:center;padding:40px 20px}
.box{background:#1a1a1a;padding:25px;border-radius:15px;max-width:350px;margin:auto;border:1px solid #00ff88}
input{width:90%;padding:15px;border-radius:10px;border:none;margin:15px 0;font-size:16px;text-align:center}
button{background:#00ff88;color:black;padding:15px 30px;border:none;border-radius:10px;font-weight:bold;font-size:16px;width:100%}
h1{color:#00ff88} .err{color:red} a{color:#00ff88}</style></head>
<body><div class="box"><h1>🤖 CART3R 5.0</h1><p>Enter License Key to Unlock</p>
{% if error %}<p class="err">{{error}}</p>{% endif %}
<form method="POST"><input name="key" placeholder="CART3R-XXXX-XXXX" required><br>
<button type="submit">UNLOCK APP 🔓</button></form>
<p style="font-size:12px;color:#888">Don't have a key? Ask Melokuhle for one</p>
<a href="/admin" style="font-size:12px">👑 Admin - Generate Keys Here</a>
</div></body></html>
"""

MAIN_HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{background:#0a0a0a;color:white;font-family:Arial;text-align:center;padding:20px}
.card{background:#1a1a1a;padding:20px;border-radius:15px;margin:15px auto;max-width:350px}
.buy{color:#00ff88;font-size:28px;font-weight:bold} .sell{color:#ff4444;font-size:28px;font-weight:bold}
button{background:#333;color:white;padding:10px 20px;border:none;border-radius:8px}</style></head>
<body><h1>🤖 CART3R 5.0</h1><p>Key: {{key}} | Expires: {{expiry}}</p>
<div class="card"><h3>XAUUSD / GOLD</h3><div class="buy">BUY ▲</div><p>Balance: $992.52</p></div>
<div class="card"><h3>NAS100</h3><div class="sell">SELL ▼</div></div>
<a href="/logout"><button>Lock App</button></a>
</body></html>
"""

@app.route("/", methods=["GET","POST"])
def home():
    if "key" not in session:
        if request.method == "POST":
            entered = request.form.get("key","").strip().upper()
            keys = load_keys()
            if entered in keys:
                exp = keys[entered].get("expires","never")
                if exp != "never" and time.time() > float(exp):
                    return render_template_string(LOCK_HTML, error="Key Expired! Ask for new key")
                session["key"] = entered
                return redirect("/")
            else:
                return render_template_string(LOCK_HTML, error="Invalid Key! Try again")
        return render_template_string(LOCK_HTML, error=None)
    keys = load_keys()
    info = keys.get(session["key"], {})
    exp = info.get("expires","never")
    exp_str = "Never" if exp=="never" else datetime.fromtimestamp(float(exp)).strftime("%d %b %Y")
    return render_template_string(MAIN_HTML, key=session["key"], expiry=exp_str)

@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") != ADMIN_PASSWORD:
            return "Wrong password!"
        days = request.form.get("days","30")
        new_key = make_key()
        keys = load_keys()
        expires = "never" if days == "never" else str(time.time() + int(days)*86400)
        keys[new_key] = {"expires": expires, "created": str(datetime.now())}
        save_keys(keys)
        return f"<body style='background:#111;color:white;font-family:Arial;text-align:center;padding:30px'><h1>New Key Generated! 🎉</h1><h2 style='color:#00ff88'>{new_key}</h2><p>Expires in: {days} days</p><a href='/admin?pass={ADMIN_PASSWORD}' style='color:#00ff88'>Generate Another</a><br><br><a href='/' style='color:#00ff88'>Go Test Key</a></body>"
    if request.args.get("pass") == ADMIN_PASSWORD:
        return """
        <body style="background:#111;color:white;font-family:Arial;text-align:center;padding:30px">
        <h1>CART3R ADMIN 👑</h1><p>Welcome Melokuhle - Generate Keys Here</p>
        <form method="POST"><input type="hidden" name="password" value="cart3radmin">
        <label>Key lasts for:</label><br><br>
        <select name="days" style="padding:10px;font-size:16px">
        <option value="7">7 Days</option><option value="30" selected>30 Days</option><option value="never">Never Expires (Lifetime)</option>
        </select><br><br>
        <button style="background:#00ff88;padding:15px 30px;font-weight:bold;border:none;border-radius:10px">GENERATE NEW KEY 🔑</button>
        </form></body>
        """
    return """
    <body style="background:#111;color:white;font-family:Arial;text-align:center;padding:30px">
    <h1>CART3R ADMIN 👑</h1><form method="POST">
    <input type="password" name="password" placeholder="Admin Password" style="padding:12px"><br><br>
    <button style="padding:12px 25px;background:#00ff88;font-weight:bold">Login</button></form></body>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
