from flask import Flask, render_template, jsonify, Response, send_file
import pandas as pd
import random, io
from openpyxl import Workbook

app = Flask(__name__)

# Carregar les cartes des del CSV
cartes_dfBeta = pd.read_csv("FontBeta.csv")
cartes_dfAL = pd.read_csv("FontAL.csv")

# Separar cartes segons tipus
cartes_Beta = {
    "Ordinary": cartes_dfBeta[cartes_dfBeta["tipus"] == "Ordinary"].to_dict(orient="records"),
    "Booster": cartes_dfBeta[cartes_dfBeta["tipus"] == "Booster"].to_dict(orient="records"),
    "BoosterAvatar": cartes_dfBeta[cartes_dfBeta["tipus"] == "BoosterAvatar"].to_dict(orient="records"),
    "Exceptional": cartes_dfBeta[cartes_dfBeta["tipus"] == "Exceptional"].to_dict(orient="records"),
    "Elite": cartes_dfBeta[cartes_dfBeta["tipus"] == "Elite"].to_dict(orient="records"),
    "Unique": cartes_dfBeta[cartes_dfBeta["tipus"] == "Unique"].to_dict(orient="records"),
}
cartes_AL = {
    "Ordinary": cartes_dfAL[cartes_dfAL["tipus"] == "Ordinary"].to_dict(orient="records"),
    "Exceptional": cartes_dfAL[cartes_dfAL["tipus"] == "Exceptional"].to_dict(orient="records"),
    "Elite": cartes_dfAL[cartes_dfAL["tipus"] == "Elite"].to_dict(orient="records"),
    "Unique": cartes_dfAL[cartes_dfAL["tipus"] == "Unique"].to_dict(orient="records"),
}

def generar_sobre_Beta():
    sobre = []
    
    # 3 Exceptional
    sobre.extend(random.sample(cartes_Beta["Exceptional"], 3))
    # 1 Elite o Unique
    if random.random() < 0.76:  # 76% Elite
        sobre.append(random.choice(cartes_Beta["Elite"]))
    else:  # 24% Unique
        sobre.append(random.choice(cartes_Beta["Unique"]))
    # 10 Ordinary
    sobre.extend(random.sample(cartes_Beta["Ordinary"], 10))
    # 1 BoosterAvatar or BoosterSite
    if random.random() < 0.05:  # 10% BoosterAvatarElite
        sobre.append(random.choice(cartes_Beta["BoosterAvatar"]))
    else:  # 24% Unique
        sobre.append(random.choice(cartes_Beta["Booster"]))
    return sobre
    
def generar_sobre_AL():
    sobre = []
        # 3 Exceptional
    sobre.extend(random.sample(cartes_AL["Exceptional"], 3))
    # 1 Elite o Unique
    if random.random() < 0.8:  # 76% Elite
        sobre.append(random.choice(cartes_AL["Elite"]))
    else:  # 24% Unique
        sobre.append(random.choice(cartes_AL["Unique"]))
    # 11 Ordinary
    sobre.extend(random.sample(cartes_AL["Ordinary"], 11))
    
    return sobre

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/Pack/<int:n>")
def sobres(n):
    return jsonify([generar_sobre() for _ in range(n)])

@app.route("/export_xlsx/<int:jocs>/<int:n1>/<int:n2>")
def export_xlsx(jocs, n1, n2):
    wb = Workbook()
    # Prioritat dels elements
    elem_order = {"DB": 0, "Air": 1, "Earth": 2, "Fire": 3, "Water": 4, "MC": 5}

    for jugador in range(1, jocs+1):
        # Crear full per cada jugador
        if jugador == 1:
            ws = wb.active
            ws.title = f"Player {jugador}"
        else:
            ws = wb.create_sheet(title=f"Player {jugador}")

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
