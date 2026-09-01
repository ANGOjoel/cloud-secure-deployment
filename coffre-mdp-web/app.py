"""
Coffre-fort de mots de passe — version web (Flask)

Reprend la logique de chiffrement du script desktop original
(Fernet, stockage JSON) et l'expose via des routes web simples,
pour pouvoir être conteneurisée et déployée dans le cloud.
"""
import os
import json
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash
from cryptography.fernet import Fernet
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = Flask(__name__)

DATA_FILE = "identifiant.json"

KEYVAULT_URL = "https://kv-coffre-mdp-joel.vault.azure.net"
FERNET_SECRET_NAME = "fernet-key"
FLASK_SECRET_NAME = "flask-secret"


def get_keyvault_client():
    credential = DefaultAzureCredential(
        managed_identity_client_id=os.environ.get("AZURE_CLIENT_ID")
    )

    return SecretClient(
        vault_url=KEYVAULT_URL,
        credential=credential
    )


keyvault_client = get_keyvault_client()

app.secret_key = keyvault_client.get_secret(FLASK_SECRET_NAME).value


# ---------- Chiffrement ----------

def get_cypher():
    key = keyvault_client.get_secret(FERNET_SECRET_NAME).value
    return Fernet(key.encode())


cypher = get_cypher()
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def find_user(nom_uti):
    for e in load_data():
        if e["Identifiant"] == nom_uti:
            return e
    return None


def verify_login(nom_uti, mdp_prin):
    user = find_user(nom_uti)
    if not user:
        return False
    try:
        mdp_dechiffre = cypher.decrypt(user["Mot de passe"].encode()).decode()
    except Exception:
        return False
    return mdp_dechiffre == mdp_prin


# ---------- Auth helper ----------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "nom_uti" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


# ---------- Routes ----------

@app.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", nom_uti=session["nom_uti"])


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nom_uti = request.form.get("identifiant", "").strip()
        mdp = request.form.get("mdp", "").strip()
        conf = request.form.get("conf", "").strip()

        if not nom_uti or not mdp:
            flash("Veuillez remplir tous les champs.", "warning")
            return redirect(url_for("register"))
        if mdp != conf:
            flash("Les mots de passe ne correspondent pas.", "warning")
            return redirect(url_for("register"))
        if find_user(nom_uti):
            flash("Ce compte existe déjà.", "warning")
            return redirect(url_for("register"))

        data = load_data()
        data.append({
            "Identifiant": nom_uti,
            "Mot de passe": cypher.encrypt(mdp.encode()).decode(),
            "Credentiels": [],
        })
        save_data(data)
        flash("Compte créé avec succès, vous pouvez vous connecter.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nom_uti = request.form.get("identifiant", "").strip()
        mdp = request.form.get("mdp", "").strip()
        if verify_login(nom_uti, mdp):
            session["nom_uti"] = nom_uti
            session["mdp_prin"] = mdp  # nécessaire pour déchiffrer les crédentiels de l'utilisateur
            return redirect(url_for("dashboard"))
        flash("Identifiant ou mot de passe incorrect.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/credentials")
@login_required
def list_credentials():
    user = find_user(session["nom_uti"])
    creds = []
    if user:
        for c in user.get("Credentiels", []):
            try:
                mdp_clair = cypher.decrypt(c["Mot de passe"].encode()).decode()
            except Exception:
                mdp_clair = "?"
            creds.append({"Site": c["Site"], "Nom": c["Nom"], "Mot de passe": mdp_clair})
    return render_template("credentials.html", creds=creds)


@app.route("/credentials/add", methods=["GET", "POST"])
@login_required
def add_credential():
    if request.method == "POST":
        site = request.form.get("site", "").strip()
        nom = request.form.get("nom", "").strip()
        mdp = request.form.get("mdp", "").strip()

        if not site or not nom or not mdp:
            flash("Veuillez remplir tous les champs.", "warning")
            return redirect(url_for("add_credential"))

        data = load_data()
        for e in data:
            if e["Identifiant"] == session["nom_uti"]:
                e.setdefault("Credentiels", [])
                e["Credentiels"].append({
                    "Site": site,
                    "Nom": nom,
                    "Mot de passe": cypher.encrypt(mdp.encode()).decode(),
                })
                break
        save_data(data)
        flash("Crédentiel enregistré avec succès.", "success")
        return redirect(url_for("list_credentials"))

    return render_template("add_credential.html")


@app.route("/credentials/delete/<int:index>", methods=["POST"])
@login_required
def delete_credential(index):
    data = load_data()
    for e in data:
        if e["Identifiant"] == session["nom_uti"]:
            creds = e.get("Credentiels", [])
            if 0 <= index < len(creds):
                creds.pop(index)
            break
    save_data(data)
    flash("Crédentiel supprimé.", "success")
    return redirect(url_for("list_credentials"))


@app.route("/health")
def health():
    # utile pour les probes Azure Container Instances / App Service
    return {"status": "ok"}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
