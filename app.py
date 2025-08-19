# app.py  — Flask 3.x / Python 3.10+
import os
import random, secrets
import requests

from flask import (
    Flask, render_template, request, redirect, url_for,
    jsonify, send_from_directory
)

from generators.excusegenerator import make_excuse, ALL_CATS
from generators.petname import make_pet_name

app = Flask(__name__, static_folder="static", template_folder="templates")

# ---------- Paths for the built React app (ai-image-colab) ----------
AI_IMG_STATIC_DIR = os.path.join(app.root_path, "static", "apps", "ai-image-colab")

# ---------- External API base (your Colab/ngrok URL) ----------
AI_IMG_API = os.environ.get("AI_IMG_API", "").rstrip("/")

# ---------- Sample data ----------
excuses = [
    "My Wi-Fi was abducted by aliens.",
    "I accidentally joined a goat yoga class instead of the meeting.",
    "My laptop fell asleep and refuses to wake up.",
    "I was busy defending my coffee from a cat attack.",
    "My time machine was set to the wrong year."
]

# ---------- Routes: basic pages ----------
@app.route("/")
def home():
    return render_template("home.html")

@app.get("/excuse-generator")
def excuse_generator_page():
    return render_template("excusegenerator.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# ---------- Excuse API ----------
@app.route("/excuse")
def get_excuse():
    return jsonify({"excuse": random.choice(excuses)})

# supports ?category=general|work|school and ?seed=123
@app.get("/api/excuse")
def api_excuse():
    category = request.args.get("category")
    seed_param = request.args.get("seed")
    try:
        seed = int(seed_param) if seed_param is not None else secrets.randbits(32)
    except ValueError:
        seed = secrets.randbits(32)

    rng = random.Random(seed)
    used_cat, text = make_excuse(category, rng)
    return jsonify({"category": used_cat, "excuse": text, "seed": seed})

@app.get("/api/categories")
def api_categories():
    return jsonify({"categories": ALL_CATS})

# ---------- Pet Name Generator ----------
@app.get("/petname-generator")
def petname_page():
    return render_template("petnamegenerator.html", active="petname")

@app.get("/api/petname")
def petname_api():
    cat = request.args.get("category")
    seed = request.args.get("seed")
    try:
        seed = int(seed) if seed is not None else secrets.randbits(32)
    except ValueError:
        seed = secrets.randbits(32)

    rng = random.Random(seed)
    used, name = make_pet_name(cat, rng)
    return jsonify({"category": used, "name": name, "seed": seed})

# ---------- Serve the built React app (AI Image – Colab) ----------
@app.route("/ai-image-colab/")
def ai_image_colab_index():
    return send_from_directory(AI_IMG_STATIC_DIR, "index.html")

@app.route("/ai-image-colab/<path:asset>")
def ai_image_colab_assets(asset):
    return send_from_directory(AI_IMG_STATIC_DIR, asset)

# ---------- Proxy to your Colab FastAPI (avoids CORS on frontend) ----------
@app.post("/api/ai-img/generate")
def ai_img_generate():
    if not AI_IMG_API:
        return jsonify({"detail": "Backend is not configured"}), 503
    try:
        r = requests.post(f"{AI_IMG_API}/generate", json=request.json, timeout=65)
        resp = app.response_class(
            r.content,
            status=r.status_code,
            mimetype=r.headers.get("content-type", "application/json"),
        )
        # allow the React app (served by this Flask) to call its own proxy
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
    except requests.RequestException as e:
        return jsonify({"detail": f"Proxy error: {e}"}), 502

@app.get("/api/ai-img/health")
def ai_img_health():
    if not AI_IMG_API:
        return jsonify({"status": "down", "reason": "AI_IMG_API not set"}), 503
    try:
        r = requests.get(f"{AI_IMG_API}/health", timeout=10)
        return (r.content, r.status_code,
                {"Content-Type": r.headers.get("content-type", "application/json")})
    except requests.RequestException as e:
        return jsonify({"status": "down", "reason": str(e)}), 502

# ---------- Projects page ----------
@app.route("/projects")
def projects_page():
    # Build the projects list *inside* the view so url_for has a request context
    colab_link = url_for("ai_image_colab_index")

    projects = [
        {
            "id": "excuse-generator",
            "title": "🎯 Excuse Generator",
            "description": "A witty excuse generator with creative responses and modern UI design. Perfect for those moments when you need a creative explanation.",
            "category": "Web App",
            "status": "Live Demo",
            "technologies": ["Flask", "Python", "CSS3", "HTML5"],
            "features": ["Random excuse generation", "Modern UI/UX", "Responsive design"],
            "link": "/excuse-generator",
            "github": None,
            "image": None,
            "priority": 1,
        },
        {
            "id": "petname-generator",
            "title": "🐾 Pet Name Generator",
            "description": "Creative pet naming tool with categories and beautiful animations. Generate unique names for your furry friends. Try it out!",
            "category": "Web App",
            "status": "Interactive",
            "technologies": ["JavaScript", "CSS3", "HTML5", "APIs"],
            "features": ["Category-based generation", "Beautiful animations", "Responsive design"],
            "link": "/petname-generator",
            "github": None,
            "image": None,
            "priority": 2,
        },
        {
            "id": "ai-image-colab",
            "title": "🖼️ AI Image Generator (Colab)",
            "description": "Prompt-to-image app powered by Stable Diffusion v1.5 running on Google Colab. Frontend served by Flask, API proxied to Colab (no CORS).",
            "category": "Web App",
            "status": "Live Demo",
            "technologies": ["React (Vite)", "Flask", "FastAPI", "Diffusers", "ngrok"],
            "features": ["Prompt input", "Neon painterly UI", "FastAPI proxy"],
            "link": url_for("ai_image_colab_index"),
            "github": "https://github.com/Manudd25/AI-Image-Generator",
            "priority": 3,
        },
    ]

    sorted_projects = sorted(projects, key=lambda x: x["priority"])
    return render_template("projects.html", projects=sorted_projects)

# ---------- Dev entrypoint ----------
if __name__ == "__main__":
    # Optionally set a default Colab URL while developing:
    # os.environ.setdefault("AI_IMG_API", "https://<your-ngrok>.ngrok-free.app")
    app.run(host="127.0.0.1", port=5000, debug=True)
