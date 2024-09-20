#!/bin/bash

# Installer les dépendances Python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Installer les dépendances Node.js
npm install
