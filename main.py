from api_google import rechercher_livre
from database import creer_base
from database import enregistrer_livre, lister_livres, livre_existe, supprimer_livre, rechercher_dans_bibliotheque, vider_bibliotheque
from images_manager import telecharger_image, supprimer_image, creer_nom_image, vider_images
from excel_manager import exporter_excel

LINE_WIDTH = 70


def afficher_entete(titre):
    print("\n" + "=" * LINE_WIDTH)
    print(titre.center(LINE_WIDTH))
    print("=" * LINE_WIDTH)


def afficher_separator():
    print("-" * LINE_WIDTH)


def afficher_liste_livres(livres, titre):
    afficher_entete(titre)
    for numero, livre in enumerate(livres, start=1):
        print(f"{numero}. {livre.titre}")
        print(f"   Auteur : {livre.auteur} | Date : {livre.date_parution or 'Date inconnu'} | Genre : {livre.genre or 'Genre non repertorie'}")
        afficher_separator()


def afficher_resultats_recherche(livres):
    afficher_entete("Résultats de la recherche")
    for numero, livre in enumerate(livres, start=1):
        print(f"{numero}. {livre.titre} — {livre.auteur}")
        print(f"   Date : {livre.date_parution or 'Date inconnu'} | Genre : {livre.genre or 'Genre non repertorie'}")
        print(f"   ISBN : {livre.isbn or 'ISBN non repertorié'}")
        afficher_separator()


def demander_entier(prompt, minimum=None, maximum=None):
    try:
        valeur = int(input(prompt))
    except ValueError:
        return None

    if minimum is not None and valeur < minimum:
        return None
    if maximum is not None and valeur > maximum:
        return None

    return valeur


def main():
    creer_base()

    while True:
        afficher_entete("Catalogue Livres")
        print("1 - Rechercher un livre")
        print("2 - Voir mes livres")
        print("3 - Rechercher dans ma bibliothèque")
        print("4 - Supprimer un livre")
        print("5 - Export Excel")
        print("6 - Quitter")
        print("1721 - Vider toute la bibliothèque")

        choix_menu = input("Votre choix : ")

        if choix_menu == "1":
            recherche = input("Quel livre cherchez-vous ? ")

            try:
                livres = rechercher_livre(recherche)
            except Exception as err:
                print("Erreur de recherche :", err)
                continue

            if livres:
                afficher_resultats_recherche(livres)
                choix = demander_entier("Choisir un livre (numéro) : ", minimum=1, maximum=len(livres))
                if choix is not None:
                    livre_choisi = livres[choix - 1]

                    if livre_existe(livre_choisi):
                        print("Ce livre existe déjà")
                    else:
                        enregistrer_livre(livre_choisi)
                        nom_image = creer_nom_image(livre_choisi)
                        fichier = telecharger_image(livre_choisi.image, nom_image)

                        print("Livre enregistré !")
                        print(f"Image téléchargée : {fichier}")
                else:
                    print("Choix invalide")
            else:
                print("Aucun livre trouvé.")

        elif choix_menu == "2":
            livres_enregistres = lister_livres()

            if livres_enregistres:
                afficher_liste_livres(livres_enregistres, "Ma bibliothèque")
            else:
                print("Votre bibliothèque est vide")

        elif choix_menu == "3":
            recherche = input("Recherche titre / auteur / genre / ISBN : ")

            livres_trouves = rechercher_dans_bibliotheque(recherche)

            if livres_trouves:
                afficher_liste_livres(livres_trouves, "Résultats de la recherche")
            else:
                print("Aucun livre trouvé dans votre bibliothèque")

        elif choix_menu == "4":
            livres_enregistres = lister_livres()

            if livres_enregistres:
                afficher_liste_livres(livres_enregistres, "Ma bibliothèque")
                choix = demander_entier("Choisir un livre à supprimer : ", minimum=1, maximum=len(livres_enregistres))
                if choix is not None:
                    livre_choisi = livres_enregistres[choix - 1]
                    supprimer_livre(livre_choisi.isbn)
                    supprimer_image(creer_nom_image(livre_choisi))
                    print("Livre supprimé !")
                else:
                    print("Choix invalide")
            else:
                print("Votre bibliothèque est vide")

        elif choix_menu == "1721":
            livres_enregistres = lister_livres()

            if livres_enregistres:
                confirmation = input("Confirmer la suppression totale de la bibliothèque ? (o/N) : ")
                if confirmation.lower() == "o":
                    vider_bibliotheque()
                    vider_images()
                    print("Bibliothèque vidée.")
                else:
                    print("Opération annulée")
            else:
                print("Votre bibliothèque est déjà vide")

        elif choix_menu == "5":
            livres_enregistres = lister_livres()

            if livres_enregistres:
                try:
                    fichier = exporter_excel(livres_enregistres)
                    print("Export terminé :", fichier)
                except PermissionError as err:
                    print("Erreur lors de l'export :", err)
                except Exception as err:
                    print("Erreur lors de l'export :", err)
            else:
                print("Votre bibliothèque est vide")

        elif choix_menu == "6":
            print("À bientôt")
            break

        else:
            print("Choix invalide")


if __name__ == "__main__":
    main()