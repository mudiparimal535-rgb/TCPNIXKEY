from flask import Flask, render_template_string, request, redirect, url_for, session
import requests
import secrets
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "norix_vip_secret_9846")

# --- CONFIGURATION ---
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "norix123")  # Admin Login Password
VPLINK_API_TOKEN = "696b1ae76598956d84ac9d914d6c68e0ccc1cc94"
TELEGRAM_CHANNEL = "https://t.me/NORIX44"
YOUTUBE_CHANNEL = "https://youtube.com/@NorixMod.s"

# Vercel writable temporary storage
KEYS_FILE = "/tmp/keys_pool.json"

def load_keys():
    if not os.path.exists(KEYS_FILE):
        return []
    try:
        with open(KEYS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_keys(keys_list):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(keys_list, f, indent=2)

# --- USER PORTAL UI ---
USER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NORIX MODS | VIP Key Portal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #030712;
            background-image: 
                radial-gradient(at 0% 0%, rgba(6, 182, 212, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(217, 70, 239, 0.15) 0px, transparent 50%);
        }
        .font-cyber { font-family: 'Orbitron', sans-serif; }
        .glass-card {
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(56, 189, 248, 0.2);
            box-shadow: 0 0 40px -10px rgba(6, 182, 212, 0.25);
        }
        .btn-cyber {
            background: linear-gradient(90deg, #06b6d4, #8b5cf6, #ec4899);
            background-size: 200% auto;
            transition: 0.4s;
        }
        .btn-cyber:hover {
            background-position: right center;
            box-shadow: 0 0 25px rgba(139, 92, 246, 0.6);
        }
        .grid-bg {
            background-size: 30px 30px;
            background-image: linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                              linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        }
    </style>
</head>
<body class="text-slate-100 min-h-screen flex flex-col justify-between grid-bg">

    <header class="border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md sticky top-0 z-50">
        <div class="max-w-5xl mx-auto px-4 py-3.5 flex items-center justify-between">
            <div class="flex items-center gap-2.5">
                <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-400 to-fuchsia-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
                    <i class="fa-solid fa-bolt text-slate-950 text-lg"></i>
                </div>
                <span class="font-cyber font-black text-lg tracking-wider bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-500 bg-clip-text text-transparent">
                    NORIX MODS
                </span>
            </div>
            <div class="flex items-center gap-3">
                <span class="px-3 py-1 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> {{ stock }} KEYS LEFT
                </span>
                <a href="/admin" class="text-slate-400 hover:text-cyan-400 text-sm transition" title="Admin Panel">
                    <i class="fa-solid fa-user-shield"></i>
                </a>
            </div>
        </div>
    </header>

    <main class="flex-grow flex items-center justify-center px-4 py-10">
        <div class="w-full max-w-md">
            <div class="glass-card rounded-3xl p-6 sm:p-8 relative overflow-hidden">
                <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500"></div>
                
                <div class="text-center mb-6">
                    <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-slate-900 border border-cyan-500/30 mb-4 shadow-inner">
                        <i class="fa-solid fa-key text-3xl text-cyan-400"></i>
                    </div>
                    <h1 class="font-cyber text-2xl font-bold tracking-wide text-white">VIP ACCESS KEY</h1>
                    <p class="text-xs text-slate-400 mt-1.5">Complete 1 quick verification step to claim your active VIP key.</p>
                </div>

                {% if error %}
                <div class="mb-5 p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2.5">
                    <i class="fa-solid fa-triangle-exclamation text-base"></i>
                    <span>{{ error }}</span>
                </div>
                {% endif %}

                {% if key %}
                <div class="space-y-4">
                    <div class="p-4 rounded-2xl bg-slate-950/90 border border-emerald-500/40 text-center">
                        <span class="text-[10px] uppercase tracking-widest text-emerald-400 font-bold block mb-1">Unlocked VIP Key</span>
                        <div id="vipKey" class="font-cyber text-base sm:text-lg font-bold text-white tracking-wider select-all py-1 break-all">
                            {{ key }}
                        </div>
                    </div>
                    <button onclick="copyKey()" id="copyBtn" class="w-full py-3.5 rounded-xl font-bold text-sm bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20">
                        <i class="fa-regular fa-copy"></i> <span id="copyText">COPY VIP KEY</span>
                    </button>
                </div>
                {% else %}
                <div class="space-y-5">
                    <div class="bg-slate-950/60 rounded-2xl p-4 border border-slate-800 space-y-2.5 text-xs text-slate-300">
                        <div class="flex items-center justify-between">
                            <span class="text-slate-400"><i class="fa-solid fa-database text-cyan-400 mr-1.5"></i> Available Stock</span>
                            <span class="font-semibold text-white">{{ stock }} Keys</span>
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-slate-400"><i class="fa-solid fa-shield-halved text-purple-400 mr-1.5"></i> Security</span>
                            <span class="font-semibold text-emerald-400">Main ID Safe</span>
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-slate-400"><i class="fa-solid fa-bolt text-pink-400 mr-1.5"></i> Delivery</span>
                            <span class="font-semibold text-white">Instant</span>
                        </div>
                    </div>

                    {% if stock > 0 %}
                    <a href="/start-verification" class="btn-cyber w-full py-4 rounded-xl font-cyber font-bold text-sm text-white tracking-wider flex items-center justify-center gap-2 shadow-xl">
                        <i class="fa-solid fa-unlock-keyhole"></i> GET VIP KEY NOW
                    </a>
                    {% else %}
                    <button disabled class="w-full py-4 rounded-xl font-cyber font-bold text-sm bg-slate-800 text-slate-500 cursor-not-allowed">
                        OUT OF STOCK - CHECK TELEGRAM
                    </button>
                    {% endif %}
                </div>
                {% endif %}

                <div class="mt-7 pt-5 border-t border-slate-800/80 grid grid-cols-2 gap-3">
                    <a href="{{ tg_link }}" target="_blank" class="py-2.5 px-3 rounded-xl bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 text-sky-400 text-xs font-semibold flex items-center justify-center gap-2 transition">
                        <i class="fa-brands fa-telegram text-base"></i> Telegram
                    </a>
                    <a href="{{ yt_link }}" target="_blank" class="py-2.5 px-3 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-400 text-xs font-semibold flex items-center justify-center gap-2 transition">
                        <i class="fa-brands fa-youtube text-base"></i> YouTube
                    </a>
                </div>
            </div>
        </div>
    </main>

    <footer class="py-5 text-center text-xs text-slate-500 border-t border-slate-900">
        <p>Powered by <span class="text-cyan-400 font-semibold">NORIX TCP</span></p>
    </footer>

    <script>
        function copyKey() {
            const keyText = document.getElementById("vipKey").innerText.trim();
            navigator.clipboard.writeText(keyText).then(() => {
                const btn = document.getElementById("copyBtn");
                const txt = document.getElementById("copyText");
                txt.innerText = "COPIED!";
                btn.classList.replace("bg-emerald-500", "bg-cyan-400");
                setTimeout(() => {
                    txt.innerText = "COPY VIP KEY";
                    btn.classList.replace("bg-cyan-400", "bg-emerald-500");
                }, 2500);
            });
        }
    </script>
</body>
</html>
"""

# --- ADMIN PANEL UI ---
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NORIX ADMIN | Key Manager</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #030712; }
        .font-cyber { font-family: 'Orbitron', sans-serif; }
    </style>
</head>
<body class="text-slate-100 min-h-screen p-4 sm:p-8">

    {% if not logged_in %}
    <!-- Admin Login Box -->
    <div class="max-w-sm mx-auto mt-20 bg-slate-900/90 border border-cyan-500/30 rounded-3xl p-7 shadow-2xl">
        <div class="text-center mb-6">
            <i class="fa-solid fa-user-shield text-4xl text-cyan-400 mb-3"></i>
            <h2 class="font-cyber text-xl font-bold">NORIX ADMIN LOGIN</h2>
        </div>
        {% if msg %}
        <div class="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs text-center">{{ msg }}</div>
        {% endif %}
        <form method="POST" action="/admin" class="space-y-4">
            <input type="password" name="password" placeholder="Enter Admin Password" required
                class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-700 focus:border-cyan-400 outline-none text-sm">
            <button type="submit" class="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-600 font-bold text-sm hover:opacity-90 transition">
                UNLOCK DASHBOARD
            </button>
        </form>
        <div class="text-center mt-4">
            <a href="/" class="text-xs text-slate-400 hover:text-white">← Back to Website</a>
        </div>
    </div>

    {% else %}
    <!-- Admin Dashboard -->
    <div class="max-w-3xl mx-auto space-y-6">
        <div class="flex flex-wrap items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
            <div>
                <h1 class="font-cyber text-xl font-bold text-cyan-400">NORIX KEY CONTROL</h1>
                <p class="text-xs text-slate-400">Upload .txt key files or manage active stock</p>
            </div>
            <div class="flex items-center gap-3">
                <a href="/" class="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold">View Site</a>
                <a href="/admin/logout" class="px-3.5 py-2 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-semibold">Logout</a>
            </div>
        </div>

        {% if msg %}
        <div class="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center gap-2">
            <i class="fa-solid fa-circle-check text-base"></i> {{ msg }}
        </div>
        {% endif %}

        <!-- Upload Section -->
        <div class="grid md:grid-cols-2 gap-6">
            <!-- Upload .txt File -->
            <div class="bg-slate-900/80 border border-cyan-500/20 rounded-2xl p-6">
                <h3 class="font-bold text-sm text-white mb-1 flex items-center gap-2">
                    <i class="fa-solid fa-file-arrow-up text-cyan-400"></i> Upload Key File (.txt)
                </h3>
                <p class="text-xs text-slate-400 mb-4">Ek line mein ek key honi chahiye.</p>
                <form method="POST" action="/admin/upload" enctype="multipart/form-data" class="space-y-4">
                    <input type="file" name="key_file" accept=".txt" required
                        class="w-full text-xs text-slate-300 file:mr-3 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-cyan-500/20 file:text-cyan-400 hover:file:bg-cyan-500/30 bg-slate-950 border border-slate-800 rounded-xl p-2">
                    <button type="submit" class="w-full py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition">
                        UPLOAD FILE & ADD KEYS
                    </button>
                </form>
            </div>

            <!-- Paste Bulk Keys -->
            <div class="bg-slate-900/80 border border-purple-500/20 rounded-2xl p-6">
                <h3 class="font-bold text-sm text-white mb-1 flex items-center gap-2">
                    <i class="fa-solid fa-paste text-purple-400"></i> Paste Keys Directly
                </h3>
                <p class="text-xs text-slate-400 mb-4">Direct text box mein keys paste karein.</p>
                <form method="POST" action="/admin/upload" class="space-y-3">
                    <textarea name="bulk_keys" rows="3" placeholder="NORIX-KEY-1&#10;NORIX-KEY-2"
                        class="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs focus:border-purple-400 outline-none"></textarea>
                    <button type="submit" class="w-full py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs transition">
                        ADD PASTED KEYS
                    </button>
                </form>
            </div>
        </div>

        <!-- Active Keys Stock List -->
        <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
            <div class="flex items-center justify-between mb-4">
                <h3 class="font-bold text-sm text-white">Active Stock ({{ keys|length }} Keys)</h3>
                {% if keys %}
                <form method="POST" action="/admin/clear">
                    <button type="submit" class="px-3 py-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-semibold">
                        Clear All Keys
                    </button>
                </form>
                {% endif %}
            </div>
            
            {% if keys %}
            <div class="max-h-60 overflow-y-auto space-y-2 pr-1">
                {% for k in keys %}
                <div class="flex items-center justify-between px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800/80 text-xs font-mono">
                    <span class="text-cyan-300">{{ k }}</span>
                    <span class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400">READY</span>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <p class="text-xs text-slate-500 text-center py-6">Abhi koi key uploaded nahi hai. Upar se .txt file upload karein.</p>
            {% endif %}
        </div>
    </div>
    {% endif %}
</body>
</html>
"""

# --- ROUTES ---
@app.route('/')
def index():
    keys = load_keys()
    return render_template_string(
        USER_HTML,
        key=None,
        stock=len(keys),
        error=request.args.get('error'),
        tg_link=TELEGRAM_CHANNEL,
        yt_link=YOUTUBE_CHANNEL
    )

@app.route('/start-verification')
def start_verification():
    keys = load_keys()
    if not keys:
        return redirect(url_for('index', error="Keys out of stock! Admin will upload soon."))

    token = secrets.token_urlsafe(16)
    session['verify_token'] = token
    
    base_url = request.url_root.rstrip('/')
    if "vercel.app" in base_url and base_url.startswith("http://"):
        base_url = base_url.replace("http://", "https://", 1)
        
    callback_url = f"{base_url}/verify/{token}"
    api_url = f"https://vplink.in/api?api={VPLINK_API_TOKEN}&url={callback_url}"
    
    try:
        res = requests.get(api_url, timeout=10).json()
        if res.get("status") == "success" and res.get("shortenedUrl"):
            return redirect(res["shortenedUrl"])
        return redirect(url_for('index', error="Shortlink API error! Try again."))
    except Exception:
        return redirect(url_for('index', error="Connection error! Please try again."))

@app.route('/verify/<token>')
def verify(token):
    saved_token = session.get('verify_token')
    if not saved_token or saved_token != token:
        return redirect(url_for('index', error="Invalid or expired verification link!"))
    
    session.pop('verify_token', None)
    keys = load_keys()
    if not keys:
        return redirect(url_for('index', error="Sorry, all keys just got claimed!"))

    # Pop 1st key from uploaded list so it isn't given twice
    assigned_key = keys.pop(0)
    save_keys(keys)

    return render_template_string(
        USER_HTML,
        key=assigned_key,
        stock=len(keys),
        error=None,
        tg_link=TELEGRAM_CHANNEL,
        yt_link=YOUTUBE_CHANNEL
    )

# --- ADMIN ROUTES ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin'))
        return render_template_string(ADMIN_HTML, logged_in=False, msg="Galat Password!")

    if not session.get('is_admin'):
        return render_template_string(ADMIN_HTML, logged_in=False, msg=None)

    return render_template_string(
        ADMIN_HTML,
        logged_in=True,
        keys=load_keys(),
        msg=request.args.get('msg')
    )

@app.route('/admin/upload', methods=['POST'])
def admin_upload():
    if not session.get('is_admin'):
        return redirect(url_for('admin'))

    new_keys = []
    # Check .txt file upload
    if 'key_file' in request.files and request.files['key_file'].filename != '':
        file = request.files['key_file']
        content = file.read().decode('utf-8', errors='ignore')
        new_keys.extend([line.strip() for line in content.splitlines() if line.strip()])

    # Check direct pasted text
    bulk_text = request.form.get('bulk_keys', '')
    if bulk_text.strip():
        new_keys.extend([line.strip() for line in bulk_text.splitlines() if line.strip()])

    if new_keys:
        existing = load_keys()
        existing.extend(new_keys)
        save_keys(existing)
        return redirect(url_for('admin', msg=f"{len(new_keys)} keys successfully upload ho gayi!"))

    return redirect(url_for('admin', msg="Koi valid key nahi mili!"))

@app.route('/admin/clear', methods=['POST'])
def admin_clear():
    if session.get('is_admin'):
        save_keys([])
    return redirect(url_for('admin', msg="Saari keys clear kar di gayi hain."))

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
