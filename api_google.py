import requests
from config import API_KEY
from models import Livre


def rechercher_livre(titre):
    url = (
        f"https://www.googleapis.com/books/v1/volumes"
        f"?q={titre}&key={API_KEY}"
    )

    response = requests.get(url)

    print(url)
    print(response.status_code)
    data = response.json()

    if "items" not in data:
        return []

    livres = []

    for item in data["items"]:
        volume = item["volumeInfo"]

        titre = volume.get("title", "")
        auteur = volume.get("authors", ["Inconnu"])[0]
        description = volume.get("description", "")
        genre = volume.get("categories", [""])[0]
        image = volume.get("imageLinks", {}).get("thumbnail", "")

        '''
        if image:
            image = image.replace("zoom=1", "zoom=2")

        '''    
                # Récupération ISBN
        isbn = ""

        for identifiant in volume.get("industryIdentifiers", []):
            if identifiant["type"] == "ISBN_13":
                isbn = identifiant["identifier"]
                break

        # Si pas d'ISBN-13, on cherche un ISBN-10
        if isbn == "":
            for identifiant in volume.get("industryIdentifiers", []):
                if identifiant["type"] == "ISBN_10":
                    isbn = identifiant["identifier"]
                    break

        livre = Livre(
            titre,
            auteur,
            description,
            genre,
            image,
            isbn
        )

        livres.append(livre)

    return livres