CatalogueBA
===========

Description
-----------
CatalogueBA est une application de gestion de livres qui permet de rechercher des livres via l'API Google Books, d'enregistrer une bibliothèque locale, d'exporter vers Excel et de travailler via une interface graphique.

Utilisation
-----------

1. CLI (interface en ligne de commande)

   - Lancer : `python main.py`
   - Options disponibles :
     - Rechercher un livre
     - Voir mes livres
     - Rechercher dans ma bibliothèque
     - Supprimer un livre
     - Export Excel
     - Quitter
     - Vider toute la bibliothèque (option 1721)

2. GUI (interface graphique)

   - Lancer : `python gui.py`
   - Une fenêtre s'ouvre avec :
     - un champ de recherche Google Books
     - une liste de résultats en ligne
     - un bouton pour ajouter un livre à la bibliothèque
     - la bibliothèque locale affichée
     - un bouton pour supprimer un livre
     - un bouton pour vider toute la bibliothèque
     - un bouton pour exporter vers Excel
     - une zone de détails pour afficher la fiche du livre sélectionné

Prérequis
---------

- Python 3.x
- packages Python :
  - requests
  - python-dotenv
  - openpyxl
  - Pillow

Remarques
---------

- Le fichier `.env` doit contenir la clé API Google Books :
  `API_KEY=ta_cle_api`
- Le GUI utilise la même logique métier que le CLI, de sorte que la bibliothèque est partagée.
- Si le fichier `bibliotheque.xlsx` est ouvert lors de l'export, fermez-le avant de relancer l'export.
