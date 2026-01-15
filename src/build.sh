#!/usr/bin/env bash
# Salir si hay error
set -o errexit

# Se instalan dependencias
pip install -r requirements.txt

# Se recopilan archivos estáticos (CSS/JS)
python src/manage.py collectstatic --no-input

# Se aplican migraciones de la base de datos
python src/manage.py migrate