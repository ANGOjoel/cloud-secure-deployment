# Cloud Secure Deployment — Azure

Projet de déploiement cloud sécurisé sur Microsoft Azure, avec Infrastructure as Code (Terraform), conteneurisation, gestion des secrets et dossier de gouvernance (EBIOS RM, ISO 27001).

## Objectif

Démontrer une chaîne complète de déploiement cloud sécurisé : de l'infrastructure de base jusqu'à l'analyse de risques et la conformité, en restant dans le free tier Azure.

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
- Terraform (v1.16.0) installé et initialisé
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
- `jour2-deploy/compute.tf` — déploiement du conteneur sur Azure

**URL de l'application déployée :**
`http://coffre-mdp-joel.francecentral.azurecontainer.io:8080`

**Preuve de déploiement :**

![Application déployée sur Azure](screenshots/app-deployed.png)

Statut confirmé "En cours d'exécution" dans le portail Azure, conteneur unique, adresse IP publique attribuée.

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

**Fichiers :**
- `security/iam-notes.md` — documentation IAM et gestion des secrets
- `coffre-mdp-web/app.py` — récupération des secrets depuis Azure Key Vault
- `coffre-mdp-web/requirements.txt` — dépendances Azure Identity et Key Vault

**Principe de moindre privilège :**

La Managed Identity `id-coffre-mdp` est utilisée par l'application pour s'authentifier auprès d'Azure sans stocker de mot de passe ou de clé d'accès dans le code.

L'identité dispose uniquement des permissions nécessaires pour récupérer les secrets de l'application depuis Azure Key Vault.

Aucun rôle `Owner` ou `Contributor` global n'est accordé à l'application.

**Gestion des secrets :**

Les secrets applicatifs ne sont pas stockés en clair dans le code source. Ils sont centralisés dans Azure Key Vault et récupérés à l'exécution par l'application grâce à la Managed Identity.

**Chiffrement :**

Les mots de passe utilisateurs sont chiffrés avec Fernet avant leur stockage. La clé Fernet est conservée dans Azure Key Vault et n'est donc plus présente dans l'image Docker.

Le stockage Azure utilisé pour les données est également chiffré au repos conformément aux mécanismes de protection Azure.

**Fichier de documentation :**

`security/iam-notes.md`

Ce fichier documente les choix effectués concernant l'IAM, la gestion des secrets et le chiffrement.

## Jour 4 — Analyse de risques EBIOS RM

**Réalisé :**
- Identification des biens essentiels de l'application
- Identification des biens supports nécessaires au fonctionnement du service
- Identification des sources de risque
- Construction de scénarios de risque
- Analyse des mesures de sécurité déjà présentes
- Identification du risque résiduel
- Proposition de mesures complémentaires

**Principaux scénarios étudiés :**

### Scénario 1 — Compromission d'identifiants et accès aux secrets

Un attaquant récupère des identifiants permettant d'accéder à l'environnement Azure et tente d'obtenir les secrets stockés dans Key Vault.

**Mesures existantes :**
- Managed Identity pour éviter le stockage de credentials Azure dans l'application
- Principe du moindre privilège
- Permissions limitées sur Key Vault
- Secrets centralisés dans Azure Key Vault
- Absence de clé Fernet dans l'image Docker

**Risque résiduel :**

Une compromission d'un compte disposant de permissions suffisantes ou une erreur humaine pourrait toujours permettre un accès non autorisé.

**Mesure complémentaire proposée :**

Mettre en place une authentification multifacteur, une surveillance des accès et une détection automatique des secrets exposés dans les dépôts Git.

### Scénario 2 — Interception des communications

L'application étant exposée sur un endpoint HTTP, un attaquant positionné sur le chemin réseau pourrait intercepter les communications.

**Mesures existantes :**
- Application conteneurisée
- Accès limité au port applicatif
- Secrets non transmis directement dans le code source
- Chiffrement des mots de passe côté application

**Risque résiduel :**

Le chiffrement applicatif des mots de passe ne protège pas toutes les données échangées entre le navigateur et l'application si la connexion HTTP n'est pas protégée par TLS.

**Mesure complémentaire proposée :**

Placer l'application derrière un endpoint HTTPS avec certificat TLS afin de protéger les communications entre l'utilisateur et l'application.

**Fichier :**
- `gouvernance/ebios-rm-analyse.md` — analyse des risques et mesures de sécurité

## Jour 5 — Conformité ISO 27001 et destruction des ressources

**Réalisé :**
- Vérification des principaux contrôles de sécurité applicables au projet
- Documentation des mesures IAM
- Documentation de la gestion des secrets
- Documentation du chiffrement
- Vérification de la traçabilité et de la gestion des accès
- Documentation de l'analyse de risques
- Destruction des ressources Azure à la fin du projet

**Documentation :**
- `gouvernance/iso27001-checklist.md` — checklist de conformité ISO 27001
- `gouvernance/ebios-rm-analyse.md` — analyse de risques EBIOS RM
- `security/iam-notes.md` — documentation IAM et gestion des secrets

### Destruction des ressources

Pour éviter toute facturation inutile, les ressources Azure utilisées pendant le projet ont été supprimées à la fin du TP.

La suppression a été effectuée avec :

```bash
az group delete --name rg-homelab-cloud --yes
