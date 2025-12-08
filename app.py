from flask import Flask, render_template, jsonify, Response, send_file
import pandas as pd
import random, io
from openpyxl import Workbook

app = Flask(__name__)

# --- CARREGA FITXERS CSV ---
cartes_dfBeta = pd.read_csv("FontBeta.csv")
cartes_dfDL = pd.read_csv("FontDL.csv")
cartes_dfAL = pd.read_csv("FontAL.csv")
cartes_dfGothic = pd.read_csv("FontGothic.csv")

# --- SEPARA PER TIPUS DE CARTA ---
cartes_Beta = { "Ordinary": cartes_dfBeta[cartes_dfBeta["tipus"] == 
               "Ordinary"].to_dict(orient="records"), 
               "Booster": cartes_dfBeta[cartes_dfBeta["tipus"] == "Booster"].to_dict(orient="records"), 
               "BoosterAvatar": cartes_dfBeta[cartes_dfBeta["tipus"] == "BoosterAvatar"].to_dict(orient="records"), 
               "Exceptional": cartes_dfBeta[cartes_dfBeta["tipus"] == "Exceptional"].to_dict(orient="records"),
               "Elite": cartes_dfBeta[cartes_dfBeta["tipus"] == "Elite"].to_dict(orient="records"),
               "Unique": cartes_dfBeta[cartes_dfBeta["tipus"] == "Unique"].to_dict(orient="records"), 
      }
cartes_AL = { "Ordinary": cartes_dfAL[cartes_dfAL["tipus"] == "Ordinary"].to_dict(orient="records"), 
             "Exceptional": cartes_dfAL[cartes_dfAL["tipus"] == "Exceptional"].to_dict(orient="records"),
             "Elite": cartes_dfAL[cartes_dfAL["tipus"] == "Elite"].to_dict(orient="records"), 
             "Unique": cartes_dfAL[cartes_dfAL["tipus"] == "Unique"].to_dict(orient="records"),
            }

cartes_Gothic = { "Ordinary": cartes_dfGothic[cartes_dfAL["tipus"] == "Ordinary"].to_dict(orient="records"), 
             "Exceptional": cartes_dfGothic[cartes_dfAL["tipus"] == "Exceptional"].to_dict(orient="records"),
             "Elite": cartes_dfGothic[cartes_dfAL["tipus"] == "Elite"].to_dict(orient="records"), 
             "Unique": cartes_dfGothic[cartes_dfAL["tipus"] == "Unique"].to_dict(orient="records"),
            }

cartes_Beta = separar_cartes(cartes_dfBeta)
cartes_AL = separar_cartes(cartes_dfAL)
cartes_Gothic = separar_cartes(cartes_dfGothic)
cartes_DL = cartes_dfDL.to_dict(orient="records")

# --- GENERADORS DE SOBRES ---
def generar_sobre_Beta():
    sobre = []
    sobre.extend(random.sample(cartes_Beta["Exceptional"], 3))
    if random.random() < 0.76:
        sobre.append(random.choice(cartes_Beta["Elite"]))
    else:
        sobre.append(random.choice(cartes_Beta["Unique"]))
    sobre.extend(random.sample(cartes_Beta["Ordinary"], 10))
    if random.random() < 0.05:
        sobre.append(random.choice(cartes_Beta["BoosterAvatar"]))
    else:
        sobre.append(random.choice(cartes_Beta["Booster"]))
    return sobre

def generar_sobre_AL():
    sobre = []
    sobre.extend(random.sample(cartes_AL["Exceptional"], 3))
    if random.random() < 0.8:
        sobre.append(random.choice(cartes_AL["Elite"]))
    else:
        sobre.append(random.choice(cartes_AL["Unique"]))
    sobre.extend(random.sample(cartes_AL["Ordinary"], 11))
    return sobre

def generar_sobre_Gothic():
    sobre = []
    sobre.extend(random.sample(cartes_Gothic["Exceptional"], 3))
    if random.random() < 0.8:
        sobre.append(random.choice(cartes_Gothic["Elite"]))
    else:
        sobre.append(random.choice(cartes_Gothic["Unique"]))
    sobre.extend(random.sample(cartes_Gothic["Ordinary"], 11))
    return sobre

def generar_sobre_DL():
    return cartes_DL.copy()

# --- RUTES ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/Pack/<int:n>")
def sobres(n):
    return jsonify([generar_sobre_Beta() for _ in range(n)])

@app.route("/export_xlsx/<int:jocs>/<int:beta>/<int:al>/<int:gothic>/<int:dl>")
def export_xlsx(jocs, beta, al, gothic, dl):
    wb = Workbook()
    elem_order = {"DB": 0, "Air": 1, "Earth": 2, "Fire": 3, "Water": 4, "MC": 5}

    total_sobres = beta + al + gothic

    # Validacions igual que abans, però ara amb Gothic
    if dl == 1 and total_sobres != 5:
        return Response("❌ Error: Amb DragonLord activat, els sobres Beta+AL+Gothic han de sumar EXACTAMENT 5.", status=400)
    if dl == 0 and total_sobres != 6:
        return Response("❌ Error: Sense DragonLord, els sobres Beta+AL+Gothic han de sumar EXACTAMENT 6.", status=400)

    # Generació per jugador
    for jugador in range(1, jocs + 1):
        ws = wb.active if jugador == 1 else wb.create_sheet(title=f"P{jugador}")
        if jugador == 1:
            ws.title = f"P{jugador}"

        ws.append(["Avatars", "Spells", "Sites"])

        cartes_jugador = []

        for _ in range(beta):
            cartes_jugador.extend(generar_sobre_Beta())
        for _ in range(al):
            cartes_jugador.extend(generar_sobre_AL())
        for _ in range(gothic):
            cartes_jugador.extend(generar_sobre_Gothic())
        if dl == 1:
            cartes_jugador.extend(generar_sobre_DL())

        avatars = sorted([c["nom"] for c in cartes_jugador if c["cat"] == "Avatar"])
        spells = [c for c in cartes_jugador if c["cat"] == "Spell"]
        sites = sorted([c["nom"] for c in cartes_jugador if c["cat"] == "Site"])

        spells_sorted = sorted(spells, key=lambda c: (elem_order.get(c["elem"], 99), c["nom"]))
        spells_names = [f"{c['nom']}" for c in spells_sorted]

        max_len = max(len(avatars), len(spells_names), len(sites))
        for i in range(max_len):
            fila = [
                avatars[i] if i < len(avatars) else "",
                spells_names[i] if i < len(spells_names) else "",
                sites[i] if i < len(sites) else "",
            ]
            ws.append(fila)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="lots_jugadors.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    app.run(debug=True)
