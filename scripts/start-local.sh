#!/bin/bash

# Script pour démarrer l'application localement avec Docker Compose

set -e

echo "🚀 Démarrage de l'application FastAPI localement..."
echo ""

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier que Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier si le fichier .env existe
if [ ! -f .env ]; then
    echo "⚠️  Le fichier .env n'existe pas. Création d'un fichier .env par défaut..."
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
    echo "✅ Fichier .env créé avec les valeurs par défaut."
    echo "⚠️  Veuillez modifier les mots de passe en production!"
    echo ""
fi

# Arrêter les services existants
echo "🛑 Arrêt des services existants..."
docker-compose down 2>/dev/null || true

# Construire et lancer les services
echo "🏗️  Construction des images Docker..."
docker-compose build

echo "🚀 Démarrage des services..."
docker-compose up -d

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 10

# Vérifier la santé de l'API
echo "🔍 Vérification de la santé de l'API..."
max_attempts=30
attempt=0

# Vérifier si curl est disponible
if command -v curl &> /dev/null; then
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:5000/health > /dev/null 2>&1; then
            echo "✅ L'API est prête!"
            break
        fi
        attempt=$((attempt + 1))
        if [ $((attempt % 5)) -eq 0 ]; then
            echo "   Tentative $attempt/$max_attempts..."
        fi
        sleep 2
    done

    if [ $attempt -eq $max_attempts ]; then
        echo "⚠️  L'API n'est pas prête après $max_attempts tentatives."
        echo "📋 Vérifiez les logs avec: docker-compose logs fastapi"
        echo "   Les services peuvent être en cours de démarrage."
    fi
else
    echo "⚠️  curl n'est pas installé. Impossible de vérifier la santé de l'API."
    echo "   Installer curl: sudo apt install -y curl"
    echo "   Ou vérifier manuellement: docker-compose logs fastapi"
fi

# Afficher les informations
echo ""
echo "=========================================="
echo "✅ Application démarrée!"
echo "=========================================="
echo ""
echo "📍 Endpoints disponibles:"
echo "   - API: http://localhost:5000"
echo "   - Documentation: http://localhost:5000/docs"
echo "   - Health: http://localhost:5000/health"
echo "   - PGAdmin: http://localhost:8082"
echo ""
echo "🔑 Identifiants PGAdmin:"
echo "   - Email: admin@admin.com"
echo "   - Password: admin123"
echo ""
echo "📋 Commandes utiles:"
echo "   - Voir les logs: docker-compose logs -f"
echo "   - Arrêter: docker-compose down"
echo "   - Tester l'API: ./test-api.sh"
echo ""
echo "🧪 Pour tester l'API:"
echo "   curl http://localhost:5000/health"
echo ""
