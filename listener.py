from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from brevo_client import BrevoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
brevo = BrevoClient()
BREVO_LIST_ID = int(os.getenv("BREVO_LIST_ID", "3"))

# Servir les fichiers statiques (CSS, JS, images)
import pathlib
static_path = pathlib.Path(__file__).parent / "static"
css_path = pathlib.Path(__file__).parent / "css"
js_path = pathlib.Path(__file__).parent / "js"

if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")
if css_path.exists():
    app.mount("/css", StaticFiles(directory="css"), name="css")
if js_path.exists():
    app.mount("/js", StaticFiles(directory="js"), name="js")

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/submit")
async def submit(request: Request):
    form_data = await request.form()
    prenom = form_data.get('firstname', form_data.get('prenom', '')).strip()
    email  = form_data.get('email', '').strip()
    role   = form_data.get('role', '').strip()

    if not email:
        return HTMLResponse(content="Email manquant", status_code=400)

    # Ajouter dans Brevo
    brevo.create_or_update_contact(email, {"PRENOM": prenom, "ROLE": role})
    brevo.add_contact_to_list(email, BREVO_LIST_ID)

    # Envoyer email de confirmation
    subject = "✅ Votre place est réservée — L'Architecte IA"
    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px">
    <h2 style="color:#6366f1">✅ Votre place est confirmée</h2>
    <p>Bonjour {prenom},</p>
    <p>Vous êtes inscrit(e) au webinaire
    <strong>"Votre entreprise peut devenir une mini-IA en 90 jours"</strong>.</p>
    <p>Je vous enverrai le lien de connexion 24h avant la session.</p>
    <hr style="border:1px solid #e5e7eb;margin:20px 0">
    <p>D'ici là, préparez mentalement une réponse à cette question :</p>
    <blockquote style="border-left:4px solid #6366f1;padding:12px 20px;
    background:#f5f3ff;margin:16px 0">
    <strong>Quel processus mobilise le plus de temps humain
    sur des tâches répétitives dans votre organisation ?</strong>
    </blockquote>
    <p>À très vite,</p>
    <p><strong>L'Architecte IA</strong></p>
    </div>"""

    brevo.send_transactional_email(email, subject, html_body)

    # Page de confirmation
    return HTMLResponse(content="""
    <html><head><meta charset="UTF-8">
    <style>body{font-family:Arial,sans-serif;background:#0a0a1f;color:#fff;
    display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
    .box{text-align:center;padding:60px;max-width:500px}
    h2{color:#6366f1;font-size:2rem}
    p{color:#9ca3af;margin-top:16px}
    .btn{display:inline-block;margin-top:32px;padding:14px 28px;
    background:#6366f1;color:#fff;text-decoration:none;border-radius:8px}
    </style></head>
    <body><div class="box">
    <div style="font-size:48px">✅</div>
    <h2>Place confirmée !</h2>
    <p>Vérifiez votre boîte mail — un email de confirmation vient de vous être envoyé.</p>
    <a href="/" class="btn">Retour au site</a>
    </div></body></html>""")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
