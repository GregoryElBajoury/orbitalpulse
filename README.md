#  OrbitalPulse // Live ISS Telemetry Hub

> Pipeline de données et de télémétrie en temps réel de la Station Spatiale Internationale (ISS), orchestré via Kubernetes (Minikube) et visualisé à l'aide d'un dashboard Streamlit interactif (Globe 3D Plotly).

---

##  Architecture & Stack Technique

Le projet est conçu selon une approche cloud-native, conteneurisée et découplée :

* **Collecteur de Données :** Script Python interrogeant l'API officielle de l'ISS (`wheretheiss.at`), exécuté de manière éphémère et automatisée via un `CronJob` Kubernetes (un conteneur est instancié à chaque exécution planifiée pour collecter et insérer la télémétrie, puis disparaît à la fin de la tâche).
* **Stockage :** Base de données relationnelle **PostgreSQL** pour l'historisation des points de télémétrie (latitude, longitude, altitude, vitesse, visibilité, horodatage).
* **Interface & Visualisation :** Application **Streamlit** intégrée avec **Plotly** (`graph_objects`) pour un affichage sphérique en 3D (projection orthographique) avec tracé de la trajectoire orbitale récente.
* **Orchestration & DevOps :** Docker, Docker Compose (pour le développement local) et Kubernetes / Minikube (pour la production/homelab).

---

##  Arborescence du Projet

```text
orbitalpulse/
├── k8s/                        # Manifestes Kubernetes
│   ├── adminer.yaml
│   ├── collector-cronjob.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-init-configmap.yaml
│   ├── pvc.yaml
│   ├── secret.yaml
│   └── ui-deployment.yaml
├── sql/                        # Scripts d'initialisation de la BDD
├── app.py                      # Application Streamlit (UI & Globe 3D)
├── collector.py                # Script de collecte des données de l'ISS
├── Dockerfile                  # Multi-stage Dockerfile pour l'UI et le collector
├── docker-compose.yml          # Stack locale de développement
├── requirements.txt            # Dépendances Python
└── README.md
```

##  Guide de Démarrage

### Option 1 : Lancement rapide en local avec Docker Compose
Idéal pour tester rapidement l'ensemble des services sur sa machine.

1. **Configurer les variables d'environnement :**
   Duplique le fichier d'exemple et renseigne tes identifiants :

   ```bash
   cp .env.example .env
   ```

 ## 1.Lancer la stack complète :

```bash
docker compose up --build -d
```

## 2.Accéder aux services :

Dashboard Streamlit (UI) : http://localhost:8501

Adminer (Base de données) : http://localhost:8080

### Option 2 : Déploiement sur un cluster Kubernetes (Minikube)

Idéal pour reproduire un environnement de production orienté DevOps.

### Démarrer Minikube :

```bash
minikube start
```

### Appliquer tous les manifests Kubernetes du dossier k8s :
(Veillez à bien exclure les fichiers d'exemple non encodés de type secret.example.yaml)

```bash
kubectl apply -f k8s/
```

### Builder et charger l'image de l'UI dans Minikube :

```bash
docker build -t orbitalpulse-ui:latest .
minikube image load orbitalpulse-ui:latest
kubectl rollout restart deployment/orbitalpulse-ui
```

### Accéder aux interfaces web (Minikube) :

Pour ouvrir directement les interfaces graphiques dans votre navigateur :

- Afficher l'interface Adminer (Gestion de la base de données) :
Ouvrez un premier terminal et exécutez :

```bash
minikube service orbitalpulse-ui-service
```

- Afficher le Dashboard Streamlit (Interface 3D de l'ISS) :
Ouvrez un autre onglet de terminal et exécutez :

```bash
minikube service orbitalpulse-adminer-svc
```


### Fonctionnalités Clés

- Actualisation en temps réel : Utilisation de streamlit-autorefresh pour interroger périodiquement la base de données PostgreSQL sans rechargement manuel de la page.

- Visualisation Spatiale Avancée : Affichage d'un globe 3D interactif centré sur la position courante de l'ISS avec affichage de la traînée historique des derniers points relevés.

- Résilience : Gestion des tâches de collecte automatisées par Kubernetes CronJobs.


### Pistes d'Amélioration & Optimisations Futures

Gestion du rendu de l'interface : Optimisation du cycle de rafraîchissement de l'application Streamlit (gestion de la frame/redessin du globe 3D) pour fluidifier l'expérience utilisateur et éviter les micro-scintillements lors des requêtes périodiques en base de données.


