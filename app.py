# app.py
from flask import Flask, render_template, request, redirect, url_for
import os
import numpy as np
from numpy import trapz
import pandas as pd
import matplotlib.pyplot as plt
import plotly
import plotly.express as px
import json
from werkzeug.utils import secure_filename 

app = Flask(__name__)

# Configuration pour l'upload
app.config['UPLOAD_FOLDER'] = 'data'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Fonction pour charger et nettoyer les données
def load_and_clean_data(file_path, delimiter='\t', decimal=','):
    df = pd.read_csv(file_path, delimiter=delimiter, decimal=decimal, skiprows=1)
    df.columns = ['Temps', 'Déplacement', 'Force']
    df['Temps'] = pd.to_numeric(df['Temps'], errors='coerce')
    df['Déplacement'] = pd.to_numeric(df['Déplacement'], errors='coerce')
    df['Force'] = pd.to_numeric(df['Force'], errors='coerce')
    return df

# Fonctions de calcul
def calculate_stiffness(df):
    elastic_region = df.iloc[:int(0.1 * len(df))]
    stiffness = np.polyfit(elastic_region['Déplacement'], elastic_region['Force'], 1)[0]
    return stiffness

def calculate_energy_absorbed(df):
    energy_absorbed = trapz(df['Force'], df['Déplacement'])
    return energy_absorbed

def find_rupture_point(df):
    max_force = df['Force'].max()
    rupture_index = df['Force'].idxmax()
    rupture_displacement = df.iloc[rupture_index]['Déplacement']
    return max_force, rupture_displacement

# Fonction pour générer les graphiques et les résultats
def generate_plots():
    # Chemins des fichiers CSV
    carbone_file_path = os.path.join('data', 'Iso-578-carboneV2.csv')
    kevlar_file_path = os.path.join('data', 'iso-578-kevlarV2.csv')
    kevlar_cv2_file_path = os.path.join('data', 'iso-578-kevlar-CV2.csv')

    # Charger les fichiers
    df_carbone = load_and_clean_data(carbone_file_path, delimiter=';', decimal=',')
    df_kevlar = load_and_clean_data(kevlar_file_path, delimiter='\t', decimal=',')
    df_kevlar_cv2 = load_and_clean_data(kevlar_cv2_file_path, delimiter='\t', decimal=',')

    # Calculs pour chaque matériau
    carbon_stiffness = calculate_stiffness(df_carbone)
    carbon_energy_absorbed = calculate_energy_absorbed(df_carbone)
    carbon_max_force, carbon_rupture_displacement = find_rupture_point(df_carbone)

    kevlar_stiffness = calculate_stiffness(df_kevlar)
    kevlar_energy_absorbed = calculate_energy_absorbed(df_kevlar)
    kevlar_max_force, kevlar_rupture_displacement = find_rupture_point(df_kevlar)

    kevlar_cv2_stiffness = calculate_stiffness(df_kevlar_cv2)
    kevlar_cv2_energy_absorbed = calculate_energy_absorbed(df_kevlar_cv2)
    kevlar_cv2_max_force, kevlar_cv2_rupture_displacement = find_rupture_point(df_kevlar_cv2)

    # Graphique pour le Carbone avec couleur personnalisée
    fig_carbone = px.line(df_carbone, x='Déplacement', y='Force', title='Carbone', color_discrete_sequence=['#e74c3c'])
    graphJSON_carbone = json.dumps(fig_carbone, cls=plotly.utils.PlotlyJSONEncoder)

    # Graphique pour le Kevlar
    fig_kevlar = px.line(df_kevlar, x='Déplacement', y='Force', title='Kevlar', color_discrete_sequence=['#3498db'])
    graphJSON_kevlar = json.dumps(fig_kevlar, cls=plotly.utils.PlotlyJSONEncoder)

    # Graphique pour le Kevlar CV2
    fig_kevlar_cv2 = px.line(df_kevlar_cv2, x='Déplacement', y='Force', title='Kevlar CV2', color_discrete_sequence=['#2ecc71'])
    graphJSON_kevlar_cv2 = json.dumps(fig_kevlar_cv2, cls=plotly.utils.PlotlyJSONEncoder)


    # Générer les graphiques interactifs avec Plotly
    fig_carbone = px.line(df_carbone, x='Déplacement', y='Force', title='Carbone')
    graphJSON_carbone = json.dumps(fig_carbone, cls=plotly.utils.PlotlyJSONEncoder)

    fig_kevlar = px.line(df_kevlar, x='Déplacement', y='Force', title='Kevlar')
    graphJSON_kevlar = json.dumps(fig_kevlar, cls=plotly.utils.PlotlyJSONEncoder)

    fig_kevlar_cv2 = px.line(df_kevlar_cv2, x='Déplacement', y='Force', title='Kevlar CV2')
    graphJSON_kevlar_cv2 = json.dumps(fig_kevlar_cv2, cls=plotly.utils.PlotlyJSONEncoder)

    # Résultats sous forme de DataFrame
    results = {
        'Matériau': ['Carbone', 'Kevlar', 'Kevlar CV2'],
        'Raideur (kN/mm)': [carbon_stiffness, kevlar_stiffness, kevlar_cv2_stiffness],
        'Énergie Absorbée (kJ)': [carbon_energy_absorbed, kevlar_energy_absorbed, kevlar_cv2_energy_absorbed],
        'Force Maximale (kN)': [carbon_max_force, kevlar_max_force, kevlar_cv2_max_force],
        'Déplacement à la Rupture (mm)': [carbon_rupture_displacement, kevlar_rupture_displacement, kevlar_cv2_rupture_displacement]
    }

    results_df = pd.DataFrame(results)
    return results_df, graphJSON_carbone, graphJSON_kevlar, graphJSON_kevlar_cv2

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Vérifier si le fichier est présent dans la requête
        if 'file' not in request.files:
            return 'Aucun fichier sélectionné'
        file = request.files['file']
        if file.filename == '':
            return 'Aucun fichier sélectionné'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Traiter le fichier téléchargé si nécessaire
            return redirect(url_for('index'))
    results_df, graphJSON_carbone, graphJSON_kevlar, graphJSON_kevlar_cv2 = generate_plots()
    results_html = results_df.to_html(classes='table table-striped table-bordered', index=False)
    return render_template('index.html', tables=[results_html],
                           graphJSON_carbone=graphJSON_carbone,
                           graphJSON_kevlar=graphJSON_kevlar,
                           graphJSON_kevlar_cv2=graphJSON_kevlar_cv2)

if __name__ == '__main__':
    app.run(debug=True)
