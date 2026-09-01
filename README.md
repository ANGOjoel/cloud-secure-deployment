# Cloud Secure Deployment — Azure

Projet de déploiement cloud sécurisé sur Microsoft Azure, avec Infrastructure as Code (Terraform), conteneurisation, gestion des secrets et dossier de gouvernance (EBIOS RM, ISO 27001).

## Objectif

Démontrer une chaîne complète de déploiement cloud sécurisé : de l’infrastructure de base jusqu’à l’analyse de risques et la conformité, en restant dans le free tier Azure.

## Architecture

Compte Azure (Free Tier)
    └── Resource Group : rg-homelab-cloud (France Central)
            ├── Container Registry : coffremdpacr
            ├── Container Instance : coffre-mdp-app (gestionnaire de mots de passe, port 8080)
            └── Key Vault : kv-coffre-mdp-joel (secrets de l'application)

## Avancement

- [x] **Jour 1** — Bootstrap Infrastructure as Code
- [x] **Jour 2** — Déploiement de l'application conteneurisée
- [x] **Jour 3** — IAM least-privilege et chiffrement
- [x] **Jour 4** — Analyse de risques EBIOS RM
- [x] **Jour 5** — Conformité ISO 27001 et destruction des ressources

## Jour 1 — Bootstrap Infrastructure as Code

**Réalisé :**
- Compte Azure gratuit configuré (free tier)
- Azure CLI installé et authentifié
- Terraform installé et initialisé
- Premier resource group déployé par code via Terraform : `rg-homelab-cloud` (région France Central)

**Fichiers :**
- `jour1-bootstrap/main.tf` — définition du provider Azure et du resource group

**Preuve de déploiement :**

![Resource group créé](screenshots/resource-group-created.png)

Vérification indépendante via Azure CLI (`az group show --name rg-homelab-cloud`), confirmant `"provisioningState": "Succeeded"`.

## Jour 2 — Déploiement conteneurisé de l'application

**Réalisé :**
- Application Flask (gestionnaire de mots de passe, chiffrement Fernet) conteneurisée via Docker
- Image poussée vers Azure Container Registry (`coffremdpacr`)
- Déploiement du conteneur via Terraform sur Azure Container Instances
- Application accessible publiquement, uniquement sur le port applicatif (8080), sans accès SSH exposé

**Fichiers :**
- `coffre-mdp-web/Dockerfile` — définition de l'image Docker
- `coffre-mdp-web/app.py` — application Flask
- `coffre-mdp-web/requirements.txt` — dépendances Python
- `jour2-deploy/compute.tf` — déploiement du conteneur sur Azure

**URL de l'application déployée :**
`http://coffre-mdp-joel.francecentral.azurecontainer.io:8080`

**Preuve de déploiement :**

![Application déployée sur Azure](screenshots/app-deployed.png)

Statut confirmé "En cours d'exécution" dans le portail Azure, conteneur unique et adresse IP publique attribuée.

## Jour 3 — IAM least-privilege et chiffrement

**Réalisé :**
- Azure Key Vault `kv-coffre-mdp-joel` créé pour centraliser les secrets
- Secret `fernet-key` stocké dans Key Vault pour le chiffrement des mots de passe
- Secret `flask-secret` stocké dans Key Vault pour la clé de session Flask
- Managed Identity User Assigned `id-coffre-mdp` créée et attachée au conteneur
- Permission `Get` accordée à la Managed Identity pour accéder aux secrets
- Application Flask modifiée pour utiliser `DefaultAzureCredential` et `SecretClient`
- Clé Fernet retirée du conteneur : aucun fichier `key.key` présent dans `/app`
- Image Docker reconstruite et poussée vers Azure Container Registry
- Application redéployée et testée avec succès
- Compte utilisateur de test créé afin de vérifier le fonctionnement du coffre-fort

**Fichiers :**
- `security/iam-notes.md` — documentation IAM et gestion des secrets
- `coffre-mdp-web/app.py` — récupération des secrets depuis Azure Key Vault
- `coffre-mdp-web/requirements.txt` — dépendances Azure Identity et Key Vault

**Architecture de sécurité :**

`Utilisateur → Azure Container Instance → Flask → Managed Identity → Azure Key Vault → Secrets`

Le principe du moindre privilège est appliqué : l'application utilise une Managed Identity dédiée et dispose uniquement des permissions nécessaires pour récupérer les secrets.

## Jour 4 — Analyse de risques EBIOS RM

**Réalisé :**
- Analyse de risques menée selon la méthode EBIOS Risk Manager (version simplifiée)
- Identification des biens essentiels et des biens supports
- Identification des sources de risque
- Construction de deux scénarios de risque principaux
- Analyse des mesures de sécurité déjà présentes
- Identification du risque résiduel
- Proposition d'actions complémentaires

**Scénarios étudiés :**
- Fuite d'identifiants → accès non autorisé aux secrets du Key Vault
- Absence de TLS (HTTP non chiffré) → interception des données en transit

**Atelier 5 :**
Pour chaque scénario, les mesures de sécurité déjà mises en place, le risque résiduel et une action complémentaire ont été identifiés.

**Fichiers :**
- `gouvernance/ebios-rm-analyse.md` — analyse de risques EBIOS RM

**Synthèse :**

Le principal risque résiduel identifié est l'absence de chiffrement des communications entre l'utilisateur et l'application, celle-ci étant exposée en HTTP sur le port 8080.

## Jour 5 — Conformité ISO 27001 et destruction des ressources

**Réalisé :**
- Vérification des principaux contrôles de sécurité du projet à travers une checklist ISO 27001
- Vérification de la gestion des secrets
- Vérification de l'utilisation d'une Managed Identity
- Vérification du principe du moindre privilège
- Vérification de la protection des données
- Destruction des ressources Azure à la fin du projet afin d'éviter toute facturation inutile

**Fichiers :**
- `f7b2beb` — checklist ISO 27001 documentée dans le dépôt

**Destruction des ressources :**

La destruction a été effectuée afin de supprimer les ressources Azure utilisées pendant le projet.

La commande utilisée pour finaliser la suppression du Resource Group a été :

```bash
az group delete --name rg-homelab-cloud --yes
