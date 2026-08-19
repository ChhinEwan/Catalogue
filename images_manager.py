import requests
import os
import re
import unicodedata
from PIL import Image, ImageDraw

def telecharger_image(url, nom_fichier):

    if not url:
        return ""

    dossier = "images"

    os.makedirs(dossier, exist_ok=True)

    chemin = os.path.join(dossier, nom_fichier)

    response = requests.get(url)

    with open(chemin, "wb") as fichier:
        fichier.write(response.content)

    return chemin

def supprimer_image(nom_fichier):

    chemin = os.path.join("images", nom_fichier)

    if os.path.exists(chemin):
        os.remove(chemin)


def vider_images():

    dossier = "images"

    if not os.path.isdir(dossier):
        return

    for nom_fichier in os.listdir(dossier):
        chemin = os.path.join(dossier, nom_fichier)
        if os.path.isfile(chemin):
            os.remove(chemin)

def nettoyer_nom(texte):

    texte = unicodedata.normalize("NFD", texte)
    texte = texte.encode("ascii", "ignore").decode("utf-8")

    texte = texte.lower()

    texte = re.sub(r"[^a-z0-9]+", "_", texte)

    return texte.strip("_")


def creer_nom_image(livre):

    titre = nettoyer_nom(livre.titre)

    if livre.isbn:
        return f"{livre.isbn}_{titre}.jpg"

    else:
        return f"{titre}.jpg"


def creer_couverture_reliure(nom_fichier=None, largeur=120, hauteur=180, afficher_texte=True):
    dossier = "images"
    os.makedirs(dossier, exist_ok=True)

    if not nom_fichier:
        nom_fichier = "reliure_defaut.jpg"
    elif not nom_fichier.lower().endswith((".jpg", ".jpeg", ".png")):
        nom_fichier = f"{nom_fichier}.jpg"

    chemin = os.path.join(dossier, nom_fichier)

    image = Image.new("RGB", (largeur, hauteur), "#7a4a2a")
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, largeur, hauteur), outline="#3b1f15", width=4)
    draw.rectangle((8, 8, largeur - 8, hauteur - 8), outline="#9b5d3b", width=2)
    draw.rectangle((16, 0, 28, hauteur), fill="#4d2c1c")

    if afficher_texte:
        draw.text((largeur // 2, hauteur // 2), "RELIURE", fill="#f3d7a0", anchor="mm", stroke_width=1, stroke_fill="#3b1f15")

    for y in range(0, hauteur, 12):
        couleur = (max(0, 122 - (y // 12) * 3), max(0, 74 - (y // 12) * 2), max(0, 42 - (y // 12) * 2))
        draw.line((32, y, largeur - 12, y), fill=couleur, width=2)

    image.save(chemin, "JPEG", quality=90)
    return chemin


def obtenir_vignette_sans_image():
    return creer_couverture_reliure("vignetteLivreMarron.jpg", afficher_texte=False)