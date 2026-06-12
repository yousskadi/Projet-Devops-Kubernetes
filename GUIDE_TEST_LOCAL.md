# Guide de Test Local sur VM

Ce guide vous explique comment tester l'application FastAPI en local sur une VM.

## 📋 Prérequis

### Sur la VM

1. **Docker et Docker Compose**
```bash
# Vérifier l'installation
docker --version
docker-compose --version

# Si non installé (Ubuntu/Debian)
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Déconnexion/reconnexion nécessaire après usermod
```

2. **Git** (pour cloner le projet)
```bash
sudo apt install -y git
```

3. **Curl** (pour tester les endpoints)
```bash
sudo apt install -y curl
```

## 🚀 Méthode 1 : Test avec Docker Compose (Recommandé)

### Étape 1 : Cloner et préparer le projet

```bash
# Cloner le repository
git clone <votre-repo-url>
cd Projet-Devops-Kubernetes

# Ou si déjà cloné, aller dans le répertoire
cd ~/Projet-Devops-Kubernetes
```

### Étape 2 : Créer le fichier .env

```bash
# Créer le fichier .env
cat > .env << 'EOF'
# Database Configuration
DB_HOST=db
DB_PORT=5432
DB_NAME=storedb
DB_USER=admin
DB_PASSWORD=password123

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=5000
API_RELOAD=false

# Security
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
DEBUG=true

# PostgreSQL
POSTGRES_USER=admin
POSTGRES_PASSWORD=password123
POSTGRES_DB=storedb

# PGAdmin
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin123

# CORS
CORS_ORIGINS=*
EOF
```

### Étape 3 : Lancer les services

```bash
# Construire et lancer les containers
docker-compose up -d --build

# Vérifier que les containers sont en cours d'exécution
docker-compose ps

# Vérifier les logs
docker-compose logs -f fastapi
```

### Étape 4 : Vérifier que les services sont prêts

```bash
# Attendre quelques secondes que les services démarrent
sleep 10

# Vérifier la santé de l'API
curl http://localhost:5000/health

# Vérifier le endpoint root
curl http://localhost:5000/

# Vérifier la documentation
curl http://localhost:5000/docs
```

### Étape 5 : Tester les endpoints API

```bash
# 1. Créer un utilisateur
curl -X POST "http://localhost:5000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "password": "securepassword123"
  }'

# 2. Récupérer tous les utilisateurs
curl http://localhost:5000/users/

# 3. Récupérer un utilisateur par ID (remplacer 1 par l'ID réel)
curl http://localhost:5000/users/1

# 4. Compter les utilisateurs
curl http://localhost:5000/users/count

# 5. Mettre à jour un utilisateur
curl -X PUT "http://localhost:5000/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Updated",
    "email": "john.updated@example.com",
    "password": "newpassword123"
  }'

# 6. Supprimer un utilisateur
curl -X DELETE "http://localhost:5000/users/1"
```

### Étape 6 : Accéder à l'interface web

```bash
# Sur la VM, ouvrir dans un navigateur (si GUI disponible)
# Sinon, depuis votre machine locale, utiliser le port forwarding SSH

# API Documentation
http://localhost:5000/docs

# PGAdmin
http://localhost:8082
# Email: admin@admin.com
# Password: admin123
```

### Étape 7 : Vérifier les logs

```bash
# Logs de FastAPI
docker-compose logs fastapi

# Logs de PostgreSQL
docker-compose logs db

# Logs de tous les services
docker-compose logs

# Suivre les logs en temps réel
docker-compose logs -f
```

### Étape 8 : Arrêter les services

```bash
# Arrêter les services
docker-compose down

# Arrêter et supprimer les volumes (⚠️ supprime les données)
docker-compose down -v
```

## 🐍 Méthode 2 : Test avec Python directement

### Étape 1 : Installer Python et les dépendances

```bash
# Installer Python 3.11
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip

# Créer un environnement virtuel
python3.11 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### Étape 2 : Démarrer PostgreSQL avec Docker

```bash
# Lancer seulement PostgreSQL
docker run -d \
  --name postgres-test \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password123 \
  -e POSTGRES_DB=storedb \
  -p 5432:5432 \
  postgres:15-alpine

# Attendre que PostgreSQL soit prêt
sleep 5
```

### Étape 3 : Configurer les variables d'environnement

```bash
# Créer le fichier .env
cat > .env << 'EOF'
DB_HOST=localhost
DB_PORT=5432
DB_NAME=storedb
DB_USER=admin
DB_PASSWORD=password123
API_HOST=0.0.0.0
API_PORT=5000
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=*
EOF
```

### Étape 4 : Lancer l'application

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer l'application
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

### Étape 5 : Tester l'application

```bash
# Dans un autre terminal
curl http://localhost:5000/health
curl http://localhost:5000/
```

## 🧪 Méthode 3 : Tests unitaires

### Étape 1 : Installer les dépendances de test

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances (déjà incluses dans requirements.txt)
pip install -r requirements.txt
```

### Étape 2 : Lancer les tests

```bash
# Tous les tests
pytest tests/ -v

# Tests avec coverage
pytest tests/ -v --cov=. --cov-report=html

# Tests spécifiques
pytest tests/test_users.py -v

# Voir le rapport de coverage
# Ouvrir htmlcov/index.html dans un navigateur
```

## 🔍 Vérifications et Dépannage

### Vérifier que les ports sont disponibles

```bash
# Vérifier les ports utilisés
sudo netstat -tulpn | grep -E '5000|5432|8082'

# Ou avec ss
sudo ss -tulpn | grep -E '5000|5432|8082'
```

### Vérifier les containers Docker

```bash
# Lister les containers
docker ps -a

# Vérifier les logs d'un container
docker logs <container-name>

# Vérifier les ressources utilisées
docker stats
```

### Problèmes courants

#### 1. Port déjà utilisé

```bash
# Trouver le processus utilisant le port
sudo lsof -i :5000

# Tuer le processus
sudo kill -9 <PID>

# Ou changer le port dans docker-compose.yml
```

#### 2. Erreur de connexion à la base de données

```bash
# Vérifier que PostgreSQL est démarré
docker-compose ps db

# Vérifier les logs
docker-compose logs db

# Vérifier la connexion
docker-compose exec db psql -U admin -d storedb -c "SELECT 1;"
```

#### 3. Erreur de permissions Docker

```bash
# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER

# Déconnexion/reconnexion nécessaire
newgrp docker
```

#### 4. Erreur "Module not found"

```bash
# Vérifier que l'environnement virtuel est activé
which python
# Doit afficher le chemin vers venv/bin/python

# Réinstaller les dépendances
pip install -r requirements.txt
```

## 📊 Script de test automatisé

Créez un script de test simple :

```bash
# Créer le script
cat > test-api.sh << 'EOF'
#!/bin/bash

API_URL="http://localhost:5000"

echo "🔍 Test de l'API FastAPI"
echo "========================"
echo ""

# Test healthcheck
echo "1. Test healthcheck..."
curl -s "$API_URL/health" | jq '.' || echo "❌ Healthcheck failed"
echo ""

# Test root
echo "2. Test root endpoint..."
curl -s "$API_URL/" | jq '.' || echo "❌ Root endpoint failed"
echo ""

# Test création d'utilisateur
echo "3. Test création d'utilisateur..."
USER_RESPONSE=$(curl -s -X POST "$API_URL/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "testpassword123"
  }')
echo "$USER_RESPONSE" | jq '.' || echo "$USER_RESPONSE"
USER_ID=$(echo "$USER_RESPONSE" | jq -r '.id')
echo ""

# Test récupération des utilisateurs
echo "4. Test récupération des utilisateurs..."
curl -s "$API_URL/users/" | jq '.' || echo "❌ Get users failed"
echo ""

# Test récupération d'un utilisateur
echo "5. Test récupération d'un utilisateur..."
curl -s "$API_URL/users/$USER_ID" | jq '.' || echo "❌ Get user failed"
echo ""

# Test comptage
echo "6. Test comptage..."
curl -s "$API_URL/users/count" | jq '.' || echo "❌ Count failed"
echo ""

echo "✅ Tests terminés"
EOF

# Rendre le script exécutable
chmod +x test-api.sh

# Installer jq pour le formatage JSON (optionnel)
sudo apt install -y jq

# Exécuter le script
./test-api.sh
```

## 🌐 Accès depuis votre machine locale

Si vous testez sur une VM distante, vous pouvez utiliser le port forwarding SSH :

```bash
# Depuis votre machine locale
ssh -L 5000:localhost:5000 -L 8082:localhost:8082 user@vm-ip

# Puis accéder à l'API depuis votre navigateur local
# http://localhost:5000/docs
# http://localhost:8082 (PGAdmin)
```

## 📝 Checklist de test

- [ ] Docker et Docker Compose installés
- [ ] Fichier .env créé
- [ ] Services Docker démarrés
- [ ] Healthcheck endpoint répond
- [ ] Documentation accessible
- [ ] Création d'utilisateur fonctionne
- [ ] Récupération des utilisateurs fonctionne
- [ ] Mise à jour d'utilisateur fonctionne
- [ ] Suppression d'utilisateur fonctionne
- [ ] PGAdmin accessible
- [ ] Tests unitaires passent

## 🎯 Prochaines étapes

Une fois les tests locaux réussis, vous pouvez :

1. **Tester sur Kubernetes local** (minikube, kind, k3s)
2. **Déployer sur EKS** (AWS)
3. **Configurer CI/CD** (GitHub Actions)
4. **Ajouter l'observabilité** (Prometheus, Grafana)

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

