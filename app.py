# app.py
from flask import Flask, render_template
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

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

# Fonction pour calculer l'énergie absorbée
def calculate_energy_absorbed(df, displacement_col='Déplacement', force_col='Force'):
    energy_absorbed = np.trapz(df[force_col], df[displacement_col])
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

    # Générer les graphiques
    if not os.path.exists('static/images'):
        os.makedirs('static/images')

    plt.figure()
    plt.plot(df_carbone['Déplacement'], df_carbone['Force'], label='Carbone')
    plt.xlabel('Déplacement (mm)')
    plt.ylabel('Force (kN)')
    plt.title('Courbe Force-Déplacement pour le Carbone')
    plt.legend()
    plt.savefig('static/images/carbone.png')
    plt.close()

    plt.figure()
    plt.plot(df_kevlar['Déplacement'], df_kevlar['Force'], label='Kevlar', color='orange')
    plt.xlabel('Déplacement (mm)')
    plt.ylabel('Force (kN)')
    plt.title('Courbe Force-Déplacement pour le Kevlar')
    plt.legend()
    plt.savefig('static/images/kevlar.png')
    plt.close()

    plt.figure()
    plt.plot(df_kevlar_cv2['Déplacement'], df_kevlar_cv2['Force'], label='Kevlar CV2', color='green')
    plt.xlabel('Déplacement (mm)')
    plt.ylabel('Force (kN)')
    plt.title('Courbe Force-Déplacement pour le Kevlar CV2')
    plt.legend()
    plt.savefig('static/images/kevlar_cv2.png')
    plt.close()

    # Résultats sous forme de DataFrame
    results = {
        'Matériau': ['Carbone', 'Kevlar', 'Kevlar CV2'],
        'Raideur (kN/mm)': [carbon_stiffness, kevlar_stiffness, kevlar_cv2_stiffness],
        'Énergie Absorbée (kJ)': [carbon_energy_absorbed, kevlar_energy_absorbed, kevlar_cv2_energy_absorbed],
        'Force Maximale (kN)': [carbon_max_force, kevlar_max_force, kevlar_cv2_max_force],
        'Déplacement à la Rupture (mm)': [carbon_rupture_displacement, kevlar_rupture_displacement, kevlar_cv2_rupture_displacement]
    }

    results_df = pd.DataFrame(results)
    return results_df

@app.route('/')
def index():
    results_df = generate_plots()
    results_html = results_df.to_html(classes='table table-striped', index=False)
    return render_template('index.html', tables=[results_html])

if __name__ == '__main__':
    app.run(debug=True)
