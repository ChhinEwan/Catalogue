import time
import requests
from requests.exceptions import RequestException
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
        if not cat_norm and "comic" in cat.lower():
            cat_norm = "Bandes dessinées"
        resultats.append(cat_norm or cat)
    return ", ".join(resultats)


def _rechercher_livre_langue(titre, langue, start_index=0, max_results=20):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": titre,
        "maxResults": max_results,
        "startIndex": start_index,
        "langRestrict": langue
    }
    if API_KEY:
        params["key"] = API_KEY

    headers = {"User-Agent": "CatalogueBA/1.0"}
    tentatives = 4
    retryable_statuses = {429, 500, 502, 503, 504}

    for tentative in range(1, tentatives + 1):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
        except RequestException as err:
            if tentative == tentatives:
                raise RuntimeError("Erreur réseau lors de la recherche Google Books. Vérifiez votre connexion.") from err
            time.sleep(2 ** tentative)
            continue

        try:
            data = response.json()
        except ValueError:
            if tentative == tentatives:
                raise RuntimeError(f"Réponse invalide de l'API Google Books (statut {response.status_code}).")
            time.sleep(2 ** tentative)
            continue

        if response.status_code == 200:
            break

        message = None
        if isinstance(data, dict):
            message = data.get("error", {}).get("message")

        if response.status_code in retryable_statuses and tentative < tentatives:
            time.sleep(2 ** tentative)
            continue

        if not message:
            message = response.reason or "Erreur inconnue"

        if response.status_code in retryable_statuses:
            raise RuntimeError(f"Google Books temporairement indisponible. Réessayez plus tard. ({message} code {response.status_code})")

        raise RuntimeError(f"Google Books API : {message} (code {response.status_code})")

    total_items = data.get("totalItems", 0) if isinstance(data, dict) else 0
    if "items" not in data:
        return [], total_items

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

        isbn = ""
        for identifiant in volume.get("industryIdentifiers", []):
            if identifiant["type"] == "ISBN_13":
                isbn = identifiant["identifier"]
                break

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

    return livres, total_items


def _fusionner_livres(livres):
    vus = set()
    result = []
    for livre in livres:
        cle = livre.isbn.strip() if livre.isbn else f"{livre.titre}:{livre.auteur}".lower().strip()
        if not cle:
            continue
        if cle in vus:
            continue
        vus.add(cle)
        result.append(livre)
    return result


def rechercher_livre(titre, start_index=0, return_total=False, max_results=20):
    titre = (titre or "").strip()
    if not titre:
        return [] if not return_total else ([], 0)

    livres_fr, total_items = _rechercher_livre_langue(titre, "fr", start_index=start_index, max_results=max_results)
    livres_fr = _fusionner_livres(livres_fr)
    if return_total:
        return livres_fr, total_items
    return livres_fr
