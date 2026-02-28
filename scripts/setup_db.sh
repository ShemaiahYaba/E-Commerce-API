#!/usr/bin/env bash

set -e

echo "Running database migrations..."
flask db upgrade

echo "Running category seed script..."
python scripts/seed.py

echo "Running product seed script..."
python scripts/seed_products.py

echo "Database setup complete."
