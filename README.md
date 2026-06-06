# Afiri - Plateforme de Connexion Étudiant & Emploi 🚀

Afiri est une application web conçue pour aider les étudiants à trouver des offres d'emploi, stages ou alternances correspondant à leur profil grâce à un quiz d'orientation dynamique et un système d'évaluation de la complétion du profil.

Le projet est composé de :
*   **Back-end** : Une API REST développée avec **FastAPI** (Python 3) et **SQLAlchemy** (base de données SQLite par défaut).
*   **Front-end** : Une interface utilisateur moderne, réactive et esthétique en HTML5, CSS3 standard et JavaScript.

---

## 🛠️ Déploiement en Local (PC)

### Prérequis
*   Avoir **Python 3** installé sur votre machine.

### Étape 1 : Configurer et démarrer le Back-end
1.  Ouvrez votre terminal et naviguez dans le dossier `back-end` :
    ```powershell
    cd back-end
    ```
2.  Installez les dépendances requises :
    ```powershell
    py -m pip install -r requirements.txt
    ```
    *(Si vous utilisez macOS/Linux, utilisez `python3 -m pip install -r requirements.txt`)*
3.  Démarrez le serveur de développement local :
    ```powershell
    py -m uvicorn main:app --port 8000 --reload
    ```
    Le serveur démarrera sur [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Étape 2 : Lancer le Front-end
Le front-end étant composé de fichiers statiques simples, vous pouvez :
*   **Option 1** : Double-cliquer directement sur le fichier `Frontend/index.html` ou `Frontend/signup.html` pour l'ouvrir dans votre navigateur.
*   **Option 2 (Recommandée)** : Servir le dossier `Frontend` à l'aide d'un serveur local pour éviter les restrictions CORS de certains navigateurs :
    - Si vous utilisez VS Code, installez l'extension **Live Server**, puis faites un clic droit sur `index.html` et choisissez **Open with Live Server**.
    - Ou lancez un serveur Python rapide depuis le dossier `Frontend` :
      ```powershell
      cd ../Frontend
      py -m http.server 3000
      ```
      Puis ouvrez [http://localhost:3000](http://localhost:3000) dans votre navigateur.

---

## ☁️ Déploiement sur Render

Render permet de déployer l'intégralité du projet (Back-end + Front-end) de manière automatisée grâce au fichier `render.yaml` (Blueprint) situé à la racine du projet.

### Étape 1 : Préparer votre dépôt Git
1.  Publiez votre code sur un dépôt Git privé ou public (GitHub ou GitLab).
2.  Assurez-vous que le fichier `render.yaml` est bien présent à la racine de votre dépôt.

### Étape 2 : Lancer le déploiement sur Render
1.  Connectez-vous à votre tableau de bord [Render.com](https://render.com).
2.  Cliquez sur le bouton **New +** en haut à droite, puis sélectionnez **Blueprint**.
3.  Connectez votre compte GitHub/GitLab et sélectionnez le dépôt contenant le code du projet Afiri.
4.  Render détectera automatiquement le fichier `render.yaml` et configurera les deux services :
    *   **afiri-api** (Service Web Python FastAPI)
    *   **afiri-frontend** (Service Statique Web)
5.  Cliquez sur **Apply** pour lancer la création et le déploiement automatique des services.

> [!IMPORTANT]
> **Base de données persistante SQLite sur Render** :
> Le fichier `render.yaml` inclut un disque persistant (`afiri-sqlite-disk`) de 1 Go pour sauvegarder les données SQLite. 
> *   *Note* : Le plan de base gratuit de Render ne supporte pas les disques persistants. Si vous utilisez le plan gratuit, votre base de données sera réinitialisée à chaque fois que le serveur s'arrête ou redémarre.
> *   *Alternative* : Pour conserver une base gratuite persistante, vous pouvez provisionner une base de données **Render PostgreSQL** (gratuite pendant 90 jours) et remplacer la variable d'environnement `DATABASE_URL` par l'URL de votre base PostgreSQL.

### Étape 3 : Configurer l'URL de l'API dans le Frontend
Une fois le back-end déployé :
1.  Copiez l'URL de votre service `afiri-api` (ex: `https://afiri-api.onrender.com`).
2.  Sur votre machine locale, modifiez le fichier `Frontend/config.js` si nécessaire, ou configurez la variable `window.AFIRI_API_URL` pour pointer vers l'URL de production de votre API.
