from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn
from brevo_client import BrevoClient
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

app = FastAPI()
brevo = BrevoClient()
BREVO_LIST_ID = os.getenv("BREVO_LIST_ID", "3")

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

    brevo.create_or_update_contact(email, {"PRENOM": prenom, "ROLE": role})
    brevo.add_contact_to_list(email, int(BREVO_LIST_ID))

    subject = "✅ Votre place est réservée — webinaire L'Architecte IA"
    html = f"""<p>Bonjour {prenom},</p>
    <p>Votre place est confirmée pour le webinaire <strong>"Votre entreprise peut devenir une mini-IA en 90 jours"</strong>.</p>
    <p>Je vous enverrai le lien de connexion 24h avant.</p>
    <p>En attendant, préparez la réponse à cette question :<br>
    <strong>Quel processus mobilise le plus de temps humain dans votre organisation ?</strong></p>
    <p>À très vite,<br><strong>L'Architecte IA</strong></p>"""

    brevo.send_transactional_email(email, subject, html)

    return HTMLResponse(content="""<html><body style='font-family:sans-serif;text-align:center;padding:60px'>
    <h2>✅ Merci !</h2><p>Votre place est confirmée. Vérifiez votre boîte mail.</p>
    </body></html>""")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
