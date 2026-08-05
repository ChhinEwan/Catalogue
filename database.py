import sqlite3
from models import Livre

def creer_base():

    connexion = sqlite3.connect("livres.db")
    curseur = connexion.cursor()

    curseur.execute("""
    CREATE TABLE IF NOT EXISTS livres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT,
        auteur TEXT,
        description TEXT,
        genre TEXT,
        date_parution TEXT,
        image TEXT,
        isbn TEXT,
        publisher TEXT
    )
    """)

    curseur.execute("PRAGMA table_info(livres)")
    colonnes = [ligne[1] for ligne in curseur.fetchall()]
    if "publisher" not in colonnes:
        curseur.execute("ALTER TABLE livres ADD COLUMN publisher TEXT")

    connexion.commit()
    connexion.close()


def enregistrer_livre(livre):

    connexion = sqlite3.connect("livres.db")

    curseur = connexion.cursor()

    curseur.execute("""
    INSERT INTO livres (titre, auteur, description, genre, date_parution, image, isbn, publisher)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        livre.titre,
        livre.auteur,
        livre.description,
        livre.genre,
        livre.date_parution,
        livre.image,
        livre.isbn,
        getattr(livre, "editeur", "")
    ))

    connexion.commit()

    connexion.close()

def lister_livres():

    connexion = sqlite3.connect("livres.db")

    curseur = connexion.cursor()

    curseur.execute("SELECT * FROM livres")

    resultats = curseur.fetchall()

    livres = []

    for ligne in resultats:
        publisher = ligne[8] if len(ligne) > 8 else ""
        livre = Livre(
            ligne[1],
            ligne[2],
            ligne[3],
            ligne[4],
            ligne[5],
            ligne[6],
            ligne[7],
            publisher
        )

        livres.append(livre)

    connexion.close()

    return livres

def livre_existe(livre):

    connexion = sqlite3.connect("livres.db")
    curseur = connexion.cursor()

    if livre.isbn != "":

        curseur.execute(
            """
            SELECT * FROM livres
            WHERE isbn = ?
            """,
            (livre.isbn,)
        )

    else:

        curseur.execute(
            """
            SELECT * FROM livres
            WHERE titre = ?
            AND auteur = ?
            """,
            (livre.titre, livre.auteur)
        )

    resultat = curseur.fetchone()

    connexion.close()

    return resultat is not None

def supprimer_livre(isbn):

    connexion = sqlite3.connect("livres.db")

    curseur = connexion.cursor()

    curseur.execute(
        """
        DELETE FROM livres
        WHERE isbn = ?
        """,
        (isbn,)
    )

    connexion.commit()
    connexion.close()


def vider_bibliotheque():

    connexion = sqlite3.connect("livres.db")

    curseur = connexion.cursor()

    curseur.execute("DELETE FROM livres")

    connexion.commit()
    connexion.close()

def rechercher_dans_bibliotheque(recherche):

    connexion = sqlite3.connect("livres.db")

    curseur = connexion.cursor()

    requete = """
        SELECT * FROM livres
        WHERE titre LIKE ?
        OR auteur LIKE ?
        OR genre LIKE ?
        OR isbn LIKE ?
        OR publisher LIKE ?
        """

    motif = f"%{recherche}%"
    curseur.execute(requete, (motif, motif, motif, motif, motif))

    resultats = curseur.fetchall()

    connexion.close()

    livres = []

    for ligne in resultats:
        publisher = ligne[8] if len(ligne) > 8 else ""
        livre = Livre(
            ligne[1],
            ligne[2],
            ligne[3],
            ligne[4],
            ligne[5],
            ligne[6],
            ligne[7],
            publisher
        )

        livres.append(livre)

    return livres