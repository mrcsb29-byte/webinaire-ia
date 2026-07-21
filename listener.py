from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from brevo_client import BrevoClient
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from urllib.parse import parse_qs

load_dotenv()

app = FastAPI()
brevo = BrevoClient()
BREVO_LIST_ID = os.getenv("BREVO_LIST_ID", "3")

@app.post("/submit")
async def submit(request: Request):
    try:
        # 1. Récupérer les données du formulaire
        # FastAPI handles form data with request.form()
        form_data = await request.form()
        prenom = form_data.get('prenom', '').strip()
        email  = form_data.get('email', '').strip()
        role   = form_data.get('role', '').strip()

        if not email:
            return HTMLResponse(content="Email manquant", status_code=400)

        # 2. Ajouter le contact dans Brevo
        attributes = {
            "PRENOM": prenom,
            "ROLE": role,
            "SOURCE": "webinaire-ia"
        }

        # Use the brevo client to create/update
        success_contact = brevo.create_or_update_contact(email, attributes)
        if not success_contact:
            return HTMLResponse(content="Erreur lors de l'ajout du contact dans Brevo", status_code=500)

        # Add to the webinar list
        success_list = brevo.add_contact_to_list(email, BREVO_LIST_ID)
        if not success_list:
            # We still continue as the contact exists, but log the list failure
            print(f"DEBUG: Failed to add {email} to list {BREVO_LIST_ID}")

        # --- NEW: Send immediate confirmation email (Direct Delivery) ---
        email_subject = "✅ Votre place est réservée — 11/07/2026 à 20h00"
        email_body = f"""
        <p>Bonjour {prenom},</p>
        <p>Votre place est confirmée pour le webinaire "Votre entreprise peut devenir une mini-IA en 90 jours".</p>
        <p><strong>Date : Vendredi 11/07/2026 à 20h00</strong><br>
        <strong>Lien de connexion : <a href='https://calendly.com/mrcsb-29/30min?month=2026-07'>https://calendly.com/mrcsb-29/30min?month=2026-07</a></strong><br>
        <strong>Durée : 45 minutes exactement</strong></p>
        <p>Pour que ce webinaire soit le plus utile possible pour vous, préparez mentalement une réponse à cette question avant de vous connecter :</p>
        <p><strong>Dans votre organisation, quel est le processus qui mobilise le plus de temps humain sur des tâches répétitives ?</strong></p>
        <p>Pas besoin d'une réponse parfaite. Juste une intuition. On travaillera dessus ensemble.</p>
        <p>À Vendredi,</p>
        <p>L'Architecte IA</p>
        """
        email_sent = brevo.send_transactional_email(email, email_subject, email_body)
        if not email_sent:
            print(f"DEBUG: Failed to send confirmation email to {email}")
        else:
            print(f"DEBUG: Confirmation email successfully sent to {email}")
        # -----------------------------------------------------------------

        # 3. Logger l'inscription localement
        log_entry = {
            "date": datetime.now().isoformat(),
            "prenom": prenom,
            "email": email,
            "role": role,
            "brevo_status": "success" if success_contact else "failed"
        }

        logs_path = "inscriptions_log.json"
        existing = []
        if os.path.exists(logs_path):
            try:
                with open(logs_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except Exception:
                existing = []

        existing.append(log_entry)
        with open(logs_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

        # 4. Rediriger vers page de confirmation
        return RedirectResponse(url="/merci", status_code=303)

    except Exception as e:
        return HTMLResponse(content=f"<h1 style='color:white; background:black; padding:20px;'>Erreur lors de l'inscription</h1><p style='color:white; background:black;'>{str(e)}</p>", status_code=500)

@app.get("/merci")
async def merci():
    return HTMLResponse(content="""
    <html><head><meta charset="utf-8">
    <title>Inscription confirmée</title>
    <style>
    body{font-family:sans-serif;display:flex;align-items:center;
         justify-content:center;height:100vh;margin:0;background:#0a0a0f;color:#fff}
    .box{text-align:center;padding:40px}
    h1{font-size:32px;margin-bottom:16px}
    p{color:#9ca3af;font-size:16px;max-width:400px}
    </style></head>
    <body><div class="box">
    <h1 style="color:white">✅ Votre place est réservée !</h1>
    <p style="color:#9ca3af">Vous allez recevoir un email de confirmation dans les prochaines minutes.
    Vérifiez vos spams si vous ne le recevez pas.</p>
    </div></body></html>
    """)

@app.post("/webhook/formspree")
async def formspree_webhook(request: Request):
    # Keep for backward compatibility or tests
    return await submit(request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
