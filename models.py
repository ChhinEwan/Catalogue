class Livre:

    def __init__(self, titre, auteur, description, genre, date_parution, image, isbn):
        self.titre = titre
        self.auteur = auteur
        self.description = description
        self.genre = genre
        self.date_parution = date_parution
        self.image = image
        self.isbn = isbn

    def __str__(self):
        return f"{self.titre} - {self.auteur}"
    
    def afficher_details(self):
        print("Titre :", self.titre)
        print("Auteur :", self.auteur)
        print("Genre :", self.genre)
        print("Date de parution :", self.date_parution or "N/A")
        print("ISBN :", self.isbn)
        print("Description :", self.description)
        print("Image :", self.image)