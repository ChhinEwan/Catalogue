from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.utils import get_column_letter
import os
from images_manager import creer_nom_image


def exporter_excel(livres):

    fichier = "bibliotheque.xlsx"

    classeur = Workbook()
    feuille = classeur.active

    feuille.title = "Livres"

    feuille.append([
        "Titre",
        "Auteur",
        "Genre",
        "ISBN",
        "Description",
        "Image"
    ])
    for livre in livres:

        ligne = feuille.max_row + 1

        feuille.append([
            livre.titre,
            livre.auteur,
            livre.genre,
            livre.isbn,
            livre.description,
            ""
        ])
        
        chemin_image = os.path.join(
            "images",
            creer_nom_image(livre)
        )

        if os.path.exists(chemin_image):

            image = Image(chemin_image)

            image.width = 100
            image.height = 150

            feuille.add_image(
                image,
                f"F{ligne}"
            )
    
    classeur.save(fichier)

    return fichier