#!/usr/bin/env bash
# build.sh — Script de build exécuté par Render avant de démarrer le serveur.
# Render l'appelle automatiquement si tu le spécifies dans buildCommand.

# Arrête immédiatement si une commande échoue
set -o errexit

echo "==> Installation des dépendances Python..."
pip install -r requirements.txt

echo "==> Build terminé avec succès."
