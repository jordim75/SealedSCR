from flask import Flask, render_template, jsonify, Response, send_file
import pandas as pd
import random, io
from openpyxl import Workbook

app = Flask(__name__)

# Carregar les cartes des del CSV
cartes_df = pd.read_csv("FontBeta.csv")
cartes_df_AL = pd.read_csv("FontAL.csv")

# Separar cartes segons tipus
cartes_per_tipus = {
    "Ordinary": cartes_df[cartes_df["tipus"] == "Ordinary"].to_dict(orient="records"),
    "Booster": cartes_df[cartes_df["tipus"] == "Booster"].to_dict(orient="records"),
    "BoosterAvatar": cartes_df[cartes_df["tipus"] == "BoosterAvatar"].to_dict(orient="records"),
    "Exceptional": cartes_df[cartes_df["tipus"] == "Exceptional"].to_dict(orient="records"),
    "Elite": cartes_df[cartes_df["tipus"] == "Elite"].to_dict(orient="records"),
    "Unique": cartes_df[cartes_df["tipus"] == "Unique"].to_dict(orient="records"),
}

def generar_sobre_Beta():
    sobre = []

    
    # 3 Exceptional
    sobre.extend(random.sample(cartes_per_tipus["Exceptional"], 3))

    # 1 Elite o Unique
    if random.random() < 0.76:  # 76% Elite
        sobre.append(random.choice(cartes_per_tipus["Elite"]))
    else:  # 24% Unique
        sobre.append(random.choice(cartes_per_tipus["Unique"]))
        
    # 10 Ordinary
    sobre.extend(random.sample(cartes_per_tipus["Ordinary"], 10))

    # 1 BoosterAvatar or BoosterSite
    if random.random() < 0.05:  # 10% BoosterAvatarElite
        sobre.append(random.choice(cartes_per_tipus["BoosterAvatar"]))
    else:  # 24% Unique
        sobre.append(random.choice(cartes_per_tipus["Booster"]))
    return sobre
    
def generar_sobre_AL(cartes):
    """
    Genera un sobre de tipus 2:
      - 11 Ordinary
      - 3 Exceptional
      - 1 Elite o Unique (81.25% Elite, 18.75% Unique)
    """
    sobre = []

    # 11 Ordinary
    ordinary = [c for c in cartes if c["tipus"] == "Ordinary"]
    sobre.extend(random.sample(ordinary, 11))

    # 3 Exceptional
    exceptional = [c for c in cartes if c["tipus"] == "Exceptional"]
    sobre.extend(random.sample(exceptional, 3))

    # 1 Elite o Unique amb probabilitat
    if random.random() < 0.8125:  # 81.25% Elite
        elite = [c for c in cartes if c["tipus"] == "Elite"]
        sobre.append(random.choice(elite))
    else:  # 18.75% Unique
        unique = [c for c in cartes if c["tipus"] == "Unique"]
        sobre.append(random.choice(unique))

    return sobre

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/Pack/<int:n>")
def sobres(n):
    return jsonify([generar_sobre() for _ in range(n)])

@app.route("/export_xlsx/<int:jocs>/<int:sobres>")
def export_xlsx(jocs, sobres):
    wb = Workbook()
    # Prioritat dels elements
    elem_order = {"DB": 0, "Air": 1, "Earth": 2, "Fire": 3, "Water": 4}

    for jugador in range(1, jocs+1):
        # Crear full per cada jugador
        if jugador == 1:
            ws = wb.active
            ws.title = f"Jugador {jugador}"
        else:
            ws = wb.create_sheet(title=f"Jugador {jugador}")

        # Capsaleres
        ws.append(["Avatars", "Spells", "Sites"])

        cartes_jugador = []
        for _ in range(n1):
            cartes_jugador.extend(generar_sobre_Beta())
        for _ in range(n2):
            cartes_jugador.extend(generar_sobre_AL())

        # Filtrar per categoria
        avatars = sorted([c["nom"] for c in cartes_jugador if c["cat"] == "Avatar"])
        spells  = [c for c in cartes_jugador if c["cat"] == "Spell"]
        sites   = sorted([c["nom"] for c in cartes_jugador if c["cat"] == "Site"])

        # Ordenar Spells per element i nom
        spells_sorted = sorted(
            spells,
            key=lambda c: (elem_order.get(c["elem"], 99), c["nom"])
        )
        # Només noms amb element entre claudàtors
        spells_names = [f"{c['nom']}" for c in spells_sorted]

        # Trobar la longitud màxima de les columnes
        max_len = max(len(avatars), len(spells_names), len(sites))

        # Afegir les files
        for i in range(max_len):
            fila = [
                avatars[i] if i < len(avatars) else "",
                spells_names[i] if i < len(spells_names) else "",
                sites[i] if i < len(sites) else "",
            ]
            ws.append(fila)

    # Guardar a memòria i retornar com a fitxer
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="lots_jugadors.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    app.run(debug=True)
