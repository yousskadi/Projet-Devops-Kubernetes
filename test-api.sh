#!/bin/bash

# Script de test automatique pour l'API FastAPI
# Usage: ./test-api.sh [API_URL]
#
# Prérequis: curl et jq (optionnel pour le formatage JSON)
# Installer jq: sudo apt install -y jq

API_URL="${1:-http://localhost:5000}"

# Vérifier que curl est installé
if ! command -v curl &> /dev/null; then
    echo "❌ curl n'est pas installé. Veuillez l'installer:"
    echo "   sudo apt install -y curl"
    exit 1
fi

# Couleurs pour l'output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Test de l'API FastAPI"
echo "========================"
echo "API URL: $API_URL"
echo ""

# Fonction pour tester un endpoint
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    
    echo -n "Test: $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$url")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✅ OK (HTTP $http_code)${NC}"
        if [ -n "$body" ] && [ "$body" != "null" ]; then
            # Essayer de formater avec jq si disponible, sinon afficher tel quel
            if command -v jq &> /dev/null; then
                echo "$body" | jq '.' 2>/dev/null || echo "$body"
            else
                echo "$body"
            fi
        fi
        return 0
    else
        echo -e "${RED}❌ FAILED (HTTP $http_code)${NC}"
        echo "$body"
        return 1
    fi
    echo ""
}

# Test 1: Healthcheck
echo "1. Test healthcheck..."
test_endpoint "Healthcheck" "GET" "$API_URL/health"
echo ""

# Test 2: Root endpoint
echo "2. Test root endpoint..."
test_endpoint "Root" "GET" "$API_URL/"
echo ""


# Test 3: Création d'utilisateur
echo "3. Test création d'utilisateur..."

# Générer un email unique pour éviter les conflits
TIMESTAMP=$(date +%s)
USER_EMAIL="test${TIMESTAMP}@example.com"

USER_DATA=$(cat <<EOF
{
    "name": "User${TIMESTAMP}",
    "email": "${USER_EMAIL}",
    "password": "testpassword123"
}
EOF
)

# Envoyer la requête POST
USER_RESPONSE=$(curl -s -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "$USER_DATA")

USER_HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/users/" \
    -H "Content-Type: application/json" \
    -d "$USER_DATA")

# Gérer la réponse
if [ "$USER_HTTP_CODE" -ge 200 ] && [ "$USER_HTTP_CODE" -lt 300 ]; then
    echo -e "${GREEN}✅ OK (HTTP $USER_HTTP_CODE)${NC}"
elif [ "$USER_HTTP_CODE" -eq 409 ]; then
    echo -e "${YELLOW}⚠️ Utilisateur existe déjà (HTTP 409)${NC}"
else
    echo -e "${RED}❌ FAILED (HTTP $USER_HTTP_CODE)${NC}"
    echo "$USER_RESPONSE"
fi

# Récupérer l'ID de l'utilisateur pour les tests suivants
if command -v jq &> /dev/null; then
    USER_ID=$(echo "$USER_RESPONSE" | jq -r '.id' 2>/dev/null)
else
    USER_ID=$(echo "$USER_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
fi

# Fallback si l'ID est vide
if [ -z "$USER_ID" ] || [ "$USER_ID" = "null" ]; then
    USER_ID=1
fi

echo "Utilisateur ID utilisé pour tests suivants: $USER_ID"
echo ""


# Test 4: Récupération des utilisateurs
echo "4. Test récupération des utilisateurs..."
test_endpoint "Get Users" "GET" "$API_URL/users/"
echo ""

# Test 5: Récupération d'un utilisateur
echo "5. Test récupération d'un utilisateur (ID: $USER_ID)..."
test_endpoint "Get User" "GET" "$API_URL/users/$USER_ID"
echo ""

# Test 6: Comptage
echo "6. Test comptage..."
test_endpoint "Count Users" "GET" "$API_URL/users/count"
echo ""

# Test 7: Mise à jour d'utilisateur
echo "7. Test mise à jour d'utilisateur..."
UPDATE_DATA='{
    "name": "Updated User",
    "email": "updated@example.com",
    "password": "newpassword123"
}'
test_endpoint "Update User" "PUT" "$API_URL/users/$USER_ID" "$UPDATE_DATA"
echo ""

# Test 8: Suppression d'utilisateur
echo "8. Test suppression d'utilisateur..."
DELETE_HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$API_URL/users/$USER_ID")
if [ "$DELETE_HTTP_CODE" -eq 204 ] || [ "$DELETE_HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✅ OK (HTTP $DELETE_HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ FAILED (HTTP $DELETE_HTTP_CODE)${NC}"
fi
echo ""

# Test 9: Vérifier que l'utilisateur est supprimé
echo "9. Vérification que l'utilisateur est supprimé..."
GET_AFTER_DELETE_HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/users/$USER_ID")
if [ "$GET_AFTER_DELETE_HTTP_CODE" -eq 404 ]; then
    echo -e "${GREEN}✅ OK (HTTP 404 - User not found)${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING (HTTP $GET_AFTER_DELETE_HTTP_CODE)${NC}"
fi
echo ""

echo "========================"
echo "✅ Tests terminés"
echo ""
echo "Pour voir la documentation interactive:"
echo "  $API_URL/docs"
echo ""
echo "Pour accéder à PGAdmin:"
echo "  http://localhost:8082"

