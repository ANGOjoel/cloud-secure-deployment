# Analyse de risques EBIOS RM — Jour 4

## Atelier 1 — Biens essentiels et biens supports

**Biens essentiels :**
- Les mots de passe des utilisateurs (données stockées, même chiffrées)
- La disponibilité de l'application

**Biens supports :**
- Azure Key Vault
- Managed Identity (id-coffre-mdp)
- Conteneur applicatif (coffre-mdp-app)
- Registre ACR (coffremdpacr)
- Clé de chiffrement Fernet

## Atelier 2 — Sources de risque

1. Attaquant externe opportuniste (scan/bot automatisé cherchant des services mal configurés)
2. Erreur de configuration IAM (droits trop larges accordés par erreur)
3. Fuite d'identifiants/secrets (credentials exposés accidentellement, ex. commit git ou terminal)

## Ateliers 3-4 — Scénarios de risque

### Scénario 1 — Fuite d'identifiants → accès non autorisé à Key Vault

- **Source :** fuite d'identifiants cloud
- **Scénario :** un attaquant récupère un identifiant Azure exposé accidentellement (historique git, terminal, repo mal configuré) et s'en sert pour s'authentifier auprès de Key Vault.
- **Impact :** récupération de la clé Fernet, permettant de déchiffrer les mots de passe utilisateurs.
- **Bien essentiel touché :** confidentialité des mots de passe utilisateurs
- **Vraisemblance :** moyenne
- **Gravité :** critique

### Scénario 2 — Absence de TLS → interception réseau

- **Source :** attaquant externe opportuniste
- **Scénario :** l'application étant exposée en HTTP simple sur le port 8080, un attaquant en position d'interception réseau capture le trafic en clair (identifiants de connexion, cookie de session).
- **Impact :** vol d'un mot de passe utilisateur en clair au moment de sa saisie, ou détournement de session.
- **Bien essentiel touché :** confidentialité des mots de passe utilisateurs (en transit)
- **Vraisemblance :** moyenne à forte
- **Gravité :** forte

## Atelier 5 — Mesures en place et risque résiduel

### Scénario 1

**Mesures en place :**
- Managed Identity : l'application n'a jamais besoin de manipuler un identifiant Azure elle-même.
- Rôle IAM scopé au Resource Group, pas à la souscription entière.
- `plan.tfplan` retiré du dépôt et ajouté au `.gitignore`.

**Risque résiduel :** une fuite reste possible par erreur humaine, mais son impact est limité par le scope réduit du rôle IAM.

**Action complémentaire proposée :** utiliser un hook pre-commit (ex. git-secrets) pour bloquer automatiquement tout commit contenant un pattern de credential.

### Scénario 2

**Mesures en place :**
- Port exposé limité au strict nécessaire (8080), pas d'accès SSH public.
- Mots de passe chiffrés au repos (Fernet).

**Risque résiduel :** aucun chiffrement en transit actuellement — le risque d'interception au moment de la saisie reste entier.

**Action complémentaire proposée :** ajouter un reverse proxy (Azure Application Gateway ou Nginx) avec certificat TLS.
