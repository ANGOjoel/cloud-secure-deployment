# Checklist de conformité ISO/IEC 27001:2022 — Annexe A

| ID contrôle | Description | Statut | Preuve |
|---|---|---|---|
| A.5.15 | Contrôle d'accès | Implémenté | Rôle IAM scopé au Resource Group (`security/iam-notes.md`), Managed Identity `id-coffre-mdp` avec permission `Get` uniquement sur les secrets |
| A.5.23 | Sécurité de l'information pour l'usage des services cloud | Implémenté | Utilisation exclusive du free tier Azure, ressources scopées à un seul Resource Group (`rg-homelab-cloud`) |
| A.8.9 | Gestion de la configuration | Partiel | Infrastructure définie en Terraform (`main.tf`, `compute.tf`, `iam.tf`, `keyvault.tf`), mais pas de pipeline CI/CD automatisé pour valider les changements |
| A.8.16 | Activités de surveillance | Non applicable | Aucun outil de monitoring/logging centralisé mis en place dans ce lab (hors périmètre du TP) |
| A.8.24 | Utilisation de la cryptographie | Implémenté | Chiffrement Fernet des mots de passe au repos, clé stockée dans Key Vault (`kv-coffre-mdp-joel`) plutôt qu'en clair |
| A.8.20 | Sécurité des réseaux | Partiel | Port exposé limité au strict nécessaire (8080), pas d'accès SSH public — mais absence de TLS (voir `gouvernance/ebios-rm-analyse.md`) |
| A.8.3 | Restriction d'accès à l'information | Implémenté | Secrets applicatifs (clé Fernet, clé de session Flask) stockés exclusivement dans Key Vault, jamais en variable d'environnement en clair ou dans l'image Docker |
| A.5.10 | Utilisation acceptable de l'information et des actifs associés | Implémenté | `.gitignore` couvrant `.terraform/`, `*.tfstate`, `*.tfvars` — aucun secret ni état d'infrastructure commité |
| A.8.28 | Codage sécurisé | Partiel | Récupération des secrets via `DefaultAzureCredential`/`SecretClient` (bonne pratique SDK Azure), mais pas d'analyse statique de code (SAST) mise en place |
| A.5.7 | Renseignement sur les menaces | Implémenté | Analyse de risques EBIOS RM menée (`gouvernance/ebios-rm-analyse.md`), scénarios de menace identifiés et évalués |
| A.5.9 | Inventaire des informations et autres actifs associés | Implémenté | Atelier 1 de l'analyse EBIOS RM : biens essentiels et biens supports recensés |
| A.5.30 | Préparation aux TIC pour la continuité d'activité | Non applicable | Hors périmètre : projet de démonstration en free tier, pas d'exigence de disponibilité en production |

**Légende statut :** Implémenté / Partiel / Non applicable
