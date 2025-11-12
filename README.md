# Projet DevOps Kubernetes - API FastAPI

Projet Fil Rouge Bootcamp DEVOPS 2023 - Application de gestion d'utilisateurs avec FastAPI, PostgreSQL et Kubernetes.

## 🎯 Description

Ce projet déploie une API REST FastAPI pour la gestion d'utilisateurs, avec les services suivants:

- **FastAPI**: Application backend Python pour la gestion des utilisateurs
- **PostgreSQL**: Base de données relationnelle
- **PGAdmin**: Interface d'administration pour PostgreSQL
- **Kubernetes**: Déploiement sur Amazon EKS avec Helm

## 🚀 Fonctionnalités

- ✅ CRUD complet pour les utilisateurs
- ✅ Hashage sécurisé des mots de passe (bcrypt)
- ✅ Validation d'email
- ✅ Gestion d'erreurs HTTP complète
- ✅ Healthcheck endpoint
- ✅ Documentation OpenAPI automatique
- ✅ Tests unitaires
- ✅ CI/CD automatisé
- ✅ Observabilité (Prometheus)

## 📋 Prérequis

- Python 3.11+
- Docker & Docker Compose
- Kubernetes cluster (EKS)
- Helm 3.x
- kubectl

## 🛠️ Installation

### Démarrage Rapide sur VM

**⚠️ Pour tester rapidement sur une VM, voir [QUICK_START.md](QUICK_START.md)**

### Développement Local

1. **Cloner le repository**
```bash
git clone <repository-url>
cd Projet-Devops-Kubernetes
```

2. **Créer un fichier .env**
```bash
cp .env.example .env
# Éditer .env avec vos valeurs (optionnel pour le développement)
```

3. **Démarrer avec Docker Compose** (Méthode recommandée)
```bash
# Option 1: Script automatique
./scripts/start-local.sh

# Option 2: Commande manuelle
docker-compose up -d --build
```

4. **Tester l'API**
```bash
# Vérifier la santé
curl http://localhost:5000/health

# Script de test automatisé
./test-api.sh

# Ou accéder à la documentation
# http://localhost:5000/docs
```

5. **Accéder aux services**
- API: http://localhost:5000
- Documentation: http://localhost:5000/docs
- PGAdmin: http://localhost:8082
  - Email: `admin@admin.com`
  - Password: `admin123`

### Installation Manuelle (sans Docker)

1. **Installer les dépendances**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Démarrer PostgreSQL avec Docker**
```bash
docker run -d --name postgres-test \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password123 \
  -e POSTGRES_DB=storedb \
  -p 5432:5432 \
  postgres:15-alpine
```

3. **Lancer l'application**
```bash
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

### Déploiement Kubernetes

1. **Configurer kubectl**
```bash
aws eks update-kubeconfig --name <cluster-name> --region eu-west-3
```

2. **Installer les dépendances Helm**
```bash
# Ingress Controller
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace

# Cert-Manager
helm upgrade --install cert-manager cert-manager \
  --repo https://charts.jetstack.io \
  --create-namespace --namespace cert-manager \
  --set installCRDs=true

# Prometheus Stack
helm upgrade --install kube-prometheus-stack kube-prometheus-stack \
  --namespace kube-prometheus-stack --create-namespace \
  --repo https://prometheus-community.github.io/helm-charts
```

3. **Déployer l'application**
```bash
# Développement
helm upgrade --install myapp-release-dev myapp1/ \
  --values myapp1/values.yaml \
  -f myapp1/values-dev.yaml \
  -n dev --create-namespace

# Production
helm upgrade --install myapp-release-prod myapp1/ \
  --values myapp1/values.yaml \
  -f myapp1/values-prod.yaml \
  -n prod --create-namespace
```

## 🧪 Tests

```bash
# Lancer tous les tests
pytest tests/ -v

# Tests avec coverage
pytest tests/ -v --cov=. --cov-report=html

# Tests spécifiques
pytest tests/test_users.py -v
```

## 🔒 Sécurité

### Secrets Management

- **Local**: Utiliser `.env` (ne pas committer)
- **Kubernetes**: Utiliser Secrets (migrer vers External Secrets Operator)
- **CI/CD**: Utiliser GitHub Secrets

### Bonnes Pratiques

- ✅ Mots de passe hashés avec bcrypt
- ✅ Secrets externalisés
- ✅ Authentification PostgreSQL activée
- ✅ Utilisateur non-root dans Docker
- ✅ NetworkPolicies configurées
- ✅ Resource limits définis

## 📊 Observabilité

### Métriques Prometheus

Les métriques sont exposées sur `/metrics`:
- `http_requests_total`: Nombre total de requêtes HTTP
- `http_request_duration_seconds`: Durée des requêtes HTTP
- `db_connections_active`: Connexions actives à la DB
- `users_total`: Nombre total d'utilisateurs

### Logs

Les logs sont structurés et incluent:
- Timestamp
- Niveau de log
- Message
- Contexte (méthode HTTP, endpoint, etc.)

## 🔄 CI/CD

### GitHub Actions

Le workflow CI/CD inclut:
1. **Lint**: Vérification du code avec Ruff, Black, MyPy
2. **Test**: Exécution des tests unitaires
3. **Security Scan**: Scan avec Trivy
4. **Build**: Construction de l'image Docker
5. **Deploy**: Déploiement sur EKS (dev/prod)

### Jenkins

Le Jenkinsfile existant peut être amélioré pour:
- Utiliser des variables au lieu de chemins hardcodés
- Ajouter des stages de test
- Ajouter un scan de sécurité
- Améliorer la gestion des erreurs

## 📝 Migrations de Base de Données

```bash
# Créer une nouvelle migration
alembic revision --autogenerate -m "Description de la migration"

# Appliquer les migrations
alembic upgrade head

# Revenir en arrière
alembic downgrade -1
```

## 🏗️ Architecture

```
┌─────────────────┐
│   FastAPI App   │
│   (Port 5000)   │
└────────┬────────┘
         │
         │ SQL
         │
┌────────▼────────┐
│   PostgreSQL    │
│   (Port 5432)   │
└─────────────────┘

┌─────────────────┐
│    PGAdmin      │
│   (Port 8082)   │
└─────────────────┘
```

## 📚 Documentation

- [QUICK_START.md](QUICK_START.md) - 🚀 Guide de démarrage rapide pour tester localement
- [GUIDE_TEST_LOCAL.md](GUIDE_TEST_LOCAL.md) - 📖 Guide complet pour tester sur une VM
- [REVIEW_ANALYSIS.md](REVIEW_ANALYSIS.md) - Analyse détaillée du projet
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Guide d'implémentation
- [SUMMARY.md](SUMMARY.md) - Résumé des améliorations
- [API Documentation](http://localhost:5000/docs) - Documentation OpenAPI (une fois l'API démarrée)

## 🔧 Configuration

### Variables d'Environnement

Voir `.env.example` pour la liste complète des variables d'environnement.

### Helm Values

- `values.yaml` - Valeurs par défaut
- `values-dev.yaml` - Valeurs pour l'environnement de développement
- `values-prod.yaml` - Valeurs pour l'environnement de production
- `values-staging.yaml` - Valeurs pour l'environnement de staging

## 🐛 Dépannage

### Problèmes Courants

1. **Erreur de connexion à la base de données**
   - Vérifier que PostgreSQL est démarré
   - Vérifier les variables d'environnement
   - Vérifier les credentials

2. **Erreur de permissions Docker**
   - Vérifier que l'utilisateur non-root est configuré
   - Vérifier les permissions du volume

3. **Erreur de déploiement Kubernetes**
   - Vérifier les secrets Kubernetes
   - Vérifier les resource limits
   - Vérifier les healthchecks

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

## 👥 Auteurs

- **Youssef Kadi** - Développement initial
- **Équipe DevOps** - Améliorations et revue

## 🔗 Liens Utiles

- [EKS Configuration Terraform](https://github.com/yousskadi/EKS-Config-terraform)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)

## 📊 Améliorations Apportées

Ce projet a été entièrement revu et amélioré avec:

- ✅ **50+ améliorations** de sécurité, performance et maintenabilité
- ✅ **Tests unitaires** avec pytest
- ✅ **CI/CD automatisé** avec GitHub Actions
- ✅ **Observabilité** avec Prometheus
- ✅ **Sécurité renforcée** (bcrypt, secrets externalisés, non-root)
- ✅ **Documentation complète**

Voir [SUMMARY.md](SUMMARY.md) pour plus de détails.

## 🎯 Prochaines Étapes

- [ ] Implémenter l'authentification JWT
- [ ] Ajouter des tests d'intégration
- [ ] Configurer ServiceMonitor pour Prometheus
- [ ] Migrer vers External Secrets Operator
- [ ] Créer des dashboards Grafana
- [ ] Ajouter HPA (Horizontal Pod Autoscaler)
- [ ] Ajouter PodDisruptionBudgets
