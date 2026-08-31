# IAM et chiffrement — Jour 3

## Objectif

Le déploiement applique le principe du moindre privilège et les secrets de l'application ne sont pas stockés en clair dans le code ou dans l'image Docker.

## IAM

### Service Principal

Le Service Principal `sp-coffre-mdp` est utilisé pour les opérations de déploiement.

Le rôle `Contributor` est limité au Resource Group du projet :

`rg-homelab-cloud`

Il ne possède pas de rôle `Owner` ou `Contributor` au niveau global de la souscription.

### Managed Identity

L'application utilise une Managed Identity User Assigned :

`id-coffre-mdp`

Cette identité est attachée au Container Instance :

`coffre-mdp-app`

L'application utilise son `clientId` via la variable d'environnement `AZURE_CLIENT_ID`.

## Principe du moindre privilège

La Managed Identity de l'application possède uniquement les permissions nécessaires pour récupérer les secrets dans Azure Key Vault.

Permission utilisée :

* `Get` sur les secrets

L'application ne possède pas de droits d'administration sur le Key Vault.

## Azure Key Vault

Key Vault utilisé :

`kv-coffre-mdp-joel`

Les secrets suivants sont stockés dans Key Vault :

* `fernet-key` : clé utilisée par Fernet pour chiffrer et déchiffrer les mots de passe.
* `flask-secret` : clé secrète utilisée par Flask pour la gestion des sessions.

Les secrets ne sont pas stockés dans `app.py` et la clé Fernet n'est pas stockée dans l'image Docker.

## Fonctionnement de l'application

Au démarrage, l'application Flask utilise `DefaultAzureCredential` pour s'authentifier auprès d'Azure avec la Managed Identity du conteneur.

Le `SecretClient` permet ensuite de récupérer les secrets depuis Key Vault.

Flux d'accès :

`Flask → Azure Identity → Managed Identity → Key Vault → secret`

## Chiffrement au repos

Les données et secrets utilisés par les services Azure bénéficient du chiffrement au repos fourni par Azure.

Le projet ne stocke donc pas la clé de chiffrement de l'application directement dans le système de fichiers du conteneur.

La clé Fernet est centralisée dans Azure Key Vault.

## Vérifications réalisées

* Key Vault créé avec Terraform.
* `fernet-key` présent dans Key Vault.
* `flask-secret` présent dans Key Vault.
* Managed Identity créée et attachée au conteneur.
* Permissions de l'identité vérifiées.
* Application modifiée pour utiliser Azure Key Vault.
* Image Docker reconstruite et poussée vers Azure Container Registry.
* Application redéployée sur Azure Container Instances.
* Absence de `key.key` vérifiée dans `/app`.
* Application Web accessible.
* Création d'un compte de test réussie.
* Données enregistrées sous forme chiffrée.
* Aucun secret Fernet présent en clair dans le code source.

## Conclusion

La gestion des secrets a été externalisée vers Azure Key Vault.

L'application utilise une Managed Identity afin d'accéder aux secrets sans stocker d'identifiants Azure dans le code.

Le principe du moindre privilège est appliqué au niveau de l'accès aux secrets.
 
