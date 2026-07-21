import requests
import os
from dotenv import load_dotenv

load_dotenv()

class BrevoClient:
    def __init__(self):
        self.api_key = os.getenv("BREVO_API_KEY")
        self.base_url = "https://api.brevo.com/v3"
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def create_or_update_contact(self, email, attributes):
        """
        Creates or updates a contact in Brevo with specified attributes.
        """
        endpoint = f"{self.base_url}/contacts"
        payload = {
            "email": email,
            "attributes": attributes,
            "updateEnabled": True
        }

        response = requests.post(endpoint, json=payload, headers=self.headers)
        if response.status_code in [201, 204]:
            return True
        return False

    def add_contact_to_list(self, email, list_id):
        """
        Adds a contact to a specific Brevo list.
        """
        endpoint = f"{self.base_url}/contacts/lists/{list_id}/contacts/add"
        payload = {
            "emails": [email]
        }

        response = requests.post(endpoint, json=payload, headers=self.headers)
        if response.status_code not in [200, 201, 204]:
            print(f"DEBUG Brevo List Error: {response.status_code} - {response.text}")
        return response.status_code in [200, 201, 204]

    def create_list(self, name):
        """
        Creates a new contact list in Brevo.
        """
        endpoint = f"{self.base_url}/contacts-lists"
        payload = {"name": name}

        response = requests.post(endpoint, json=payload, headers=self.headers)
        if response.status_code == 201:
            return response.json().get("id")
        print(f"DEBUG: create_list failed with status {response.status_code}: {response.text}")
        return None

    def create_attribute(self, name, type="text"):
        """
        Creates a contact attribute (e.g., PRENOM, ROLE).
        """
        endpoint = f"{self.base_url}/attributes"
        payload = {
            "name": name,
            "type": type
        }

        response = requests.post(endpoint, json=payload, headers=self.headers)
        return response.status_code == 201

    def send_transactional_email(self, to_email, subject, html_content):
        """
        Sends a transactional email via Brevo.
        """
        endpoint = f"{self.base_url}/smtp/email"

        # Sender details are mandatory for transactional emails
        sender_email = os.getenv("BREVO_SENDER_EMAIL", "contact@yourdomain.com")
        sender_name = os.getenv("BREVO_SENDER_NAME", "L'Architecte IA")

        payload = {
            "sender": {
                "name": sender_name,
                "email": sender_email
            },
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_content
        }

        response = requests.post(endpoint, json=payload, headers=self.headers)
        if response.status_code not in [200, 201, 202]:
            print(f"DEBUG Brevo Email Error: {response.status_code} - {response.text}")
        return response.status_code in [200, 201, 202]
