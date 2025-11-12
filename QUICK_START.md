# 🚀 Démarrage Rapide - Test Local sur VM

Guide rapide pour tester l'application en local sur une VM.

## 📋 Prérequis Minimum

```bash
# Vérifier Docker
docker --version
docker-compose --version

# Si non installé (Ubuntu/Debian)
sudo apt update && sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER
# Déconnexion/reconnexion nécessaire
```

## ⚡ Démarrage Rapide (3 étapes)

### 1. Cloner et préparer

```bash
cd ~/Projet-Devops-Kubernetes

# Créer le fichier .env
cp .env.example .env
# (Optionnel: modifier les mots de passe dans .env)
```

### 2. Démarrer avec Docker Compose

```bash
# Méthode 1: Script automatique
./scripts/start-local.sh

# Méthode 2: Commande manuelle
docker-compose up -d --build
```

### 3. Tester l'API

```bash
# Vérifier la santé
curl http://localhost:5000/health

# Voir la documentation
curl http://localhost:5000/docs

# Tester avec le script
./test-api.sh
```

## 🌐 Accès aux Services

- **API**: http://localhost:5000
- **Documentation**: http://localhost:5000/docs
- **Health**: http://localhost:5000/health
- **PGAdmin**: http://localhost:8082
  - Email: `admin@admin.com`
  - Password: `admin123`

## 🧪 Tests Rapides

```bash
# 1. Créer un utilisateur
curl -X POST "http://localhost:5000/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "test123"}'

# 2. Lister les utilisateurs
curl http://localhost:5000/users/

# 3. Compter les utilisateurs
curl http://localhost:5000/users/count
```

## 🔍 Vérification

```bash
# Vérifier les containers
docker-compose ps

# Voir les logs
docker-compose logs -f fastapi

# Arrêter les services
docker-compose down
```

## 📚 Documentation Complète

Pour plus de détails, voir [GUIDE_TEST_LOCAL.md](GUIDE_TEST_LOCAL.md)

## 🐛 Problèmes Courants

### Port déjà utilisé
```bash
# Trouver le processus
sudo lsof -i :5000
# Tuer le processus ou changer le port dans docker-compose.yml
```

### Erreur de connexion DB
```bash
# Vérifier les logs
docker-compose logs db
# Vérifier que PostgreSQL est démarré
docker-compose ps db
```

### Permission Docker
```bash
sudo usermod -aG docker $USER
newgrp docker
```

## 🎯 Prochaines Étapes

1. ✅ Tester localement (vous êtes ici)
2. ⏭️ Tester sur Kubernetes local (minikube/kind)
3. ⏭️ Déployer sur EKS
4. ⏭️ Configurer CI/CD

