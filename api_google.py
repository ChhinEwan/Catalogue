import requests
from config import API_KEY
from models import Livre

GENRE_FR = {
    "Fiction": "Fiction",
    "Juvenile Fiction": "Roman jeunesse",
    "Young Adult Fiction": "Jeunesse",
    "Fantasy": "Fantastique",
    "Science Fiction": "Science-fiction",
    "Mystery & Detective": "Policier / Enquête",
    "Suspense": "Thriller",
    "Romance": "Romance",
    "Historical Fiction": "Roman historique",
    "Horror": "Horreur",
    "Adventure": "Aventure",
    "Biography & Autobiography": "Biographie / Autobiographie",
    "History": "Histoire",
    "Science": "Science",
    "Mathematics": "Mathématiques",
    "Psychology": "Psychologie",
    "Philosophy": "Philosophie",
    "Religion": "Religion",
    "Spirituality": "Spiritualité",
    "Self-Help": "Développement personnel",
    "Business & Economics": "Affaires / Économie",
    "Computers": "Informatique",
    "Technology": "Technologie",
    "Health & Fitness": "Santé / Fitness",
    "Cooking": "Cuisine",
    "Travel": "Voyage",
    "Art": "Art",
    "Music": "Musique",
    "Sports & Recreation": "Sports / Loisirs",
    "Nature": "Nature",
    "Law": "Droit",
    "Politics": "Politique",
    "Education": "Éducation",
    "Reference": "Référence",
    "Crafts & Hobbies": "Loisirs créatifs",
    "Parenting": "Parentalité",
    "Comics": "Bandes dessinées",
    "Poetry": "Poésie",
    "Drama": "Théâtre",
    "Boarding schools": "Internat",
    "England": "Angleterre",
    "United States": "États-Unis",
    "Juvenile Nonfiction": "Documentaire jeunesse"
}


def normaliser_genres(categories):
    if not categories:
        return ""

    resultats = []
    for cat in categories:
        cat_norm = GENRE_FR.get(cat)
        if not cat_norm and "comics" in cat.lower():
            cat_norm = "Bande dessinée"
        resultats.append(cat_norm or cat)
    return ", ".join(resultats)


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
        categories = volume.get("categories", [])
        genre = normaliser_genres(categories)
        date_raw = volume.get("publishedDate", "") or volume.get("pubDate", "")
        date_parution = date_raw.split("-")[0] if date_raw else ""
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
            date_parution,
            image,
            isbn
        )

        livres.append(livre)

    return livres