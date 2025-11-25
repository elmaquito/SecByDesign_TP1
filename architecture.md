# Schéma d'architecture et justifications

## 1. Schéma d'architecture 3-Tiers

```
+-----------------+      +-----------------+      +-----------------+
|                 |      |                 |      |                 |
|    Frontend     |----->|     Backend     |----->|   Base de       |
| (Navigateur Web)|      |   (Serveur API) |      |    Données      |
|                 |      |                 |      |                 |
+-----------------+      +-----------------+      +-----------------+
       |                        |                        |
       | HTTPS                  | Chiffrement            | Cloisonnement
       |                        | des mots de passe      |
       | Authentification       |                        |
       | et RBAC (côté client)  | Validation côté serveur|
       |                        |                        |
       |                        | Principe du moindre    |
       |                        | privilège              |
       |                        |                        |
       |                        | Journalisation         |
```

## 2. Justification des choix de sécurité

### Frontend (Client)

*   **HTTPS (via `app.js`)**: La communication entre le navigateur et le backend se fait via HTTPS. Le `fetch` dans `app.js` est configuré pour appeler une URL en `https://`. Cela chiffre les données en transit, y compris les identifiants de connexion et les jetons JWT, empêchant les attaques de type "man-in-the-middle".
*   **Authentification et RBAC (côté client)**: Le frontend gère l'état de connexion de l'utilisateur. Après une connexion réussie, un jeton JWT est stocké et utilisé pour les requêtes authentifiées. L'interface utilisateur s'adapte en fonction de l'état de connexion (par exemple, en affichant ou masquant les sections de notes).

### Backend (Serveur d'API)

*   **HTTPS (via `app.py`)**: Le serveur Flask est configuré pour s'exécuter avec un contexte SSL (`ssl_context=('cert.pem', 'key.pem')`). Cela garantit que toutes les communications avec le serveur sont chiffrées.
*   **Chiffrement des mots de passe (via `app.py`)**: La bibliothèque `Flask-Bcrypt` est utilisée pour hacher et saler les mots de passe avant de les stocker dans la base de données. La fonction `bcrypt.generate_password_hash` crée un hachage robuste, et `bcrypt.check_password_hash` compare en toute sécurité un mot de passe fourni avec le hachage stocké.
*   **Validation côté serveur (implicite dans `app.py`)**: Bien que non explicite avec une bibliothèque de validation, le backend valide implicitement les données. Par exemple, lors de la connexion, il vérifie si l'utilisateur existe et si le mot de passe est correct. Pour la création de notes, il s'assure que l'utilisateur est authentifié. Des bibliothèques comme `Marshmallow` ou `Pydantic` pourraient être ajoutées pour une validation plus stricte des schémas de données en entrée.
*   **Principe du moindre privilège (via `app.py`)**:
    *   Les utilisateurs normaux (`user`) ne peuvent voir et gérer que leurs propres notes. La route `/api/notes` filtre les notes en fonction de l'ID de l'utilisateur authentifié (`current_user`).
    *   Un rôle `admin` a des privilèges plus élevés, comme la possibilité de voir toutes les notes de tous les utilisateurs via la route `/api/admin/notes`.
*   **Authentification et RBAC (Role-Based Access Control) (via `app.py`)**:
    *   `Flask-JWT-Extended` est utilisé pour gérer l'authentification basée sur les jetons JWT. Les routes protégées nécessitent un jeton valide avec le décorateur `@jwt_required()`.
    *   Un décorateur personnalisé `role_required(role)` a été créé pour mettre en œuvre le RBAC. Il vérifie si l'utilisateur authentifié a le rôle requis pour accéder à une ressource spécifique.
*   **Journalisation**: Flask intègre un système de journalisation. En mode `debug=True`, les journaux sont détaillés. En production, on configurerait un système de journalisation plus robuste (par exemple, envoi des journaux vers un service centralisé) pour surveiller les activités suspectes, les erreurs et les tentatives d'accès non autorisé.

### Base de Données

*   **Cloisonnement de la BDD**: La base de données est sur un "tier" séparé. L'application backend est le seul composant qui a un accès direct à la base de données. Le frontend (client) ne peut jamais interroger directement la base de données. Toute interaction passe par l'API backend, qui applique la logique de contrôle d'accès. L'utilisateur de la base de données configuré pour l'application Flask devrait avoir uniquement les permissions nécessaires (CRUD sur les tables de l'application) et non des droits d'administration sur le serveur de base de données.

## 3. Répartition des responsabilités

*   **Frontend**: Responsable de la présentation de l'interface utilisateur, de la capture des entrées utilisateur et de la communication avec l'API backend. Il gère l'état de l'interface en fonction de l'authentification mais ne prend pas de décisions de sécurité critiques.
*   **Backend**: C'est le cœur de la sécurité. Il est responsable de :
    *   L'authentification des utilisateurs.
    *   L'application des règles de contrôle d'accès (RBAC).
    *   La validation des données.
    *   La communication sécurisée avec la base de données.
    *   La journalisation des événements de sécurité.
*   **Base de Données**: Responsable du stockage sécurisé des données. Le chiffrement des données au repos (en plus du hachage des mots de passe) pourrait être ajouté pour une sécurité renforcée. Les permissions d'accès à la base de données sont limitées au strict minimum pour l'application backend.
