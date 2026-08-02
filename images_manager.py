import requests
import os
import re
import unicodedata

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