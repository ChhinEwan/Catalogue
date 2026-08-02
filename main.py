from api_google import rechercher_livre
from database import creer_base
from database import enregistrer_livre, lister_livres, livre_existe, supprimer_livre, rechercher_dans_bibliotheque
from images_manager import telecharger_image, supprimer_image, creer_nom_image
from excel_manager import exporter_excel


def main():
    creer_base()

    while True:
        print("\n===== Catalogue Livres =====")
        print("1 - Rechercher un livre")
        print("2 - Voir mes livres")
        print("3 - Rechercher dans ma bibliothèque")
        print("4 - Supprimer un livre")
        print("5 - Export Excel")
        print("6 - Quitter")

        choix_menu = input("Votre choix : ")

        if choix_menu == "1":
            recherche = input("Quel livre cherchez-vous ? ")

            livres = rechercher_livre(recherche)

            if livres:
                for numero, livre in enumerate(livres, start=1):
                    print("\n----------------")
                    print("Livre", numero)
                    print("Titre :", livre.titre)
                    print("Auteur :", livre.auteur)
                    print("ISBN :", livre.isbn)

                choix = int(input("Choisir un livre : ")) - 1

                if 0 <= choix < len(livres):
                    livre_choisi = livres[choix]

                    if livre_existe(livre_choisi):
                        print("Ce livre existe déjà")
                    else:
                        enregistrer_livre(livre_choisi)

                        nom_image = creer_nom_image(livre_choisi)
                        print(nom_image)

                        fichier = telecharger_image(
                            livre_choisi.image,
                            nom_image
                        )

                        print("Livre enregistré !")
                else:
                    print("Choix invalide")

        elif choix_menu == "2":
            livres_enregistres = lister_livres()

            if livres_enregistres:
                print("\n===== Ma bibliothèque =====")

                for numero, livre in enumerate(livres_enregistres, start=1):
                    print("\n----------------")
                    print("Livre", numero)
                    livre.afficher_details()
            else:
                print("Votre bibliothèque est vide")

        elif choix_menu == "3":
            recherche = input("Quel livre recherchez-vous ? ")

            livres_trouves = rechercher_dans_bibliotheque(recherche)

            if livres_trouves:
                print("\n===== Résultats =====")

                for numero, livre in enumerate(livres_trouves, start=1):
                    print("\n----------------")
                    print("Livre", numero)
                    livre.afficher_details()
            else:
                print("Aucun livre trouvé dans votre bibliothèque")

        elif choix_menu == "4":
            livres_enregistres = lister_livres()

            if livres_enregistres:
                print("\n===== Ma bibliothèque =====")

                for numero, livre in enumerate(livres_enregistres, start=1):
                    print("\n----------------")
                    print("Livre", numero)
                    livre.afficher_details()

                choix = int(input("Choisir un livre à supprimer : ")) - 1

                if 0 <= choix < len(livres_enregistres):
                    livre_choisi = livres_enregistres[choix]

                    supprimer_livre(livre_choisi.isbn)
                    supprimer_image(creer_nom_image(livre_choisi))
                    print("Livre supprimé !")
                else:
                    print("Choix invalide")
            else:
                print("Votre bibliothèque est vide")

        elif choix_menu == "5":
            livres_enregistres = lister_livres()

            if livres_enregistres:
                fichier = exporter_excel(livres_enregistres)
                print("Export terminé :", fichier)
            else:
                print("Votre bibliothèque est vide")

        elif choix_menu == "6":
            print("À bientôt")
            break

        else:
            print("Choix invalide")


if __name__ == "__main__":
    main()