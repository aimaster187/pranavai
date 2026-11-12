import os, sqlite3, secrets, datetime, json
from flask import Flask, request, jsonify, render_template_string, redirect, session

app = Flask(__name__)
app.secret_key = "pranav_master_3d_secret"
ADMIN_PASS = "pranav123"
MASTER_GEMINI_KEY = os.environ.get("MASTER_GEMINI_KEY", "")

DB_PATH = "pranav_ai_master.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        license_key TEXT PRIMARY KEY,
        user_name TEXT,
        plan TEXT,
        device_id TEXT,
        device_model TEXT,
        character_3d TEXT,
        allowed_tools TEXT,
        daily_limit INTEGER,
        used_today INTEGER,
        expires_at TEXT,
        status TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS global_config (
        id INTEGER PRIMARY KEY,
        system_prompt TEXT,
        glb_jarvis_url TEXT,
        glb_venom_url TEXT,
        glb_maya_url TEXT,
        announcement TEXT
    )''')
    # Default Global 3D & Prompt Config
    if not c.execute("SELECT * FROM global_config").fetchone():
        c.execute("INSERT INTO global_config VALUES (1, ?, ?, ?, ?, ?)", (
            "Tu PRANAV AI hai, ek advance 3D voice assistant. Hinglish mein smart aur direct jawab de.",
            "https://models.readyplayer.me/64bfa15f0e72c63d7c3934a6.glb",
            "https://models.readyplayer.me/64bfa15f0e72c63d7c3934a6.glb",
            "https://models.readyplayer.me/64bfa15f0e72c63d7c3934a6.glb",
            "Welcome to PRANAV AI 3D v1.0!"
        ))
    conn.commit()
    conn.close()

init_db()

HTML_DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PRANAV AI — 3D Master Control</title>
  <style>
    body { font-family: 'Segoe UI', sans-serif; background: #070b14; color: #e2e8f0; padding: 14px; margin: 0; }
    h2, h3 { color: #00f0ff; margin-top: 0; }
    .card { background: #111827; padding: 15px; border-radius: 14px; margin-bottom: 16px; border: 1px solid #00f0ff33; box-shadow: 0 4px 20px #00000066; }
    input, select, textarea, button { width: 100%; padding: 10px; margin: 6px 0; border-radius: 8px; border: 1px solid #1f2937; background: #1f2937; color: #fff; box-sizing: border-box; }
    button { background: linear-gradient(90deg, #00f0ff, #7b2cbf); color: #fff; font-weight: bold; border: none; cursor: pointer; }
    .badge { padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; background: #00f0ff22; color: #00f0ff; }
    .btn-sm { padding: 6px 10px; font-size: 12px; width: auto; display: inline-block; margin: 2px; text-decoration: none; border-radius: 6px; color: #fff; }
    .bg-red { background: #dc2626; } .bg-amber { background: #d97706; } .bg-green { background: #059669; }
    .checks { display: flex; flex-wrap: wrap; gap: 10px; margin: 8px 0; font-size: 13px; }
    .checks label { display: flex; align-items: center; gap: 5px; background: #1f2937; padding: 6px 10px; border-radius: 6px; }
    .checks input { width: auto; margin: 0; }
    .user-box { border-bottom: 1px solid #1f2937; padding: 12px 0; }
  </style>
</head>
<body>
  <h2>⚡ PRANAV AI — 3D Master Admin</h2>
  {% if not logged_in %}
    <div class="card">
      <form method="POST" action="/login">
        <input type="password" name="password" placeholder="Master Password डालें" required>
        <button type="submit">Unlock Control Panel</button>
      </form>
    </div>
  {% else %}
    <!-- 1. Generate User & Full 3D Access -->
    <div class="card">
      <h3>🔑 नया यूज़र & 3D Access बनाएँ</h3>
      <form method="POST" action="/create_user">
        <input type="text" name="user_name" placeholder="User Name (जैसे: Rahul)" required>
        <select name="plan">
          <option value="FREE">Free Plan (Basic Orb)</option>
          <option value="PRO_MAX">Pro Max (User API + All 3D)</option>
          <option value="AGENTIC_FULL">Agentic Full Access (Your API + All 3D + All Tools)</option>
        </select>
        <select name="character_3d">
          <option value="HOLOGRAM_ORB">3D Hologram Orb</option>
          <option value="JARVIS_3D">Jarvis 3D Avatar</option>
          <option value="VENOM_3D">Venom 3D Avatar</option>
          <option value="MAYA_3D">Maya 3D Avatar</option>
          <option value="ALL_3D">All 3D Characters Unlocked</option>
        </select>
        <div class="checks">
          <label><input type="checkbox" name="tools" value="phone_control" checked> Phone Control</label>
          <label><input type="checkbox" name="tools" value="whatsapp" checked> WhatsApp</label>
          <label><input type="checkbox" name="tools" value="vision" checked> Screen Vision</label>
          <label><input type="checkbox" name="tools" value="coding" checked> Coding/Web</label>
          <label><input type="checkbox" name="tools" value="whiteboard" checked> 3D Whiteboard</label>
        </div>
        <input type="number" name="daily_limit" value="500" placeholder="Daily AI Request Limit">
        <input type="number" name="days" value="365" placeholder="Validity (Days)">
        <button type="submit">Create Key & Grant Access</button>
      </form>
    </div>

    <!-- 2. Global 3D Models & System Prompt -->
    <div class="card">
      <h3>🌐 Global 3D Models & Brain Config</h3>
      <form method="POST" action="/update_global">
        <label>Master System Prompt:</label>
        <textarea name="system_prompt" rows="3">{{ cfg[1] }}</textarea>
        <label>Jarvis 3D (.glb URL):</label>
        <input type="text" name="glb_jarvis" value="{{ cfg[2] }}">
        <label>Venom 3D (.glb URL):</label>
        <input type="text" name="glb_venom" value="{{ cfg[3] }}">
        <label>Maya 3D (.glb URL):</label>
        <input type="text" name="glb_maya" value="{{ cfg[4] }}">
        <label>In-App Notice / Broadcast:</label>
        <input type="text" name="announcement" value="{{ cfg[5] }}">
        <button type="submit">Push Live to All Apps</button>
      </form>
    </div>

    <!-- 3. All Users List -->
    <div class="card">
      <h3>👥 Users & Access Control ({{ users|length }})</h3>
      {% for u in users %}
      <div class="user-box">
        <b>{{ u[1] }}</b> — <span class="badge">{{ u[0] }}</span> <span class="badge">{{ u[2] }}</span><br>
        <small>3D: <b>{{ u[5] }}</b> | Usage: {{ u[8] }}/{{ u[7] }} | Exp: {{ u[9] }}</small><br>
        <small>Phone: {{ u[4] or 'Not Linked' }} ({{ u[3] or 'No ID' }})</small><br>
        <small>Tools: {{ u[6] }}</small><br><br>
        <a class="btn-sm bg-green" href="/full_access/{{ u[0] }}">Give Full Access</a>
        <a class="btn-sm bg-amber" href="/unlink/{{ u[0] }}">Unlink Device</a>
        <a class="btn-sm bg-red" href="/toggle/{{ u[0] }}">{{ 'Block' if u[10]=='ACTIVE' else 'Unblock' }}</a>
      </div>
      {% endfor %}
    </div>
  {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    if not session.get("admin"):
        return render_template_string(HTML_DASHBOARD, logged_in=False)
    conn = sqlite3.connect(DB_PATH)
    users = conn.execute("SELECT * FROM users").fetchall()
    cfg = conn.execute("SELECT * FROM global_config WHERE id=1").fetchone()
    conn.close()
    return render_template_string(HTML_DASHBOARD, logged_in=True, users=users, cfg=cfg)

@app.route("/login", methods=["POST"])
def login():
    if request.form.get("password") == ADMIN_PASS:
        session["admin"] = True
    return redirect("/")

@app.route("/create_user", methods=["POST"])
def create_user():
    if not session.get("admin"): return redirect("/")
    name = request.form.get("user_name")
    plan = request.form.get("plan")
    char3d = request.form.get("character_3d")
    tools = ",".join(request.form.getlist("tools"))
    limit = int(request.form.get("daily_limit", 500))
    days = int(request.form.get("days", 30))
    key = "PRANAV-" + secrets.token_hex(3).upper()
    exp = (datetime.date.today() + datetime.timedelta(days=days)).isoformat()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO users VALUES (?, ?, ?, '', '', ?, ?, ?, 0, ?, 'ACTIVE')",
                 (key, name, plan, char3d, tools, limit, exp))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/full_access/<key>")
def full_access(key):
    if not session.get("admin"): return redirect("/")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""UPDATE users SET plan='AGENTIC_FULL', character_3d='ALL_3D',
                    allowed_tools='phone_control,whatsapp,vision,coding,whiteboard',
                    daily_limit=99999, status='ACTIVE' WHERE license_key=?""", (key,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/update_global", methods=["POST"])
def update_global():
    if not session.get("admin"): return redirect("/")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""UPDATE global_config SET system_prompt=?, glb_jarvis_url=?, glb_venom_url=?,
                    glb_maya_url=?, announcement=? WHERE id=1""",
                 (request.form["system_prompt"], request.form["glb_jarvis"],
                  request.form["glb_venom"], request.form["glb_maya"], request.form["announcement"]))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/unlink/<key>")
def unlink(key):
    if not session.get("admin"): return redirect("/")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE users SET device_id='', device_model='' WHERE license_key=?", (key,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/toggle/<key>")
def toggle(key):
    if not session.get("admin"): return redirect("/")
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT status FROM users WHERE license_key=?", (key,)).fetchone()
    if row:
        st = "BLOCKED" if row[0] == "ACTIVE" else "ACTIVE"
        conn.execute("UPDATE users SET status=? WHERE license_key=?", (st, key))
        conn.commit()
    conn.close()
    return redirect("/")

# Android App API Endpoint
@app.route("/verify", methods=["POST"])
def verify():
    data = request.json or {}
    key = data.get("key", "").strip()
    dev_id = data.get("device_id", "").strip()
    dev_model = data.get("device_model", "Android").strip()

    conn = sqlite3.connect(DB_PATH)
    u = conn.execute("SELECT * FROM users WHERE license_key=?", (key,)).fetchone()
    cfg = conn.execute("SELECT * FROM global_config WHERE id=1").fetchone()

    if not u:
        conn.close()
        return jsonify({"valid": False, "msg": "Invalid License Key!"})

    _, name, plan, saved_dev, _, char3d, tools, limit, used, exp, status = u
    if status != "ACTIVE":
        conn.close()
        return jsonify({"valid": False, "msg": "Account Blocked by Admin!"})
    if exp < datetime.date.today().isoformat():
        conn.close()
        return jsonify({"valid": False, "msg": "Plan Expired!"})

    if not saved_dev:
        conn.execute("UPDATE users SET device_id=?, device_model=? WHERE license_key=?", (dev_id, dev_model, key))
        conn.commit()
    elif saved_dev != dev_id:
        conn.close()
        return jsonify({"valid": False, "msg": "Key already linked to another phone!"})

    conn.close()
    return jsonify({
        "valid": True,
        "user_name": name,
        "plan": plan,
        "character_3d": char3d,
        "allowed_tools": tools.split(","),
        "daily_limit": limit,
        "api_key": MASTER_GEMINI_KEY if "AGENTIC" in plan else "",
        "system_prompt": cfg[1],
        "models_3d": {"jarvis": cfg[2], "venom": cfg[3], "maya": cfg[4]},
        "announcement": cfg[5]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
